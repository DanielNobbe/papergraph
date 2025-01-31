# Replace <service-account-email> with your service account's email
# Replace <project-id> with your GCP project ID

PROJECT_ID=principal-rhino-449413-s3
SERVICE_ACCOUNT_EMAIL=47463167639-compute@developer.gserviceaccount.com

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member "serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role "roles/bigquery.jobUser"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member "serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role "roles/bigquery.dataViewer"
