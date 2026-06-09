import os
import glob
import pandas as pd
from google.cloud import bigquery

PROJECT_ID = "assignment-project-498814"
DATASET_ID = "raw_olist"

# Comprehensive mapping of all 11 CSV datasets found in the repository
target_files = {
    "closed_deals": "olist_closed_deals_dataset.csv",
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "marketing_leads": "olist_marketing_qualified_leads_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "category_translation": "product_category_name_translation.csv"
}

# Initialize native BigQuery client
client = bigquery.Client(project=PROJECT_ID)
print("🚀 Starting complete 11-file data ingestion to BigQuery...\n")

for key, target_name in target_files.items():
    found_files = glob.glob(f"**/{target_name}", recursive=True)
    
    if not found_files:
        print(f"⚠️ Warning: Could not find '{target_name}' in the project folders. Skipping...")
        continue
        
    file_path = found_files[0]
    table_name = target_name.replace(".csv", "")
    destination_table = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
    
    print(f"🔄 Found: {file_path}")
    print(f"   Uploading to {destination_table}...")
    
    try:
        # Read files safely as string types to prevent casting bugs during landing
        df = pd.read_csv(file_path, dtype=str)
        
        job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
        job = client.load_table_from_dataframe(df, destination_table, job_config=job_config)
        job.result()  # Wait for upload to complete
        
        print(f"✅ Loaded {table_name}! ({len(df)} rows)\n")
    except Exception as e:
        print(f"💥 Failed to upload {target_name}: {e}\n")

print("🎉 Complete ingestion run finished. Check your BigQuery raw_olist schema!")
