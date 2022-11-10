from db import DBConnection
import json
import streamlit as st


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
        st.write(self.plans)

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

        st.write(settings)
        result = self.db.execute(
            settings + 'EXPLAIN (ANALYZE, COSTS, VERBOSE, BUFFERS, FORMAT JSON ) ' + self.sql_query)
        return result


sql_query = """select * from part where p_brand = 'Brand#13' and p_size <> (select max(p_size) from part);"""

db = DBConnection()
aqp_instance = Alternative_query_plan_generator(db, sql_query)
aqp = aqp_instance.get_dbms_aqp()
col1, col2 = st.columns(2)
with col1:
    st.write(aqp_instance.qep_json)
with col2:
    st.write(json.loads(json.dumps(aqp[0][0])))
