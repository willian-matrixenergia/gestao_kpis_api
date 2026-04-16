import os
import json
from google.cloud import bigquery

# Use local credentials
local_creds = "bigquery_credentials.json"
if os.path.exists(local_creds):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = local_creds

client = bigquery.Client()
project = "matrix-data-products-prd"
dataset = "ds_gestao_kpis"
view_name = "vw_kpi_ultimo_valor"

table_ref = f"{project}.{dataset}.{view_name}"
print(f"Testing view: {table_ref}")

try:
    # Get table info (which includes the view query)
    table = client.get_table(table_ref)
    print(f"View definition: {table.view_query}")

    # Try querying it
    sql = f"SELECT COUNT(*) FROM `{table_ref}`"
    print(f"Querying: {sql}")
    query_job = client.query(sql)
    results = query_job.result()
    for row in results:
        print(f"Result: {row[0]}")
except Exception as e:
    print(f"Error: {e}")
