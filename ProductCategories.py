import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Load the required Olist datasets (Update paths if necessary)
base_path = '/home/moswal/m2/M2Project/'

order_items = pd.read_csv(f'{base_path}olist_order_items_dataset.csv')
orders = pd.read_csv(f'{base_path}olist_orders_dataset.csv')
customers = pd.read_csv(f'{base_path}olist_customers_dataset.csv')
products = pd.read_csv(f'{base_path}olist_products_dataset.csv')
translation = pd.read_csv(f'{base_path}product_category_name_translation.csv')

# 2. Merge datasets to link orders, customers, and product categories
# Link items to orders to get the customer_id
merged_df = pd.merge(order_items, orders, on='order_id', how='inner')
# Link to customers to get the customer_city
merged_df = pd.merge(merged_df, customers, on='customer_id', how='inner')
# Link to products to get the product_category_name
merged_df = pd.merge(merged_df, products, on='product_id', how='inner')
# Link to translation to get English names for a readable plot
merged_df = pd.merge(merged_df, translation, on='product_category_name', how='inner')

# 3. Identify the Top 3 Cities by overall sales revenue (price)
top_3_cities = merged_df.groupby('customer_city')['price'].sum().nlargest(3).index
print(f"Top 3 Cities by Sales Value: {list(top_3_cities)}")

# Filter the merged data to keep only transactions from these top 3 cities
df_top_cities = merged_df[merged_df['customer_city'].isin(top_3_cities)]

# 4. Calculate total sales per product category inside these top 3 cities
city_product_sales = df_top_cities.groupby(['customer_city', 'product_category_name_english'])['price'].sum().reset_index()

# Sort by city and sales revenue, then select the top 3 categories per city
top_products_per_city = city_product_sales.sort_values(
    by=['customer_city', 'price'], 
    ascending=[True, False]
).groupby('customer_city').head(3)

# Create a quick look matrix of categories vs cities
pivot_check = top_products_per_city.pivot(
    index='product_category_name_english', 
    columns='customer_city', 
    values='price'
)
print(pivot_check)

# 5. Plotting the results
plt.figure(figsize=(12, 6))
sns.set_theme(style="whitegrid")

# Create a grouped bar chart
ax = sns.barplot(
    data=top_products_per_city,
    x='customer_city',
    y='price',
    hue='product_category_name_english',
    palette='Set2'
)

# Customizing labels and titles
plt.title('Top 3 Product Categories by Sales Revenue in the Top 3 Cities', fontsize=15, fontweight='bold', pad=15)
plt.xlabel('Customer City', fontsize=12, fontweight='bold')
plt.ylabel('Total Sales (BRL)', fontsize=12, fontweight='bold')

# Format the y-axis with comma separators for clean financial reading
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))

# Adjust legend location so it doesn't overlap with bars
plt.legend(title='Product Category', bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=10)
plt.tight_layout()

# Save and show the plot
plt.savefig(f'{base_path}top_products_in_top_cities.png', dpi=300)
plt.show()


import pandas as pd

# 1. Load the required Olist datasets
base_path = '/home/moswal/m2/M2Project/'

order_items = pd.read_csv(f'{base_path}olist_order_items_dataset.csv')
products = pd.read_csv(f'{base_path}olist_products_dataset.csv')
translation = pd.read_csv(f'{base_path}product_category_name_translation.csv')
sellers = pd.read_csv(f'{base_path}olist_sellers_dataset.csv')

# 2. Filter for São Paulo (SP) sellers only
sp_sellers = sellers[sellers['seller_state'] == 'SP']

# 3. Calculate lifetime total revenue per São Paulo seller
sp_seller_revenue = order_items[order_items['seller_id'].isin(sp_sellers['seller_id'])] \
    .groupby('seller_id')['price'].sum().reset_index(name='total_revenue')

# 4. Define "Power Seller" threshold (Top 20% by revenue among SP sellers)
revenue_threshold = sp_seller_revenue['total_revenue'].quantile(0.80)

power_seller_ids = sp_seller_revenue[sp_seller_revenue['total_revenue'] >= revenue_threshold]['seller_id']
non_power_seller_ids = sp_seller_revenue[sp_seller_revenue['total_revenue'] < revenue_threshold]['seller_id']

