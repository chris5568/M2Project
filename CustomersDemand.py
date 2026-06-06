import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Define your local base path
base_path = '/home/moswal/m2/M2Project/'

# 2. Load the required Olist datasets
order_items = pd.read_csv(f'{base_path}olist_order_items_dataset.csv')
orders = pd.read_csv(f'{base_path}olist_orders_dataset.csv')
customers = pd.read_csv(f'{base_path}olist_customers_dataset.csv')
sellers = pd.read_csv(f'{base_path}olist_sellers_dataset.csv')
products = pd.read_csv(f'{base_path}olist_products_dataset.csv')
translation = pd.read_csv(f'{base_path}product_category_name_translation.csv')

# 3. Master Merge (Linking Customer Location, Seller Location, and Categories)
merged_df = pd.merge(order_items, orders, on='order_id', how='inner')
merged_df = pd.merge(merged_df, customers, on='customer_id', how='inner')
merged_df = pd.merge(merged_df, sellers, on='seller_id', how='inner')
merged_df = pd.merge(merged_df, products, on='product_id', how='inner')
merged_df = pd.merge(merged_df, translation, on='product_category_name', how='inner')

# === NEW: Filter for 2017 and 2018 data only ===
merged_df['order_purchase_timestamp'] = pd.to_datetime(merged_df['order_purchase_timestamp'])
merged_df = merged_df[merged_df['order_purchase_timestamp'].dt.year.isin([2017, 2018])]

# 4. Identify the Top 3 Highest Cities based on Customer Orders (Demand hubs)
top_3_cities = merged_df.groupby('customer_city')['order_id'].nunique().nlargest(3).index.tolist()
print(f"Top 3 Identified Market Cities (2017-2018): {top_3_cities}")

# 5. Identify the Top 5 Product Categories overall across the entire platform
top_5_categories = merged_df['product_category_name_english'].value_counts().head(5).index.tolist()
print(f"Top 5 Target Product Categories (2017-2018): {top_5_categories}\n")

# 6. Filter master dataframe for our target parameters
df_filtered = merged_df[
    (merged_df['customer_city'].isin(top_3_cities)) & 
    (merged_df['product_category_name_english'].isin(top_5_categories))
]

# 7. Calculate DEMAND (Count items ordered by customers residing in those cities)
demand_df = df_filtered.groupby(['customer_city', 'product_category_name_english']).size().reset_index(name='Volume')
demand_df['Metric'] = 'Demand (Customer City)'
demand_df = demand_df.rename(columns={'customer_city': 'City'})

# 8. Calculate SUPPLY (Count items fulfilled by sellers residing in those same cities)
# Note: We filter the main merged data where seller_city is one of our top 3 consumer cities
df_supply_filtered = merged_df[
    (merged_df['seller_city'].isin(top_3_cities)) & 
    (merged_df['product_category_name_english'].isin(top_5_categories))
]
supply_df = df_supply_filtered.groupby(['seller_city', 'product_category_name_english']).size().reset_index(name='Volume')
supply_df['Metric'] = 'Supply (Seller City)'
supply_df = supply_df.rename(columns={'seller_city': 'City'})

# 9. Combine dataframes for plotting
plot_data = pd.concat([demand_df, supply_df], ignore_index=True)

# 10. Generate a Faceted Plot to cleanly show Demand vs Supply side-by-side per city
sns.set_theme(style="whitegrid")

g = sns.catplot(
    data=plot_data,
    x='product_category_name_english',
    y='Volume',
    hue='Metric',
    col='City',
    kind='bar',
    palette='Set1',
    height=5,
    aspect=1.2,
    edgecolor='black'
)

# Rotate labels for crisp text layout
g.set_xticklabels(rotation=45, horizontalalignment='right')

# Adjust layout titles
g.set_titles("{col_name}", size=14, weight='bold')
g.set_axis_labels("Product Category", "Total Item Volume", fontsize=12, fontweight='bold')

plt.subplots_adjust(top=0.8)
g.fig.suptitle('Demand (Customer Orders) vs Supply (Seller Fulfillment) in Top Cities (2017-2018)', fontsize=16, fontweight='bold')

# Save and Show
plt.savefig(f'{base_path}demand_supply_top_cities_2017_2018.png', dpi=300, bbox_inches='tight')
plt.show()

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# 1. Setup global plotting aesthetics
sns.set_theme(style="whitegrid")

# 2. Load the required Olist datasets
orders = pd.read_csv("olist_orders_dataset.csv")
order_items = pd.read_csv("olist_order_items_dataset.csv")
customers = pd.read_csv("olist_customers_dataset.csv")
sellers = pd.read_csv("olist_sellers_dataset.csv")

