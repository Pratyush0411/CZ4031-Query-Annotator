import psycopg2
import json

class DBConnection:
    def __init__(self, host="localhost", port = 5432, user="postgres", password="password123", schema="tpch1g"):
        self.schema = schema
        self.conn = psycopg2.connect(host=host, port=port, user=user, password=password)
        
        self.cur = self.conn.cursor()
        
        self.cur.execute(f"SET search_path TO {schema};")

    def execute(self,query):
        self.cur.execute(query)
        query_results = self.cur.fetchall()
        return query_results

    def close(self):
        self.cur.close()
        self.conn.close()
        
        