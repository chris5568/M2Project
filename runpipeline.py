import os
import glob
import hashlib
from dotenv import load_dotenv
import pandas as pd
from google.cloud import storage
from google.cloud import bigquery

# --- DYNAMIC ENVIRONMENT & PATH RESOLUTION ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(SCRIPT_DIR, ".env")

if os.path.exists(env_path):
    load_dotenv(env_path)
    print("✅ Configuration assets loaded successfully from local environment context.")
else:
    load_dotenv()

# --- TARGET ENV RECOVERY ---
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")

# Converts the relative path ("./dataset") seamlessly into an absolute tracker string
raw_csv_dir_env = os.getenv("LOCAL_CSV_DIR", "./dataset")
LOCAL_CSV_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, raw_csv_dir_env))

# --- THE SINGLE MAIN OLIST CONTAINER LAYER ---
MAIN_DATASET = "Olist_data"

def get_clients():
    """Build cloud application bindings dynamically from service metrics."""
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if cred_path:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_path
        
    storage_client = storage.Client(project=PROJECT_ID)
    bq_client = bigquery.Client(project=PROJECT_ID)
    return storage_client, bq_client

def ensure_dataset_exists(bq_client, dataset_id):
    """Initializes the single main container dataset within BigQuery."""
    dataset_ref = bq_client.dataset(dataset_id)
    try:
        bq_client.get_dataset(dataset_ref)
    except Exception:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"
        bq_client.create_dataset(dataset)
        print(f"📁 Created Main BigQuery Dataset Container: '{dataset_id}'")

# =====================================================================
# PHASE 1: SYNC RAW FILES WITH DATA LAKE CORES
# =====================================================================
def upload_local_csv_to_gcs(storage_client):
    print("\n--- PHASE 1: PROCESSING ARTIFACT ARCHIVES TO CLOUD STORAGE ---")
    try:
        bucket = storage_client.get_bucket(BUCKET_NAME)
    except Exception:
        bucket = storage_client.create_bucket(BUCKET_NAME, location="US")

    csv_files = glob.glob(os.path.join(LOCAL_CSV_DIR, "*.csv"))
    if not csv_files:
        print(f"❌ Resolution failure: No source file targets found in path: {LOCAL_CSV_DIR}")
        return False

    for file_path in csv_files:
        filename = os.path.basename(file_path)
        blob = bucket.blob(filename)
        print(f"  Streaming component archive to storage -> {filename}")
        blob.upload_from_filename(file_path)
    return True

