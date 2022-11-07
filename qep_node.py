


class Query_plan_node(object):
    
    def __init__(self, node_type, relation_name, schema, alias, group_key, sort_key, join_type, index_name, 
            hash_condition, table_filter, index_condition, merge_condition, recheck_condition, join_filter, subplan_name, actual_rows,
            actual_time,description):
        self.node_type = node_type
        self.children = []
        self.relation_name = relation_name
        self.schema = schema
        self.alias = alias
        self.group_key = group_key
        self.sort_key = sort_key
        self.join_type = join_type
        self.index_name = index_name
        self.hash_condition = hash_condition
        self.table_filter = table_filter
        self.index_condition = index_condition
        self.merge_condition = merge_condition
        self.recheck_condition = recheck_condition
        self.join_filter = join_filter
        self.subplan_name = subplan_name
        self.actual_rows = actual_rows
        self.actual_time = actual_time
        self.description = description
        self.annotation = None
        
    def write_annotation(self, annotation:str):
        self.annotation = annotation
    def add_child(self, child):
        self.children.append(child)
        
        
    def __str__(self):
        
        print_str = f'Node Type: {self.node_type} '
        
        if self.index_condition is not None:
            print_str += f'Index Condition: {self.index_condition} '
            
        if self.hash_condition is not None:
            print_str += f'Hash Condition: {self.hash_condition} '
            
        if self.merge_condition is not None:
            print_str += f'Merge Condition: {self.merge_condition} '
            
        if self.relation_name is not None:
            print_str += f'Relation Name: {self.relation_name} '
        
        if self.table_filter is not None:
            print_str += f'Filter Condition: {self.table_filter} '
        
        if self.alias is not None:
            print_str += f'Alias: {self.alias} '
        

        return print_str
    
    def is_conditional(self):
        
        if self.index_condition is None and self.hash_condition is None and self.merge_condition is None and self.table_filter is None:
            return False
        
        return True
    
    def get_condition(self):
        
        if self.index_condition is not None:
            return self.index_condition
            
        if self.hash_condition is not None:
             return self.hash_condition
            
        if self.merge_condition is not None:
           return self.merge_condition
        
        if self.table_filter is not None:
            return self.table_filter
        