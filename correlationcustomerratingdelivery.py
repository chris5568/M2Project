import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# 1. Setup global plotting aesthetics
sns.set_theme(style="whitegrid")
plt.rcParams.update({"font.size": 11, "axes.labelsize": 12})

# 2. Load the Olist dataset files
# Ensure these files are placed in your working directory
orders = pd.read_csv("olist_orders_dataset.csv")
reviews = pd.read_csv("olist_order_reviews_dataset.csv")
customers = pd.read_csv("olist_customers_dataset.csv")

# 3. Filter for delivered orders and convert date columns cleanly
orders = orders[orders["order_status"] == "delivered"].dropna(
    subset=["order_delivered_customer_date", "order_estimated_delivery_date"]
)

orders["order_delivered_customer_date"] = pd.to_datetime(
    orders["order_delivered_customer_date"]
)
orders["order_estimated_delivery_date"] = pd.to_datetime(
    orders["order_estimated_delivery_date"]
)

# 4. Calculate delivery performance (Difference in days)
# Positive = Late, Negative = Early
orders["delivery_delay_days"] = (
    orders["order_delivered_customer_date"]
    - orders["order_estimated_delivery_date"]
).dt.total_seconds() / (24 * 3600)

# 5. Merge dataframes to link customer locations with their reviews
df = orders.merge(reviews, on="order_id", how="inner").merge(
    customers, on="customer_id", how="inner"
)

# 6. Extract the top 5 cities with the highest transaction volumes
top_5_cities = (
    df.groupby("customer_city")["order_id"].count().nlargest(5).index.tolist()
)

# Filter main dataset for only these 5 locations
df_top5 = df[df["customer_city"].isin(top_5_cities)].copy()
df_top5["customer_city"] = df_top5["customer_city"].str.title()

# 7. Create the Multi-Panel Regression Grid Visualization
fig, axes = plt.subplots(1, 5, figsize=(22, 5), sharey=True)

# Sort alphabetically so the subplots match sequentially
sorted_cities = sorted(df_top5["customer_city"].unique())

for i, city in enumerate(sorted_cities):
    city_data = df_top5[df_top5["customer_city"] == city]

    # Sample data points if the city dataset is massive (improves plot rendering speed)
    sample_size = min(len(city_data), 500)
    plot_sample = city_data.sample(n=sample_size, random_state=42)

    # Plot using x and y jittering to accommodate the discrete 1-to-5 review structure
    sns.regplot(
        data=plot_sample,
        x="delivery_delay_days",
        y="review_score",
        ax=axes[i],
        scatter_kws={"alpha": 0.25, "color": "#2b5c8f"},
        line_kws={"color": "#d9534f", "linewidth": 2.5},
        x_jitter=0.3,
        y_jitter=0.2,
    )

    # Calculate Pearson correlation coefficient on the complete data for that city
    r_value = city_data["delivery_delay_days"].corr(city_data["review_score"])

    # Configure subplots properties
    axes[i].set_title(f"{city}\nCorrelation ($r$): {r_value:.2f}", weight="bold")
    axes[i].set_xlabel("Delivery Delay (Days)")
    axes[i].set_xlim(-15, 20)  # Focus window around the zero delivery target line

    if i == 0:
        axes[i].set_ylabel("Customer Review Score (1-5)")
    else:
        axes[i].set_ylabel("")

# Global layout settings
plt.suptitle(
    "How Delivery Delays Impact Customer Satisfaction Across the Top 5 Cities",
    y=1.08,
    fontsize=16,
    weight="bold",
)
plt.tight_layout()

# Render plot
plt.show()


import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# 1. Setup global plotting aesthetics
sns.set_theme(style="whitegrid")
plt.rcParams.update({"font.size": 11, "axes.labelsize": 12})

# 2. Load the Olist dataset files
# Ensure these files are placed in your working directory
orders = pd.read_csv("olist_orders_dataset.csv")
reviews = pd.read_csv("olist_order_reviews_dataset.csv")
customers = pd.read_csv("olist_customers_dataset.csv")

# 3. Filter for delivered orders and convert date columns cleanly
orders = orders[orders["order_status"] == "delivered"].dropna(
    subset=["order_delivered_customer_date", "order_estimated_delivery_date"]
)

orders["order_delivered_customer_date"] = pd.to_datetime(
    orders["order_delivered_customer_date"]
)
orders["order_estimated_delivery_date"] = pd.to_datetime(
    orders["order_estimated_delivery_date"]
)

# === NEW: Filter for 2017 and 2018 data only ===
orders["order_purchase_timestamp"] = pd.to_datetime(orders["order_purchase_timestamp"])
orders = orders[orders["order_purchase_timestamp"].dt.year.isin([2017, 2018])]

# 4. Calculate delivery performance (Difference in days)
# Positive = Late, Negative = Early
orders["delivery_delay_days"] = (
    orders["order_delivered_customer_date"]
    - orders["order_estimated_delivery_date"]
).dt.total_seconds() / (24 * 3600)

# 5. Merge dataframes to link customer locations with their reviews
df = orders.merge(reviews, on="order_id", how="inner").merge(
    customers, on="customer_id", how="inner"
)

# 6. Extract the top 5 cities with the highest transaction volumes (for 2017-2018)
top_5_cities = (
    df.groupby("customer_city")["order_id"].count().nlargest(5).index.tolist()
)

# Filter main dataset for only these 5 locations
df_top5 = df[df["customer_city"].isin(top_5_cities)].copy()
df_top5["customer_city"] = df_top5["customer_city"].str.title()

# 7. Create the Multi-Panel Regression Grid Visualization
fig, axes = plt.subplots(1, 5, figsize=(22, 5), sharey=True)

