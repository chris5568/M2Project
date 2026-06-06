import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# 1. Setup global plotting aesthetics
sns.set_theme(style="whitegrid")
plt.rcParams.update({"font.size": 10, "axes.labelsize": 11})

# 2. Load the required Olist datasets
orders = pd.read_csv("olist_orders_dataset.csv")
order_items = pd.read_csv("olist_order_items_dataset.csv")
customers = pd.read_csv("olist_customers_dataset.csv")
sellers = pd.read_csv("olist_sellers_dataset.csv")

# 3. Master Merge to link orders, customers, and sellers
merged_df = pd.merge(order_items, orders, on="order_id", how="inner")
merged_df = pd.merge(merged_df, customers, on="customer_id", how="inner")
merged_df = pd.merge(merged_df, sellers, on="seller_id", how="inner")

# Drop rows missing actual delivery timestamps for clean tracking
merged_df = merged_df.dropna(subset=["order_delivered_customer_date"])

# 4. Filter for Years 2017 & 2018 only
merged_df["order_purchase_timestamp"] = pd.to_datetime(
    merged_df["order_purchase_timestamp"]
)
merged_df["order_delivered_customer_date"] = pd.to_datetime(
    merged_df["order_delivered_customer_date"]
)
merged_df["Year"] = merged_df["order_purchase_timestamp"].dt.year

df_years = merged_df[merged_df["Year"].isin([2017, 2018])].copy()

# 5. Extract the Top 3 Cities based on Total Customer Orders (Unique order_id)
top_3_cities = (
    df_years.groupby("customer_city")["order_id"]
    .nunique()
    .nlargest(3)
    .index.tolist()
)
print(f"Top 3 Identified Demand Cities (2017-2018): {top_3_cities}\n")

# Filter main dataset for only these 3 target consumer areas
df_filtered = df_years[df_years["customer_city"].isin(top_3_cities)].copy()

# Standardize case formatting for clean visualization titles
df_filtered["customer_city"] = df_filtered["customer_city"].str.title()

# 6. Calculate actual delivery transit time (in days)
df_filtered["delivery_time_days"] = (
    df_filtered["order_delivered_customer_date"]
    - df_filtered["order_purchase_timestamp"]
).dt.total_seconds() / (24 * 3600)

# 7. Drop duplicate item entries to evaluate unique orders
df_unique_orders = df_filtered.drop_duplicates(subset=["order_id"]).copy()

# Segment sellers into Local (Same City) vs External (Different City)
df_unique_orders["Seller Type"] = df_unique_orders.apply(
    lambda row: (
        "Local Seller"
        if row["seller_city"].lower() == row["customer_city"].lower()
        else "External Seller"
    ),
    axis=1,
)

# 8. Aggregate Metrics (Total Volume & Mean Delivery Days)
metrics_df = (
    df_unique_orders.groupby(["customer_city", "Year", "Seller Type"])
    .agg(
        order_count=("order_id", "count"),
        avg_delivery_days=("delivery_time_days", "mean"),
    )
    .reset_index()
)

print("=== LOGISTICS COMPARISON FOR TOP 3 CITIES ===")
print(metrics_df.to_string(index=False))

# 9. Plotting Multi-Panel Subplots (1 row, 3 columns)
sorted_cities = sorted(metrics_df["customer_city"].unique())
fig, axes = plt.subplots(1, 3, figsize=(20, 6), sharey=False)

