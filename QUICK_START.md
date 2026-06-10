# Quick Start Guide

Get the RAG service running in minutes.

## 5-Minute Setup (Local)

### 1. Prerequisites
```bash
python --version  # 3.11+
docker --version  # Latest
gcloud --version  # Latest
```

### 2. Configure GCP
```bash
export PROJECT_ID="your-gcp-project-id"
gcloud config set project $PROJECT_ID
gcloud auth application-default login
```

### 3. Clone and Install (Using Makefile - Recommended)
```bash
git clone <repo>
cd LLMOps-template
make setup        # Creates venv, installs deps, copies .env
make config       # Edit .env with your GCP project ID
```

Or manually:
```bash
git clone <repo>
cd LLMOps-template
python -m venv venv
source venv/bin/activate
pip install -r services/api/requirements.txt
cp config/dev.env.example .env
```

### 4. Edit Environment
```bash
# Update .env with your GCP project ID and other values
nano .env
```

### 5. Run API
```bash
make api        # Using Makefile (recommended)
# Or manually:
cd services/api
python -m uvicorn app:app --reload
```

Visit `http://localhost:8000/docs` to test!

## 15-Minute Setup (With Ingestion)

Perform steps 1-5 above, then:

### 6. Create Vector Search Index
1. Go to [Vertex AI > Vector Search](https://console.cloud.google.com/vertex-ai/vector-search)
2. Create index named "rag-documents"
3. Copy the endpoint URL
4. Update `.env` with `VECTOR_STORE_ENDPOINT`

### 7. Upload Sample Documents
```bash
# Create a sample document
echo "Machine Learning is a subset of AI that learns from data." > sample.txt

# Upload to GCS
gsutil cp sample.txt gs://$PROJECT_ID-documents/documents/
```

### 8. Run Ingestion
```bash
cd services/ingestion
python main.py
```

### 9. Test End-to-End
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is machine learning?"}'
```

## Deploy to GCP (30 Minutes)

### Prerequisites
- Completed local setup
- GitHub repository created
- GCP service account with permissions

### 1. Create GitHub Secrets
In GitHub repo settings, add:
- `GCP_PROJECT_ID`: your-project-id
- `GCP_SA_KEY`: (service account key JSON)

### 2. Deploy Infrastructure
```bash
cd infra/terraform
terraform init
terraform apply \
  -var="project_id=$PROJECT_ID" \
  -var="gcs_bucket_name=$PROJECT_ID-documents"
```

### 3. Push to GitHub
```bash
git add .
git commit -m "Initial LLMOps template"
git push origin main
```

GitHub Actions will automatically:
- Build Docker images
- Push to Artifact Registry
- Deploy to Cloud Run

### 4. Verify Deployment
```bash
# Get service URL
gcloud run services describe api-service --region us-central1

# Test health endpoint
curl https://api-service-xxxxx.run.app/health
```

## Project Structure

```
.
├── services/
│   ├── api/              # RAG API (FastAPI)
│   └── ingestion/        # Document processing
├── infra/terraform/      # Infrastructure as code
├── .github/workflows/    # CI/CD pipelines
├── docs/                 # Documentation
└── config/               # Configuration templates
```

## Key Commands

### Using Makefile (Recommended)
```bash
make help               # Show all available commands
make api               # Start API service
make ingest            # Run ingestion pipeline
make test              # Run tests
make lint              # Check code style
make format            # Format code
make quality           # Run lint + type-check + tests
make docker-up         # Start with Docker Compose
make gcp-deploy        # Deploy to Cloud Run
```

### Manual Commands
```bash
# Start API
python -m uvicorn services/api/app:app --reload

# Run ingestion
python services/ingestion/main.py

# Run tests
pytest services/api/tests

# Lint and type check
ruff check services/api
mypy services/api
```

### GCP Operations
```bash
# View logs
gcloud logging read "resource.type=cloud_run_revision" --limit 50

# List services
gcloud run services list

# Deploy manually
gcloud run deploy api-service --source services/api --region us-central1
```

### Docker
```bash
# Build locally
docker build -t api:latest services/api

# Run locally
docker-compose up

# Push to Artifact Registry
docker push us-docker.pkg.dev/$PROJECT_ID/rag-services/api-service:latest
```

## Common Workflows

### Add a New Document for RAG
```bash
# Create or download document
cat > my_document.txt << EOF
Your document content here.
Multiple paragraphs are fine.
EOF

# Upload to GCS
gsutil cp my_document.txt gs://$PROJECT_ID-documents/documents/

# Trigger ingestion
gcloud run jobs execute ingestion-pipeline --region us-central1

# Wait a few minutes, then test
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "question about your document"}'
```

### Deploy a Code Change
```bash
# Make changes
# ... edit code ...

# Test locally
pytest services/api/tests

# Commit and push
git add .
git commit -m "Improve retrieval logic"
git push origin main

# GitHub Actions automatically builds and deploys
# Monitor deployment: GitHub Actions tab
```

### Scale the API
```bash
# Increase max instances
gcloud run deploy api-service \
  --max-instances 100 \
  --memory 2Gi \
  --cpu 2
```

### Check API Health
```bash
# Local
curl http://localhost:8000/health

# Production
curl https://api-service-xxxxx.run.app/health

# View logs
gcloud logging read "resource.type=cloud_run_revision \
  AND resource.labels.service_name=api-service" \
  --limit 10 --format json
```

## Troubleshooting

### API Won't Start
```bash
# Check Python version
python --version  # Must be 3.11+

# Reinstall dependencies
pip install -r services/api/requirements.txt

# Check .env file
cat .env | grep GCP_PROJECT_ID
```

### Vector Search Index Not Found
```bash
# Check index exists
gcloud ai indexes list --region us-central1

# Check .env has correct ID and endpoint
grep VECTOR_STORE .env

# Verify endpoint is deployed
# Go to Vertex AI console > Vector Search
```

### GCP Permission Errors
```bash
# Verify authentication
gcloud auth list
gcloud auth application-default login

# Check service account permissions
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --format="table(bindings.role)"
```

## Next Steps

1. **Read full documentation**: [docs/SETUP.md](docs/SETUP.md)
2. **Understand architecture**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
3. **API reference**: [docs/API.md](docs/API.md)
4. **Production deployment**: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
5. **Customize**: Modify models, chunk sizes, retrieval parameters

## Getting Help

- Check [docs/](docs/) for detailed guides
- Review [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines
- Search [GitHub Issues](../../issues) for common problems
- Ask in [GitHub Discussions](../../discussions)

## What You Have

✅ Production-ready RAG architecture
✅ Modular API and ingestion services  
✅ Automated CI/CD pipelines
✅ Infrastructure as code (Terraform)
✅ Comprehensive documentation
✅ Configuration management
✅ Local development setup
✅ GCP deployment ready
✅ Monitoring & logging
✅ Type safety (Python + MyPy)

Happy building! 🚀
