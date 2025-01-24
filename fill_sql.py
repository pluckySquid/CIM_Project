import xml.etree.ElementTree as ET
import os
import sqlite3
import re

def parse_sql_schema(schema_file):
    """
    Parses the SQL schema file to extract table names, their columns,
    and handle FOREIGN KEY constraints for SQLite compatibility.

    Returns:
        tables (dict): Dictionary mapping table names to a list of their columns.
        create_script (str): Combined and adjusted CREATE TABLE statements.
    """
    tables = {}
    create_statements = []
    current_table = None
    current_statement_lines = []
    current_columns = []
    foreign_keys = []

    with open(schema_file, 'r') as file:
        lines = file.readlines()

    in_create_table = False

    for line in lines:
        line_stripped = line.strip()

        # Detect the start of a CREATE TABLE statement
        if line_stripped.upper().startswith("CREATE TABLE"):
            in_create_table = True
            current_statement_lines = [line]  # Start collecting lines for this table

            # Extract table name from CREATE TABLE "TableName"
            parts = line_stripped.split('"')
            if len(parts) >= 2:
                current_table = parts[1]
                tables[current_table] = []
                current_columns = []
                foreign_keys = []
            else:
                current_table = None
                print(f"Warning: Could not parse table name in line: {line}")

        elif in_create_table:
            current_statement_lines.append(line)

            # Check if the line ends the CREATE TABLE block
            if line_stripped.endswith(");"):
                in_create_table = False
                # Combine the collected lines into one CREATE TABLE statement
                statement = "".join(current_statement_lines)

                # Extract column names and FOREIGN KEY constraints
                for col_line in current_statement_lines:
                    col_line_stripped = col_line.strip()
                    # Match column definitions: "columnName" DATA_TYPE ...
                    col_match = re.match(r'^"([^"]+)"\s+([\w\s]+)', col_line_stripped)
                    if col_match:
                        column_name = col_match.group(1)
                        tables[current_table].append(column_name)
                    # Match FOREIGN KEY constraints
                    fk_match = re.match(r'^FOREIGN KEY\s*\(([^)]+)\)\s*REFERENCES\s+"([^"]+)"\s*\(([^)]+)\)', col_line_stripped, re.IGNORECASE)
                    if fk_match:
                        fk_columns = fk_match.group(1).strip()
                        ref_table = fk_match.group(2).strip()
                        ref_columns = fk_match.group(3).strip()
                        foreign_keys.append((fk_columns, ref_table, ref_columns))

                # Modify the CREATE TABLE statement for SQLite
                # SQLite requires FOREIGN KEY constraints to be within the table definition
                # and does not support certain syntax variations.
                # We'll reconstruct the CREATE TABLE statement accordingly.

                # Remove existing FOREIGN KEY lines
                adjusted_statement_lines = []
                for col_line in current_statement_lines:
                    if not re.match(r'^FOREIGN KEY', col_line.strip(), re.IGNORECASE):
                        adjusted_statement_lines.append(col_line)

                # Reconstruct the CREATE TABLE statement
                adjusted_statement = "".join(adjusted_statement_lines)

                # Append FOREIGN KEY constraints at the end of column definitions
                if foreign_keys:
                    fk_constraints = []
                    for fk in foreign_keys:
                        fk_columns, ref_table, ref_columns = fk
                        fk_constraints.append(f'    FOREIGN KEY ({fk_columns}) REFERENCES "{ref_table}" ({ref_columns})')
                    # Insert the FOREIGN KEY constraints before the closing parenthesis
                    adjusted_statement = adjusted_statement.rstrip(");") + ",\n" + ",\n".join(fk_constraints) + "\n);"

                create_statements.append(adjusted_statement)

                # Reset for the next table
                current_table = None
                current_statement_lines = []
                current_columns = []
                foreign_keys = []

    # Combine all adjusted CREATE TABLE statements into a single script
    create_script = "\n".join(create_statements)
    return tables, create_script

def create_sqlite_db(db_file, create_script):
    """
    Creates (or overwrites) a SQLite database at db_file,
    then executes the create_script to build the schema.

    Returns:
        conn (sqlite3.Connection): SQLite database connection object.
    """
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"Existing database '{db_file}' removed.")

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Enable foreign key support in SQLite
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Debug: Print the CREATE TABLE script
    print("=== CREATE TABLE Script ===")
    print(create_script)
    print("=== End of CREATE TABLE Script ===\n")

    try:
        cursor.executescript(create_script)
        conn.commit()
        print(f"SQLite database '{db_file}' created and tables defined successfully.\n")
    except sqlite3.OperationalError as e:
        print(f"Error executing CREATE TABLE script: {e}")
        conn.close()
        raise

    return conn