for i, city in enumerate(sorted_cities):
    city_data = metrics_df[metrics_df["customer_city"] == city]
    ax1 = axes[i]

    # Primary Axis: Bars for Volume Counts
    sns.barplot(
        data=city_data,
        x="Year",
        y="order_count",
        hue="Seller Type",
        palette="Set2",
        edgecolor="black",
        ax=ax1,
    )

    ax1.set_title(f"Marketplace Hub: {city}", fontsize=13, fontweight="bold", pad=12)
    ax1.set_xlabel("Order Year", fontweight="bold")
    ax1.set_ylabel("Number of Unique Orders", fontweight="bold")

    # Add count numbers directly on top of the bars
    for container in ax1.containers:
        ax1.bar_label(container, fmt="%d", padding=3, fontsize=9, fontweight="bold")

    # Secondary Axis: Line Overlay for Average Transit Days
    ax2 = ax1.twinx()

    # Align lines directly over the categorical grouped bar indexes
    x_coords_local = [-0.2, 0.8]
    x_coords_external = [0.2, 1.2]

    avg_local = city_data[city_data["Seller Type"] == "Local Seller"][
        "avg_delivery_days"
    ].tolist()
    avg_external = city_data[city_data["Seller Type"] == "External Seller"][
        "avg_delivery_days"
    ].tolist()

    # Handle scenario variations if a city has missing combinations
    if avg_local:
        ax2.plot(
            x_coords_local,
            avg_local,
            color="#1f77b4",
            marker="o",
            linewidth=2,
            linestyle="-.",
            label="Avg Days (Local)",
        )
        for x, y in zip(x_coords_local, avg_local):
            ax2.text(
                x,
                y + 0.5,
                f"{y:.1f}d",
                color="#1f77b4",
                fontweight="bold",
                ha="center",
                fontsize=9,
            )

    if avg_external:
        ax2.plot(
            x_coords_external,
            avg_external,
            color="#d62728",
            marker="s",
            linewidth=2,
            linestyle="-.",
            label="Avg Days (External)",
        )
        for x, y in zip(x_coords_external, avg_external):
            ax2.text(
                x,
                y + 0.5,
                f"{y:.1f}d",
                color="#d62728",
                fontweight="bold",
                ha="center",
                fontsize=9,
            )

    ax2.set_ylabel("Average Delivery Time (Days)", color="#d62728", fontweight="bold")
    ax2.tick_params(axis="y", labelcolor="#d62728")
    ax2.grid(False)

    # Clean layout: combine legends for the first panel only, hide others to avoid clutter
    if i == 0:
        bars, bar_labels = ax1.get_legend_handles_labels()
        lines, line_labels = ax2.get_legend_handles_labels()
        ax1.legend(bars + lines, bar_labels + line_labels, loc="upper left")
    else:
        ax1.get_legend().remove()

    # Equalize vertical padding for lines
    ax2.set_ylim(0, metrics_df["avg_delivery_days"].max() * 1.2)

# Global layout settings
plt.suptitle(
    "Fulfillment Volumes vs. Delivery Timelines in the Top 3 Highest Consumer Cities (2017-2018)",
    y=1.05,
    fontsize=16,
    weight="bold",
)
plt.tight_layout()
plt.show()


# ignoring outliers in 2017 and 2018

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# 1. Setup global plotting aesthetics
sns.set_theme(style="whitegrid")
plt.rcParams.update({"font.size": 10, "axes.labelsize": 11})

# 2. Load the required Olist datasets
orders = pd.read_csv("olist_orders_dataset.csv")
order_items = pd.read_csv("olist_order_items_dataset.csv")
customers = pd.read_csv("olist_customers_dataset.csv")
sellers = pd.read_csv("olist_sellers_dataset.csv")

# 3. Master Merge to link orders, customers, and sellers
merged_df = pd.merge(order_items, orders, on="order_id", how="inner")
merged_df = pd.merge(merged_df, customers, on="customer_id", how="inner")
merged_df = pd.merge(merged_df, sellers, on="seller_id", how="inner")

# Drop rows missing actual delivery timestamps
merged_df = merged_df.dropna(subset=["order_delivered_customer_date"])

# 4. Filter for Years 2017 & 2018 only
merged_df["order_purchase_timestamp"] = pd.to_datetime(
    merged_df["order_purchase_timestamp"]
)
merged_df["order_delivered_customer_date"] = pd.to_datetime(
    merged_df["order_delivered_customer_date"]
)
merged_df["Year"] = merged_df["order_purchase_timestamp"].dt.year

df_years = merged_df[merged_df["Year"].isin([2017, 2018])].copy()

# 5. Calculate actual delivery transit time (in days)
df_years["delivery_time_days"] = (
    df_years["order_delivered_customer_date"]
    - df_years["order_purchase_timestamp"]
).dt.total_seconds() / (24 * 3600)

# =====================================================================
# === NEW: OUTLIER REMOVAL USING IQR METHOD ===
# =====================================================================
Q1 = df_years["delivery_time_days"].quantile(0.25)
Q3 = df_years["delivery_time_days"].quantile(0.75)
IQR = Q3 - Q1

# Define thresholds (typically, extreme delivery times are on the upper tail)
lower_bound = max(0, Q1 - 1.5 * IQR)  # Delivery time cannot be negative
upper_bound = Q3 + 1.5 * IQR

print("=== OUTLIER THRESHOLDS ===")
print(f"Minimum days: {lower_bound:.2f}")
print(f"Maximum days (Cut-off): {upper_bound:.2f}")

# Filter out the outliers
df_clean = df_years[
    (df_years["delivery_time_days"] >= lower_bound)
    & (df_years["delivery_time_days"] <= upper_bound)
].copy()

removed_count = len(df_years) - len(df_clean)
print(
    f"Removed {removed_count} outlier items out of {len(df_years)} total entries.\n"
)
# =====================================================================

