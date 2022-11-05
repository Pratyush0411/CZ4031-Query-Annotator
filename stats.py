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

def retrieve_maps():
    
    tables = __get_all_table_names()
    
    ct_map = {}
    tc_map = {}
    
    
    for tb in tables:
        
        if tb not in tc_map:
            tc_map[tb] = __get_columns_ordinal_sorted(table_name=tb)
            for c in tc_map[tb]:
                if c not in ct_map:
                    ct_map[c] = tb
        
    return tc_map, ct_map
            

# print(__get_all_table_names())
# print(__get_columns_ordinal_sorted("region"))
# t,c = __retrieve_maps()
# print(t)
# print(c)