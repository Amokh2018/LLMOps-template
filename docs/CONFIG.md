# Configuration Guide

## Environment Variables

All services use environment variables for configuration, with `.env` files providing defaults.

## API Service Configuration

### Location
`services/api/.env` (copy from `config/dev.env.example`)

### Variables

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `GCP_PROJECT_ID` | string | Yes | - | Your GCP project ID |
| `GCP_REGION` | string | No | us-central1 | GCP region |
| `VERTEX_AI_LOCATION` | string | No | us-central1 | Vertex AI location |
| `GEMINI_MODEL` | string | No | gemini-1.5-pro | Model to use for generation |
| `VECTOR_STORE_INDEX_ID` | string | Yes | - | Vector Search index ID |
| `VECTOR_STORE_ENDPOINT` | string | Yes | - | Vector Search endpoint URL |
| `API_HOST` | string | No | 0.0.0.0 | API server host |
| `API_PORT` | integer | No | 8000 | API server port |
| `API_LOG_LEVEL` | string | No | INFO | Logging level |
| `CORS_ORIGINS` | string | No | http://localhost:3000 | Comma-separated CORS origins |
| `RETRIEVAL_TOP_K` | integer | No | 5 | Default top-k documents |
| `RETRIEVAL_DISTANCE_THRESHOLD` | float | No | 0.7 | Default similarity threshold |
| `RATE_LIMIT_REQUESTS_PER_MINUTE` | integer | No | 100 | Rate limit threshold |
| `ENABLE_CLOUD_LOGGING` | boolean | No | false | Enable Cloud Logging |

### Example Configuration

**Development**
```env
GCP_PROJECT_ID=my-dev-project
GEMINI_MODEL=gemini-1.5-pro
VECTOR_STORE_INDEX_ID=rag-documents-dev
VECTOR_STORE_ENDPOINT=https://12345-us-central1.vertexai.goog
API_LOG_LEVEL=DEBUG
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
RETRIEVAL_TOP_K=5
```

**Production**
```env
GCP_PROJECT_ID=my-prod-project
GEMINI_MODEL=gemini-1.5-pro
VECTOR_STORE_INDEX_ID=rag-documents-prod
VECTOR_STORE_ENDPOINT=https://67890-us-central1.vertexai.goog
API_LOG_LEVEL=INFO
CORS_ORIGINS=https://myapp.com
ENABLE_CLOUD_LOGGING=true
RATE_LIMIT_REQUESTS_PER_MINUTE=1000
```

## Ingestion Service Configuration

### Location
`services/ingestion/.env` (copy from `config/dev.env.example`)

### Variables

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `GCP_PROJECT_ID` | string | Yes | - | Your GCP project ID |
| `GCP_REGION` | string | No | us-central1 | GCP region |
| `VERTEX_AI_LOCATION` | string | No | us-central1 | Vertex AI location |
| `GCS_BUCKET` | string | Yes | - | GCS bucket name |
| `GCS_INGESTION_PREFIX` | string | No | documents/ | GCS prefix for documents |
| `GCS_PROCESSED_PREFIX` | string | No | processed/ | GCS prefix for processed docs |
| `VECTOR_STORE_INDEX_ID` | string | Yes | - | Vector Search index ID |
| `VECTOR_STORE_ENDPOINT` | string | Yes | - | Vector Search endpoint URL |
| `CHUNK_SIZE` | integer | No | 1000 | Document chunk size (chars) |
| `CHUNK_OVERLAP` | integer | No | 100 | Overlap between chunks |
| `EMBEDDING_MODEL` | string | No | text-embedding-004 | Embedding model |
| `LOG_LEVEL` | string | No | INFO | Logging level |
| `ENABLE_CLOUD_LOGGING` | boolean | No | false | Enable Cloud Logging |

### Chunking Strategy

The `CHUNK_SIZE` and `CHUNK_OVERLAP` parameters control text splitting:

```
Document: "This is a very long document with many sentences. Chunk 1..."
                           
CHUNK_SIZE=1000, CHUNK_OVERLAP=100

Chunk 1: [0:1000]
Chunk 2: [900:1900]    # Overlaps previous by 100
Chunk 3: [1800:2800]   # Overlaps previous by 100
```

**Recommended Settings**:
- **Small chunks** (500-800): Better precision, more requests
- **Medium chunks** (1000-1500): Balanced
- **Large chunks** (2000+): Better context, more compute

### Example Configuration

**Development**
```env
GCP_PROJECT_ID=my-dev-project
GCS_BUCKET=my-project-documents-dev
VECTOR_STORE_INDEX_ID=rag-documents-dev
VECTOR_STORE_ENDPOINT=https://12345-us-central1.vertexai.goog
CHUNK_SIZE=1000
CHUNK_OVERLAP=100
LOG_LEVEL=DEBUG
ENABLE_CLOUD_LOGGING=false
```

