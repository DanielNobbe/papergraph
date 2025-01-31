# papergraph
LangGraph-based scientific paper processing with storage to BigQuery.

# Run locally
To run locally follow the following steps:

## Pre-requisites
1. Make a Mistral API key (for free) and set it as the MISTRAL_API_KEY environment variable.
2. Install [Docker](https://docs.docker.com/get-docker/) if not installed
3. If you want to use the included data files, unzip the data.zip file to a new 'data' directory.
4. Install and authenticate with the gcloud CLI.
5. Create a GCP project and enable the BigQuery API.
6. Set the `configs/config.yaml` configuration to point to your project, you can pick any dataset id and table id.
7. Run `python scripts/create_table.py` to create the BigQuery table, according to the schema file defined in `configs/config.yaml`. (recommended to use a virtualenv for this, you can use e.g. poetry)


## Run locally
1. Run `bash sh/docker_build.sh`
2. Run `bash sh/docker_run.sh`. You may need to modify the local path of the 
gcloud credentials.json file in the bash script, to mount it to the container.
3. Run `python scripts/call_app.py --local`. Optionally set the file path with the `--file` flag.

Note that the app runs by default on port 8000. To change this, modify the PORT
variable in the `docker_run.sh` file, and include the --port variable in when running
`call_app.py`.

## Run on GCP
2. Run `bash sh/deploy.sh` (make sure that the MISTRAL_API_KEY environment variable is set).
    This will return a URL to the deployed app.
3. Run `python scripts/call_app.py --url <URL>`.


# NOTES
## Limitations:
- Google Cloud Run allows up to ~23MB files. Some PDFs will be too large, and might need to be compressed locally first.
- Built with Mistral API. It would be easy to allow the config or the request to set the model type, that would only require a wrapper around the model APIs in LangChain.
- The Mistral free API is very rate limited, allowing this app to only work with each node executed sequentially. With a paid API, this would be possible to run in parallel, drastically speeding up inference. It would be possible to stagger the requests to the free API, but I wonder how much that would improve performance.
- Currently, input schemas and files are not validated, and the app will fail if the input is not correct, or worse. This could be improved fairly easily.
- Most nodes are pretty similar in implementation, the code could be shared for easy maintainability.
## Testing:
- Currently I have only tested the app manually, in three settings (local python, local Docker, Google Cloud Run).
- In a production setting I would add unit and smoke tests for all graph nodes, and accurate unit tests for all utility functions.
- Other tests to add would be a full integration test of the app on GCP, and autoomatic CI/CD deployment.

