# GCP Deployment Guide

## Prerequisites

- GCP Project set up
- Terraform installed (>= 1.0)
- gcloud CLI configured
- GitHub repository with secrets configured

## Step 1: Set Up GitHub Secrets

Configure the following secrets in your GitHub repository:

1. `GCP_PROJECT_ID` - Your GCP project ID
2. `GCP_SA_KEY` - Service account key JSON (base64 encoded)

### Create Service Account Key

```bash
# Set your project ID
export PROJECT_ID="your-gcp-project-id"

# Create service account
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions CI/CD" \
  --project=$PROJECT_ID

# Grant necessary roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

# Create key
gcloud iam service-accounts keys create key.json \
  --iam-account=github-actions@$PROJECT_ID.iam.gserviceaccount.com

# Encode and set as secret
cat key.json | base64 | xclip -selection clipboard
# Or just print it and copy manually
cat key.json
```

Then go to GitHub repo Settings > Secrets and add the secrets.

## Step 2: Deploy Infrastructure with Terraform

### Initialize Terraform

```bash
cd infra/terraform

# Set your project ID
export PROJECT_ID="your-gcp-project-id"
export GCS_BUCKET_NAME="$PROJECT_ID-documents"

# Initialize Terraform
terraform init
```

### Plan Deployment

```bash
terraform plan \
  -var="project_id=$PROJECT_ID" \
  -var="gcs_bucket_name=$GCS_BUCKET_NAME"
```

### Apply Configuration

```bash
terraform apply \
  -var="project_id=$PROJECT_ID" \
  -var="gcs_bucket_name=$GCS_BUCKET_NAME"
```

This creates:
- Service account for RAG services
- GCS bucket for documents
- IAM bindings
- Cloud Logging bucket (optional)

## Step 3: Create Vector Search Index

While Terraform sets up base infrastructure, Vector Search index must be created manually (requires special Vertex AI configuration):

### Via Google Cloud Console