def extract_data_from_xml(xml_file, tables):
    """
    Parses the XML file and extracts data for the specified tables.
    """
    # Define namespaces
    namespaces = {
        'cim': 'http://iec.ch/TC57/2006/CIM-schema-cim10#',
        'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
        'etx': 'http://www.ercot.com/CIM11R0/2008/2.0/extension#',
        'spc': 'http://www.siemens-ptd/SHIMM1.0#'
    }

    data = {table: [] for table in tables}

    # Initialize parser
    context = ET.iterparse(xml_file, events=("end",))
    for event, elem in context:
        # Get the tag without namespace
        tag = elem.tag.split('}')[-1]
        
        if tag in tables:
            row = {}
            # Extract mRID from rdf:ID attribute
            mRID = elem.attrib.get(f'{{{namespaces["rdf"]}}}ID', '').strip()
            row['mRID'] = mRID if mRID else None  # Use None for NULL

            # Extract value
            value_elem = elem.find('cim:AnalogLimit.value', namespaces)
            if value_elem is not None and value_elem.text:
                try:
                    value = float(value_elem.text.strip())
                    row['value'] = value
                except ValueError:
                    print(f"Error: Invalid value '{value_elem.text}' for mRID {mRID}. Setting to NULL.")
                    row['value'] = None
            else:
                print(f"Warning: 'value' element missing for mRID {mRID}. Setting to NULL.")
                row['value'] = None

            # Extract LimitSet
            limit_set_elem = elem.find('cim:AnalogLimit.LimitSet', namespaces)
            if limit_set_elem is not None:
                limit_set_resource = limit_set_elem.attrib.get(f'{{{namespaces["rdf"]}}}resource', '').strip()
                if '#' in limit_set_resource:
                    limit_set = limit_set_resource.split('#')[-1]
                else:
                    limit_set = limit_set_resource
                row['LimitSet'] = limit_set if limit_set else None
            else:
                print(f"Warning: 'LimitSet' element missing for mRID {mRID}. Setting to NULL.")
                row['LimitSet'] = None

            # Handle all other columns generically
            for col in tables[tag]:
                if col in ("mRID", "value", "LimitSet"):
                    continue  # Already handled

                # Attempt to read from attribute
                val = elem.attrib.get(col)
                if val is not None and val.strip() != "":
                    row[col] = val.strip()
                else:
                    # Attempt to read from a child element ignoring namespace
                    child_found = False
                    for child in elem:
                        child_local = child.tag.split('}')[-1]
                        if child_local == col:
                            text_val = child.text.strip() if child.text else None
                            row[col] = text_val if text_val else None
                            child_found = True
                            break
                    if not child_found and col not in row:
                        row[col] = None

            # Debug: Print the extracted row
            print(f"Extracted Row: {row}")

            # Append to data
            data[tag].append(row)

            # Clear the element to save memory
            elem.clear()

    return data

def generate_sql_insert_statements(data, output_file):
    """
    Generates SQL INSERT statements from the extracted data.
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        for table, rows in data.items():
            for row in rows:
                columns = ', '.join([f'"{col}"' for col in row.keys()])
                values = []
                for col, val in row.items():
                    if val is None:
                        values.append("NULL")
                    elif isinstance(val, (int, float)):
                        values.append(f"{val}")
                    else:
                        # Escape single quotes in strings
                        escaped_val = val.replace("'", "''")
                        values.append(f"'{escaped_val}'")
                values_str = ', '.join(values)
                insert_stmt = f'INSERT INTO "{table}" ({columns}) VALUES ({values_str});\n'
                
                # Debug: Print the SQL statement
                print(f"Generated SQL: {insert_stmt.strip()}")
                
                # Write to file
                f.write(insert_stmt)

def insert_data_into_db(conn, data):
    """
    Inserts the extracted data into the SQLite database.
    """
    cursor = conn.cursor()
    for table, rows in data.items():
        for row in rows:
            columns = ', '.join([f'"{col}"' for col in row.keys()])
            placeholders = ', '.join(['?' for _ in row.keys()])
            insert_sql = f'INSERT INTO "{table}" ({columns}) VALUES ({placeholders})'

            # Prepare the parameters tuple
            params = tuple(row[col] for col in row.keys())

            try:
                cursor.execute(insert_sql, params)
            except sqlite3.IntegrityError as e:
                print(f"IntegrityError while inserting into '{table}': {e}. Row data: {row}")
                continue  # Skip this row
            except sqlite3.OperationalError as e:
                print(f"OperationalError while inserting into '{table}': {e}. Row data: {row}")
                continue  # Skip this row

    # Commit all inserts
    conn.commit()
    print(f"\nAll data inserted into the SQLite database successfully.\n")

def main():
    # Define file paths
    sql_schema_file = "TestProfile.sql"    # Path to your SQL schema
    xml_file = "test.xml"                  # Path to your XML file
    output_sql_file = "output_filled.sql"  # Path for the generated SQL
    db_file = "output.db"                  # SQLite database file to create

    # Check if files exist
    if not os.path.isfile(sql_schema_file):
        print(f"Error: SQL schema file '{sql_schema_file}' not found.")
        return
    if not os.path.isfile(xml_file):
        print(f"Error: XML file '{xml_file}' not found.")
        return

    # 1. Parse the SQL schema to get tables and columns
    print("Parsing SQL schema...")
    tables, create_script = parse_sql_schema(sql_schema_file)
    print("\nParsed SQL schema tables and columns:")
    for table, columns in tables.items():
        print(f"  Table: {table}, Columns: {columns}")

    # 2. Create the SQLite database and execute CREATE TABLE statements
    print("\nCreating SQLite database and setting up tables...")
    try:
        conn = create_sqlite_db(db_file, create_script)
    except sqlite3.OperationalError:
        print("Failed to create the SQLite database due to schema errors.")
        return

    # 3. Extract data from XML
    print("\nExtracting data from XML...")
    data = extract_data_from_xml(xml_file, tables)

    # 4. Insert data into the database
    print("\nInserting data into the SQLite database...")
    insert_data_into_db(conn, data)

    # 5. Generate SQL INSERT statements
    print("\nGenerating SQL INSERT statements...")
    generate_sql_insert_statements(data, output_sql_file)

    print(f"\nSQL INSERT statements have been written to '{output_sql_file}'.")
    print(f"SQLite database '{db_file}' has been populated with the extracted data.")

    # 6. Close the database connection
    conn.close()
    print("\nDatabase connection closed.")
    print("\nProcess completed successfully.")

if __name__ == "__main__":
    main()