# Sort alphabetically so the subplots match sequentially
sorted_cities = sorted(df_top5["customer_city"].unique())

for i, city in enumerate(sorted_cities):
    city_data = df_top5[df_top5["customer_city"] == city]

    # Sample data points if the city dataset is massive (improves plot rendering speed)
    sample_size = min(len(city_data), 500)
    plot_sample = city_data.sample(n=sample_size, random_state=42)

    # Plot using x and y jittering to accommodate the discrete 1-to-5 review structure
    sns.regplot(
        data=plot_sample,
        x="delivery_delay_days",
        y="review_score",
        ax=axes[i],
        scatter_kws={"alpha": 0.25, "color": "#2b5c8f"},
        line_kws={"color": "#d9534f", "linewidth": 2.5},
        x_jitter=0.3,
        y_jitter=0.2,
    )

    # Calculate Pearson correlation coefficient on the complete data for that city
    r_value = city_data["delivery_delay_days"].corr(city_data["review_score"])

    # Configure subplots properties
    axes[i].set_title(f"{city}\nCorrelation ($r$): {r_value:.2f}", weight="bold")
    axes[i].set_xlabel("Delivery Delay (Days)")
    axes[i].set_xlim(-15, 20)  # Focus window around the zero delivery target line

    if i == 0:
        axes[i].set_ylabel("Customer Review Score (1-5)")
    else:
        axes[i].set_ylabel("")

# Global layout settings
plt.suptitle(
    "How Delivery Delays Impact Customer Satisfaction Across the Top 5 Cities (2017-2018)",
    y=1.08,
    fontsize=16,
    weight="bold",
)
plt.tight_layout()

# Render plot
plt.show()

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# 1. Setup global plotting aesthetics
sns.set_theme(style="whitegrid")
plt.rcParams.update({"font.size": 11, "axes.labelsize": 12})

# 2. Load the Olist dataset files
orders = pd.read_csv("olist_orders_dataset.csv")
reviews = pd.read_csv("olist_order_reviews_dataset.csv")
customers = pd.read_csv("olist_customers_dataset.csv")

# 3. Filter for delivered orders and convert date columns cleanly
orders = orders[orders["order_status"] == "delivered"].dropna(
    subset=[
        "order_purchase_timestamp",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]
)

orders["order_purchase_timestamp"] = pd.to_datetime(
    orders["order_purchase_timestamp"]
)
orders["order_delivered_customer_date"] = pd.to_datetime(
    orders["order_delivered_customer_date"]
)

# === Filter for 2017 and 2018 data only ===
orders = orders[orders["order_purchase_timestamp"].dt.year.isin([2017, 2018])]

# 4. Calculate actual delivery time (From purchase date to doorstep delivery in days)
orders["actual_delivery_time_days"] = (
    orders["order_delivered_customer_date"] - orders["order_purchase_timestamp"]
).dt.total_seconds() / (24 * 3600)

# 5. Merge dataframes to link customer locations with their reviews
df = orders.merge(reviews, on="order_id", how="inner").merge(
    customers, on="customer_id", how="inner"
)

# === Compute Global Platform Correlation ===
global_r = df["actual_delivery_time_days"].corr(df["review_score"])
print(f"=== OLIST DATASET CORRELATION ANALYSIS (2017-2018) ===")
print(
    f"Overall correlation between actual delivery days and customer ratings: {global_r:.4f}\n"
)

# 6. Extract the top 5 cities with the highest transaction volumes (for 2017-2018)
top_5_cities = (
    df.groupby("customer_city")["order_id"].count().nlargest(5).index.tolist()
)

# Filter main dataset for only these 5 locations
df_top5 = df[df["customer_city"].isin(top_5_cities)].copy()
df_top5["customer_city"] = df_top5["customer_city"].str.title()

# 7. Create the Multi-Panel Regression Grid Visualization
fig, axes = plt.subplots(1, 5, figsize=(22, 5), sharey=True)

# Sort alphabetically so the subplots match sequentially
sorted_cities = sorted(df_top5["customer_city"].unique())

for i, city in enumerate(sorted_cities):
    city_data = df_top5[df_top5["customer_city"] == city]

    # Sample data points if the city dataset is massive (improves plot rendering speed)
    sample_size = min(len(city_data), 500)
    plot_sample = city_data.sample(n=sample_size, random_state=42)

    # Plot using x and y jittering to accommodate the discrete 1-to-5 review structure
    sns.regplot(
        data=plot_sample,
        x="actual_delivery_time_days",
        y="review_score",
        ax=axes[i],
        scatter_kws={"alpha": 0.25, "color": "#2b5c8f"},
        line_kws={"color": "#d9534f", "linewidth": 2.5},
        x_jitter=0.3,
        y_jitter=0.2,
    )

    # Calculate Pearson correlation coefficient on the complete data for that city
    r_value = city_data["actual_delivery_time_days"].corr(city_data["review_score"])

    # Configure subplots properties
    axes[i].set_title(f"{city}\nCorrelation ($r$): {r_value:.2f}", weight="bold")
    axes[i].set_xlabel("Actual Delivery Time (Days)")
    axes[i].set_xlim(0, 45)  # Window adapted for delivery timeline variations

    if i == 0:
        axes[i].set_ylabel("Customer Review Score (1-5)")
    else:
        axes[i].set_ylabel("")

# Global layout settings
plt.suptitle(
    "How Total Delivery Processing Time Impacts Customer Ratings Across Top 5 Cities (2017-2018)",
    y=1.08,
    fontsize=16,
    weight="bold",
)
plt.tight_layout()

# Render plot
plt.show()