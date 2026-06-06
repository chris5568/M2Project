import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ==============================================================================
# 1. LOAD THE REQUIRED DATASETS
# ==============================================================================
print("Loading Olist transaction files...")
orders = pd.read_csv('/home/moswal/m2/M2Project/olist_orders_dataset.csv')
items = pd.read_csv('/home/moswal/m2/M2Project/olist_order_items_dataset.csv')

# ==============================================================================
# 2. DATA MANIPULATION & FEATURE ENGINEERING
# ==============================================================================
print("Formatting timestamps and building timeline...")
# Convert purchase strings into datetime objects
orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])

# Create a clean year column to filter the core timeframe
orders['year'] = orders['order_purchase_timestamp'].dt.year

# Create a chronological YYYY-MM column for chronological grouping
orders['year_month'] = orders['order_purchase_timestamp'].dt.to_period('M').astype(str)

# Combine datasets to tie the individual transaction values to their purchase month
df_merged = items.merge(orders, on='order_id')

# Filter exclusively for the primary project scope (2016 - 2018)
df_merged = df_merged[df_merged['year'].isin([2016, 2017, 2018])]

# Aggregate total item prices grouped month-by-month
monthly_sales = df_merged.groupby('year_month')['price'].sum().reset_index(name='total_revenue')

# Sort the dataset chronologically
monthly_sales = monthly_sales.sort_values(by='year_month')

# ==============================================================================
# 3. CONSOLE REPORT MATRIX
# ==============================================================================
print("\n--- Chronological Monthly Sales Revenue Report ---")
print(monthly_sales.to_string(index=False))

# ==============================================================================
# 4. MONTH-BY-MONTH TREND VISUALIZATION
# ==============================================================================
print("\nRendering chronological line chart dashboard...")
sns.set_theme(style="whitegrid")
plt.figure(figsize=(15, 7))

# Plot a line chart to reveal historical growth and seasonal spikes
ax = sns.lineplot(
    data=monthly_sales, 
    x='year_month', 
    y='total_revenue', 
    marker='o', 
    linewidth=2.5, 
    color='darkcyan'
)

# Apply descriptive labeling and structural headers
plt.title('Olist Marketplace Monthly Revenue Stream (2016-2018)', fontsize=15, weight='bold', pad=15)
plt.xlabel('Timeline Period (Year-Month)', fontsize=12)
plt.ylabel('Total Sales Revenue in Brazilian Real (BRL R$)', fontsize=12)

# Rotate labels by 45 degrees so they are readable without crowding each other
plt.xticks(rotation=45, ha='right')

# Format the Y-axis numbers to read clearly with standard currency comma separators
ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: f"R$ {int(x):,}"))

# Optional: Annotate the highest outlier data point (November 2017 Black Friday)
highest_month = monthly_sales.loc[monthly_sales['total_revenue'].idxmax()]
ax.annotate(
    f"Black Friday Peak\n(R$ {highest_month['total_revenue']:,.2f})", 
    xy=(highest_month['year_month'], highest_month['total_revenue']),
    xytext=(2, 15), 
    textcoords='offset points', 
    arrowprops=dict(arrowstyle="->", color="black"),
    fontsize=10, 
    weight='bold', 
    color='crimson'
)

# Adjust plot boundaries to clear rotated label space, then display
plt.tight_layout()
plt.show()