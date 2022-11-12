import sqlparse

from sqlparse.sql import IdentifierList, Identifier, Where, Comparison, Having, Parenthesis
from sqlparse.tokens import Keyword, DML, Whitespace
import stats


# convert in operator to a join condition

# annotate having clauses

# alias detection
class dummyToken:
    def __init__(self, comparison) -> None:
        self.value = comparison


class Parser:
    
    
    def __init__(self, raw_query):
        
        self.tc_map, self.ct_map = stats.retrieve_maps()
        self.cnt = 1 # subquery count
        self.new_clause_to_org_clause = {}
        self.cleaned_query = self._clean(raw_query)
        
        self.tokens = self.__get_tokens(self.cleaned_query)
       
        self.table_names = self.__get_table_names(self.tokens)
        self.where_clauses = self.__extract_where_and_having_clauses(self.tokens,0)
        
        print("All where and having clauses ..") 
        i = 1
        for item in self.where_clauses:
            print (f"{i}. {item.value}")
            i+=1
        print("Map to original clauses ..") 
        print(self.new_clause_to_org_clause)
        
        self.aliasDict = self.__alias_dict(self.tokens)
        
        
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
    
    def __is_subquery(self, parsed):
        if not parsed.is_group:
            return False
        val =  False
        for i in range(len(parsed.tokens)):
            if isinstance(parsed.tokens[i], Parenthesis):
                if parsed.tokens[i].tokens[1].ttype is DML and  parsed.tokens[i].tokens[1].value.upper() == 'SELECT':
                    return True
            
            val = val or self.__is_subquery(parsed.tokens[i])
                
        return val
        
    def __alias_dict(self, tokens):
        
        aldict = {}
        column_identifiers = []
        
        # for i in range(len(tokens)):
            # if tokens[i].ttype is Keyword and 'as' in tokens[i].value.lower():
                # aliasIs = tokens[i+1].value
                # realIs = tokens[i-1].value
                # aldict[aliasIs] = realIs
                
        # for tok in tokens:
            # if isinstance(tok, sqlparse.sql.Comment):
                # continue
            # if str(tok).lower() == 'select':
                # in_select = True
            # elif in_select and tok.ttype is None:
                # for identifier in tok.get_identifiers():
                    # column_identifiers.append(identifier)
                # break

        # # get column names
        # for column_identifier in column_identifiers:
            # #aldict[column_identifier] = column_identifier.get_name()
            # aldict[column_identifier.get_real_name()] = column_identifier.get_name()
        return aldict
            
    
    def reconstruct_comparisons(self, token, sub_query_number):
        
        if not token.is_group:
            
            if token.value in self.ct_map:
                if (sub_query_number == 0):
                    token.value = f'{self.ct_map[token.value]}.{token.value}'
                else:
                    token.value = f'{self.ct_map[token.value]}_{sub_query_number}.{token.value}'
            return token

        new_t = []
        new_value = ''
        for t in token.tokens:
            
            tk = self.reconstruct_comparisons(t,sub_query_number)
            new_t.append(tk)
            new_value += tk.value
            
        token.tokens = new_t
        token.value = new_value
        
        return token
    
    def __return_subquery(self, parsed):
        if not parsed.is_group:
            return None
        
        for item in parsed.tokens:
            if item.ttype is DML and item.value.upper() == 'SELECT':
                return parsed
            else:
                val = self.__return_subquery(item)
                
        return val
    
    def __handle_comparison(self, t, sub_query_number, ans):
        if (not self.__is_subquery(t)):
            org = t.value
            new_t = self.reconstruct_comparisons(t, sub_query_number)
            ans.append(new_t)
            self.new_clause_to_org_clause[new_t.value] = org
            
        else:
            subq = self.__return_subquery(t)
            # print(subq)
            ans += self.__extract_where_and_having_clauses(subq.tokens, sub_query_number+self.cnt)
            
            # In->Join
            if len(t.tokens) >= 3 and t.tokens[2].value.lower() == "in":
                colName = t.tokens[0].value
                tableName = subTableName = self.ct_map[colName]
                if sub_query_number > 0:
                    tableName += "_{}".format(sub_query_number)
                subTableName += "_{}".format(
                    sub_query_number+self.cnt)
                x = dummyToken(tableName+"."+colName +
                                "="+subTableName+"."+colName)
                ans.append(x)
                org_clause = f"{t.tokens[0].value} {t.tokens[2].value}"
                self.new_clause_to_org_clause[x.value] = org_clause
            
            self.cnt +=1
        return ans
    
    def __extract_where_and_having_clauses(self, tokens, sub_query_number = 0):
        
        ans = []
        for i in range(len(tokens)):
         
            if isinstance(tokens[i],Where) or isinstance(tokens[i],Having) or tokens[i].is_group:
            
                for t in tokens[i].tokens:
                    if isinstance(t,Parenthesis):
                        
                        ans += self.__extract_where_and_having_clauses(t.tokens, sub_query_number)
                    
                    if isinstance(t, Comparison):
                        ans = self.__handle_comparison(t, sub_query_number, ans)
                        
            elif  self.__is_subquery(tokens[i]):
                for t in tokens[i].tokens:
            
                    subq = self.__return_subquery(t)
                    if subq is not None:
                        ans += self.__extract_where_and_having_clauses(subq.tokens, sub_query_number+self.cnt)
                        
                        self.cnt +=1
                    
                       
        return ans

            
        
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
        

# raw_query = '''
# SELECT n_name
# FROM nation, region,supplier
# WHERE r_regionkey=n_regionkey AND s_nationkey = n_nationkey AND n_name IN 
# (SELECT DISTINCT n_name FROM nation,region WHERE r_regionkey=n_regionkey AND r_name <> 'AMERICA' AND
# r_name in (SELECT DISTINCT r_name from region where r_name <> 'LATIN AMERICA' AND r_name <> 'AFRICA')) AND
# r_name in (SELECT DISTINCT r_name from region where r_name <> 'ASIA');
# '''   
    
# p = Parser(raw_query)