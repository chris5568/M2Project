import pandas as pd

# 1. Load the required datasets from your directory
orders = pd.read_csv('/home/moswal/m2/M2Project/olist_orders_dataset.csv')
customers = pd.read_csv('/home/moswal/m2/M2Project/olist_customers_dataset.csv')

# 2. Merge the files together on 'customer_id'
df_merged = orders.merge(customers, on='customer_id')

# 3. Group by city and count total order records
city_counts = df_merged.groupby('customer_city').size().reset_index(name='total_orders')

# 4. Extract the top 5 largest cities by volume
top_5_cities = city_counts.nlargest(5, 'total_orders')

# Display the final ranking
print("--- Top 5 Cities with Highest Customer Orders ---")
print(top_5_cities.to_string(index=False))