**Production**
```env
GCP_PROJECT_ID=my-prod-project
GCS_BUCKET=my-project-documents-prod
VECTOR_STORE_INDEX_ID=rag-documents-prod
VECTOR_STORE_ENDPOINT=https://67890-us-central1.vertexai.goog
CHUNK_SIZE=1500
CHUNK_OVERLAP=150
LOG_LEVEL=INFO
ENABLE_CLOUD_LOGGING=true
```

## Cloud Run Deployment Configuration

When deploying to Cloud Run, override environment variables:

```bash
gcloud run deploy api-service \
  --set-env-vars \
    GCP_PROJECT_ID=$PROJECT_ID,\
    VECTOR_STORE_INDEX_ID=prod-index,\
    VECTOR_STORE_ENDPOINT=$ENDPOINT,\
    ENABLE_CLOUD_LOGGING=true
```

## Docker Compose Configuration

Configure services via environment file for Docker Compose:

```bash
# Create .env file for docker-compose
cat > .env.docker << EOF
GCP_PROJECT_ID=my-project
VECTOR_STORE_INDEX_ID=rag-documents
VECTOR_STORE_ENDPOINT=https://...
GCS_BUCKET=my-bucket
GEMINI_MODEL=gemini-1.5-pro
EOF

# Run with specific env file
docker-compose --env-file .env.docker up
```

## Configuration in Code

Services use Pydantic `Settings` for type-safe configuration:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    gcp_project_id: str
    retrieval_top_k: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

**Benefits**:
- Type validation
- Automatic coercion (string "123" → int 123)
- Case-insensitive environment variables
- Default values
- IDE autocomplete

## Advanced Configuration

### Logging Levels

| Level | Use Case |
|-------|----------|
| DEBUG | Development, detailed logging |
| INFO | Production, key events |
| WARNING | Warnings and errors |
| ERROR | Error events only |
| CRITICAL | Critical errors only |

### CORS Configuration

```env
# Multiple origins
CORS_ORIGINS=https://app1.com,https://app2.com,http://localhost:3000

# Specific port
CORS_ORIGINS=https://myapp.com:3000

# All origins (not recommended)
CORS_ORIGINS=*
```

### Model Selection

**Gemini Models Available**:
- `gemini-1.5-pro` - Most capable (default)
- `gemini-1.5-flash` - Faster, lower cost
- `gemini-1.0-pro` - Previous generation

**Embedding Models**:
- `text-embedding-004` - Latest (768 dimensions)
- `text-embedding-003` - Previous generation

### Performance Tuning

#### For Better Retrieval
```env
RETRIEVAL_TOP_K=10          # More context
RETRIEVAL_DISTANCE_THRESHOLD=0.5  # Lower threshold
CHUNK_SIZE=800              # Smaller chunks for precision
```

#### For Better Performance
```env
RETRIEVAL_TOP_K=3           # Fewer documents
RETRIEVAL_DISTANCE_THRESHOLD=0.8  # Higher threshold
CHUNK_SIZE=2000             # Larger chunks
```

#### For Large Scale
```env
CHUNK_SIZE=1500
CHUNK_OVERLAP=150
ENABLE_CLOUD_LOGGING=true
RATE_LIMIT_REQUESTS_PER_MINUTE=10000
```

## Secrets Management

### Using Google Secret Manager

For production, store secrets in Google Secret Manager:

```bash
# Create secret
echo -n "your-secret-value" | gcloud secrets create MY_SECRET --data-file=-

# Reference in Cloud Run
gcloud run deploy api-service \
  --set-env-vars MY_SECRET=ref:MY_SECRET
```

### Environment-Specific Configuration

```
.env.development     # Development defaults
.env.staging         # Staging overrides
.env.production      # Production (secrets)
```

Load with:
```bash
# Local development
export $(cat .env.development | xargs)

# Production (Cloud Run)
# Use Secret Manager references
```

## Configuration Validation

Both services validate configuration on startup:

```python
try:
    settings = Settings()
except ValidationError as e:
    # Missing required variables
    # Invalid types
    # Out of range values
    sys.exit(1)
```

## Troubleshooting Configuration

### Missing Variables
```
pydantic_core._pydantic_core.ValidationError: 
  1 validation error for Settings
  gcp_project_id
    Field required
```

**Solution**: Add required variables to `.env` or environment

### Type Errors
```
ValidationError: 
  1 validation error for Settings
  retrieval_top_k
    Input should be a valid integer
```

**Solution**: Ensure value is correct type (e.g., "5" not "five")

### Out of Range
```
ValidationError:
  1 validation error for Settings
  retrieval_distance_threshold
    Input should be in range [0.0, 1.0]
```

**Solution**: Check value is within valid range

## Next Steps

- See [SETUP.md](SETUP.md) for local development
- See [DEPLOYMENT.md](DEPLOYMENT.md) for production
- See [API.md](API.md) for API configuration