print(f"Power Seller Threshold (Top 20%): >= {revenue_threshold:,.2f} BRL")
print(f"Number of Power Sellers in SP: {len(power_seller_ids)}")
print(f"Number of Non-Power Sellers in SP: {len(non_power_seller_ids)}\n")

# 5. Merge items with category details
merged_items = pd.merge(order_items, products, on='product_id', how='inner')
merged_items = pd.merge(merged_items, translation, on='product_category_name', how='inner')

# Filter for items sold by SP sellers
sp_items = merged_items[merged_items['seller_id'].isin(sp_sellers['seller_id'])].copy()

# 6. Assign a tier label to each item transaction
sp_items['seller_tier'] = 'Non-Power Seller'
sp_items.loc[sp_items['seller_id'].isin(power_seller_ids), 'seller_tier'] = 'Power Seller'

# 7. Find the Top 3 Product Categories by revenue for each tier
tier_product_sales = sp_items.groupby(['seller_tier', 'product_category_name_english'])['price'] \
    .sum().reset_index(name='category_revenue')

# Sort and slice the top 3 per tier
top_3_per_tier = tier_product_sales.sort_values(by=['seller_tier', 'category_revenue'], ascending=[True, False]) \
    .groupby('seller_tier').head(3).reset_index(drop=True)

# Format revenue for presentation
top_3_per_tier['category_revenue'] = top_3_per_tier['category_revenue'].map('{:,.2f} BRL'.format)

# Display the final tables
for tier in ['Power Seller', 'Non-Power Seller']:
    print(f"=== Top 3 Product Categories Sold by {tier}s ===")
    df_tier = top_3_per_tier[top_3_per_tier['seller_tier'] == tier][['product_category_name_english', 'category_revenue']]
    print(df_tier.to_string(index=False, header=['Product Category', 'Total Revenue']))
    print("\n")

    import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Load the required Olist datasets
base_path = '/home/moswal/m2/M2Project/'

order_items = pd.read_csv(f'{base_path}olist_order_items_dataset.csv')
products = pd.read_csv(f'{base_path}olist_products_dataset.csv')
translation = pd.read_csv(f'{base_path}product_category_name_translation.csv')
sellers = pd.read_csv(f'{base_path}olist_sellers_dataset.csv')

# 2. Filter for São Paulo (SP) sellers only
sp_sellers = sellers[sellers['seller_state'] == 'SP']

# 3. Calculate total product count (volume) per SP seller to rank them
sp_seller_volume = order_items[order_items['seller_id'].isin(sp_sellers['seller_id'])] \
    .groupby('seller_id').size().reset_index(name='total_units_sold')

# Sort sellers from absolute best to lowest performance
sp_seller_volume = sp_seller_volume.sort_values(by='total_units_sold', ascending=False).reset_index(drop=True)

num_sellers = len(sp_seller_volume)
print(f"Total active sellers in São Paulo: {num_sellers}")

# 4. Extract specific IDs for the 3 target groups
top_3_ids = sp_seller_volume.head(3)['seller_id'].tolist()

# Median group: Find the exact absolute middle index and grab 3 surrounding sellers
mid_idx = num_sellers // 2
median_3_ids = sp_seller_volume.iloc[mid_idx-1 : mid_idx+2]['seller_id'].tolist()

lowest_3_ids = sp_seller_volume.tail(3)['seller_id'].tolist()

# 5. Link items to categories
merged_items = pd.merge(order_items, products, on='product_id', how='inner')
merged_items = pd.merge(merged_items, translation, on='product_category_name', how='inner')

# Filter for just our target groups and tag them with their specific tier label
target_ids = top_3_ids + median_3_ids + lowest_3_ids

df_targets = merged_items[merged_items['seller_id'].isin(target_ids)].copy()

def assign_tier(seller_id):
    if seller_id in top_3_ids: return 'Top 3 Sellers'
    if seller_id in median_3_ids: return 'Median 3 Sellers'
    if seller_id in lowest_3_ids: return 'Lowest 3 Sellers'
    return 'Unknown'

df_targets['seller_group'] = df_targets['seller_id'].apply(assign_tier)

