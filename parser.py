import sqlparse

from sqlparse.sql import IdentifierList, Identifier, Where, Comparison, Having
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

        self.cleaned_query = self._clean(raw_query)
        # print("Cleaning result ..")
        # print(self.cleaned_query)
        self.tokens = self.__get_tokens(self.cleaned_query)
        # print("Tokenization ..")
        # print (self.tokens)
        self.table_names = self.__get_table_names(self.tokens)
        print("Table names ..")
        print(self.table_names)
        self.where_clauses = self.__extract_where_clauses(self.tokens, 0)
        print("Where clauses ..")
        i = 1
        for item in self.where_clauses:
            print(f"{i}. {item.value}")
            i += 1
        self.having_clauses = self.__extract_having_clauses(self.tokens, 0)
        print("Having clauses ..")
        print(self.having_clauses)

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
                if isinstance(tokens[i+1], Identifier):
                    tables.append(tokens[i+1].value)
                elif isinstance(tokens[i+1], IdentifierList):
                    for id in tokens[i+1].get_identifiers():
                        tables.append(id.value)

        return tables

    def __is_subquery(self, parsed):
        if not parsed.is_group:
            return False
        val = False
        for item in parsed.tokens:
            if item.ttype is DML and item.value.upper() == 'SELECT':
                return True
            else:
                val = val or self.__is_subquery(item)

        return val

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

            tk = self.reconstruct_comparisons(t, sub_query_number)
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

    def __extract_where_clauses(self, tokens, sub_query_number=0):

        where = []
        cnt = 1
        for i in range(len(tokens)):

            if isinstance(tokens[i], Where):

                for t in tokens[i].tokens:

                    if isinstance(t, Comparison):

                        if (not self.__is_subquery(t)):

                            new_t = self.reconstruct_comparisons(
                                t, sub_query_number)
                            # print(new_t.value.lower())
                            where.append(new_t)

                        else:
                            subq = self.__return_subquery(t)
                            # print(subq)
                            where += self.__extract_where_clauses(
                                subq.tokens, sub_query_number+cnt)

                            # In->Join
                            colName = t.tokens[0].value
                            tableName = subTableName = self.ct_map[colName]
                            if sub_query_number > 0:
                                tableName += "_{}".format(sub_query_number)
                            subTableName += "_{}".format(sub_query_number+cnt)
                            x = dummyToken(tableName+"."+colName +
                                           "="+subTableName+"."+colName)
                            where.append(x)

                            cnt += 1

        return where

    def __extract_having_clauses(self, tokens, sub_query_number=0):

        having = []
        cnt = 1

        for i in range(len(tokens)):

            if isinstance(tokens[i], Having):

                for t in tokens[i].tokens:

                    if isinstance(t, Comparison):

                        if (not self.__is_subquery(t)):

                            new_t = self.reconstruct_comparisons(
                                t, sub_query_number)
                            print(new_t.value)
                            where.append(new_t)

                        else:
                            subq = self.__return_subquery(t)
                            print(subq)
                            where += self.__extract_where_clauses(
                                subq.tokens, sub_query_number+cnt)
                            cnt += 1

        return having

    def _clean(self, raw_query) -> list:
        # only consider the first query
        statements = sqlparse.split(raw_query)
        sql_parsed = sqlparse.format(
            statements[0], reindent=True, keyword_case='upper')
        sql_parsed_split = sql_parsed.splitlines()
        cleaned_query = ''
        for item in sql_parsed_split:
            cleaned_query += ' {}'.format(item.strip())
        return cleaned_query

    def parse_query(self, raw_query) -> str:

        return ""


raw_query = '''
SELECT n_name
FROM nation, region,supplier
WHERE r_regionkey=n_regionkey AND s_nationkey = n_nationkey AND n_name IN 
(SELECT DISTINCT n_name FROM nation,region WHERE r_regionkey=n_regionkey AND r_name <> 'AMERICA') AND
r_name in (SELECT DISTINCT r_name from region where r_name <> 'ASIA');
'''

p = Parser(raw_query)
