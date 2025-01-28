import re

def parse_sql_schema(schema_file):
    """
    Parses the SQL schema file to extract table names and their columns.

    Args:
        schema_file (str): Path to the SQL schema file.

    Returns:
        dict: A dictionary mapping table names to a list of their column names.
    """
    # Read the entire content of the SQL schema file
    with open(schema_file, 'r', encoding='utf-8') as file:
        content = file.read()

    # Remove all SQL single-line comments starting with '--'
    content_no_comments = re.sub(r'--.*', '', content)

    # Regex pattern to match CREATE TABLE statements
    # It captures the table name and the columns definition block
    create_table_pattern = re.compile(
        r'CREATE\s+TABLE\s+"([^"]+)"\s*\((.*?)\);',
        re.IGNORECASE | re.DOTALL
    )

    # Find all CREATE TABLE statements
    matches = create_table_pattern.findall(content_no_comments)

    tables = {}

    for match in matches:
        table_name = match[0]
        columns_block = match[1]

        # Use re.findall to extract all column names
        # Each column starts with "column_name" optionally followed by spaces, then data type
        # This pattern captures the column name regardless of spacing
        columns = re.findall(r'"([^"]+)"\s*[^,]+,?', columns_block)

        # Debug: Print columns found for each table
        print(f"Table '{table_name}' has {len(columns)} columns.")
        for col in columns:
            print(f"  - Column: {col}")

        tables[table_name] = columns

    return tables

def print_tables_and_columns(tables):
    """
    Prints each table with its list of columns.

    Args:
        tables (dict): Dictionary mapping table names to column lists.
    """
    if not tables:
        print("No tables found to display.")
        return

    print("\n=== Tables and Their Columns ===")
    for table, columns in tables.items():
        print(f"\nTable: {table}")
        print("Columns:")
        for column in columns:
            print(f"  - {column}")
    print("\n=== End of Tables ===\n")

def main():
    schema_file = "TestProfile.sql"  # Path to your SQL schema file

    # Check if the schema file exists
    try:
        with open(schema_file, 'r', encoding='utf-8') as f:
            pass
    except FileNotFoundError:
        print(f"Error: Schema file '{schema_file}' not found.")
        return

    # Parse the SQL schema
    print(f"Reading and parsing the schema file: '{schema_file}'\n")
    tables = parse_sql_schema(schema_file)

    # Print the tables and their columns
    print_tables_and_columns(tables)

if __name__ == "__main__":
    main()
