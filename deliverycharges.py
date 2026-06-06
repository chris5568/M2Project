import pandas as pd

# 1. Load the required dataset files
orders = pd.read_csv('/home/moswal/m2/M2Project/olist_orders_dataset.csv')
customers = pd.read_csv('/home/moswal/m2/M2Project/olist_customers_dataset.csv')
items = pd.read_csv('/home/moswal/m2/M2Project/olist_order_items_dataset.csv')
payments = pd.read_csv('/home/moswal/m2/M2Project/olist_order_payments_dataset.csv')

# 2. Merge dataframes to connect customer states with financials
df = orders.merge(customers, on='customer_id')
df = df.merge(items, on='order_id')
df = df.merge(payments, on='order_id')

# 3. Group by state and calculate totals
state_financials = df.groupby('customer_state').agg(
    total_freight=('freight_value', 'sum'),
    total_payment=('payment_value', 'sum')
).reset_index()

# 4. Calculate the percentage metric
state_financials['freight_percentage'] = (state_financials['total_freight'] / state_financials['total_payment'] * 100).round(2)

# 5. Sort output descending
state_financials = state_financials.sort_values(by='freight_percentage', ascending=False)
print(state_financials)

import matplotlib.pyplot as plt
import seaborn as sns

# Set up the plotting environment style
sns.set_theme(style="whitegrid")
plt.figure(figsize=(12, 8))

# Create a horizontal bar plot (y='customer_state' keeps the labels easy to read)
ax = sns.barplot(
    data=state_financials, 
    x='freight_percentage', 
    y='customer_state', 
    palette='viridis'
)

# Add titles and clean labels
plt.title('Freight Cost as a % of Total Payment by Brazilian State', fontsize=15, pad=15, weight='bold')
plt.xlabel('Freight Percentage (%)', fontsize=12)
plt.ylabel('Customer State', fontsize=12)

# Dynamically add the data percentage labels to the end of each bar
for container in ax.containers:
    ax.bar_label(container, fmt='%.1f%%', padding=5, fontsize=9)

# Optimize spacing and render the visual
plt.tight_layout()
plt.show()