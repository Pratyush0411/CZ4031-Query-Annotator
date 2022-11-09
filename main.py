import queue
from qep_node import Query_plan_node
from qep_generator import Query_plan_generator
from db import DBConnection
import json
from qep_matcher import QEP_matcher
from parser import Parser
from qep_traverser import Query_plan_traverser


# sql_query = '''
# SELECT n_name
# FROM nation N, region R,supplier S
# WHERE R.r_regionkey=N.n_regionkey AND S.s_nationkey = N.n_nationkey AND N.n_name IN 
# (SELECT DISTINCT n_name FROM nation,region WHERE r_regionkey=n_regionkey AND r_name <> 'AMERICA') AND
# r_name in (SELECT DISTINCT r_name from region where r_name <> 'ASIA');
# '''   
  
#sql_query = " select * from part where p_brand = 'Brand#13' and p_size <> (select max(p_size) from part);"   

sql_query = '''
SELECT n_name
FROM nation, region,supplier
WHERE r_regionkey=n_regionkey AND s_nationkey = n_nationkey AND n_name IN 
(SELECT DISTINCT n_name FROM nation,region WHERE r_regionkey=n_regionkey AND r_name <> 'AMERICA' AND
r_name in (SELECT DISTINCT r_name from region where r_name <> 'LATIN AMERICA' AND r_name <> 'AFRICA')) AND
r_name in (SELECT DISTINCT r_name from region where r_name <> 'ASIA');
''' 

# sql_query = '''
# select
#       n_name,
#       sum(l_extendedprice * (1 - l_discount)) as revenue
#     from
#       customer,
#       orders,
#       lineitem,
#       supplier,
#       nation,
#       region
#     where
#       c_custkey = o_custkey
#       and l_orderkey = o_orderkey
#       and l_suppkey = s_suppkey
#       and c_nationkey = s_nationkey
#       and s_nationkey = n_nationkey
#       and n_regionkey = r_regionkey
#       and r_name = 'ASIA'
#       and o_orderdate >= '1994-01-01'
#       and o_orderdate < '1995-01-01'
#       and c_acctbal > 10
#       and s_acctbal > 20
#     group by
#       n_name
#     order by
#       revenue desc;

# '''
# sql_query = '''
# select
#       supp_nation,
#       cust_nation,
#       l_year,
#       sum(volume) as revenue
#     from
#       (
#         select
#           n1.n_name as supp_nation,
#           n2.n_name as cust_nation,
#           DATE_PART('YEAR',l_shipdate) as l_year,
#           l_extendedprice * (1 - l_discount) as volume
#         from
#           supplier,
#           lineitem,
#           orders,
#           customer,
#           nation n1,
#           nation n2
#         where
#           s_suppkey = l_suppkey
#           and o_orderkey = l_orderkey
#           and c_custkey = o_custkey
#           and s_nationkey = n1.n_nationkey
#           and c_nationkey = n2.n_nationkey
#           and (
#             (n1.n_name = 'FRANCE' and n2.n_name = 'GERMANY')
#             or (n1.n_name = 'GERMANY' and n2.n_name = 'FRANCE')
#           )
#           and l_shipdate between '1995-01-01' and '1996-12-31'
#           and o_totalprice > 100
#           and c_acctbal > 10
#       ) as shipping
#     group by
#       supp_nation,
#       cust_nation,
#       l_year
#     order by
#       supp_nation,
#       cust_nation,
#       l_year;

# '''


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
    db = DBConnection()
    qp = Query_plan_generator(db, sql_query)
    qep_json = qp.get_dbms_qep()
    qep_json = json.loads(json.dumps(qep_json[0][0]))
    qpt = Query_plan_traverser(qep_json)
    parser = Parser(sql_query)

    qm = QEP_matcher()
    condition_to_node_map, table_reads_map = qpt.get_conditional_nodes_and_table_reads()
    m,c = qm.string_matcher(parser.where_clauses,condition_to_node_map)

    dc = __deconstruct_conditions_map(m, parser.new_clause_to_org_clause)
    ans = __combine_maps(dc,table_reads_map)
    
    return ans, parser.cleaned_query

answer,cleaned_query = main(sql_query)


print ("----------- ANS ----------------")
for k,v in answer.items():
    
    print(f'{k} : {v}')

print("---------------Cleaned Query---------------")

print(cleaned_query)
    
    