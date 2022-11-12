from thefuzz import fuzz
import queue
from qep_node import Query_plan_node

class Alternative_query_plan_matcher():
    
    
    
    def __init__(self) -> None:
        self.threshold = 95
    
    def __write_justification(self,qep_node:Query_plan_node, aqp_node:Query_plan_node):
        
        factor = float(qep_node.actual_time)//float(aqp_node.actual_time)
        justification_string = ''
        if factor > 1:
            print(f"Crazzy results for{str(qep_node)} and {str(aqp_node)}")
            qep_node.justification_is_fair = True
            justification_string += f"This is because the cost of {qep_node.node_type} is {factor} times that of {aqp_node.node_type}"
            
        else:
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
            
            
        
        