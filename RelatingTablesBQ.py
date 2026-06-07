import os
from dotenv import load_dotenv
from google.cloud import bigquery

# Load credentials from your .env file
load_dotenv()

def auto_apply_constraints():
    project_id = os.getenv("GCP_PROJECT_ID")
    dataset_id = os.getenv("BQ_DATASET_ID")

    bq_client = bigquery.Client(project=project_id)
    
    # 1. Fetch all tables from your BigQuery dataset dynamically
    dataset_ref = bq_client.dataset(dataset_id)
    tables = list(bq_client.list_tables(dataset_ref))
    
    print(f"🔎 Found {len(tables)} tables in '{dataset_id}'. Mapping columns...")

    # Dictionary to map which column name belongs to which primary table
    # Example: {'customer_id': 'olist_customers_dataset'}
    primary_key_map = {}
    table_schemas = {}

    # Step A: Scan all tables to map schemas and discover Primary Keys
    for table_item in tables:
        full_table = bq_client.get_table(table_item.reference)
        table_name = full_table.table_id
        
        # Extract column names
        columns = [field.name for field in full_table.schema]
        table_schemas[table_name] = columns
        
        # Look for the natural Primary Key (e.g. 'customer_id' inside 'olist_customers_dataset')
        for col in columns:
            if col.endswith('_id'):
                # Strip 'olist_' and '_dataset' to check core name match
                clean_table_name = table_name.replace("olist_", "").replace("_dataset", "")
                clean_col_name = col.replace("_id", "")
                
                # Check if column name aligns with table name (singular vs plural handled cleanly)
                if clean_col_name in clean_table_name or clean_table_name in clean_col_name:
                    primary_key_map[col] = table_name

    # Step B: Programmatically execute ALTER TABLE statements
    print("\n🛠️ Applying constraints dynamically...")

    # 1. Set Primary Keys First
    for col_name, table_name in primary_key_map.items():
        pk_sql = f"""
        ALTER TABLE `{project_id}.{dataset_id}.{table_name}`
        ADD PRIMARY KEY ({col_name}) NOT ENFORCED;
        """
        try:
            bq_client.query(pk_sql).result()
            print(f"✅ Set PRIMARY KEY ({col_name}) on table: {table_name}")
        except Exception as e:
            # If it already exists, BigQuery might throw an error; we can skip it safely
            if "already exists" in str(e).lower():
                print(f"ℹ️ PRIMARY KEY on {table_name} already exists.")
            else:
                print(f"❌ Error setting PK on {table_name}: {e}")

    # 2. Set Foreign Keys Second (Link child tables back to primary tables)
    constraint_counter = 1
    for child_table, columns in table_schemas.items():
        for col_name in columns:
            # If this column is a known Primary Key of a DIFFERENT table
            if col_name in primary_key_map and child_table != primary_key_map[col_name]:
                parent_table = primary_key_map[col_name]
                
                fk_name = f"fk_{child_table[-10:]}_{col_name}_{constraint_counter}"
                fk_sql = f"""
                ALTER TABLE `{project_id}.{dataset_id}.{child_table}`
                ADD CONSTRAINT {fk_name}
                FOREIGN KEY ({col_name}) 
                REFERENCES `{project_id}.{dataset_id}.{parent_table}`({col_name}) NOT ENFORCED;
                """
                try:
                    bq_client.query(fk_sql).result()
                    print(f"🔗 Linked Foreign Key: {child_table}.{col_name} -> {parent_table}.{col_name}")
                    constraint_counter += 1
                except Exception as e:
                    if "already exists" in str(e).lower():
                        pass
                    else:
                        print(f"❌ Error linking {child_table} to {parent_table}: {e}")

    print("\n🎉 Data lake structure complete! All relationships applied dynamically.")

if __name__ == "__main__":
    auto_apply_constraints()