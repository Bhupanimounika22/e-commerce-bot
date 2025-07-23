import pandas as pd
import sqlite3
import os

os.makedirs('db', exist_ok=True)
conn = sqlite3.connect('db/datasets.db')

# Load and write each CSV to a table
pd.read_csv('data/ad_sales.csv').to_sql('ad_sales', conn, if_exists='replace', index=False)
pd.read_csv('data/total_sales.csv').to_sql('total_sales', conn, if_exists='replace', index=False)
pd.read_csv('data/eligibility.csv').to_sql('eligibility', conn, if_exists='replace', index=False)

conn.close()
print("Data imported successfully!") 