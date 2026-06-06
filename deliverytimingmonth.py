import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ==============================================================================
# 1. LOAD THE REQUIRED DATASETS
# ==============================================================================
print("Loading Olist transaction files...")
orders = pd.read_csv('/home/moswal/m2/M2Project/olist_orders_dataset.csv')
items = pd.read_csv('/home/moswal/m2/M2Project/olist_order_items_dataset.csv')
customers = pd.read_csv('/home/moswal/m2/M2Project/olist_customers_dataset.csv')
reviews = pd.read_csv('/home/moswal/m2/M2Project/olist_order_reviews_dataset.csv')

# ==============================================================================
# 2. DATA CLEANING & TRANSIT TIME CALCULATION
# ==============================================================================
print("Processing transaction dates and transit times...")
# Filter for successfully delivered orders and drop missing delivery records
orders = orders[orders['order_status'] == 'delivered']
orders = orders.dropna(subset=['order_purchase_timestamp', 'order_delivered_customer_date'])

# Convert timestamp strings to datetime objects
orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])
orders['order_delivered_customer_date'] = pd.to_datetime(orders['order_delivered_customer_date'])

# Calculate actual delivery timing in days
orders['delivery_time_days'] = (orders['order_delivered_customer_date'] - orders['order_purchase_timestamp']).dt.days

# Extract the calendar year and create a chronological YYYY-MM grouping column
orders['year'] = orders['order_purchase_timestamp'].dt.year
orders['year_month'] = orders['order_purchase_timestamp'].dt.to_period('M').astype(str)

# Filter exclusively for the primary project timeline (2016 - 2018)
orders_filtered = orders[orders['year'].isin([2016, 2017, 2018])]

# ==============================================================================
# 3. IDENTIFY TOP 5 CITIES BY TOTAL SALES REVENUE
# ==============================================================================
print("Identifying top 5 cities by total sales revenue...")
# Merge items, orders, and customers to compute gross revenue per city
revenue_df = items.merge(orders_filtered, on='order_id').merge(customers, on='customer_id')
city_revenue = revenue_df.groupby('customer_city')['price'].sum().reset_index()
top_5_cities_list = city_revenue.nlargest(5, 'price')['customer_city'].tolist()

print(f"Top 5 Cities Selected: {top_5_cities_list}")

# ==============================================================================
# 4. MERGE REVIEWS AND PREPARE PLOTTING DATAFRAME
# ==============================================================================
# Final merge to link orders, customers, and reviews together
master_df = orders_filtered.merge(customers, on='customer_id').merge(reviews, on='order_id')

# ==============================================================================
# 5. GENERATE 5 SEPARATE PLOTS (FIXED ZIP FUNCTION)
# ==============================================================================
print("\nGenerating 5 separate dual-axis line charts...")
sns.set_theme(style="whitegrid")

color_delivery = 'chocolate'
color_rating = 'teal'

# Loop through each city and render a unique independent figure window
for i, city in enumerate(top_5_cities_list, start=1):
    # Filter data for this specific city
    city_data = master_df[master_df['customer_city'] == city]
    
    # Aggregate average delivery days and average customer ratings month-by-month
    monthly_city_metrics = city_data.groupby('year_month').agg(
        avg_delivery_days=('delivery_time_days', 'mean'),
        avg_customer_rating=('review_score', 'mean'),
        total_orders=('order_id', 'count')
    ).reset_index().sort_values(by='year_month')
    
    # Skip plotting if the city doesn't have sufficient multi-month timeline records
    if len(monthly_city_metrics) < 2:
        continue
        
    # Instantiate a completely separate figure window
    fig, ax1 = plt.subplots(figsize=(14, 6))
    
    # --------------------------------------------------------------------------
    # LEFT Y-AXIS: Average Delivery Timing (Days)
    # --------------------------------------------------------------------------
    sns.lineplot(
        data=monthly_city_metrics, 
        x='year_month', 
        y='avg_delivery_days', 
        marker='o', 
        linewidth=2.5, 
        color=color_delivery,
        ax=ax1,
        label='Avg Delivery Days'
    )
    
    ax1.set_title(f"Plot {i}: {city.upper()} - Operational Speed vs. Customer Ratings", fontsize=14, weight='bold', pad=15)
    ax1.set_xlabel('Timeline Period (Year-Month)', fontsize=11)
    ax1.set_ylabel('Average Delivery Time (Days)', color=color_delivery, fontsize=12)
    ax1.tick_params(axis='y', labelcolor=color_delivery)
    ax1.set_xticklabels(monthly_city_metrics['year_month'], rotation=45, ha='right')
    
    # Add values above the delivery points for stable sample sizes
    for x, y, vol in zip(monthly_city_metrics['year_month'], monthly_city_metrics['avg_delivery_days'], monthly_city_metrics['total_orders']):
        if vol > 2:
            ax1.text(x, y + 0.5, f"{y:.1f}d", ha='center', color='saddlebrown', fontsize=8, weight='bold')

    # --------------------------------------------------------------------------
    # RIGHT Y-AXIS: Average Customer Rating (Stars)
    # --------------------------------------------------------------------------
    ax2 = ax1.twinx()  
    sns.lineplot(
        data=monthly_city_metrics, 
        x='year_month', 
        y='avg_customer_rating', 
        marker='s', 
        linewidth=2.5, 
        color=color_rating,
        ax=ax2,
        label='Avg Customer Rating'
    )
    
    ax2.set_ylabel('Average Customer Rating (Stars 1-5)', color=color_rating, fontsize=12)
    ax2.tick_params(axis='y', labelcolor=color_rating)
    ax2.set_ylim(2.5, 5.0)  # Zoomed scale to clearly view drops across all cities
    ax2.grid(False)         # Remove secondary grid overlap lines
    
    # FIX: Removed the internal assignment labels inside zip()
    for x, y, vol in zip(monthly_city_metrics['year_month'], monthly_city_metrics['avg_customer_rating'], monthly_city_metrics['total_orders']):
        if vol > 2:
            ax2.text(x, y - 0.12, f"{y:.2f}★", ha='center', color='darkslategrey', fontsize=8, weight='bold')

    # Combine the legends into a single box container on the left
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.get_legend().remove()
    ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=10)
    
    plt.tight_layout()
    plt.show()