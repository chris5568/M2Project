import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ==============================================================================
# 1. LOAD THE REQUIRED DATASETS
# ==============================================================================
print("Loading Olist marketplace files...")
items = pd.read_csv('/home/moswal/m2/M2Project/olist_order_items_dataset.csv')
products = pd.read_csv('/home/moswal/m2/M2Project/olist_products_dataset.csv')
translation = pd.read_csv('/home/moswal/m2/M2Project/product_category_name_translation.csv')

# ==============================================================================
# 2. DATA MANIPULATION & AGGREGATION
# ==============================================================================
print("Processing and merging relational tables...")
# Merge order items with product specs, then add English category translations
df = items.merge(products, on='product_id')
df = df.merge(translation, on='product_category_name')

# Calculate total volume sales, average item prices, and average shipping fees
category_analysis = df.groupby('product_category_name_english').agg(
    total_items_sold=('order_item_id', 'count'),
    avg_product_value=('price', 'mean'),
    avg_freight_charge=('freight_value', 'mean')
).reset_index()

# Round financial figures to standard two decimal places
category_analysis['avg_product_value'] = category_analysis['avg_product_value'].round(2)
category_analysis['avg_freight_charge'] = category_analysis['avg_freight_charge'].round(2)

# Sort the dataset by the highest item sales volume
category_analysis = category_analysis.sort_values(by='total_items_sold', ascending=False)

# ==============================================================================
# 3. TEXT-BASED REPORT EXPORT
# ==============================================================================
print("\n--- Olist Product Categories with Avg Value & Freight Charges ---")
print(category_analysis.head(15).to_string(index=False))
print("\nGenerating comprehensive 3-part visualization dashboard...")

# ==============================================================================
# 4. COMPREHENSIVE DASHBOARD VISUALIZATION BLOCK
# ==============================================================================
# Isolate the top 10 most popular categories by volume for clear graphing
top_10_categories = category_analysis.head(10).copy()

# Configure the plotting grid (1 row, 2 subplots side-by-side)
sns.set_theme(style="whitegrid")
fig, axes = plt.subplots(1, 2, figsize=(18, 8))

# Global Dashboard Super-Title
fig.suptitle('Olist Product Category Performance: Volume & Financial Breakdown (Top 10 Categories)', 
             fontsize=16, weight='bold', y=0.98)

# ------------------------------------------------------------------------------
# PLOT 1: TOTAL VOLUME SOLD
# ------------------------------------------------------------------------------
ax1 = sns.barplot(
    data=top_10_categories,
    y='product_category_name_english',
    x='total_items_sold',
    ax=axes[0],
    palette='Blues_r'
)
axes[0].set_title('Total Volume of Items Sold', fontsize=13, weight='bold', pad=10)
axes[0].set_xlabel('Number of Units Sold', fontsize=11)
axes[0].set_ylabel('Product Category (English)', fontsize=11)

# Add value labels to the volume bars
for container in ax1.containers:
    ax1.bar_label(container, fmt='%d units', padding=5, fontsize=10)

# ------------------------------------------------------------------------------
# PLOT 2: FINANCIAL BREAKDOWN (PRODUCT VALUE VS FREIGHT CHARGE)
# ------------------------------------------------------------------------------
# Melt the dataframe columns specifically for the side-by-side comparison chart
melted_df = pd.melt(
    top_10_categories, 
    id_vars=['product_category_name_english'], 
    value_vars=['avg_product_value', 'avg_freight_charge'],
    var_name='Metric', 
    value_name='Amount_BRL'
)
melted_df['Metric'] = melted_df['Metric'].replace({
    'avg_product_value': 'Avg Product Value',
    'avg_freight_charge': 'Avg Freight Charge'
})

ax2 = sns.barplot(
    data=melted_df, 
    y='product_category_name_english', 
    x='Amount_BRL', 
    hue='Metric', 
    ax=axes[1],
    palette='Set2'
)
axes[1].set_title('Average Cost Breakdown per Item', fontsize=13, weight='bold', pad=10)
axes[1].set_xlabel('Value in Brazilian Real (BRL R$)', fontsize=11)
axes[1].set_ylabel('')  # Remove y-axis label to avoid repeating the category column text
axes[1].set_yticklabels([])  # Hide y-ticks on the second chart to keep layout clean
axes[1].legend(title='Financial Metric', fontsize=10)

# Add financial markers to the second chart
for container in ax2.containers:
    ax2.bar_label(container, fmt='R$ %.1f', padding=5, fontsize=10)

# ==============================================================================
# 5. RENDER THE LAYOUT
# ==============================================================================
# Adjust margins so titles don't collide with subplot components
plt.tight_layout(rect=[0, 0, 1, 0.93])
plt.show()
