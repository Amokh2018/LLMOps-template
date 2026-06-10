# Local Development Setup

## Prerequisites

- Python 3.11 or higher
- Docker & Docker Compose
- GCP Project with billing enabled
- gcloud CLI installed and authenticated
- Git

## Step 1: Clone the Repository

```bash
git clone <repository-url>
cd LLMOps-template
```

## Step 2: Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it (macOS/Linux)
source venv/bin/activate

# On Windows
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

## Step 3: Install Dependencies

```bash
# Install API service dependencies
pip install -r services/api/requirements.txt

# Install ingestion service dependencies
pip install -r services/ingestion/requirements.txt
```

## Step 4: Configure GCP

### Create a GCP Project

```bash
# Set your project ID
export PROJECT_ID="your-gcp-project-id"

# Create project (if not existing)
gcloud projects create $PROJECT_ID

# Set as default project
gcloud config set project $PROJECT_ID
```

### Enable Required APIs

```bash
gcloud services enable aiplatform.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable logging.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

### Create GCS Bucket

```bash
gsutil mb -p $PROJECT_ID -l us-central1 gs://${PROJECT_ID}-documents
```

## Step 5: Set Up Environment Variables

### Create .env file

```bash
cp config/dev.env.example .env
```

### Edit .env with your values

```bash
# .env
GCP_PROJECT_ID=your-gcp-project-id
GCP_REGION=us-central1
VERTEX_AI_LOCATION=us-central1
GEMINI_MODEL=gemini-1.5-pro

# Vector Store (configure after creating index)
VECTOR_STORE_INDEX_ID=your-vector-index-id
VECTOR_STORE_ENDPOINT=your-vector-index-endpoint

# Cloud Storage
GCS_BUCKET=your-project-id-documents
GCS_INGESTION_PREFIX=documents/

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_LOG_LEVEL=DEBUG
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Retrieval
RETRIEVAL_TOP_K=5
RETRIEVAL_DISTANCE_THRESHOLD=0.7
```

## Step 6: Create Vector Search Index

1. Go to [Vertex AI > Vector Search](https://console.cloud.google.com/vertex-ai/vector-search)
2. Click "Create Index"
3. Configure:
   - **Index Name**: rag-documents
   - **Embedding Dimension**: 768 (for text-embedding-004)
   - **Distance Measure Type**: COSINE_DISTANCE
4. Create the index and copy the endpoint URL
5. Update `.env` with `VECTOR_STORE_INDEX_ID` and `VECTOR_STORE_ENDPOINT`

## Step 7: Authenticate with GCP

```bash
# Authenticate with your GCP account
gcloud auth application-default login

# This creates credentials that services will use
```

## Step 8: Run Services Locally

### Terminal 1: API Service

```bash
cd services/api
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
- Docs: http://localhost:8000/docs
- OpenAPI schema: http://localhost:8000/openapi.json

### Terminal 2: Ingestion Service (optional for testing)

```bash
cd services/ingestion
python main.py
```

## Step 9: Test the API

### Health Check

```bash
curl http://localhost:8000/health
```

### Query Endpoint

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is RAG?",
    "top_k": 5,
    "threshold": 0.7
  }'
```

## Using Docker Compose

For a fully containerized setup:

```bash
docker-compose up
```

This will start:
- API service on port 8000
- Ingestion pipeline (runs once on startup)

## Troubleshooting

### Issue: "Permission denied" when accessing GCS

**Solution**: Run `gcloud auth application-default login` and ensure the service account has Storage permissions.

### Issue: Vector Store endpoint not found

**Solution**: Verify the Vector Search index exists and is deployed in the Vertex AI console.

### Issue: Gemini API errors

**Solution**: 
1. Verify the Vertex AI API is enabled
2. Check that your GCP project has proper quota
3. Ensure you're using a supported region

### Issue: Module import errors

**Solution**: Make sure you're in the virtual environment and dependencies are installed:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r services/api/requirements.txt
```

## Next Steps

- Read [API.md](API.md) for API documentation
- Read [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for system architecture details
