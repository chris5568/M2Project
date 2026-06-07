import os
from dotenv import load_dotenv
from google.cloud import storage

# 1. This reads the .env file and injects GOOGLE_APPLICATION_CREDENTIALS into the system background
load_dotenv()

def upload_olist_datasets(local_folder_path, bucket_name):
    # 2. Because load_dotenv() ran, storage.Client() automatically 
    # looks for GOOGLE_APPLICATION_CREDENTIALS and finds your path!
    storage_client = storage.Client()
    
    bucket = storage_client.get_bucket(bucket_name)

    for filename in os.listdir(local_folder_path):
        if filename.endswith('.csv'):
            local_file_path = os.path.join(local_folder_path, filename)
            blob_name = f"olist_raw_data/{filename}"
            blob = bucket.blob(blob_name)
            
            print(f"Uploading {filename}...")
            blob.upload_from_filename(local_file_path)
            print(f"Successfully uploaded {filename}!")

if __name__ == "__main__":
    LOCAL_DIRECTORY ="/home/moswal/m2/M2Project/dataset/"
    BUCKET_NAME ="sme-olist-data-lake"
    upload_olist_datasets(LOCAL_DIRECTORY, BUCKET_NAME)