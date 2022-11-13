q1 = '''
SELECT n_name
FROM nation N, region R,supplier S
WHERE R.r_regionkey=N.n_regionkey AND S.s_nationkey = N.n_nationkey AND N.n_name IN 
(SELECT DISTINCT n_name FROM nation,region WHERE r_regionkey=n_regionkey AND r_name <> 'AMERICA') AND
r_name in (SELECT DISTINCT r_name from region where r_name <> 'ASIA');
'''   
  
q2 = " select * from part where p_brand = 'Brand#13' and p_size <> (select max(p_size) from part);"   

q3 = '''
SELECT n_name
FROM nation, region,supplier
WHERE r_regionkey=n_regionkey AND s_nationkey = n_nationkey AND n_name IN 
(SELECT DISTINCT n_name FROM nation,region WHERE r_regionkey=n_regionkey AND r_name <> 'AMERICA' AND
r_name in (SELECT DISTINCT r_name from region where r_name <> 'LATIN AMERICA' AND r_name <> 'AFRICA')) AND
r_name in (SELECT DISTINCT r_name from region where r_name <> 'ASIA');
''' 

lantern_q1 = '''
select
      n_name,
      sum(l_extendedprice * (1 - l_discount)) as revenue
    from
      customer,
      orders,
      lineitem,
      supplier,
      nation,
      region
    where
      c_custkey = o_custkey
      and l_orderkey = o_orderkey
      and l_suppkey = s_suppkey
      and c_nationkey = s_nationkey
      and s_nationkey = n_nationkey
      and n_regionkey = r_regionkey
      and r_name = 'ASIA'
      and o_orderdate >= '1994-01-01'
      and o_orderdate < '1995-01-01'
      and c_acctbal > 10
      and s_acctbal > 20
    group by
      n_name
    order by
      revenue desc;

'''
lantern_q2 = '''
select
      supp_nation,
      cust_nation,
      l_year,
      sum(volume) as revenue
    from
      (
        select
          n1.n_name as supp_nation,
          n2.n_name as cust_nation,
          DATE_PART('YEAR',l_shipdate) as l_year,
          l_extendedprice * (1 - l_discount) as volume
        from
          supplier,
          lineitem,
          orders,
          customer,
          nation n1,
          nation n2
        where
          s_suppkey = l_suppkey
          and o_orderkey = l_orderkey
          and c_custkey = o_custkey
          and s_nationkey = n1.n_nationkey
          and c_nationkey = n2.n_nationkey
          and (
            (n1.n_name = 'FRANCE' and n2.n_name = 'GERMANY')
            or (n1.n_name = 'GERMANY' and n2.n_name = 'FRANCE')
          )
          and l_shipdate >= '1995-01-01' 
          and o_totalprice > 100
          and c_acctbal > 10
      ) as shipping
    group by
      supp_nation,
      cust_nation,
      l_year
    order by
      supp_nation,
      cust_nation,
      l_year;

'''
index_only_q1 ='''
select n_nationkey from nation where n_nationkey = 3 union select s_nationkey from supplier;
'''
adrian_q1 = '''
select
	sum(l_extendedprice) / 7.0 as avg_yearly
from
	lineitem,
	part,
        (select l_partkey as agg_partkey, 0.2 * avg(l_quantity) as avg_quantity from lineitem group by l_partkey) part_agg
where
	p_partkey = l_partkey
        and agg_partkey = l_partkey
	and p_brand = 'brand#33'
	and p_container = 'wrap jar'
	and l_quantity < avg_quantity  
limit 1;
'''

adrian_q2 = '''
select
	n_name,
	sum(l_extendedprice * (1 - l_discount)) as revenue
from
	customer,
	orders,
	lineitem,
	supplier,
	nation,
	region
where
	c_custkey = o_custkey
	and l_orderkey = o_orderkey
	and l_suppkey = s_suppkey
	and c_nationkey = s_nationkey
	and s_nationkey = n_nationkey
	and n_regionkey = r_regionkey
	and r_name = 'AMERICA'
	and o_orderdate >= date '1995-01-01'
	and o_orderdate < date '1995-01-01' + interval '1' year
group by
	n_name
order by
	revenue desc
limit 1;
'''