# 6. Group by tier and product category to count units sold
group_category_counts = df_targets.groupby(['seller_group', 'product_category_name_english']).size().reset_index(name='units_sold')

# 7. Consolidate long tail categories into "Other" per group to keep chart clean
processed_data = []
for group in ['Top 3 Sellers', 'Median 3 Sellers', 'Lowest 3 Sellers']:
    group_df = group_category_counts[group_category_counts['seller_group'] == group].copy()
    group_df = group_df.sort_values(by='units_sold', ascending=False)
    
    # Keep top 4 distinct categories per group, lump the rest into 'Other'
    top_4 = group_df.head(4)
    others_count = group_df.iloc[4:]['units_sold'].sum()
    
    if others_count > 0:
        other_row = pd.DataFrame([{
            'seller_group': group,
            'product_category_name_english': 'Other / Long Tail',
            'units_sold': others_count
        }])
        group_df_clean = pd.concat([top_4, other_row], ignore_index=True)
    else:
        group_df_clean = top_4
        
    processed_data.append(group_df_clean)

plot_df = pd.concat(processed_data, ignore_index=True)

# 8. Pivot the dataframe to align correctly for a stacked bar chart
pivot_df = plot_df.pivot(index='seller_group', columns='product_category_name_english', values='units_sold').fillna(0)
# Ensure clean visual order from top tier down to lowest
pivot_df = pivot_df.reindex(['Top 3 Sellers', 'Median 3 Sellers', 'Lowest 3 Sellers'])

# 9. Generate the Stacked Bar Chart
fig, ax = plt.subplots(figsize=(12, 7))

# Use an expansive color palette to differentiate overlapping category mixes
pivot_df.plot(kind='bar', stacked=True, ax=ax, cmap='tab20')

plt.title('Product Category Distribution Across São Paulo Seller Tiers', fontsize=15, fontweight='bold', pad=15)
plt.xlabel('Seller Performance Group', fontsize=12, fontweight='bold')
plt.ylabel('Total Units Sold', fontsize=12, fontweight='bold')
plt.xticks(rotation=0)

# Apply a log-scale on y axis only if the volume gap makes the small sellers invisible
# (Top sellers move thousands of items, while lowest sellers often have exactly 1 or 2 items)
if pivot_df.loc['Top 3 Sellers'].sum() / pivot_df.loc['Lowest 3 Sellers'].sum() > 100:
    ax.set_yscale('log')
    plt.ylabel('Total Units Sold (Log Scale for Visibility)', fontsize=12, fontweight='bold')

plt.legend(title='Product Category', bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=9)
plt.tight_layout()

# Save and show
plt.savefig(f'{base_path}sp_seller_tiers_stacked.png', dpi=300)
plt.show()

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Load the required Olist datasets
base_path = '/home/moswal/m2/M2Project/'

order_items = pd.read_csv(f'{base_path}olist_order_items_dataset.csv')
products = pd.read_csv(f'{base_path}olist_products_dataset.csv')
translation = pd.read_csv(f'{base_path}product_category_name_translation.csv')
sellers = pd.read_csv(f'{base_path}olist_sellers_dataset.csv')

# 2. Filter for São Paulo (SP) sellers only
sp_sellers = sellers[sellers['seller_state'] == 'SP']

# 3. Calculate total volume per SP seller to rank them
sp_seller_volume = order_items[order_items['seller_id'].isin(sp_sellers['seller_id'])] \
    .groupby('seller_id').size().reset_index(name='total_units_sold')

# Sort from absolute highest to lowest performance
sp_seller_volume = sp_seller_volume.sort_values(by='total_units_sold', ascending=False).reset_index(drop=True)
num_sellers = len(sp_seller_volume)

# 4. Extract specific IDs for the 3 target groups
top_3_ids = sp_seller_volume.head(3)['seller_id'].tolist()

mid_idx = num_sellers // 2
median_3_ids = sp_seller_volume.iloc[mid_idx-1 : mid_idx+2]['seller_id'].tolist()

lowest_3_ids = sp_seller_volume.tail(3)['seller_id'].tolist()

