import pandas as pd

# 1. Load data files
orders = pd.read_csv('/home/moswal/m2/M2Project/olist_orders_dataset.csv')
items = pd.read_csv('/home/moswal/m2/M2Project/olist_order_items_dataset.csv')

# 2. Extract purchase calendar year
orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])
orders['year'] = orders['order_purchase_timestamp'].dt.year

# 3. Merge to map years directly to sellers
df = items.merge(orders, on='order_id')

# Filter exclusively for the primary timeline
df = df[df['year'].isin([2016, 2017, 2018])]

print("=== APPROACH 1: YEAR-OVER-YEAR COHORT RETENTION ===")
# Find the exact set of active unique seller IDs for each calendar year
sellers_2016 = set(df[df['year'] == 2016]['seller_id'])
sellers_2017 = set(df[df['year'] == 2017]['seller_id'])
sellers_2018 = set(df[df['year'] == 2018]['seller_id'])

# Intersection calculations
recurring_in_2017 = sellers_2017.intersection(sellers_2016)
recurring_in_2018 = sellers_2018.intersection(sellers_2017.union(sellers_2016))

print(f"Sellers active in 2016: {len(sellers_2016)}")
print(f"Sellers in 2017 who previously sold in 2016: {len(recurring_in_2017)}")
print(f"Sellers in 2018 who previously sold in 2016 or 2017: {len(recurring_in_2018)}\n")


# --- ADDED CODE: COHORT PERCENTAGE CALCULATIONS ---
print("=== COHORT RETENTION PERCENTAGES ===")
pct_2016 = 0.0
pct_2017 = (len(recurring_in_2017) / len(sellers_2017)) * 100
pct_2018 = (len(recurring_in_2018) / len(sellers_2018)) * 100

print(f"2016 % Recurring: {pct_2016:.2f}% (0 / {len(sellers_2016)})")
print(f"2017 % Recurring: {pct_2017:.2f}% ({len(recurring_in_2017)} / {len(sellers_2017)})")
print(f"2018 % Recurring: {pct_2018:.2f}% ({len(recurring_in_2018)} / {len(sellers_2018)})\n")


print("=== APPROACH 2: SELLER FREQUENCY WITHIN THE SAME YEAR ===")
# Count transactions per seller per year
seller_activity = df.groupby(['year', 'seller_id']).size().reset_index(name='order_count')

# Flag high frequency sellers who processed more than 10 separate items
for yr in [2016, 2017, 2018]:
    yr_data = seller_activity[seller_activity['year'] == yr]
    high_freq = yr_data[yr_data['order_count'] > 10]
    print(f"In {yr}, {len(high_freq)} sellers processed more than 10 orders.")
