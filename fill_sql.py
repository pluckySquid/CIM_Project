import xml.etree.ElementTree as ET
import os

def parse_sql_schema(schema_file):
    """
    Parses the SQL schema file to extract table names and their columns.
    """
    tables = {}
    current_table = None

    with open(schema_file, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith("CREATE TABLE"):
                # Extract table name
                parts = line.split('"')
                if len(parts) >= 2:
                    current_table = parts[1]
                    tables[current_table] = []
                else:
                    print(f"Warning: Could not parse table name in line: {line}")
            elif current_table and line.startswith('"'):
                # Extract column name
                parts = line.split('"')
                if len(parts) >= 2:
                    column_name = parts[1]
                    tables[current_table].append(column_name)
                else:
                    print(f"Warning: Could not parse column name in line: {line}")
            elif line.startswith(");"):
                # End of table definition
                current_table = None

    return tables

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
            row['mRID'] = mRID if mRID else 'NULL'

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
                row['LimitSet'] = limit_set if limit_set else 'NULL'
            else:
                print(f"Warning: 'LimitSet' element missing for mRID {mRID}. Setting to NULL.")
                row['LimitSet'] = 'NULL'

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

def main():
    # Define file paths
    sql_schema_file = "TestProfile.sql"   # Path to your SQL schema
    xml_file = "test.xml"                 # Path to your XML file
    output_sql_file = "output_filled.sql" # Path for the generated SQL
    
    # Check if files exist
    if not os.path.isfile(sql_schema_file):
        print(f"Error: SQL schema file '{sql_schema_file}' not found.")
        return
    if not os.path.isfile(xml_file):
        print(f"Error: XML file '{xml_file}' not found.")
        return

    # Parse the SQL schema
    print("Parsing SQL schema...")
    tables = parse_sql_schema(sql_schema_file)
    print("Parsed SQL schema tables and columns:")
    for table, columns in tables.items():
        print(f"  Table: {table}, Columns: {columns}")

    # Extract data from XML
    print("\nExtracting data from XML...")
    data = extract_data_from_xml(xml_file, tables)

    # Generate SQL INSERT statements
    print("\nGenerating SQL INSERT statements...")
    generate_sql_insert_statements(data, output_sql_file)

    print(f"\nSQL INSERT statements have been written to '{output_sql_file}'.")

if __name__ == "__main__":
    main()
