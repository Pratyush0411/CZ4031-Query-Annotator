import queue
from qep_node import Query_plan_node
from qep_generator import Query_plan_generator
from db import DBConnection
import json
from qep_matcher import QEP_matcher
from parser import Parser

class Query_plan_traverser:
    
    
    def __init__(self, qep_json) -> None:
        self.root = self.__create_qep_tree(qep_json)
        self.print_tree()
        self.conditional_nodes = self.__get_conditional_nodes()
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
        
    def __bfs_intermediate_solutions(self, start):
        inter = []        
        q = [start]
    
        while (len(q) != 0 and len(inter) != 2):
            
            c = []
            for node in q:
                
                if node is not None:
                    if 'Join' in node.node_type:
                
                        inter.append(f"intermediate results from the join with SQL condition - {node.get_condition()}")
                
                    elif 'Scan' in node.node_type:
                
                        inter.append(f"the relation {node.relation_name}")
                        
                    
                    if len(node.children) != 0:
                        c+= node.children
                        
               
            q = c
        return inter
        
        
    def __annotate_joins(self, node:Query_plan_node):
        
        if len(node.children) != 2:
            return
        
        annotation_string = f"The join was performed using {node.node_type}. Actual SQL condition is {node.get_condition()}. "
        inter = self.__bfs_intermediate_solutions(node)
        
           
        annotation_string+= f'It was performed on {inter[0]} and {inter[1]}'
        
        node.write_annotation(annotation=annotation_string)
        
    def __annotate_scans(self, scan:Query_plan_node):
        
        annotation_string = f"The relation {scan.relation_name} was scanned using {scan.node_type}"
        scan.write_annotation(annotation_string)
        
    
    def __write_annotations(self, node: Query_plan_node):
        
        if 'Join' in node.node_type:
            
            self.__annotate_joins(node)
        
        elif 'Scan' in node.node_type:
            
            self.__annotate_scans(node)
            
    
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
    
    # def __annotate_joins(self):
    #     # add join ordering 
    #     if
    
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
            
            
    def __get_conditional_nodes(self,):
        
        
        level = 1
        
        q = [self.root]
        
        ans = {}
        while (len(q) != 0):
            
            c = []
            print_str = ''
            for node in q:
                
                if node is not None:
                    self.__write_annotations(node)
                    if node.is_conditional:
                        condition = node.get_condition()
                        ans [condition] = node
                        
                    
                    if len(node.children) != 0:
                        c+= node.children
                        
               
            q = c
            level +=1
            
        return ans
        
        
            

db = DBConnection()
# sql_query = '''
# SELECT n_name
# FROM nation N, region R,supplier S
# WHERE R.r_regionkey=N.n_regionkey AND S.s_nationkey = N.n_nationkey AND N.n_name IN 
# (SELECT DISTINCT n_name FROM nation,region WHERE r_regionkey=n_regionkey AND r_name <> 'AMERICA') AND
# r_name in (SELECT DISTINCT r_name from region where r_name <> 'ASIA');

# '''     
#sql_query = " select * from part where p_brand = 'Brand#13' and p_size <> (select max(p_size) from part);"   
sql_query = '''
SELECT n_name
FROM nation, region,supplier
WHERE r_regionkey=n_regionkey AND s_nationkey = n_nationkey AND n_name IN 
(SELECT DISTINCT n_name FROM nation,region WHERE r_regionkey=n_regionkey AND r_name <> 'AMERICA' AND
r_name in (SELECT DISTINCT r_name from region where r_name <> 'LATIN AMERICA' AND r_name <> 'AFRICA')) AND
r_name in (SELECT DISTINCT r_name from region where r_name <> 'ASIA');
''' 
qp = Query_plan_generator(db, sql_query)
qep_json = qp.get_dbms_qep()
qep_json = json.loads(json.dumps(qep_json[0][0]))
qpt = Query_plan_traverser(qep_json)
#print (qpt.conditional_nodes.keys())
parser = Parser(sql_query)

qm = QEP_matcher()
m = qm.string_matcher(parser.where_clauses, parser.having_clauses, qpt.conditional_nodes)


for k,v in m.items():
    
    print(f'{k}:{v}')

        
            
            
            
        
        
        
        
        