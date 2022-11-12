import queue
from qep_node import Query_plan_node
from qep_generator import Query_plan_generator
from db import DBConnection
import json
from qep_matcher import QEP_matcher
from aqp_qep_matcher import Alternative_query_plan_matcher
from parserr import Parser
from qep_traverser import Query_plan_traverser
from aqp_generator import Alternative_query_plan_generator
from queries import *

sql_query = adrian_q1

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
    
def matchything(qpt, aqp):
    q_a_dict = {}
    aqm = Alternative_query_plan_matcher()
    curQ = [qpt.root]
    planRootList = [aqp.get_join_aqp()] + [aqp.get_scan_aqp()]
    #print("No. of AQPs: ", len(planRootList))
    counter=0
    while (len(planRootList) != 0):
        #print("On AQP ", counter, " now\n")
        curA = planRootList.pop()
        #curA = planList
        while True:
            while(len(curQ) != 0):
                qNode = curQ.pop()
                while (len(curA) !=0):
                    aNode = curA.pop()
                    if qNode.is_conditional():
                        #print(qNode, aNode,"\n")
                        aqm.match_qep_justfication(qNode, aNode)
            #end of level, go to child
            if len(qNode.children)!=0:
                curQ = qNode.children
                curA = aNode.children
            else:
                break
        counter+=1
    return q_a_dict

def main(sql_query):
    db = DBConnection()
    qp = Query_plan_generator(db, sql_query)
    qep_json = qp.get_dbms_qep()
    qep_json = json.loads(json.dumps(qep_json[0][0]))
    qpt = Query_plan_traverser(qep_json)
    aqp = Alternative_query_plan_generator(db, sql_query)
    parser = Parser(sql_query)

    qm = QEP_matcher()
    condition_to_node_map, table_reads_map = qpt.get_conditional_nodes_and_table_reads()
    m,c = qm.string_matcher(parser.where_clauses,condition_to_node_map)

    dc = __deconstruct_conditions_map(m, parser.new_clause_to_org_clause)
    ans = __combine_maps(dc,table_reads_map)
    
    print(qpt.print_tree())
    
    # #start test
    matchything(qpt,aqp)
    # q_a_dict = {}
    # curQ = [qpt.root]
    # lvl=1
    # while (True):
        # print("Level: ", lvl)
        # while(len(curQ) != 0):
            # print(curQ)
            # qNode = curQ.pop()
            # if qNode.is_conditional():
                # print(qNode)
                # q_a_dict[qNode] = qNode.get_conditions
        # #end of level, go to child
        # if len(qNode.children)!=0:
            # curQ = qNode.children
        # else: break
    # #end bleh
    # print("Dict:")
    # print(q_a_dict)
    # print("end")
    return ans, parser.cleaned_query


answer,cleaned_query = main(sql_query)


print ("----------- ANS ----------------")
for k,v in answer.items():
    
    print(f'{k} : {v}')

print("---------------Cleaned Query---------------")

print(cleaned_query)
    
    