# 3. Master Merge to link orders, customers, and sellers
merged_df = pd.merge(order_items, orders, on="order_id", how="inner")
merged_df = pd.merge(merged_df, customers, on="customer_id", how="inner")
merged_df = pd.merge(merged_df, sellers, on="seller_id", how="inner")

# 4. Filter for Year 2017 and Customer City = "sao paulo"
merged_df["order_purchase_timestamp"] = pd.to_datetime(
    merged_df["order_purchase_timestamp"]
)
df_2017_sp = merged_df[
    (merged_df["order_purchase_timestamp"].dt.year == 2017)
    & (merged_df["customer_city"].str.lower() == "sao paulo")
].copy()

# 5. Segment sellers into Inside vs Outside São Paulo
# We classify based on unique orders (order_id)
df_unique_orders = df_2017_sp.drop_duplicates(subset=["order_id"]).copy()

df_unique_orders["Seller Location"] = df_unique_orders["seller_city"].apply(
    lambda x: (
        "Inside São Paulo"
        if x.lower() == "sao paulo"
        else "Outside São Paulo"
    )
)

# 6. Calculate counts
location_counts = (
    df_unique_orders["Seller Location"]
    .value_counts()
    .reset_index(name="Order Count")
)
print("=== 2017 SÃO PAULO CUSTOMER ORDER BREAKDOWN ===")
print(location_counts.to_string(index=False))

# 7. Plot the Information
plt.figure(figsize=(8, 6))

ax = sns.barplot(
    data=location_counts,
    x="Seller Location",
    y="Order Count",
    palette="Set2",
    edgecolor="black",
)

# Add value labels on top of the bars
for container in ax.containers:
    ax.bar_label(container, fmt="%d", padding=3, fontsize=11, fontweight="bold")

# Customize titles and labels
plt.title(
    "Fulfillment Sources for São Paulo Customers in 2017\n(Total Unique Orders)",
    fontsize=14,
    fontweight="bold",
    pad=15,
)
plt.xlabel("Seller Location Relative to Customer", fontsize=12, fontweight="bold")
plt.ylabel("Number of Orders", fontsize=12, fontweight="bold")

# Clean up layout and display
plt.tight_layout()
plt.show()


import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# 1. Setup global plotting aesthetics
sns.set_theme(style="whitegrid")

# 2. Load the required Olist datasets
orders = pd.read_csv("olist_orders_dataset.csv")
order_items = pd.read_csv("olist_order_items_dataset.csv")
customers = pd.read_csv("olist_customers_dataset.csv")
sellers = pd.read_csv("olist_sellers_dataset.csv")

# 3. Master Merge to link orders, customers, and sellers
merged_df = pd.merge(order_items, orders, on="order_id", how="inner")
merged_df = pd.merge(merged_df, customers, on="customer_id", how="inner")
merged_df = pd.merge(merged_df, sellers, on="seller_id", how="inner")

# 4. Filter for Years 2017 & 2018 and Customer City = "sao paulo"
merged_df["order_purchase_timestamp"] = pd.to_datetime(
    merged_df["order_purchase_timestamp"]
)
merged_df["Year"] = merged_df["order_purchase_timestamp"].dt.year

df_filtered = merged_df[
    (merged_df["Year"].isin([2017, 2018]))
    & (merged_df["customer_city"].str.lower() == "sao paulo")
].copy()

# 5. Segment sellers into Inside vs Outside São Paulo using unique orders
df_unique_orders = df_filtered.drop_duplicates(subset=["order_id"]).copy()

df_unique_orders["Seller Location"] = df_unique_orders["seller_city"].apply(
    lambda x: (
        "Inside São Paulo"
        if x.lower() == "sao paulo"
        else "Outside São Paulo"
    )
)

# 6. Calculate counts grouped by Year and Seller Location
breakdown_df = (
    df_unique_orders.groupby(["Year", "Seller Location"])
    .size()
    .reset_index(name="Order Count")
)

print("=== SÃO PAULO CUSTOMER ORDER BREAKDOWN (2017-2018) ===")
print(breakdown_df.to_string(index=False))

# 7. Plot the Information in a Side-by-Side Grouped Bar Chart
plt.figure(figsize=(10, 6))

ax = sns.barplot(
    data=breakdown_df,
    x="Year",
    y="Order Count",
    hue="Seller Location",
    palette="Set2",
    edgecolor="black",
)

# Add exact value labels on top of each bar
for container in ax.containers:
    ax.bar_label(container, fmt="%d", padding=3, fontsize=10, fontweight="bold")

