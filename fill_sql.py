import xml.etree.ElementTree as ET

def extract_equipments_from_xml(xml_file):
    """
    Parse the XML and return a list of dictionaries, 
    each representing an Equipment object with
    keys: 'mRID', 'name', 'description', 'inService' (or more as needed).
    """
    # Adjust the namespace dict to match your actual XML:
    ns = {'cim': 'http://iec.ch/TC57/2013/CIM-schema-cim16#'}

    tree = ET.parse(xml_file)
    root = tree.getroot()

    equipment_data_list = []

    # Find all Equipment elements (adjust the path as needed)
    for eq in root.findall('.//cim:Equipment', ns):
        # Extract mRID
        mRID_elem = eq.find('cim:IdentifiedObject.mRID', ns)
        mRID = mRID_elem.text if mRID_elem is not None else ''

        # Extract name
        name_elem = eq.find('cim:IdentifiedObject.name', ns)
        name = name_elem.text if name_elem is not None else ''

        # Extract description
        desc_elem = eq.find('cim:IdentifiedObject.description', ns)
        description = desc_elem.text if desc_elem is not None else ''

        # Extract inService (true/false)
        in_service_elem = eq.find('cim:Equipment.inService', ns)
        in_service_str = in_service_elem.text if in_service_elem is not None else ''
        # Convert string to a more convenient format, e.g. 'Active' or 'Inactive'
        status = 'Active' if in_service_str.lower() == 'true' else 'Inactive'

        # Build a dict for this equipment
        eq_dict = {
            'mRID': mRID,
            'NAME': name,
            'DESCRIPTION': description,
            'STATUS': status
        }

        equipment_data_list.append(eq_dict)

    return equipment_data_list

def fill_sql_from_xml(xml_file, sql_template_file, output_sql_file):
    """
    Read the XML to extract data, then read the SQL template file line by line
    and fill placeholders for each piece of equipment data.
    
    Writes all expanded SQL lines to 'output_sql_file'.
    """

    # 1. Extract a list of equipment data from the XML
    equipment_data_list = extract_equipments_from_xml(xml_file)

    # 2. Read the entire SQL file as a list of lines
    with open(sql_template_file, 'r', encoding='utf-8') as f:
        sql_lines = f.readlines()

    # 3. Open output file for writing
    with open(output_sql_file, 'w', encoding='utf-8') as out:
        
        # For each piece of equipment data, we replicate the lines that contain placeholders
        for eq_data in equipment_data_list:
            # We loop over each line in the original SQL
            # If the line contains placeholders, we replace them with eq_data
            for line in sql_lines:
                new_line = line

                # Example placeholders: {mRID}, {NAME}, {DESCRIPTION}, {STATUS}
                # Make sure the placeholders match what's in your SQL file
                new_line = new_line.replace('{mRID}', eq_data['mRID'])
                new_line = new_line.replace('{NAME}', eq_data['NAME'])
                new_line = new_line.replace('{DESCRIPTION}', eq_data['DESCRIPTION'])
                new_line = new_line.replace('{STATUS}', eq_data['STATUS'])

                # Write the updated line
                out.write(new_line)
            
            # Optionally add a blank line or separator between each set
            out.write("\n-- End of block for Equipment: " + eq_data['mRID'] + "\n\n")

if __name__ == "__main__":
    # Example usage:
    xml_file = "NMMS_Model_CIM_Sep_ML1_1_09122023.xml"
    sql_template_file = "TestProfile.sql"
    output_sql_file = "output_filled.sql"

    fill_sql_from_xml(xml_file, sql_template_file, output_sql_file)
    print(f"Done! Populated SQL is in {output_sql_file}")
