import pandas as pd

# 1. Load the required Olist files
df_orders = pd.read_csv('olist_orders_dataset.csv')
df_customers = pd.read_csv('olist_customers_dataset.csv')
df_items = pd.read_csv('olist_order_items_dataset.csv')
df_payments = pd.read_csv('olist_order_payments_dataset.csv')

# 2. Convert timestamp strings to datetime objects
df_orders['order_purchase_timestamp'] = pd.to_datetime(df_orders['order_purchase_timestamp'])
df_orders['order_delivered_customer_date'] = pd.to_datetime(df_orders['order_delivered_customer_date'])

# 3. Calculate Delivery Timing (in days)
df_orders['delivery_timing_days'] = (df_orders['order_delivered_customer_date'] - df_orders['order_purchase_timestamp']).dt.days

# 4. Extract the purchase year
df_orders['year'] = df_orders['order_purchase_timestamp'].dt.year

# Filter for relevant years (2016, 2017, 2018)
df_orders = df_orders[df_orders['year'].isin([2016, 2017, 2018])]

# 5. Aggregate Freight Charges at the Order Level
# (Since an order can have multiple items, sum the freight values first)
df_order_freight = df_items.groupby('order_id')['freight_value'].sum().reset_index()

# 6. Aggregate Total Payment at the Order Level
# (Orders can have multiple payment methods/installments, sum them up)
df_order_payments = df_payments.groupby('order_id')['payment_value'].sum().reset_index()

# 7. Merge the datasets together
# Start with orders and link the customer state
df_merged = df_orders.merge(df_customers, on='customer_id', how='inner')
# Add the freight charges
df_merged = df_merged.merge(df_order_freight, on='order_id', how='left')
# Add total customer payment
df_merged = df_merged.merge(df_order_payments, on='order_id', how='left')

# 8. Group by State and Year to calculate final metrics
final_report = df_merged.groupby(['customer_state', 'year']).agg(
    avg_delivery_timing_days=('delivery_timing_days', 'mean'),
    total_freight_charges=('freight_value', 'sum'),
    avg_freight_per_order=('freight_value', 'mean'),
    total_customer_paid=('payment_value', 'sum'),
    avg_customer_paid_per_order=('payment_value', 'mean'),
    total_orders=('order_id', 'count')
).reset_index()

# Format numeric output for readability
final_report['avg_delivery_timing_days'] = final_report['avg_delivery_timing_days'].round(1)
final_report['total_freight_charges'] = final_report['total_freight_charges'].round(2)
final_report['avg_freight_per_order'] = final_report['avg_freight_per_order'].round(2)
final_report['total_customer_paid'] = final_report['total_customer_paid'].round(2)
final_report['avg_customer_paid_per_order'] = final_report['avg_customer_paid_per_order'].round(2)

# Display the final structured output
print(final_report.to_string(index=False))