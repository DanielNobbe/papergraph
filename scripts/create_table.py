import yaml
from google.cloud import bigquery
from google.cloud.exceptions import NotFound

def create_dataset(project_id, dataset_id):
    # Initialize a BigQuery client
    client = bigquery.Client(project=project_id)

    # Define the dataset reference
    dataset_ref = f"{project_id}.{dataset_id}"

    # check if it exists
    try:
        client.get_dataset(dataset_ref)
        print(f"Dataset {dataset_id} already exists.")
    except NotFound:
        # Create the dataset
        dataset = bigquery.Dataset(dataset_ref)
        print(f"Creating dataset {dataset_id}...")
        dataset = client.create_dataset(dataset)

def create_table_from_schema(project_id, dataset_id, table_id, schema_file):
    # Initialize a BigQuery client
    client = bigquery.Client(project=project_id)

    # Load schema from JSON file
    with open(schema_file, 'r') as f:
        schema_dict = yaml.load(f, Loader=yaml.SafeLoader)

    # Convert schema dictionary to BigQuery SchemaField objects
    schema = [bigquery.SchemaField(field['name'], field['type'], mode=field['mode']) for field in schema_dict['fields']]

    # if dataset doesn't exist, create it
    create_dataset(project_id, dataset_id)

    # Define the table reference
    table_ref = f"{project_id}.{dataset_id}.{table_id}"

    # Create the table definition
    table = bigquery.Table(table_ref, schema=schema)

    # Create the table in BigQuery
    try:
        table = client.create_table(table)
        print(f"Table {table.table_id} created successfully.")
    except Exception as e:
        print(f"Failed to create table: {e}")


if __name__ == "__main__":
    config_file = 'configs/config.yaml'

    with open(config_file, 'r') as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    project_id = config['project_id']
    dataset_id = config['dataset_id']
    table_id = config['table_id']
    schema_file = config['schema_file']

    create_table_from_schema(project_id, dataset_id, table_id, schema_file)