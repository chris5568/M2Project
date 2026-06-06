import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Load the datasets from your local path
orders = pd.read_csv('/home/moswal/m2/M2Project/olist_orders_dataset.csv')
customers = pd.read_csv('/home/moswal/m2/M2Project/olist_customers_dataset.csv')

# 2. Filter for successfully delivered orders and drop rows missing timestamps
orders = orders[orders['order_status'] == 'delivered']
orders = orders.dropna(subset=['order_purchase_timestamp', 'order_delivered_customer_date'])

# 3. Convert string timestamps to datetime objects
orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])
orders['order_delivered_customer_date'] = pd.to_datetime(orders['order_delivered_customer_date'])

# 4. Calculate actual transit time in days
orders['delivery_time_days'] = (orders['order_delivered_customer_date'] - orders['order_purchase_timestamp']).dt.days

# 5. Merge with customers to map orders to cities
df_merged = orders.merge(customers, on='customer_id')

# 6. Group by city to find average delivery days and total order counts
city_metrics = df_merged.groupby('customer_city').agg(
    avg_delivery_days=('delivery_time_days', 'mean'),
    total_orders=('order_id', 'count')
).reset_index()

# 7. Extract the top 5 cities with the highest number of orders
top_5_cities = city_metrics.nlargest(5, 'total_orders').copy()
top_5_cities['avg_delivery_days'] = top_5_cities['avg_delivery_days'].round(1)

# 8. Display the text results
print("--- Top 5 Cities by Order Volume & Their Avg Delivery Times ---")
print(top_5_cities.to_string(index=False))

# 9. Optional: Plot the results immediately
import seaborn as sns
sns.set_theme(style="whitegrid")
plt.figure(figsize=(10, 5))

# Plotting average delivery days for the top 5 cities
ax = sns.barplot(
    data=top_5_cities.sort_values(by='avg_delivery_days'), 
    x='customer_city', 
    y='avg_delivery_days', 
    palette='Blues_r'
)

plt.title('Average Delivery Time for the Top 5 Highest-Volume Cities', fontsize=13, weight='bold', pad=15)
plt.xlabel('Customer City', fontsize=11)
plt.ylabel('Average Delivery Time (Days)', fontsize=11)

# Add data labels on top of the bars
for container in ax.containers:
    ax.bar_label(container, fmt='%.1f days', padding=3)

plt.tight_layout()
plt.show()
