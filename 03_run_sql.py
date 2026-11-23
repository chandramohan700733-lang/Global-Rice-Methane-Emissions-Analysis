"""
Step 3: Run all queries in sql/analysis.sql on rice.db and print the results.
"""
import sqlite3
import pandas as pd

con = sqlite3.connect("rice.db")
queries = [q.strip() for q in open("sql/analysis.sql", encoding="utf8").read().split(";") if q.strip()]
for q in queries:
    print("\n" + q.splitlines()[0])
    print(pd.read_sql(q, con).to_string(index=False))
