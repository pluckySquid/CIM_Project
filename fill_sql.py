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
                    # Match column definitions, allowing dots in column names
                    col_match = re.match(r'^"([^"]+)"\s*([\w.\s()]+)', col_line_stripped)
                    if col_match:
                        column_name = col_match.group(1)
                        tables[current_table].append(column_name)
                    # Match FOREIGN KEY constraints
                    fk_match = re.match(
                        r'^FOREIGN KEY\s*\(([^)]+)\)\s*REFERENCES\s+"([^"]+)"\s*\(([^)]+)\)',
                        col_line_stripped,
                        re.IGNORECASE
                    )
                    if fk_match:
                        fk_columns = fk_match.group(1).strip()
                        ref_table = fk_match.group(2).strip()
                        ref_columns = fk_match.group(3).strip()
                        foreign_keys.append((fk_columns, ref_table, ref_columns))

                # Modify the CREATE TABLE statement for SQLite
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
                        fk_constraints.append(
                            f'    FOREIGN KEY ({fk_columns}) REFERENCES "{ref_table}" ({ref_columns})'
                        )
                    adjusted_statement = adjusted_statement.rstrip(");") \
                        + ",\n" + ",\n".join(fk_constraints) + "\n);"

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

    Args:
        xml_file (str): Path to the XML file.
        tables (dict): Dictionary mapping table names to column lists.

    Returns:
        data (dict): Dictionary mapping table names to lists of row dictionaries.
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

            # Iterate through all child elements to extract data
            for child in elem:
                child_tag = child.tag.split('}')[-1]
                child_text = child.text.strip() if child.text else None

                # Handle references (attributes with resource)
                if child.tag.startswith(f'{{{namespaces["rdf"]}}}resource'):
                    ref_resource = child.attrib.get(f'{{{namespaces["rdf"]}}}resource', '').strip()
                    if '#' in ref_resource:
                        ref = ref_resource.split('#')[-1]
                    else:
                        ref = ref_resource
                    row[child_tag] = ref if ref else None
                else:
                    # Convert numeric values where possible
                    if child_text:
                        try:
                            if '.' in child_text:
                                row[child_tag] = float(child_text)
                            else:
                                row[child_tag] = int(child_text)
                        except ValueError:
                            row[child_tag] = child_text
                    else:
                        row[child_tag] = None

            # Handle all other columns that might not be present in the XML
            for col in tables[tag]:
                if col not in row:
                    row[col] = None  # Set missing columns to NULL

            # Debug: Print the extracted row
            #print(f"Extracted Row for table '{tag}': {row}")

            # Append to data
            data[tag].append(row)

            # Clear the element to save memory
            elem.clear()

    return data


def generate_sql_insert_statements(data, output_file):
    """
    Generates SQL INSERT statements from the extracted data.

    Args:
        data (dict): Dictionary mapping table names to lists of row dictionaries.
        output_file (str): Path to the output SQL file.
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
    If a column doesn't exist in the table, this function dynamically
    adds that column (as TEXT) to allow storing all data.
    """
    cursor = conn.cursor()

    # Helper function to add a missing column as TEXT
    def ensure_column_exists(table_name, column_name):
        try:
            cursor.execute(f'ALTER TABLE "{table_name}" ADD COLUMN "{column_name}" TEXT;')
            print(f'Added missing column "{column_name}" as TEXT in table "{table_name}"')
        except sqlite3.OperationalError as e:
            # If it's "duplicate column name", ignore
            if "duplicate column name" not in str(e).lower():
                print(f"Error adding column '{column_name}' to '{table_name}': {e}")

    for table, rows_ in data.items():
        # Retrieve existing columns from PRAGMA table_info
        cursor.execute(f'PRAGMA table_info("{table}");')
        existing_cols = [row_[1] for row_ in cursor.fetchall()]

        for row in rows_:
            # Ensure all columns exist in the DB; if not, create them as TEXT
            for col in row.keys():
                if col not in existing_cols:
                    ensure_column_exists(table, col)
                    existing_cols.append(col)

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
    xml_file = "NMMS_Model_CIM_Sep_ML1_1_09122023.xml"
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