# =====================================================================
# PHASE 2: CALCULATE METRICS AND ROUTE VIA DOUBLE UNDERSCORES
# =====================================================================
def transform_and_route_marts(storage_client, bq_client):
    print("\n--- PHASE 2: EXECUTING MODEL TRANSFORMS AND INGESTION ROUTING ---")
    ensure_dataset_exists(bq_client, MAIN_DATASET)
    
    print("Extracting vector files directly from storage into application runtime layers...")
    
    # Base Data Extraction
    df_customers = pd.read_csv(f"gs://{BUCKET_NAME}/olist_customers_dataset.csv")
    df_products = pd.read_csv(f"gs://{BUCKET_NAME}/olist_products_dataset.csv")
    df_orders = pd.read_csv(f"gs://{BUCKET_NAME}/olist_orders_dataset.csv")
    df_order_items = pd.read_csv(f"gs://{BUCKET_NAME}/olist_order_items_dataset.csv")
    df_order_payments = pd.read_csv(f"gs://{BUCKET_NAME}/olist_order_payments_dataset.csv")
    df_sellers = pd.read_csv(f"gs://{BUCKET_NAME}/olist_sellers_dataset.csv")
    
    # Enrichment Logs
    df_reviews = pd.read_csv(f"gs://{BUCKET_NAME}/olist_order_reviews_dataset.csv")
    df_leads = pd.read_csv(f"gs://{BUCKET_NAME}/olist_marketing_qualified_leads_dataset.csv")
    df_deals = pd.read_csv(f"gs://{BUCKET_NAME}/olist_closed_deals_dataset.csv")
    df_translations = pd.read_csv(f"gs://{BUCKET_NAME}/product_category_name_translation.csv")
    df_geolocation = pd.read_csv(f"gs://{BUCKET_NAME}/olist_geolocation_dataset.csv")

    # --- 1. Compute Dimensions ---
    print("Calculating system dimension structures...")
    dim_customers = df_customers.copy().rename(columns={'customer_city': 'city', 'customer_state': 'state'})
    
    dim_products = df_products.copy()
    dim_products['product_category_name'] = dim_products['product_category_name'].fillna('unknown')
    
    dim_sellers = df_sellers.copy().rename(columns={'seller_city': 'city', 'seller_state': 'state'})
    dim_order_reviews = df_reviews.copy().rename(columns={'review_comment_title': 'title', 'review_comment_message': 'message'})
    dim_marketing_leads = df_leads.copy()
    dim_closed_deals = df_deals.copy()
    dim_category_translations = df_translations.copy()
    
    dim_geolocation = df_geolocation.copy().rename(columns={
        'geolocation_zip_code_prefix': 'zip_code_prefix', 
        'geolocation_lat': 'latitude', 
        'geolocation_lng': 'longitude', 
        'geolocation_city': 'city', 
        'geolocation_state': 'state'
    })

    # Timeline calculation formatting conversions
    df_orders['order_purchase_timestamp'] = pd.to_datetime(df_orders['order_purchase_timestamp'])
    df_orders['order_delivered_customer_date'] = pd.to_datetime(df_orders['order_delivered_customer_date'])
    df_orders['order_estimated_delivery_date'] = pd.to_datetime(df_orders['order_estimated_delivery_date'])

    dim_orders = df_orders.copy()
    dim_orders['delivery_time_days'] = (dim_orders['order_delivered_customer_date'] - dim_orders['order_purchase_timestamp']).dt.days
    dim_orders['estimated_vs_actual_delivery_days'] = (dim_orders['order_estimated_delivery_date'] - dim_orders['order_delivered_customer_date']).dt.days
    dim_orders = dim_orders.rename(columns={'order_purchase_timestamp': 'order_purchase_at', 'order_delivered_customer_date': 'customer_delivery_at'})

    # --- 2. Compute Facts ---
    print("Calculating system fact values...")
    fact_order_items = df_order_items.copy()
    fact_order_items['total_order_value'] = fact_order_items['price'] + fact_order_items['freight_value']
    fact_order_items['fact_order_item_key'] = fact_order_items.apply(lambda r: hashlib.md5(f"{r['order_id']}_{r['order_item_id']}".encode('utf-8')).hexdigest(), axis=1)
    fact_order_items = fact_order_items[['fact_order_item_key', 'order_id', 'product_id', 'seller_id', 'price', 'freight_value', 'total_order_value']]

    fact_order_payments = df_order_payments.copy()
    fact_order_payments['fact_payment_key'] = fact_order_payments.apply(lambda r: hashlib.md5(f"{r['order_id']}_{r['payment_sequential']}".encode('utf-8')).hexdigest(), axis=1)

    # --- 3. Route via Valid Underline Path Layouts ---
    all_marts = {
        "models__star__dim_customers": dim_customers,
        "models__star__dim_products": dim_products,
        "models__star__dim_sellers": dim_sellers,
        "models__star__dim_order_reviews": dim_order_reviews,
        "models__star__dim_marketing_leads": dim_marketing_leads,
        "models__star__dim_closed_deals": dim_closed_deals,
        "models__star__dim_category_translations": dim_category_translations,
        "models__star__dim_geolocation": dim_geolocation,
        "models__star__dim_orders": dim_orders,
        "models__fact_order_items": fact_order_items,
        "models__fact_order_payments": fact_order_payments
    }

    print(f"\n🚀 Writing structured models to main dataset: `{MAIN_DATASET}`...")
    
    for table_id, dataframe in all_marts.items():
        destination_table = f"{PROJECT_ID}.{MAIN_DATASET}.{table_id}"
        job_config = bigquery.LoadJobConfig(write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE)
        bq_client.load_table_from_dataframe(dataframe, destination_table, job_config=job_config).result()
        print(f"  ✅ Materialized Model -> {MAIN_DATASET}.{table_id}")

    print("\n🎉 Pipeline Complete! Everything has been deployed neatly into your main Olist folder.")

if __name__ == "__main__":
    storage_cl, bq_cl = get_clients()
    success = upload_local_csv_to_gcs(storage_cl)
    if success:
        transform_and_route_marts(storage_cl, bq_cl)