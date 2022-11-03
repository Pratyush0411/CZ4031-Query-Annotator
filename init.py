import db


def __get_all_table_names():


    connection = db.DBConnection()
    query = f"""
        SELECT 
            table_name 
        FROM 
            information_schema.tables 
        WHERE 
            table_type = 'BASE TABLE' 
            AND table_schema = '{connection.schema}';
    """
    result = connection.execute(query)
    connection.close()

    tables = []
    for table_name in result:
        tables.append(table_name[0])

    return tables

def __get_columns_ordinal_sorted(table_name):
    query = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = '{table_name}' 
        ORDER BY ORDINAL_POSITION
    """.format(table_name=table_name)

    connection = db.DBConnection()
    result = connection.execute(query)
    connection.close()

    columns = []
    for table_name in result:
        columns.append(table_name[0])

    return columns

print(__get_all_table_names())
print(__get_columns_ordinal_sorted("region"))