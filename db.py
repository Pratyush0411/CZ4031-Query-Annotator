import psycopg2
import json


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


class DBConnection:
    def __init__(self, host="localhost", port=5432, user="postgres", password="pratyush002", schema="tpch1g"):
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
