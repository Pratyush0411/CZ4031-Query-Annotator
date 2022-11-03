import sqlparse

from sqlparse.sql import IdentifierList, Identifier, Where, Comparison
from sqlparse.tokens import Keyword, DML, Whitespace

class Parser:
    
    

    
    
    def __init__(self, raw_query):
        
        self.cleaned_query = self._clean(raw_query)
        print("Cleaning result..")
        print(self.cleaned_query)
        self.tokens = self.__get_tokens(self.cleaned_query)
        print("Tokenization ..")
        print (self.tokens)
        self.table_names = self.__get_table_names(self.tokens)
        print("Table names ..")
        print(self.table_names)
        self.__extract_where_clauses(self.tokens)
        
        
    def __get_tokens(self, cleaned_query):
        
        parsed = sqlparse.parse(cleaned_query)[0]
        
        clean_parse = []
        
        for token in parsed.tokens:
            
            if token.ttype is Whitespace:
                continue
            clean_parse.append(token)
        
        return clean_parse
    
    def __get_table_names(self, tokens):
        
        tables = []
        
        for i in range(len(tokens)):
         
            if tokens[i].ttype is Keyword and 'from' in tokens[i].value.lower():
                if isinstance(tokens[i+1],Identifier):
                    tables.append(tokens[i+1].value)
                elif isinstance(tokens[i+1],IdentifierList):
                    for id in tokens[i+1].get_identifiers():
                        tables.append(id.value)
                    
        return tables
    
    def __extract_where_clauses(self, tokens):
        
        where = []
        
        for i in range(len(tokens)):
         
            if isinstance(tokens[i],Where):
                
                print(tokens[i].tokens)
                for t in tokens[i].tokens:
                    
                    if isinstance(t, Comparison):
                        
                        print(t.tokens)                 
                    
        return None
        
            
        
        
    def _clean(self, raw_query)->list:
        # only consider the first query 
        statements = sqlparse.split(raw_query)
        sql_parsed = sqlparse.format(statements[0], reindent=True, keyword_case='upper')
        sql_parsed_split = sql_parsed.splitlines()
        cleaned_query = ''
        for item in sql_parsed_split:
            cleaned_query += ' {}'.format(item.strip())
        return cleaned_query
    
    def parse_query(self, raw_query) -> str:
        
        
        
        return ""
        

raw_query = '''
SELECT count(n_name) as CNT
FROM nation, region,supplier
WHERE r_regionkey=n_regionkey AND s_nationkey = n_nationkey AND r_name IN (SELECT r_name FROM region WHERE r_name <> 'AMERICA');

'''   
    
p = Parser(raw_query)