from thefuzz import fuzz
from thefuzz import process


class QEP_matcher():
    
    def __init__(self,):
        pass
    
    def string_matcher(self,where_clauses:list, condition_to_nodes_map: dict)->dict:
        
        condition_nodes= condition_to_nodes_map.keys()
        
        condition_to_qep_map = {}
        annotation_map = {}
        
        
        for item in where_clauses:
            item = item.value
            x,_ = process.extractOne(item, condition_nodes, scorer=fuzz.token_sort_ratio)
            if item not in condition_to_qep_map:
                
                if condition_to_nodes_map[x].annotation is not None:
                    condition_to_qep_map[item] = x
                    annotation_map[item] = condition_to_nodes_map[x].annotation
                else:
                    condition_to_qep_map[item] = x
                    annotation_map[item] = condition_to_nodes_map[x].node_type
                
        return annotation_map,condition_to_qep_map,
                
        
        
        
    