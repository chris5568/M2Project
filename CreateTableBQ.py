import os
from dotenv import load_dotenv
from google.cloud import storage
from google.cloud import bigquery

# Load the environment configurations
load_dotenv()

def autodetect_gcs_to_bigquery():
    # 1. Fetch variables from .env
    project_id = os.getenv("GCP_PROJECT_ID")
    bucket_name = os.getenv("GCS_BUCKET_NAME")
    dataset_id = os.getenv("BQ_DATASET_ID")

    # 2. Initialize Clients
    storage_client = storage.Client(project=project_id)
    bq_client = bigquery.Client(project=project_id)

    # 3. Create BigQuery Dataset if it doesn't exist
    dataset_ref = bq_client.dataset(dataset_id)
    try:
        bq_client.get_dataset(dataset_ref)
        print(f"Dataset '{dataset_id}' already exists.")
    except Exception:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"  # Adjust region if your bucket is elsewhere
        bq_client.create_dataset(dataset)
        print(f"Created new BigQuery dataset: '{dataset_id}'")

    # 4. Programmatically list all files inside the GCS Bucket
    bucket = storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs()

    print("Scanning bucket for CSV files...")
    
    for blob in blobs:
        # Check if the file is a CSV
        if blob.name.endswith('.csv'):
            
            # Extract just the file name (e.g., 'olist_raw_data/olist_orders_dataset.csv' -> 'olist_orders_dataset.csv')
            filename = os.path.basename(blob.name)
            
            # Remove the '.csv' extension to use it as the BigQuery Table Name
            table_name = os.path.splitext(filename)[0]
            
            # Sanitize table name (BigQuery tables can't have dashes or start with numbers)
            table_name = table_name.replace("-", "_")
            
            table_ref = dataset_ref.table(table_name)

            # Define Ingestion Configurations
            job_config = bigquery.LoadJobConfig(
                source_format=bigquery.SourceFormat.CSV,
                skip_leading_rows=1,      # Skip header row
                autodetect=True,          # Let BigQuery auto-infer schemas/data types
                write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE, # Overwrite if exists
                # --- ADD THIS LINE BELOW TO FIX THE ORDER REVIEWS ERROR ---
                allow_quoted_newlines=True
            )

            # Generate the cloud URI for the current file
            gcs_uri = f"gs://{bucket_name}/{blob.name}"
            
            print(f"Found file: {blob.name} -> Creating table: {table_name}")
            
            try:
                # Trigger the load job
                load_job = bq_client.load_table_from_uri(
                    gcs_uri, table_ref, job_config=job_config
                )
                load_job.result()  # Wait for this specific table to finish building
                print(f"Successfully created table: {table_name}")
            except Exception as e:
                print(f"Error importing {table_name}: {e}")

if __name__ == "__main__":
    autodetect_gcs_to_bigquery()