# 5. Link items to categories
merged_items = pd.merge(order_items, products, on='product_id', how='inner')
merged_items = pd.merge(merged_items, translation, on='product_category_name', how='inner')

# Filter for target groups and tag them
target_ids = top_3_ids + median_3_ids + lowest_3_ids
df_targets = merged_items[merged_items['seller_id'].isin(target_ids)].copy()

def assign_tier(seller_id):
    if seller_id in top_3_ids: return 'Top 3 Sellers'
    if seller_id in median_3_ids: return 'Median 3 Sellers'
    if seller_id in lowest_3_ids: return 'Lowest 3 Sellers'
    return 'Unknown'

df_targets['seller_group'] = df_targets['seller_id'].apply(assign_tier)

# 6. Calculate total units sold per exact category per group (No "Other" filtering)
final_counts = df_targets.groupby(['seller_group', 'product_category_name_english']).size().reset_index(name='units_sold')

# Sort data cleanly for visualization
final_counts = final_counts.sort_values(by=['seller_group', 'units_sold'], ascending=[True, False])

# 7. Print the raw data to console for exact validation
print("=== ACTUAL PRODUCT CATEGORY BREAKDOWN ===")
for group in ['Top 3 Sellers', 'Median 3 Sellers', 'Lowest 3 Sellers']:
    print(f"\n--- {group} ---")
    sub_df = final_counts[final_counts['seller_group'] == group][['product_category_name_english', 'units_sold']]
    print(sub_df.to_string(index=False, header=['Product Category', 'Units Sold']))

# 8. Plot the actual distribution using a horizontal layout to prevent overlap text
plt.figure(figsize=(12, 10))
sns.set_theme(style="whitegrid")

# Create horizontal grouped bars
ax = sns.barplot(
    data=final_counts,
    y='product_category_name_english',
    x='units_sold',
    hue='seller_group',
    palette='Set1',
    edgecolor='black'
)

# Use Log Scale because Top 3 move 1,000+ units, while Lowest 3 move exactly 1 unit
ax.set_xscale('log')

plt.title('Uncensored Product Category Sales Across São Paulo Seller Tiers', fontsize=15, fontweight='bold', pad=15)
plt.ylabel('Actual Product Category (English)', fontsize=12, fontweight='bold')
plt.xlabel('Units Sold (Log Scale for Visibility)', fontsize=12, fontweight='bold')
plt.legend(title='Seller Group', loc='lower right', fontsize=11)

plt.tight_layout()
plt.savefig(f'{base_path}sp_seller_tiers_actual.png', dpi=300)
plt.show()

import pandas as pd

# 1. Load the required Olist datasets
base_path = '/home/moswal/m2/M2Project/'

order_items = pd.read_csv(f'{base_path}olist_order_items_dataset.csv')
products = pd.read_csv(f'{base_path}olist_products_dataset.csv')
translation = pd.read_csv(f'{base_path}product_category_name_translation.csv')
sellers = pd.read_csv(f'{base_path}olist_sellers_dataset.csv')

# 2. Filter for São Paulo (SP) sellers
sp_sellers = sellers[sellers['seller_state'] == 'SP']

# 3. Identify the Top 3 Sellers in SP by total volume (units sold)
sp_order_items = order_items[order_items['seller_id'].isin(sp_sellers['seller_id'])]
top_3_sellers = sp_order_items.groupby('seller_id').size().nlargest(3).index.tolist()

# 4. Link the Top 3 sellers' items to their product categories
top_sellers_df = sp_order_items[sp_order_items['seller_id'].isin(top_3_sellers)].copy()
top_sellers_df = pd.merge(top_sellers_df, products, on='product_id', how='inner')
top_sellers_df = pd.merge(top_sellers_df, translation, on='product_category_name', how='inner')

# 5. Calculate total units sold per category across these Top 3 sellers
top_products = top_sellers_df.groupby('product_category_name_english').size().reset_index(name='Units Sold')
top_3_products = top_products.sort_values(by='Units Sold', ascending=False).head(3).reset_index(drop=True)
top_3_products.index += 1  # Start ranking from 1

print("=== TOP 3 PRODUCTS SOLD BY TOP 3 SELLERS IN SÃO PAULO ===")
print(top_3_products.to_string())