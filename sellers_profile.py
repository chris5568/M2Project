import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Load all required marketing funnel and seller datasets
mql = pd.read_csv('/home/moswal/m2/M2Project/olist_marketing_qualified_leads_dataset.csv')
closed_deals = pd.read_csv('/home/moswal/m2/M2Project/olist_closed_deals_dataset.csv')
sellers = pd.read_csv('/home/moswal/m2/M2Project/olist_sellers_dataset.csv')

# 2. Calculate funnel metrics before merging drops any rows
total_leads = mql['mql_id'].nunique()
total_signed_deals = closed_deals['seller_id'].nunique()

# 3. Use a LEFT merge so your charts capture all 842 signed contracts
df_sellers = closed_deals.merge(sellers, on='seller_id', how='left')

# 4. Count the active live sellers (those who successfully have location data in the database)
active_live_sellers = df_sellers['seller_state'].notna().sum()

# 5. Clean up missing fields so your plots display the dropped-out leads properly
df_sellers['business_type'] = df_sellers['business_type'].fillna('unknown')
df_sellers['seller_state'] = df_sellers['seller_state'].fillna('Dropped Out During Onboarding')

# 6. Extract total count aggregates for your two subplots
type_counts = df_sellers['business_type'].value_counts().reset_index()
type_counts.columns = ['business_type', 'count']

state_counts = df_sellers['seller_state'].value_counts().reset_index()
state_counts.columns = ['seller_state', 'count']

# --- VISUALIZATION BLOCK ---
sns.set_theme(style="whitegrid")
fig, axes = plt.subplots(1, 2, figsize=(16, 8))

# Global Funnel Performance Header: Prominently listing all stages of your sales pipeline
dashboard_title = (
    f"Olist B2B Marketing & Sales Funnel Dashboard\n"
    f"Total Funnel Leads: {total_leads:,} MQLs   |   "
    f"Signed Contracts: {total_signed_deals}   |   "
    f"Active Live Sellers: {active_live_sellers}"
)
fig.suptitle(dashboard_title, fontsize=16, weight='bold', y=0.98)

# Plot 1: Type of Sellers (Business Type Breakdown)
sns.barplot(
    data=type_counts, 
    x='count', 
    y='business_type', 
    ax=axes[0], 
    palette='Blues_r'
)
axes[0].set_title('Distribution of Seller Types (All Signed)', fontsize=13, weight='bold', pad=10)
axes[0].set_xlabel('Number of Signed Sellers', fontsize=12)
axes[0].set_ylabel('Business Type', fontsize=12)

for container in axes[0].containers:
    axes[0].bar_label(container, fmt='%d', padding=3)

# Plot 2: Location of Sellers (State Breakdown)
sns.barplot(
    data=state_counts, 
    x='count', 
    y='seller_state', 
    ax=axes[1], 
    palette='viridis'
)
axes[1].set_title('Seller Geographic Distribution & Drop-off Tracker', fontsize=13, weight='bold', pad=10)
axes[1].set_xlabel('Number of Signed Sellers', fontsize=12)
axes[1].set_ylabel('Brazilian State (Abbreviation)', fontsize=12)

for container in axes[1].containers:
    axes[1].bar_label(container, fmt='%d', padding=3)

# Clear structural bounding box adjustment to keep your multi-line title from overlapping
plt.tight_layout(rect=[0, 0, 1, 0.90])
plt.show()
