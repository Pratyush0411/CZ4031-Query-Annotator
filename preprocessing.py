import psycopg2
import json
import sqlparse
import math
from sqlparse.sql import IdentifierList, Identifier, Where, Comparison, Having, Parenthesis
from sqlparse.tokens import Keyword, DML, Whitespace
from thefuzz import fuzz
from thefuzz import process
from dotenv import dotenv_values

# db.py
DEFAULT_PARAMS = {
    'enable_async_append': 'ON',
    'enable_bitmapscan': 'ON',
    'enable_gathermerge': 'ON',
    'enable_hashagg': 'ON',
    'enable_hashjoin': 'ON',
    'enable_incremental_sort': 'ON',
    'enable_indexscan': 'ON',
    'enable_indexonlyscan': 'ON',
    'enable_material': 'ON',
    'enable_memoize': 'ON',
    'enable_mergejoin': 'ON',
    'enable_nestloop': 'ON',
    'enable_parallel_append': 'ON',
    'enable_parallel_hash': 'ON',
    'enable_partition_pruning': 'ON',
    'enable_partitionwise_join': 'OFF',
    'enable_partitionwise_aggregate': 'OFF',
    'enable_seqscan': 'ON',
    'enable_sort': 'ON',
    'enable_tidscan': 'ON'
}

config = dotenv_values(".env")


class DBConnection:

    def __init__(self, host=config["host"], port=config["port"], user=config["user"], password=config["password"], schema=config["schema"]):
        self.schema = schema
        self.conn = psycopg2.connect(
            host=host, port=port, user=user, password=password)
        self.cur = self.conn.cursor()
        self.cur.execute(f"SET search_path TO {schema};")

    def execute(self, query):
        self.cur.execute(query)
        query_results = self.cur.fetchall()
        return query_results

    def close(self):
        self.cur.close()
        self.conn.close()

    def reset_settings(self):
        settings = ""
        for key, value in DEFAULT_PARAMS.items():
            settings += "SET " + key + " = '" + value + "';\n"
        self.cur.execute(settings)


# stats.py
def __get_all_table_names():
    connection = DBConnection()
    query = f"""
        SELECT 
            table_name 
        FROM 
            information_schema.tables 
        WHERE 
            table_type = 'BASE TABLE' 
            AND table_schema = '{connection.schema}';
    """
    result = connection.execute(query)
    connection.close()
    tables = []
    for table_name in result:
        tables.append(table_name[0])
    return tables


