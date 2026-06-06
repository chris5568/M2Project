import duckdb
import pandas as pd

# Step 1: Load CSV into a persistent file
with duckdb.connect(database='Module2projectdb.duckdb') as con:
    con.execute("CREATE TABLE customers_dataset AS SELECT * FROM read_csv_auto('/home/moswal/m2/M2Project/olist_customers_dataset.csv')")

# Step 2: Connect to the persistent .duckdb file and fetch the data
con = duckdb.connect(database='Module2projectdb.duckdb')

# Fixed: Added 'users' table name to the SELECT query
df = con.execute("SELECT * FROM customers_dataset").df()

# View the first few rows of your Olist customers DataFrame
print(df.head())