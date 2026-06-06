import pandas as pd

# 1. Load the required datasets
order_items = pd.read_csv('/home/moswal/m2/M2Project/olist_order_items_dataset.csv')
products = pd.read_csv('/home/moswal/m2/M2Project/olist_products_dataset.csv')
translation = pd.read_csv('/home/moswal/m2/M2Project/product_category_name_translation.csv') 

# Calculate absolute global metrics for percentage calculations
total_revenue_all_sellers = order_items['price'].sum()

# 2. Merge datasets to link sellers to their product categories
merged_df = pd.merge(order_items, products, on='product_id', how='inner')
merged_df = pd.merge(merged_df, translation, on='product_category_name', how='inner')

# 3. Calculate metrics per seller per category (Sum for revenue, Count for products sold)
seller_category_metrics = merged_df.groupby(['seller_id', 'product_category_name_english']).agg(
    category_revenue=('price', 'sum'),
    products_sold_in_category=('order_item_id', 'count')
).reset_index()

# 4. Find the absolute top 10 sellers based on total revenue across all their categories
seller_totals = merged_df.groupby('seller_id').agg(
    total_revenue=('price', 'sum'),
    total_products_sold=('order_item_id', 'count')
).reset_index()

top_10_sellers_list = seller_totals.sort_values(by='total_revenue', ascending=False).head(10)

# 5. Find the primary category (what they made the most money from) for each seller
primary_categories = seller_category_metrics.sort_values(['seller_id', 'category_revenue'], ascending=[True, False]).drop_duplicates('seller_id')

# 6. Merge the top 10 sellers with their primary category details
final_top_10 = pd.merge(top_10_sellers_list, primary_categories[['seller_id', 'product_category_name_english']], on='seller_id', how='left')

# 7. Calculate % of Total Sales (Revenue) against the ENTIRE platform
final_top_10['% of Total Sales'] = (final_top_10['total_revenue'] / total_revenue_all_sellers) * 100

# 8. Clean up the final DataFrame for display
final_top_10 = final_top_10.rename(columns={
    'seller_id': 'Seller ID',
    'total_revenue': 'Total Sales (BRL)',
    'total_products_sold': 'Total Products Sold',
    'product_category_name_english': 'Primary Product Category'
})

# Sort, reset index to start from 1
final_top_10 = final_top_10.sort_values(by='Total Sales (BRL)', ascending=False).reset_index(drop=True)
final_top_10.index += 1 

# Format percentages and currency for cleaner printing
final_top_10['% of Total Sales'] = final_top_10['% of Total Sales'].map('{:.2f}%'.format)
final_top_10['Total Sales (BRL)'] = final_top_10['Total Sales (BRL)'].map('{:,.2f}'.format)

print(final_top_10)