def __get_columns_ordinal_sorted(table_name):
    query = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = '{table_name}' 
        ORDER BY ORDINAL_POSITION
    """.format(table_name=table_name)
    connection = DBConnection()
    result = connection.execute(query)
    connection.close()
    columns = []
    for table_name in result:
        columns.append(table_name[0])

    return columns


def retrieve_maps():
    tables = __get_all_table_names()
    ct_map = {}
    tc_map = {}
    for tb in tables:
        if tb not in tc_map:
            tc_map[tb] = __get_columns_ordinal_sorted(table_name=tb)
            for c in tc_map[tb]:
                if c not in ct_map:
                    ct_map[c] = tb
    return tc_map, ct_map


# parse.py

# convert in operator to a join condition
# annotate having clauses
# alias detection
class dummyToken:
    def __init__(self, comparison) -> None:
        self.value = comparison


class Parser:

    def __init__(self, raw_query):

        self.tc_map, self.ct_map = retrieve_maps()
        self.cnt = 1  # subquery count
        self.new_clause_to_org_clause = {}
        self.cleaned_query = self._clean(raw_query)

        self.tokens = self.__get_tokens(self.cleaned_query)

        self.table_names = self.__get_table_names(self.tokens)
        self.where_clauses = self.__extract_where_and_having_clauses(
            self.tokens, 0)

        print("All where and having clauses ..")
        i = 1
        for item in self.where_clauses:
            print(f"{i}. {item.value}")
            i += 1
        print("Map to original clauses ..")
        print(self.new_clause_to_org_clause)
        #self.aliasDict = self.__alias_dict(self.tokens)

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
        for i in range(len(parsed.tokens)):
            if isinstance(parsed.tokens[i], Parenthesis):
                if parsed.tokens[i].tokens[1].ttype is DML and parsed.tokens[i].tokens[1].value.upper() == 'SELECT':
                    return True

            val = val or self.__is_subquery(parsed.tokens[i])

        return val

    def __alias_dict(self, tokens):

        aldict = {}
        column_identifiers = []

        for i in range(len(tokens)):
            if tokens[i].ttype is Keyword and 'as' in tokens[i].value.lower():
                aliasIs = tokens[i+1].value
                realIs = tokens[i-1].value
                aldict[aliasIs] = realIs

        for tok in tokens:
            if isinstance(tok, sqlparse.sql.Comment):
                continue
            if str(tok).lower() == 'select':
                in_select = True
            elif in_select and tok.ttype is None and isinstance(tok, IdentifierList):
                for identifier in tok.get_identifiers():
                    column_identifiers.append(identifier)
                break

        # get column names
        for column_identifier in column_identifiers:
            aldict[column_identifier] = column_identifier.get_name()
            #aldict[column_identifier.get_real_name()] = column_identifier.get_name()
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

    def __handle_comparison(self, t, sub_query_number, ans):
        if (not self.__is_subquery(t)):
            org = t.value
            new_t = self.reconstruct_comparisons(t, sub_query_number)
            ans.append(new_t)
            self.new_clause_to_org_clause[new_t.value] = org

        else:
            subq = self.__return_subquery(t)
            # print(subq)
            ans += self.__extract_where_and_having_clauses(
                subq.tokens, sub_query_number+self.cnt)

            # In->Join
            if len(t.tokens) >= 3 and t.tokens[2].value.lower() == "in":
                colName = t.tokens[0].value
                if colName in self.ct_map:
                    tableName = subTableName = self.ct_map[colName]
                    if sub_query_number > 0:
                        tableName += "_{}".format(sub_query_number)
                    subTableName += "_{}".format(
                        sub_query_number+self.cnt)
                    x = dummyToken(tableName+"."+colName +
                                   "="+subTableName+"."+colName)
                    ans.append(x)
                else:
                    x = dummyToken(colName +
                                   "="+colName)
                    ans.append(x)
                org_clause = f"{t.tokens[0].value} {t.tokens[2].value}"
                self.new_clause_to_org_clause[x.value] = org_clause

            self.cnt += 1
        return ans

    def __extract_where_and_having_clauses(self, tokens, sub_query_number=0):

        ans = []
        for i in range(len(tokens)):

            if isinstance(tokens[i], Where) or isinstance(tokens[i], Having) or tokens[i].is_group:

                for t in tokens[i].tokens:
                    if isinstance(t, Parenthesis):

                        ans += self.__extract_where_and_having_clauses(
                            t.tokens, sub_query_number)

                    if isinstance(t, Comparison):
                        ans = self.__handle_comparison(
                            t, sub_query_number, ans)

            elif self.__is_subquery(tokens[i]):
                for t in tokens[i].tokens:

                    subq = self.__return_subquery(t)
                    if subq is not None:
                        ans += self.__extract_where_and_having_clauses(
                            subq.tokens, sub_query_number+self.cnt)

                        self.cnt += 1

        return ans

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


# qep_node.py

class Query_plan_node(object):

    def __init__(self, node_type, relation_name, schema, alias, group_key, sort_key, join_type, index_name,
                 hash_condition, table_filter, index_condition, merge_condition, recheck_condition, join_filter, subplan_name, actual_rows,
                 actual_time, description, total_cost, loops):
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
        self.total_cost = total_cost
        self.loops = loops
        if self.loops is not None:
            self.total_cost = float(self.total_cost)*int(self.loops)
        else:
            self.total_cost = float(total_cost)
        self.annotation = None
        self.justification = None
        self.justification_is_fair = False

    def write_annotation(self, annotation: str):
        self.annotation = annotation

    def add_child(self, child):
        self.children.append(child)

    def write_justification(self, justification: str):
        self.justification = justification

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

        if self.join_filter is not None:
            print_str += f'Join filter: {self.join_filter} '

        if self.justification is not None:
            print_str += f'Justification: {self.justification} '

        if self.loops is not None:
            print_str += f'loops: {self.loops} '

        return print_str

    def is_conditional(self):

        if self.index_condition is None and self.hash_condition is None and self.merge_condition is None and self.table_filter is None and self.join_filter is None:
            return False

        return True

    def get_conditions(self):
        conditions = []
        if self.index_condition is not None:
            conditions.append(self.index_condition)

        if self.hash_condition is not None:
            conditions.append(self.hash_condition)

        if self.merge_condition is not None:
            conditions.append(self.merge_condition)

        if self.table_filter is not None:
            conditions.append(self.table_filter)

        if self.join_filter is not None:
            conditions.append(self.join_filter)

        return conditions

    def get_join_condition(self):

        if self.is_conditional is False:
            return None

        if 'Merge' in self.node_type:

            return self.merge_condition

        if 'Hash' in self.node_type:

            return self.hash_condition

        if 'Nested Loop' in self.node_type:

            return self.join_filter


# qep_matcher

class QEP_matcher():

    def __init__(self,):
        pass

    def string_matcher(self, where_clauses: list, condition_to_nodes_map: dict) -> dict:

        condition_nodes = condition_to_nodes_map.keys()

        condition_to_qep_map = {}
        annotation_map = {}

        for item in where_clauses:
            item = item.value
            x, _ = process.extractOne(
                item, condition_nodes, scorer=fuzz.token_sort_ratio)
            if item not in condition_to_qep_map:

                if condition_to_nodes_map[x].annotation is not None and condition_to_nodes_map[x].justification is not None:
                    condition_to_qep_map[item] = x
                    annotation_map[item] = condition_to_nodes_map[x].annotation + \
                        condition_to_nodes_map[x].justification
                elif condition_to_nodes_map[x].annotation is not None:
                    condition_to_qep_map[item] = x
                    annotation_map[item] = condition_to_nodes_map[x].annotation
                else:
                    condition_to_qep_map[item] = x
                    annotation_map[item] = condition_to_nodes_map[x].node_type

        return annotation_map, condition_to_qep_map,

# qep_generator


class Query_plan_generator:

    def __init__(self, db: DBConnection, sql_query):

        self.db = db
        self.sql_query = sql_query

    def get_dbms_qep(self):
        result = self.db.execute(
            'EXPLAIN (ANALYZE, COSTS, VERBOSE, BUFFERS, FORMAT JSON ) ' + self.sql_query)
        return result

# qep_traverser


class Query_plan_traverser:

    def __init__(self, qep_json=None) -> None:
        if qep_json is not None:
            self.root = self.__create_qep_tree(qep_json)
        pass

    def __return_qep_node(self, plan) -> Query_plan_node:
        relation_name = schema = alias = group_key = sort_key = join_type = index_name = hash_condition = table_filter \
            = index_condition = merge_condition = recheck_condition = join_filter = subplan_name = actual_rows = actual_time = description = total_cost = loops = None
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
        if 'Total Cost' in plan:
            total_cost = plan['Total Cost']
        if 'Actual Loops' in plan:
            loops = plan['Actual Loops']
        if 'Subplan Name' in plan:
            if "returns" in plan['Subplan Name']:
                name = plan['Subplan Name']
                subplan_name = name[name.index("$"):-1]
            else:
                subplan_name = plan['Subplan Name']

        # form a node form attributes created above
        return Query_plan_node(plan['Node Type'], relation_name, schema, alias, group_key, sort_key, join_type,
                               index_name, hash_condition, table_filter, index_condition, merge_condition, recheck_condition, join_filter,
                               subplan_name, actual_rows, actual_time, description, total_cost, loops)

    def __bfs_intermediate_solutions(self, start: Query_plan_node):
        inter = []
        q = start.children

        while (len(q) != 0 and len(inter) != 2):

            c = []
            for node in q:

                if node is not None:
                    if 'Join' in node.node_type:

                        inter.append(
                            f"intermediate results from the join with SQL condition - {node.get_join_condition()}")

                    elif 'Scan' in node.node_type:

                        inter.append(f"the relation {node.relation_name}")

                    elif 'Nested Loop' in node.node_type:
                        if node.join_filter is None:
                            self.__convert_to_index_based(node)
                        if node.join_filter is not None:
                            inter.append(
                                f"intermediate results from the join with SQL condition - {node.get_join_condition()}")

                    if len(node.children) != 0:
                        c += node.children

            q = c
        return inter

    def __convert_to_index_based(self, node: Query_plan_node):
        for child in node.children:

            if 'Index Scan' in child.node_type and child.index_condition is not None:

                node.node_type = 'Index based Nested Loop Join'
                node.join_filter = child.index_condition
                child.index_condition = None
                break

    def __annotate_nested_loop(self, node: Query_plan_node):

        if node.join_filter is None:
            self.__convert_to_index_based(node)

        if node.get_join_condition() is not None:

            annotation_string = f"The join was performed using {node.node_type}. Actual SQL condition is {node.get_join_condition()}. "
            inter = self.__bfs_intermediate_solutions(node)

            annotation_string += f'It was performed on {inter[0]} and {inter[1]}'

            node.write_annotation(annotation=annotation_string)

    def __annotate_joins(self, node: Query_plan_node):

        if len(node.children) != 2:
            return

        annotation_string = f"The join was performed using {node.node_type}. Actual SQL condition is {node.get_join_condition()}. "
        inter = self.__bfs_intermediate_solutions(node)

        annotation_string += f'It was performed on {inter[0]} and {inter[1]}. '
        if node.join_filter is not None:
            annotation_string += f'The join filter condition was {node.join_filter}. '

        node.write_annotation(annotation=annotation_string)

    def __annotate_scans(self, scan: Query_plan_node):
        annotation_string = ""
        if scan.relation_name is not None:
            annotation_string += f"The relation {scan.relation_name} was scanned using {scan.node_type}. "
        else:
            annotation_string += f"{scan.node_type} was performed. "
            scan.relation_name = "FROM"

        if 'Index' in scan.node_type:
            annotation_string += f"The index condition is {scan.index_condition}. "

        if scan.table_filter is not None:
            annotation_string += f"The filter condition is {scan.table_filter}. "

        scan.write_annotation(annotation_string)

    def __write_annotations(self, node: Query_plan_node):

        if 'Join' in node.node_type:

            self.__annotate_joins(node)

        elif 'Scan' in node.node_type:

            self.__annotate_scans(node)

        elif 'Nested Loop' in node.node_type:

            self.__annotate_nested_loop(node)

    def __create_qep_tree(self, qep_json):

        child = []

        parents = []

        plan = qep_json[0]['Plan']

        child.append(plan)

        while (len(child) != 0):

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

    def print_tree(self):

        level = 1

        q = [self.root]

        while (len(q) != 0):
            print(f'Level {level}')

            c = []
            print_str = ''
            for node in q:

                if node is not None:

                    print_str += (f'[{str(node)}] ')

                    if len(node.children) != 0:
                        c += node.children

            print(print_str)
            q = c
            level += 1

    def create_order_trees(self, root, string_arr=['Join', 'Nested Loop']):

        level = 1

        join_order_tree = []
        q = [root]

        while (len(q) != 0):
            c = []
            j = []
            for node in q:

                if node is not None:

                    for i in string_arr:

                        if i in node.node_type:
                            j.append(node)
                            if i == 'Nested Loop':
                                self.__write_annotations(node)
                            break

                    if len(node.children) != 0:
                        c += node.children

            q = c
            if len(j) != 0:
                join_order_tree.append(j)
            level += 1

        return join_order_tree

    def get_conditional_nodes_and_table_reads(self,):

        level = 1

        q = [self.root]

        ans = {}
        annotations_table_reads = {}
        while (len(q) != 0):

            c = []
            for node in q:

                if node is not None:
                    self.__write_annotations(node)
                    if node.is_conditional():
                        conditions = node.get_conditions()
                        for condition in conditions:
                            ans[condition] = node
                    elif 'Scan' in node.node_type:

                        if node.annotation is not None:

                            if node.node_type == 'Seq Scan':
                                node.annotation += "This is because there was no suitable index on the relation."
                            if node.relation_name in annotations_table_reads:

                                v = annotations_table_reads[node.relation_name]
                                if type(v) is not list:
                                    annotations_table_reads[node.relation_name] = [
                                        v]
                                annotations_table_reads[node.relation_name].append(
                                    node.annotation)
                            else:
                                annotations_table_reads[node.relation_name] = node.annotation
                        else:
                            if node.relation_name in annotations_table_reads:
                                v = annotations_table_reads[node.relation_name]
                                if type(v) is not list:
                                    annotations_table_reads[node.relation_name] = [
                                        v]
                                annotations_table_reads[node.relation_name].append(
                                    node.node_type)
                            else:
                                annotations_table_reads[node.relation_name] = node.node_type

                    if len(node.children) != 0:
                        c += node.children

            q = c
            level += 1

        return ans, annotations_table_reads

# aqp_generator


class Alternative_query_plan_generator:

    def __init__(self, db: DBConnection, sql_query):
        self.db = db
        self.sql_query = sql_query
        self.plans = {"Scan": {"Index Scan": 0, "Seq Scan": 0, "Tid Scan": 0, "Bitmap Heap Scan": 0, "Bitmap Index Scan": 0, "Index Only Scan": 0},
                      "Join": {"Hash Join": 0, "Merge Join": 0, "Nested Loop": 0}}
        self.qep = self.db.execute(
            'EXPLAIN (ANALYZE, COSTS, VERBOSE, BUFFERS, FORMAT JSON ) ' + self.sql_query)
        self.qep_json = json.loads(json.dumps(self.qep[0][0]))
        self.get_qep_plans(self.qep_json[0]["Plan"])
        self.aqp_roots = self.get_join_aqp()+self.get_scan_aqp()

    def get_qep_plans(self, dictNode):
        if "Scan" in dictNode["Node Type"]:
            self.plans["Scan"][dictNode["Node Type"]] += 1
        if "Join" in dictNode["Node Type"]:
            self.plans["Join"][dictNode["Node Type"]] += 1

        if "Plans" in dictNode:
            for subDictNode in dictNode["Plans"]:
                self.get_qep_plans(subDictNode)

    def get_dbms_aqp(self):
        countScan = self.plans["Scan"]["Bitmap Heap Scan"] + \
            self.plans["Scan"]["Bitmap Index Scan"]
        mostScan = "Bitmap Scan"
        for key, value in self.plans["Scan"].items():
            if value > countScan:
                countScan = value
                mostScan = key

        countJoin = self.plans["Join"]["Hash Join"]
        mostJoin = "Hash Join"
        for key, value in self.plans["Join"].items():
            if value > countJoin:
                countJoin = value
                mostJoin = key

        scan = ""
        join = ""
        settings = ""

        if countScan > 0:
            if mostScan == "Bitmap Scan":
                scan = 'enable_bitmapscan'
            elif mostScan == "Index Scan":
                scan = 'enable_indexscan'
            elif mostScan == "Seq Scan":
                scan = 'enable_seqscan'
            elif mostScan == "Tid Scan":
                scan = 'enable_tidscan'
            else:
                scan = 'enable_indexonlyscan'
            settings += "SET " + scan + " = OFF;"

        if countJoin > 0:
            if mostJoin == "Hash Join":
                join = 'enable_hashjoin'
            elif mostJoin == "Merge Join":
                join = 'enable_mergejoin'
            else:
                join = 'enable_nestloop'
            settings += "SET " + join + " = OFF;"

        result = self.db.execute(
            settings + 'EXPLAIN (ANALYZE, COSTS, VERBOSE, BUFFERS, FORMAT JSON ) ' + self.sql_query)
        self.db.reset_settings()
        return result

    def get_join_aqp(self):
        root_list = []

        # hash join only
        settings = "Set enable_mergejoin = OFF; Set enable_nestloop = OFF;"
        aqp = self.db.execute(
            settings + 'EXPLAIN (ANALYZE, COSTS, VERBOSE, BUFFERS, FORMAT JSON ) ' + self.sql_query)
        self.db.reset_settings()
        aqp_json = json.loads(json.dumps(aqp[0][0]))
        aqp_root = Query_plan_traverser(aqp_json).root
        root_list.append(aqp_root)

        # merge join only
        settings = "Set enable_hashjoin = OFF; Set enable_nestloop = OFF;"
        aqp = self.db.execute(
            settings + 'EXPLAIN (ANALYZE, COSTS, VERBOSE, BUFFERS, FORMAT JSON ) ' + self.sql_query)
        self.db.reset_settings()
        aqp_json = json.loads(json.dumps(aqp[0][0]))
        aqp_root = Query_plan_traverser(aqp_json).root
        root_list.append(aqp_root)

        # nestloop join only
        settings = "Set enable_hashjoin = OFF; Set enable_mergejoin = OFF;"
        aqp = self.db.execute(
            settings + 'EXPLAIN (ANALYZE, COSTS, VERBOSE, BUFFERS, FORMAT JSON ) ' + self.sql_query)
        self.db.reset_settings()
        aqp_json = json.loads(json.dumps(aqp[0][0]))
        aqp_root = Query_plan_traverser(aqp_json).root
        root_list.append(aqp_root)

        return root_list

    def get_join_order_trees(self):

        join_order_trees = []

        qpt = Query_plan_traverser()
        for root in self.aqp_roots:
            print("____Join Order____")
            jt = qpt.create_order_trees(root)
            for item in jt:
                print([str(i) for i in item])
            join_order_trees.append(jt)

        return join_order_trees

    def get_scan_order_trees(self):

        scan_order_trees = []

        qpt = Query_plan_traverser()
        for root in self.aqp_roots:
            print("____Scan Order____")
            jt = qpt.create_order_trees(root, ['Scan'])
            for item in jt:
                print([str(i) for i in item])
            scan_order_trees.append(jt)

        return scan_order_trees

    def get_scan_aqp(self):
        root_list = []

        # Index scan only
        settings = "Set enable_bitmapscan = OFF; Set enable_indexonlyscan = OFF; Set enable_seqscan = OFF; Set enable_tidscan = OFF;"
        aqp = self.db.execute(
            settings + 'EXPLAIN (ANALYZE, COSTS, VERBOSE, BUFFERS, FORMAT JSON ) ' + self.sql_query)
        self.db.reset_settings()
        aqp_json = json.loads(json.dumps(aqp[0][0]))
        aqp_root = Query_plan_traverser(aqp_json).root
        root_list.append(aqp_root)

        # Seq scan only
        settings = "Set enable_bitmapscan = OFF; Set enable_indexonlyscan = OFF; Set enable_indexscan = OFF; Set enable_tidscan = OFF;"
        aqp = self.db.execute(
            settings + 'EXPLAIN (ANALYZE, COSTS, VERBOSE, BUFFERS, FORMAT JSON ) ' + self.sql_query)
        self.db.reset_settings()
        aqp_json = json.loads(json.dumps(aqp[0][0]))
        aqp_root = Query_plan_traverser(aqp_json).root
        root_list.append(aqp_root)

        # Tid scan only
        settings = "Set enable_bitmapscan = OFF; Set enable_indexonlyscan = OFF; Set enable_indexscan = OFF; Set enable_seqscan = OFF;"
        aqp = self.db.execute(
            settings + 'EXPLAIN (ANALYZE, COSTS, VERBOSE, BUFFERS, FORMAT JSON ) ' + self.sql_query)
        self.db.reset_settings()
        aqp_json = json.loads(json.dumps(aqp[0][0]))
        aqp_root = Query_plan_traverser(aqp_json).root
        root_list.append(aqp_root)

        # Bitmap scan only
        settings = "Set enable_tidscan = OFF; Set enable_indexonlyscan = OFF; Set enable_indexscan = OFF; Set enable_seqscan = OFF;"
        aqp = self.db.execute(
            settings + 'EXPLAIN (ANALYZE, COSTS, VERBOSE, BUFFERS, FORMAT JSON ) ' + self.sql_query)
        self.db.reset_settings()
        aqp_json = json.loads(json.dumps(aqp[0][0]))
        aqp_root = Query_plan_traverser(aqp_json).root
        root_list.append(aqp_root)

        # Indexonly scan only
        settings = "Set enable_tidscan = OFF; Set enable_bitmapscan = OFF; Set enable_indexscan = OFF; Set enable_seqscan = OFF;"
        aqp = self.db.execute(
            settings + 'EXPLAIN (ANALYZE, COSTS, VERBOSE, BUFFERS, FORMAT JSON ) ' + self.sql_query)
        self.db.reset_settings()
        aqp_json = json.loads(json.dumps(aqp[0][0]))
        aqp_root = Query_plan_traverser(aqp_json).root
        root_list.append(aqp_root)

        return root_list

    def get_all_possible_join_aqp(self):
        root_list = []

        # hash join only
        settings = "Set enable_mergejoin = OFF; Set enable_nestloop = OFF;"
        aqp = self.db.execute(
            settings + 'EXPLAIN (ANALYZE, COSTS, VERBOSE, BUFFERS, FORMAT JSON ) ' + self.sql_query)
        self.db.reset_settings()
        aqp_json = json.loads(json.dumps(aqp[0][0]))
        aqp_root = Query_plan_traverser(aqp_json).root
        root_list.append(aqp_root)

        # merge join only
        settings = "Set enable_hashjoin = OFF; Set enable_nestloop = OFF;"
        aqp = self.db.execute(
            settings + 'EXPLAIN (ANALYZE, COSTS, VERBOSE, BUFFERS, FORMAT JSON ) ' + self.sql_query)
        self.db.reset_settings()
        aqp_json = json.loads(json.dumps(aqp[0][0]))
        aqp_root = Query_plan_traverser(aqp_json).root
        root_list.append(aqp_root)

        # nestloop join only
        settings = "Set enable_hashjoin = OFF; Set enable_mergejoin = OFF;"
        aqp = self.db.execute(
            settings + 'EXPLAIN (ANALYZE, COSTS, VERBOSE, BUFFERS, FORMAT JSON ) ' + self.sql_query)
        self.db.reset_settings()
        aqp_json = json.loads(json.dumps(aqp[0][0]))
        aqp_root = Query_plan_traverser(aqp_json).root
        root_list.append(aqp_root)

        settings = "Set enable_hashjoin = OFF;"
        aqp = self.db.execute(
            settings + 'EXPLAIN (ANALYZE, COSTS, VERBOSE, BUFFERS, FORMAT JSON ) ' + self.sql_query)
        self.db.reset_settings()
        aqp_json = json.loads(json.dumps(aqp[0][0]))
        aqp_root = Query_plan_traverser(aqp_json).root
        root_list.append(aqp_root)

        settings = "Set enable_mergejoin = OFF;"
        aqp = self.db.execute(
            settings + 'EXPLAIN (ANALYZE, COSTS, VERBOSE, BUFFERS, FORMAT JSON ) ' + self.sql_query)
        self.db.reset_settings()
        aqp_json = json.loads(json.dumps(aqp[0][0]))
        aqp_root = Query_plan_traverser(aqp_json).root
        root_list.append(aqp_root)

        settings = "Set enable_nestloop = OFF;"
        aqp = self.db.execute(
            settings + 'EXPLAIN (ANALYZE, COSTS, VERBOSE, BUFFERS, FORMAT JSON ) ' + self.sql_query)
        self.db.reset_settings()
        aqp_json = json.loads(json.dumps(aqp[0][0]))
        aqp_root = Query_plan_traverser(aqp_json).root
        root_list.append(aqp_root)

        return root_list

# aqp__qep_matcher


class Alternative_query_plan_matcher():

    def __init__(self, threshold=95) -> None:
        self.threshold = threshold

    def __write_justification(self, qep_node: Query_plan_node, aqp_node: Query_plan_node):

        factor = math.ceil((aqp_node.total_cost)/(qep_node.total_cost))
        justification_string = ''
        if factor > 1:
            print(f"Crazzy results for {str(qep_node)} and {str(aqp_node)}")
            qep_node.justification_is_fair = True
            justification_string += f"This is because the cost of {aqp_node.node_type} is {factor} times that of {qep_node.node_type}"

        else:
            print(f"Suprising results for {str(qep_node)} and {str(aqp_node)}")
            justification_string += f"Surprising! The cost of {aqp_node.node_type} is {factor} times that of {qep_node.node_type}"

        qep_node.write_justification(justification_string)

    def __match_join_nodes(self, qep_node: Query_plan_node, aqp_node: Query_plan_node):

        qep_condition = qep_node.get_join_condition()
        aqp_condition = qep_node.get_join_condition()

        if (fuzz.token_set_ratio(qep_condition, aqp_condition) > self.threshold):
            if qep_node.node_type != aqp_node.node_type:
                self.__write_justification(qep_node, aqp_node)

    def __match_scan_nodes(self, qep_node: Query_plan_node, aqp_node: Query_plan_node):

        if qep_node.is_conditional() and aqp_node.is_conditional():
            qep_filter = qep_node.table_filter
            aqp_filter = qep_node.table_filter

            if qep_filter is not None and aqp_filter is not None:

                if (fuzz.token_set_ratio(qep_filter, aqp_filter) > self.threshold):
                    if qep_node.node_type != aqp_node.node_type:
                        self.__write_justification(qep_node, aqp_node)

        else:

            qep_relation_name = qep_node.relation_name
            aqp_relation_name = aqp_node.relation_name

            if qep_relation_name is not None and aqp_relation_name is not None:

                if (fuzz.token_set_ratio(qep_relation_name, aqp_relation_name) > self.threshold):
                    if qep_node.node_type != aqp_node.node_type:
                        self.__write_justification(qep_node, aqp_node)

    def match_qep_justfication(self, qep_node: Query_plan_node, aqp_node: Query_plan_node) -> None:

        if not qep_node.justification_is_fair:

            if ('Join' in qep_node.node_type or 'Nested Loop' in qep_node.node_type) and ('Join' in aqp_node.node_type or 'Nested Loop' in aqp_node.node_type):

                self.__match_join_nodes(qep_node, aqp_node)

            elif 'Scan' in qep_node.node_type:

                self.__match_scan_nodes(qep_node, aqp_node)

        else:
            return

    def matchUsingList(self, qep, aqpList):
        # qep = list of join nodes
        # aqp = list of qeps of above type
        num = len(qep)
        for eachPlan in aqpList:
            for currentIndex in range(num):

                for qNode in qep[currentIndex]:
                    if currentIndex < len(eachPlan):
                        for aNode in eachPlan[currentIndex]:

                            # print("\nComparing ", qNode, " and ", aNode)
                            self.match_qep_justfication(qNode, aNode)
                    else:
                        continue
