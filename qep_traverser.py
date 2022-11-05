import queue
from qep_node import Query_plan_node
from qep_generator import Query_plan_generator
from db import DBConnection
import json

class Query_plan_traverser:
    
    
    def __init__(self, qep_json) -> None:
        self.root = self.__create_qep_tree(qep_json)
        pass
    
    def __return_qep_node(self,plan)->Query_plan_node:
        relation_name = schema = alias = group_key = sort_key = join_type = index_name = hash_condition = table_filter \
            = index_condition = merge_condition = recheck_condition = join_filter = subplan_name = actual_rows = actual_time = description = None
        if 'Relation Name' in plan:
            relation_name = plan['Relation Name']
        if 'Schema' in plan:
            schema = plan['Schema']
        if 'Alias' in plan:
            alias = plan['Alias']
        if 'Group Key' in plan:
            group_key = plan['Group Key']
        if 'Sort Key' in plan:
            sort_key = plan['Sort Key']
        if 'Join Type' in plan:
            join_type = plan['Join Type']
        if 'Index Name' in plan:
            index_name = plan['Index Name']
        if 'Hash Cond' in plan:
            hash_condition = plan['Hash Cond']
        if 'Filter' in plan:
            table_filter = plan['Filter']
        if 'Index Cond' in plan:
            index_condition = plan['Index Cond']
        if 'Merge Cond' in plan:
            merge_condition = plan['Merge Cond']
        if 'Recheck Cond' in plan:
            recheck_condition = plan['Recheck Cond']
        if 'Join Filter' in plan:
            join_filter = plan['Join Filter']
        if 'Actual Rows' in plan:
            actual_rows = plan['Actual Rows']
        if 'Actual Total Time' in plan:
            actual_time = plan['Actual Total Time']
        if 'Subplan Name' in plan:
            if "returns" in plan['Subplan Name']:
                name = plan['Subplan Name']
                subplan_name = name[name.index("$"):-1]
            else:
                subplan_name = plan['Subplan Name']
        # form a node form attributes created above
        return Query_plan_node(plan['Node Type'], relation_name, schema, alias, group_key, sort_key, join_type,
                            index_name, hash_condition, table_filter, index_condition, merge_condition, recheck_condition, join_filter,
                            subplan_name, actual_rows, actual_time, description)
        
    
    def __create_qep_tree(self,qep_json):
        
        
        child = []
        
        parents = []
        
        plan = qep_json[0]['Plan']
        
        child.append(plan)

        while(len(child) != 0):
            
            current_plan = child.pop(0)
            
            
            current_node = self.__return_qep_node(current_plan)

            
            if len(parents) != 0:
                p = parents.pop(0)
                
                p.add_child(current_node)
            else:
                root = current_node

            if 'Plans' in current_plan:
                for item in current_plan['Plans']:
                    child.append(item)
                    parents.append(current_node)
            
            
        return root
    
    def print_tree(self):
        
        
        level = 1
        
        q = [self.root]
        
        
        while (len(q) != 0):
            print (f'Level {level}')
            
            c = []
            print_str = ''
            for node in q:
                
                if node is not None:
                    
                    print_str += (f'[{str(node)}] ')
                    
                    if len(node.children) != 0:
                        c+= node.children
                        
            print(print_str)    
            q = c
            level +=1
            

db = DBConnection()
sql_query = '''
SELECT n_name
FROM nation, region,supplier
WHERE r_regionkey=n_regionkey AND s_nationkey = n_nationkey AND n_name IN 
(SELECT DISTINCT n_name FROM nation,region WHERE r_regionkey=n_regionkey AND r_name <> 'AMERICA') AND
r_name in (SELECT DISTINCT r_name from region where r_name <> 'ASIA');

'''        

qp = Query_plan_generator(db, sql_query)
qep_json = qp.get_dbms_qep()
qep_json = json.loads(json.dumps(qep_json[0][0]))
qpt = Query_plan_traverser(qep_json)
qpt.print_tree()
        
            
            
            
        
        
        
        
        