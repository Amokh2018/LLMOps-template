# System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      Client Applications                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ HTTP/REST
                     │
        ┌────────────▼────────────┐
        │   API Service (Cloud    │
        │   Run - FastAPI)        │
        │ ┌──────────────────────┐│
        │ │ Request Handler      ││
        │ │ Validation           ││
        │ │ RAG Orchestration    ││
        │ └──────────┬───────────┘│
        └────────────┼────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         │ (Async)               │ (Async)
         │                       │
    ┌────▼──────────┐    ┌──────▼─────────┐
    │ Vector Search │    │  Gemini LLM    │
    │ (Retrieval)   │    │  (Generation)  │
    └────┬──────────┘    └────────────────┘
         │
    ┌────▼──────────────────┐
    │ Vector Store Index     │
    │ (Vertex AI Vector      │
    │  Search)               │
    └────────────────────────┘
         △
         │
         │ (Batch)
         │
    ┌────┴──────────────────┐
    │ Ingestion Pipeline     │
    │ (Cloud Run Job)        │
    │ ┌───────────────────────┐
    │ │ Document Loader (GCS) │
    │ │ Text Chunking         │
    │ │ Embedding Generation  │
    │ │ Index Upload          │
    │ └───────────────────────┘
    └────────────────────────┘
         △
         │
    ┌────┴──────────────┐
    │  GCS Bucket       │
    │  (Documents)      │
    └───────────────────┘
```

## Component Details

### 1. API Service (`services/api/`)

**Technology**: FastAPI + Python 3.11

**Responsibilities**:
- Accept HTTP requests from clients
- Parse and validate user queries
- Orchestrate RAG pipeline
- Return formatted responses

**Key Files**:
- `app.py` - FastAPI application and routes
- `models.py` - Pydantic request/response schemas
- `rag.py` - RAG pipeline orchestration
- `config.py` - Configuration management

**Dependencies**:
- FastAPI
- Uvicorn (ASGI server)
- Pydantic (validation)
- google-cloud-aiplatform (Vertex AI)

**Deployment**: Cloud Run (managed serverless)

### 2. Ingestion Pipeline (`services/ingestion/`)

**Technology**: Python 3.11 + Async Processing

**Responsibilities**:
- Load documents from GCS
- Split documents into chunks
- Generate embeddings for chunks
- Index chunks in Vector Search

**Key Files**:
- `main.py` - Pipeline orchestrator
- `documents.py` - Document loading and chunking
- `embeddings.py` - Embedding generation and indexing
- `config.py` - Configuration

**Processing Flow**:
```
GCS Documents
    ↓
Document Loader (read from GCS)
    ↓
Text Chunking (overlap by 100 chars)
    ↓
Embedding Generation (text-embedding-004)
    ↓
Vector Search Indexing
```

**Deployment**: Cloud Run Job (scheduled batch processing)

### 3. Infrastructure

**GCP Services Used**:

| Service | Purpose | Config |
|---------|---------|--------|
| Vertex AI Generative API | LLM inference (Gemini) | Configured in code |
| Vertex AI Vector Search | Document retrieval | Manual index creation |
| Cloud Storage (GCS) | Document storage | Terraform |
| Cloud Run | Serverless compute | Terraform + Cloud Deploy |
| Cloud Logging | Log aggregation | Terraform |
| Cloud Monitoring | Metrics & alerts | Manual setup |
| Artifact Registry | Docker image storage | Terraform |
| Secret Manager | Secrets storage | GCP console |

**Infrastructure as Code**:
- `infra/terraform/` - Terraform configurations
- `infra/gcp-setup.sh` - Manual GCP setup steps

### 4. CI/CD Pipeline

**Platform**: GitHub Actions

**Workflows**:

1. **API CI** (`.github/workflows/api-ci.yml`)
   - Triggers on changes to `services/api/`
   - Steps:
     - Linting (ruff)
     - Type checking (mypy)
     - Testing (pytest)
     - Docker build
     - Push to Artifact Registry

2. **Ingestion CI** (`.github/workflows/ingestion-ci.yml`)
   - Triggers on changes to `services/ingestion/`
   - Same steps as API CI

3. **Deployment** (`.github/workflows/deploy.yml`)
   - Triggers on merge to `main`
   - Deploys to Cloud Run
   - Updates services

## Data Flow

### Query Processing Flow

```
1. Client Request
   POST /query
   {
     "query": "What is RAG?",
     "top_k": 5
   }
   ↓
2. API Service
   - Validate request
   - Initialize RAG service
   ↓
3. Embedding Generation
   - Convert query to embedding
   - Use text-embedding-004 model
   ↓
4. Vector Search
   - Query Vector Search index
   - Retrieve top-k similar documents
   - Filter by similarity threshold
   ↓
