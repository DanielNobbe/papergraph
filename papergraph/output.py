from google.cloud import bigquery


def unpack_result(result: dict) -> dict:
    # expand metadata
    res = {}
    res.update(**result.pop("metadata"))
    res.update(**result)

    return res


def push_result(result: dict):
    print("Pushing result to BigQuery..")

    project_id = "principal-rhino-449413-s3"
    dataset_id = "astrafy_task_2"
    table_id = "papers"

    client = bigquery.Client(project=project_id)

    table_ref = client.dataset(dataset_id).table(table_id)

    table = client.get_table(table_ref)

    result = unpack_result(result)

    # the dictionary is a single entry in the table
    # push it to the table
    rows_to_insert = [result]
    errors = client.insert_rows(table, rows_to_insert)
    if not errors:
        print("New rows have been added.")
    else:
        print(f"Encountered errors while inserting rows: {errors}")

    return result
