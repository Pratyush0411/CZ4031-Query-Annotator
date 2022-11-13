import queue
from qep_node import Query_plan_node
from qep_generator import Query_plan_generator
from db import DBConnection
import json
from qep_matcher import QEP_matcher
from parser import Parser
from qep_traverser import Query_plan_traverser
from aqp_qep_matcher import Alternative_query_plan_matcher
from aqp_generator import Alternative_query_plan_generator
from queries import *

sql_query = adrian_q2

def __combine_maps(deconstructed_map,table_reads_map):
    
    
    m = {}
    
    for k,v in deconstructed_map.items():
        
        m[k] = v
    
    for k,v in table_reads_map.items():
        
        if k in m:
            v1 = m[k]
            
            if type(v) is not list:
                v = [v]
            if type(v1) is not list:
                v1 = [v1]    
            
            m[k] = v+v1
        else:
            m[k] = v
    
    return m        
    
    
def __deconstruct_conditions_map(condition_to_node_map,new_clause_to_org_clause ):
    deconstructed_map = {}
    
    for k,v in condition_to_node_map.items():
        if new_clause_to_org_clause[k] not in deconstructed_map:
            deconstructed_map[new_clause_to_org_clause[k]] = v
        else:
            v1 = deconstructed_map[new_clause_to_org_clause[k]]
            if type(v1) is not list:
                v1 = [v1]
            v1.append(v)
            deconstructed_map[new_clause_to_org_clause[k]] = v1
    
    return deconstructed_map
    


def main(sql_query):
    # db = DBConnection(host="localhost", port = 5432, user="postgres", password="pratyush002", schema="tpch1g")
    db = DBConnection()
    qp = Query_plan_generator(db, sql_query)
    qep_json = qp.get_dbms_qep()
    qep_json = json.loads(json.dumps(qep_json[0][0]))
    aqp = Alternative_query_plan_generator(db, sql_query)
    aqm = Alternative_query_plan_matcher()
    qpt = Query_plan_traverser(qep_json)
    parser = Parser(sql_query)
    
    qep_jt= qpt.create_order_trees(qpt.root)
    aqp_jt = aqp.get_join_order_trees()
    qep_st = qpt.create_order_trees(qpt.root,['Scan'])
    aqp_st = aqp.get_scan_order_trees()
    
    aqm.matchUsingList(qep_jt,aqp_jt)
    aqm.matchUsingList(qep_st, aqp_st )
    
    qm = QEP_matcher()
    condition_to_node_map, table_reads_map = qpt.get_conditional_nodes_and_table_reads()
    m,c = qm.string_matcher(parser.where_clauses,condition_to_node_map)

    dc = __deconstruct_conditions_map(m, parser.new_clause_to_org_clause)
    ans = __combine_maps(dc,table_reads_map)
    
    qpt.print_tree()
    return ans, parser.cleaned_query


answer,cleaned_query= main(sql_query)


print ("----------- ANS ----------------")
for k,v in answer.items():
    
    print(f'{k} : {v}')

print("--------------- Cleaned Query ---------------")

print(cleaned_query)
    
    