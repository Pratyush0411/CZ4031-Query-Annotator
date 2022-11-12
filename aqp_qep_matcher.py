from thefuzz import fuzz
import queue,math
from qep_node import Query_plan_node
from copy import copy

class Alternative_query_plan_matcher():
    
    
    
    def __init__(self, threshold = 95) -> None:
        self.threshold = threshold
    
    def __write_justification(self,qep_node:Query_plan_node, aqp_node:Query_plan_node):
        
        factor = math.ceil(float(qep_node.total_cost)/(float(aqp_node.total_cost)))
        justification_string = ''
        if factor > 1:
            print(f"Crazzy results for {str(qep_node)} and {str(aqp_node)}")
            qep_node.justification_is_fair = True
            justification_string += f"This is because the cost of {qep_node.node_type} is {factor} times that of {aqp_node.node_type}"
            
        else:
            print(f"Suprising results for {str(qep_node)} and {str(aqp_node)}")
            justification_string += f"Voila! The cost of {qep_node.node_type} is {factor} times that of {aqp_node.node_type}"
            
        qep_node.write_justification(justification_string)
        
    
    def __match_join_nodes(self, qep_node:Query_plan_node, aqp_node:Query_plan_node):
        
        qep_condition = qep_node.get_join_condition()
        aqp_condition = qep_node.get_join_condition()
        
        if (fuzz.token_set_ratio(qep_condition,aqp_condition)>self.threshold):
            if qep_node.node_type != aqp_node.node_type:
                self.__write_justification(qep_node,aqp_node)
            
    
    def __match_scan_nodes(self, qep_node:Query_plan_node, aqp_node:Query_plan_node):
        
        if qep_node.is_conditional() and aqp_node.is_conditional():
            qep_filter = qep_node.table_filter
            aqp_filter = qep_node.table_filter
            
            if qep_filter is not None and aqp_filter is not None:
            
                if (fuzz.token_set_ratio(qep_filter, aqp_filter)>self.threshold):
                    if qep_node.node_type != aqp_node.node_type:
                        self.__write_justification(qep_node,aqp_node)
        
        else:
            
            qep_relation_name = qep_node.relation_name
            aqp_relation_name = aqp_node.relation_name
            
            if qep_relation_name is not None and aqp_relation_name is not None:
            
                if (fuzz.token_set_ratio(qep_relation_name, aqp_relation_name)>self.threshold):
                    if qep_node.node_type != aqp_node.node_type:
                        self.__write_justification(qep_node,aqp_node)
    
    
    def match_qep_justfication(self, qep_node:Query_plan_node, aqp_node:Query_plan_node)->None:
        
        if not qep_node.justification_is_fair:
            
            
            if 'Join' in qep_node.node_type:
            
                self.__match_join_nodes(qep_node,aqp_node)
        
            elif 'Scan' in qep_node.node_type:
                
                self.__match_scan_nodes(qep_node,aqp_node)
            
            elif 'Nested Loop' in qep_node.node_type:
                
                self.__match_join_nodes(qep_node,aqp_node)
                
        else:
            return
        
    def matchything(self, qep_root, aqp_roots):
        q_a_dict = {}
        curQ = [qep_root]
        planRootList = aqp_roots
        while (len(planRootList) != 0):
            curA = planRootList.pop()
            #curA = planList
            while True:
                while(len(curQ) != 0):
                    qNode = curQ.pop()
                    while (len(curA) !=0):
                        aNode = curA.pop()
                        if qNode.is_conditional():
                            print(qNode, aNode)
                            self.match_qep_justfication(qNode, aNode)
                #end of level, go to child
                if len(qNode.children)!=0:
                    curQ = copy(qNode.children)
                    curA = copy(aNode.children)
                else: break
        return q_a_dict
            
            
        
    def matchUsingList(self, qep, aqpList):
        #qep = list of join nodes
        #aqp = list of qeps of above type
        num = len(qep)
        for eachPlan in aqpList:
            for currentIndex in range(num):
                qNode = qep[currentIndex]
                aNode = eachPlan[currentIndex]
                print("\nComparing ", qNode, " and ", aNode)
                self.match_qep_justfication(qNode, aNode)
    