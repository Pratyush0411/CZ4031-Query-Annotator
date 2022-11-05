
from db import DBConnection
class Query_plan_generator:
    
    def __init__(self, db: DBConnection, sql_query):
        
        self.db = db
        self.sql_query = sql_query
        
        
    def get_dbms_qep(self):
        result = self.db.execute('EXPLAIN (ANALYZE, COSTS, VERBOSE, BUFFERS, FORMAT JSON ) ' + self.sql_query)
        return result
    

# db = DBConnection()
# sql_query = '''
# SELECT n_name
# FROM nation, region,supplier
# WHERE r_regionkey=n_regionkey AND s_nationkey = n_nationkey AND n_name IN 
# (SELECT DISTINCT n_name FROM nation,region WHERE r_regionkey=n_regionkey AND r_name <> 'AMERICA') AND
# r_name in (SELECT DISTINCT r_name from region where r_name <> 'ASIA');

# '''        

# qp = Query_plan_generator(db, sql_query)

# print(qp.get_dbms_qep())