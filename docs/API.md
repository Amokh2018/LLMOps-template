# RAG API Reference

## Overview

The RAG API is a FastAPI-based service that provides retrieval-augmented generation capabilities using Vertex AI's Gemini models and Vector Search.

## Base URL

**Development**: `http://localhost:8000`

**Production**: `https://api-service-<project>.run.app`

## Authentication

Currently, the API is configured to be publicly accessible (allow-unauthenticated). For production, implement authentication:

```python
# In app.py, add:
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/query")
async def query(request: QueryRequest, credentials: HTTPAuthCredentials = Depends(security)):
    # Verify token
    ...
```

## Endpoints

### 1. Health Check

Check if the API is running and healthy.

**Request**
```
GET /health
```

**Response**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

**Status Codes**
- `200` - Service is healthy
- `503` - Service unavailable (RAG service not initialized)

---

### 2. Root Endpoint

Get API information.

**Request**
```
GET /
```

**Response**
```json
{
  "name": "RAG API",
  "version": "1.0.0",
  "endpoints": {
    "health": "/health",
    "query": "/query",
    "docs": "/docs"
  }
}
```

---

### 3. Query Endpoint

Submit a query and get RAG-augmented response.

**Request**
```
POST /query
Content-Type: application/json

{
  "query": "What is machine learning?",
  "top_k": 5,
  "threshold": 0.7
}
```

**Parameters**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| query | string | Yes | - | User's question (1-1000 characters) |
| top_k | integer | No | 5 | Number of documents to retrieve (1-20) |
| threshold | number | No | 0.7 | Minimum similarity score (0.0-1.0) |

**Response**
```json
{
  "query": "What is machine learning?",
  "response": "Machine learning is a subset of artificial intelligence...",
  "retrieved_documents": [
    {
      "id": "doc1:chunk_0",
      "content": "Machine learning is a subset of artificial intelligence that...",
      "similarity_score": 0.92,
      "metadata": {
        "source": "doc1",
        "chunk": 0
      }
    }
  ],
  "model_used": "gemini-1.5-pro"
}
```

**Response Fields**

| Field | Type | Description |
|-------|------|-------------|
| query | string | The original query |
| response | string | Generated response from Gemini |
| retrieved_documents | array | List of relevant documents used as context |
| model_used | string | Name of the LLM model used |

**Retrieved Document Fields**

| Field | Type | Description |
|-------|------|-------------|
| id | string | Unique document chunk identifier |
| content | string | The document text |
| similarity_score | number | How relevant (0.0-1.0) |
| metadata | object | Additional document info |

**Status Codes**
- `200` - Successful query
- `400` - Invalid request (bad query length, invalid threshold)
- `500` - Internal server error
- `503` - Service unavailable

**Error Response**
```json
{
  "detail": "Internal server error processing query"
}
```

---

## Example Requests

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# Query with defaults
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Tell me about Python"}'

# Query with custom parameters
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I use Cloud Run?",
    "top_k": 10,
    "threshold": 0.5
  }'
```

### Using Python

```python
import httpx
import asyncio

async def query_rag():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/query",
            json={
                "query": "What is vector search?",
                "top_k": 5,
                "threshold": 0.7
            }
        )
        return response.json()

# Run it
result = asyncio.run(query_rag())
print(result["response"])
```

### Using JavaScript/TypeScript

```javascript
async function queryRAG(query) {
  const response = await fetch('http://localhost:8000/query', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: query,
      top_k: 5,
      threshold: 0.7
    })
  });
  
  return response.json();
}

// Usage
const result = await queryRAG('Tell me about embeddings');
console.log(result.response);
```

---

## Interactive Documentation

The API provides interactive documentation at:

- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`
- **OpenAPI Schema**: `/openapi.json`

Visit `http://localhost:8000/docs` to test endpoints interactively.

---

## Performance Tips

### For Better Results

1. **Craft clear queries**: More specific queries lead to better retrieval
2. **Adjust top_k**: 
   - Use 3-5 for quick responses
   - Use 10-15 for comprehensive answers
3. **Adjust threshold**:
   - Lower (0.5) for broader matches
   - Higher (0.8+) for strict relevance

### For Better Performance

1. **Batch requests**: Submit multiple queries efficiently
2. **Connection pooling**: Reuse HTTP connections
3. **Caching**: Cache similar query results

---

## Rate Limiting

By default, 100 requests per minute. Configure in `.env`:

```
RATE_LIMIT_REQUESTS_PER_MINUTE=100
```

Rate limit exceeded returns:
```
HTTP 429 Too Many Requests
```

---

## Error Handling

### Common Errors

**400 Bad Request - Invalid Query Length**
```json
{
  "detail": {
    "query": ["ensure this value has at least 1 characters"]
  }
}
```

**400 Bad Request - Invalid Threshold**
```json
{
  "detail": {
    "threshold": ["ensure this value is between 0.0 and 1.0"]
  }
}
```

**503 Service Unavailable**
```json
{
  "detail": "RAG service not initialized"
}
```

### Error Handling Best Practices

```python
import httpx

try:
    response = await client.post(
        "/query",
        json={"query": "your question"}
    )
    response.raise_for_status()
    result = response.json()
except httpx.HTTPStatusError as e:
    if e.response.status_code == 400:
        print("Invalid request:", e.response.json())
    elif e.response.status_code == 503:
        print("Service unavailable, retrying...")
        # Implement backoff and retry
    else:
        print("Error:", e)
```

---

## Model Information

### Gemini Model

- **Model ID**: `gemini-1.5-pro`
- **Context Window**: 1,000,000 tokens
- **Capabilities**: 
  - Text generation
  - Multi-turn conversations
  - Code generation
  - Reasoning over context

### Embedding Model

- **Model ID**: `text-embedding-004`
- **Dimension**: 768
- **Task Types**: SEMANTIC_SIMILARITY, RETRIEVAL_DOCUMENT, RETRIEVAL_QUERY

---

## Monitoring & Logging

### View API Logs

```bash
# Cloud Logging
gcloud logging read "resource.type=cloud_run_revision" \
  --filter="resource.labels.service_name=api-service" \
  --limit 50

# Local JSON logs
# Check application logs for JSON-formatted entries
```

### Key Metrics

- Request latency
- Error rate
- Vector store query time
- LLM generation time

---

## Versioning

Current API version: `1.0.0`

API follows semantic versioning:
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

Future versions will maintain backward compatibility within major versions.

---

## Support & Troubleshooting

### API Not Responding

1. Check if service is deployed: `gcloud run services list`
2. Check recent logs
3. Verify network connectivity

### Vector Search Returning No Results

1. Verify documents are ingested
2. Check similarity threshold (try lowering to 0.5)
3. Ensure Vector Search index is deployed

### Gemini API Errors

1. Check quota and limits
2. Verify API is enabled
3. Check service account permissions

For more help, see [SETUP.md](SETUP.md) troubleshooting section.