# Customize titles and labels
plt.title(
    "Fulfillment Sources for São Paulo Customers (2017 vs 2018)\n(Total Unique Orders)",
    fontsize=14,
    fontweight="bold",
    pad=15,
)
plt.xlabel("Order Year", fontsize=12, fontweight="bold")
plt.ylabel("Number of Orders", fontsize=12, fontweight="bold")
plt.legend(title="Seller Location", loc="upper left")

# Clean up layout and display
plt.tight_layout()
plt.show()

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# 1. Setup global plotting aesthetics
sns.set_theme(style="whitegrid")

# 2. Load the required Olist datasets
orders = pd.read_csv("olist_orders_dataset.csv")
order_items = pd.read_csv("olist_order_items_dataset.csv")
customers = pd.read_csv("olist_customers_dataset.csv")
sellers = pd.read_csv("olist_sellers_dataset.csv")

# 3. Master Merge to link orders, customers, and sellers
merged_df = pd.merge(order_items, orders, on="order_id", how="inner")
merged_df = pd.merge(merged_df, customers, on="customer_id", how="inner")
merged_df = pd.merge(merged_df, sellers, on="seller_id", how="inner")

# 4. Filter for Years 2017 & 2018 and Customer City = "sao paulo"
merged_df["order_purchase_timestamp"] = pd.to_datetime(
    merged_df["order_purchase_timestamp"]
)
merged_df["Year"] = merged_df["order_purchase_timestamp"].dt.year

df_filtered = merged_df[
    (merged_df["Year"].isin([2017, 2018]))
    & (merged_df["customer_city"].str.lower() == "sao paulo")
].copy()

# 5. Drop duplicate item entries to evaluate unique orders
df_unique_orders = df_filtered.drop_duplicates(subset=["order_id"]).copy()

df_unique_orders["Seller Location"] = df_unique_orders["seller_city"].apply(
    lambda x: (
        "Inside São Paulo"
        if x.lower() == "sao paulo"
        else "Outside São Paulo"
    )
)

# 6. Restructure data for a stacked bar chart layout
# This calculates the absolute counts per group, then pivots it to stack easily
pivot_df = (
    df_unique_orders.groupby(["Year", "Seller Location"])
    .size()
    .unstack(fill_value=0)
)

# Add a Total column to explicitly track all customer orders from São Paulo
pivot_df["Total Customer Orders"] = (
    pivot_df["Inside São Paulo"] + pivot_df["Outside São Paulo"]
)

print("=== SÃO PAULO TOTAL CUSTOMER ORDERS & SELLER BREAKDOWN ===")
print(pivot_df.to_string())

# 7. Plot the Data as a Stacked Bar Chart
fig, ax = plt.subplots(figsize=(8, 6))

# Plot the base segments
pivot_df[["Inside São Paulo", "Outside São Paulo"]].plot(
    kind="bar", stacked=True, ax=ax, color=["#4c72b0", "#c44e52"], edgecolor="black"
)

# Add text labels for the segments and the overall totals
for i, (year, row) in enumerate(pivot_df.iterrows()):
    inside_val = row["Inside São Paulo"]
    outside_val = row["Outside São Paulo"]
    total_val = row["Total Customer Orders"]

    # Label for Inside SP segment (placed in the middle of its block)
    ax.text(
        i,
        inside_val / 2,
        f"{inside_val}",
        ha="center",
        va="center",
        color="white",
        fontweight="bold",
    )

    # Label for Outside SP segment (placed in the middle of its block)
    ax.text(
        i,
        inside_val + (outside_val / 2),
        f"{outside_val}",
        ha="center",
        va="center",
        color="white",
        fontweight="bold",
    )

    # Label for the Absolute Total Volume on top of the entire bar
    ax.text(
        i,
        total_val + (total_val * 0.01),
        f"Total: {total_val}",
        ha="center",
        va="bottom",
        color="black",
        fontweight="bold",
        fontsize=11,
    )

# Customize titles, labels, and rotations
plt.title(
    "Total Orders Placed by São Paulo Customers\nSegmented by Seller Origin (2017 vs 2018)",
    fontsize=14,
    fontweight="bold",
    pad=20,
)
plt.xlabel("Order Year", fontsize=12, fontweight="bold")
plt.ylabel("Number of Unique Orders", fontsize=12, fontweight="bold")
plt.xticks(rotation=0)

# Move legend outside of plot data area cleanly
plt.legend(title="Seller Location", loc="upper left")

# Extend the y-axis slightly to ensure the top text labels do not get clipped
ax.set_ylim(0, pivot_df["Total Customer Orders"].max() * 1.1)

plt.tight_layout()
plt.show()