# 6. Extract the Top 3 Cities based on Total Customer Orders (Unique order_id)
top_3_cities = (
    df_clean.groupby("customer_city")["order_id"]
    .nunique()
    .nlargest(3)
    .index.tolist()
)
print(f"Top 3 Identified Demand Cities (2017-2018 - Cleaned): {top_3_cities}\n")

# Filter dataset for only these 3 target consumer areas
df_filtered = df_clean[df_clean["customer_city"].isin(top_3_cities)].copy()
df_filtered["customer_city"] = df_filtered["customer_city"].str.title()

# 7. Drop duplicate item entries to evaluate unique orders
df_unique_orders = df_filtered.drop_duplicates(subset=["order_id"]).copy()

# Segment sellers into Local (Same City) vs External (Different City)
df_unique_orders["Seller Type"] = df_unique_orders.apply(
    lambda row: (
        "Local Seller"
        if row["seller_city"].lower() == row["customer_city"].lower()
        else "External Seller"
    ),
    axis=1,
)

# 8. Aggregate Metrics (Total Volume & Mean Delivery Days)
metrics_df = (
    df_unique_orders.groupby(["customer_city", "Year", "Seller Type"])
    .agg(
        order_count=("order_id", "count"),
        avg_delivery_days=("delivery_time_days", "mean"),
    )
    .reset_index()
)

print("=== CLEANED LOGISTICS COMPARISON FOR TOP 3 CITIES ===")
print(metrics_df.to_string(index=False))

# 9. Plotting Multi-Panel Subplots (1 row, 3 columns)
sorted_cities = sorted(metrics_df["customer_city"].unique())
fig, axes = plt.subplots(1, 3, figsize=(20, 6), sharey=False)

for i, city in enumerate(sorted_cities):
    city_data = metrics_df[metrics_df["customer_city"] == city]
    ax1 = axes[i]

    # Primary Axis: Bars for Volume Counts
    sns.barplot(
        data=city_data,
        x="Year",
        y="order_count",
        hue="Seller Type",
        palette="Set2",
        edgecolor="black",
        ax=ax1,
    )

    ax1.set_title(
        f"Marketplace Hub: {city} (No Outliers)", fontsize=13, fontweight="bold", pad=12
    )
    ax1.set_xlabel("Order Year", fontweight="bold")
    ax1.set_ylabel("Number of Unique Orders", fontweight="bold")

    # Add count numbers directly on top of the bars
    for container in ax1.containers:
        ax1.bar_label(container, fmt="%d", padding=3, fontsize=9, fontweight="bold")

    # Secondary Axis: Line Overlay for Average Transit Days
    ax2 = ax1.twinx()

    x_coords_local = [-0.2, 0.8]
    x_coords_external = [0.2, 1.2]

    avg_local = city_data[city_data["Seller Type"] == "Local Seller"][
        "avg_delivery_days"
    ].tolist()
    avg_external = city_data[city_data["Seller Type"] == "External Seller"][
        "avg_delivery_days"
    ].tolist()

    if avg_local:
        ax2.plot(
            x_coords_local,
            avg_local,
            color="#1f77b4",
            marker="o",
            linewidth=2,
            linestyle="-.",
            label="Avg Days (Local)",
        )
        for x, y in zip(x_coords_local, avg_local):
            ax2.text(
                x,
                y + 0.3,
                f"{y:.1f}d",
                color="#1f77b4",
                fontweight="bold",
                ha="center",
                fontsize=9,
            )

    if avg_external:
        ax2.plot(
            x_coords_external,
            avg_external,
            color="#d62728",
            marker="s",
            linewidth=2,
            linestyle="-.",
            label="Avg Days (External)",
        )
        for x, y in zip(x_coords_external, avg_external):
            ax2.text(
                x,
                y + 0.3,
                f"{y:.1f}d",
                color="#d62728",
                fontweight="bold",
                ha="center",
                fontsize=9,
            )

    ax2.set_ylabel("Average Delivery Time (Days)", color="#d62728", fontweight="bold")
    ax2.tick_params(axis="y", labelcolor="#d62728")
    ax2.grid(False)

    if i == 0:
        bars, bar_labels = ax1.get_legend_handles_labels()
        lines, line_labels = ax2.get_legend_handles_labels()
        ax1.legend(bars + lines, bar_labels + line_labels, loc="upper left")
    else:
        ax1.get_legend().remove()

    # Limit the secondary axis y-scale based on the cleaned upper bound limit
    ax2.set_ylim(0, upper_bound * 1.05)

# Global layout settings
plt.suptitle(
    "Outlier-Removed Fulfillment Volumes vs. Delivery Timelines in Top 3 Cities (2017-2018)",
    y=1.05,
    fontsize=16,
    weight="bold",
)
plt.tight_layout()
plt.show()