1. Go to [Vertex AI > Vector Search](https://console.cloud.google.com/vertex-ai/vector-search)
2. Click "Create Index"
3. Configure:
   - **Name**: rag-documents
   - **Embedding Dimensions**: 768
   - **Distance Measure Type**: COSINE_DISTANCE
4. Click "Create"
5. Wait for index to be ready (can take 10-15 minutes)
6. Copy the endpoint details

### Update GCP Secrets

After index is created, update environment variables:
- Add `VECTOR_STORE_INDEX_ID` to production secrets
- Add `VECTOR_STORE_ENDPOINT` to production secrets

## Step 4: Configure Artifact Registry

```bash
# Create Artifact Registry repository
gcloud artifacts repositories create rag-services \
  --repository-format=docker \
  --location=us-central1 \
  --project=$PROJECT_ID

# Configure authentication (for local pushing)
gcloud auth configure-docker us-docker.pkg.dev
```

## Step 5: Deploy Services

### Option 1: Automatic Deployment via GitHub Actions

Push to main branch - GitHub Actions will automatically:
1. Run linting and type checks
2. Build Docker images
3. Push to Artifact Registry
4. Deploy to Cloud Run

### Option 2: Manual Deployment

#### Deploy API Service

```bash
gcloud run deploy api-service \
  --image us-docker.pkg.dev/$PROJECT_ID/rag-services/api-service:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars \
    GCP_PROJECT_ID=$PROJECT_ID,\
    VERTEX_AI_LOCATION=us-central1,\
    VECTOR_STORE_INDEX_ID=your-index-id,\
    VECTOR_STORE_ENDPOINT=your-endpoint-url \
  --service-account rag-service@$PROJECT_ID.iam.gserviceaccount.com
```

#### Deploy Ingestion as Cloud Run Job

```bash
gcloud run jobs create ingestion-pipeline \
  --image us-docker.pkg.dev/$PROJECT_ID/rag-services/ingestion-service:latest \
  --platform managed \
  --region us-central1 \
  --set-env-vars \
    GCP_PROJECT_ID=$PROJECT_ID,\
    VERTEX_AI_LOCATION=us-central1,\
    VECTOR_STORE_INDEX_ID=your-index-id,\
    VECTOR_STORE_ENDPOINT=your-endpoint-url,\
    GCS_BUCKET=$GCS_BUCKET_NAME \
  --service-account rag-service@$PROJECT_ID.iam.gserviceaccount.com
```

## Step 6: Verify Deployment

### Check API Service

```bash
# Get API URL
API_URL=$(gcloud run services describe api-service \
  --region us-central1 \
  --format 'value(status.url)' \
  --project=$PROJECT_ID)

# Test health endpoint
curl $API_URL/health
```

### Run Ingestion Job

```bash
gcloud run jobs execute ingestion-pipeline \
  --region us-central1 \
  --project=$PROJECT_ID
```

### Check Logs

```bash
# API logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=api-service" \
  --project=$PROJECT_ID \
  --limit 50

# Ingestion logs
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=ingestion-pipeline" \
  --project=$PROJECT_ID \
  --limit 50
```

## Step 7: Set Up Production Monitoring

### Enable Cloud Trace

```bash
gcloud services enable cloudtrace.googleapis.com
```

### Create Custom Dashboard

1. Go to Cloud Console > Monitoring > Dashboards
2. Create new dashboard
3. Add these widgets:
   - API latency
   - Request count by status
   - Error rate
   - Vector store query latency

## Production Environment

For production deployments:

1. **Use separate GCP projects** for dev, staging, and prod
2. **Enable VPC Service Controls** for data exfiltration prevention
3. **Configure Cloud Armor** for DDoS protection
4. **Set up alerts** for critical metrics
5. **Enable audit logging** for compliance
6. **Use Secret Manager** for sensitive credentials

### Update Production Secrets

In GitHub settings, create production variables:
- `GCP_PROJECT_ID_PROD`
- `GCP_SA_KEY_PROD`
- `VECTOR_STORE_INDEX_ID_PROD`
- `VECTOR_STORE_ENDPOINT_PROD`

### Update Workflow

Modify `.github/workflows/deploy.yml` to deploy to production on tags:

```yaml
on:
  push:
    tags:
      - 'v*'
```

## Rollback Procedure

### Rollback API Service

```bash
# View revisions
gcloud run revisions list --service api-service --region us-central1

# Route traffic to previous revision
gcloud run services update-traffic api-service \
  --to-revisions REVISION_NAME=100 \
  --region us-central1
```

### Rollback Ingestion Job

Re-run previous image:

```bash
gcloud run jobs deploy ingestion-pipeline \
  --image us-docker.pkg.dev/$PROJECT_ID/rag-services/ingestion-service:PREVIOUS_TAG \
  --region us-central1
```

## Cost Optimization

### Reduce Cloud Run Costs

- Set appropriate CPU/memory allocation
- Configure max instances and concurrency
- Use minimum instances only during peak hours

### Reduce Vector Search Costs

- Batch index operations
- Set appropriate refresh schedule
- Monitor query patterns

### Monitor Costs

```bash
# View API costs
gcloud billing accounts list
gcloud billing accounts get-iam-policy <BILLING_ACCOUNT_ID>
```

## Troubleshooting

### Service fails to start

Check logs:
```bash
gcloud logging read "resource.type=cloud_run_revision" \
  --limit 50 \
  --project=$PROJECT_ID
```

### Authentication errors

Verify service account permissions:
```bash
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:rag-service*"
```

### Vector Search unavailable

Check index status in Vertex AI console or via:
```bash
gcloud ai indexes list --region us-central1
```

## Next Steps

- Set up monitoring and alerting
- Configure backup strategy
- Set up CI/CD for other services
- Implement cost monitoring