5. Context Preparation
   - Format retrieved documents
   - Create prompt with context
   ↓
6. LLM Generation
   - Call Gemini with context + query
   - Get generated response
   ↓
7. Response Formatting
   - Combine response with documents
   - Format as JSON
   ↓
8. Return to Client
   200 OK
   {
     "query": "What is RAG?",
     "response": "RAG is...",
     "retrieved_documents": [...]
   }
```

### Document Ingestion Flow

```
1. Ingestion Job Trigger
   (Scheduled via Cloud Scheduler)
   ↓
2. Load Documents from GCS
   gs://bucket/documents/
   ↓
3. Process Each Document
   - Read file content
   - Split into chunks (1000 chars, 100 overlap)
   - Add metadata
   ↓
4. Generate Embeddings
   For each chunk:
   - Call text-embedding-004
   - Get 768-dim vector
   ↓
5. Index Documents
   - Upload vectors to Vector Search
   - Associate with document IDs
   - Update index
   ↓
6. Logging
   - Log success/failures
   - Store metrics
```

## Configuration Management

### Environment Variables

**API Service** (`services/api/.env`):
```
GCP_PROJECT_ID=project-id
VERTEX_AI_LOCATION=us-central1
GEMINI_MODEL=gemini-1.5-pro
VECTOR_STORE_INDEX_ID=index-id
VECTOR_STORE_ENDPOINT=endpoint-url
RETRIEVAL_TOP_K=5
RETRIEVAL_DISTANCE_THRESHOLD=0.7
```

**Ingestion Service** (`services/ingestion/.env`):
```
GCP_PROJECT_ID=project-id
GCS_BUCKET=bucket-name
VECTOR_STORE_INDEX_ID=index-id
VECTOR_STORE_ENDPOINT=endpoint-url
CHUNK_SIZE=1000
CHUNK_OVERLAP=100
```

### Configuration Hierarchy

```
Defaults (in code)
    ↓
Environment variables (.env files)
    ↓
Runtime overrides (arguments)
```

## Security Architecture

### Authentication & Authorization

1. **Service Account**: RAG service uses GCP service account
2. **IAM Bindings**: Least privilege access model
3. **API Access**: Currently open (add bearer token auth in production)

### Data Protection

1. **Storage**: Documents encrypted in Cloud Storage (Google-managed keys)
2. **Transit**: TLS/HTTPS for all external communication
3. **Secrets**: Use Google Secret Manager for sensitive data

### Security Best Practices

- Rotate service account keys regularly
- Enable audit logging
- Use VPC Service Controls for sensitive environments
- Enable Cloud Armor for public APIs
- Implement rate limiting

## Scalability Design

### Horizontal Scaling

**API Service**:
- Cloud Run auto-scales based on traffic
- Configure max instances, concurrency limits
- Stateless design allows easy scaling

**Ingestion Pipeline**:
- Cloud Run Jobs handle batch processing
- Processes documents in chunks
- Can run parallel jobs (with index locking)

### Performance Optimization

1. **Caching**:
   - Cache query embeddings (same queries)
   - Cache popular document chunks
   - Add Redis layer if needed

2. **Indexing**:
   - Periodic index refreshes
   - Batch document uploads
   - Monitor index size and query latency

3. **Model Inference**:
   - Vertex AI handles batching
   - Use larger batches for better throughput
   - Monitor token usage and quota

## Monitoring & Observability

### Logging

- Cloud Logging for centralized logs
- JSON-formatted application logs
- Structured logging with request IDs

### Metrics

- Request latency
- Error rates
- Vector search query time
- LLM generation time
- Document retrieval quality metrics

### Alerting

Set up alerts for:
- API error rate > 5%
- Response latency > 5s
- Vector Search unavailability
- Quota usage approaching limits

## Disaster Recovery

### Backup & Restore

1. **Document Storage**:
   - GCS versioning enabled
   - Cross-region replication (production)

2. **Vector Index**:
   - Can be rebuilt from documents
   - Keep document source as source of truth

3. **Configuration**:
   - Stored in version control
   - Terraform state backed up

### Recovery Procedures

1. **Service Failure**:
   - Cloud Run auto-restarts
   - Check recent logs for cause

2. **Data Loss**:
   - Restore from GCS versioning
   - Re-run ingestion pipeline

3. **Index Corruption**:
   - Delete corrupted index
   - Re-ingest all documents

## Future Enhancements

- [ ] Multi-tenant support
- [ ] Advanced authentication (OAuth, mTLS)
- [ ] Query result ranking/reranking
- [ ] Fine-tuned embedding models
- [ ] Document-level access control
- [ ] A/B testing framework
- [ ] Cost optimization module
- [ ] Advanced monitoring dashboard
