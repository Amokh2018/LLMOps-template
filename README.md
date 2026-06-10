# LLMOps Template: GCP RAG Service

A production-ready template for deploying Retrieval-Augmented Generation (RAG) services on Google Cloud Platform.

## 📋 Overview

This template provides a modular, scalable architecture for RAG services with:
- **LLM Inference**: Vertex AI Generative API (Gemini)
- **Vector Store**: Vertex AI Vector Search for semantic retrieval
- **Document Ingestion**: Batch processing pipeline for embedding documents
- **API Layer**: FastAPI-based orchestration service
- **CI/CD**: GitHub Actions with automated testing, linting, and Docker builds

## 🏗️ Architecture

```
┌─────────────────┐
│   Documents     │
└────────┬────────┘
         │
    ┌────▼─────┐
    │ Ingestion │  (Batch pipeline)
    │ Service   │
    └────┬──────┘
         │
    ┌────▼──────────────┐
    │ Vector Store      │  (Vertex AI Vector Search)
    │ (Embeddings)      │
    └────┬──────────────┘
         │
    ┌────▼──────────────────────┐
    │  API Service (FastAPI)    │
    │  - Retrieve relevant docs │
    │  - Call Gemini LLM        │
    │  - Return response        │
    └────────────────────────────┘
         │
    ┌────▼──────────┐
    │  Client Apps  │
    └───────────────┘
```

## 📁 Project Structure

```
.
├── services/
│   ├── api/                    # Main RAG API service
│   │   ├── app.py
│   │   ├── config.py
│   │   ├── models.py
│   │   ├── rag.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   └── ingestion/              # Document ingestion pipeline
│       ├── main.py
│       ├── config.py
│       ├── documents.py
│       ├── embeddings.py
│       ├── requirements.txt
│       └── Dockerfile
│
├── infra/
│   ├── terraform/              # Infrastructure as Code
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── gcp-setup.sh            # Manual setup script
│
├── .github/workflows/          # CI/CD pipelines
│   ├── api-ci.yml
│   ├── ingestion-ci.yml
│   └── deploy.yml
│
├── docker/                     # Shared Docker configs
│   └── Dockerfile.base
│
├── config/                     # Configuration templates
│   ├── dev.env.example
│   └── prod.env.example
│
├── tests/                      # Shared test utilities
│   ├── conftest.py
│   └── mocks.py
│
└── docs/                       # Documentation
    ├── SETUP.md               # Local development setup
    ├── DEPLOYMENT.md          # GCP deployment guide
    └── API.md                 # API reference
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- GCP Project with Vertex AI API enabled
- GitHub Actions configured

### Local Development

**Using Makefile (Recommended)**:
```bash
git clone <repo>
cd LLMOps-template
make setup      # Setup venv, install deps, create .env
make config     # Edit .env with your GCP credentials
make api        # Run API service
make ingest     # Run ingestion pipeline (separate terminal)
```

**Or manually**:
```bash
git clone <repo>
cd LLMOps-template
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r services/api/requirements.txt
pip install -r services/ingestion/requirements.txt
cp config/dev.env.example .env
# Edit .env with your GCP credentials
python -m services.api.app
```

### Docker Compose

```bash
docker-compose up
```

## 📦 Key Components

### API Service (`services/api/`)
FastAPI application that:
- Accepts user queries
- Retrieves relevant documents from vector store
- Calls Gemini for generation
- Returns augmented responses

### Ingestion Service (`services/ingestion/`)
Batch processing pipeline that:
- Reads documents from Cloud Storage
- Generates embeddings via Vertex AI
- Indexes in Vertex AI Vector Search
- Supports incremental updates

## 🔄 CI/CD Pipeline

### Automated Workflows
- **Lint & Type Check**: Code quality gates on every PR
- **Build & Push**: Docker images to Artifact Registry
- **Deploy**: Automated deployment to Cloud Run (on merge to main)

See [CI/CD Documentation](.github/workflows/) for details.

## 🛠️ Development Commands (Makefile)

Common tasks are simplified with `make`:

```bash
make setup              # Setup environment
make api               # Run API service
make test              # Run tests
make lint              # Check code style
make format            # Format code
make quality           # Run all checks
make docker-up         # Start with Docker Compose
make gcp-deploy        # Deploy to Cloud Run
make help              # Show all commands
```

See [Makefile](Makefile) for complete command reference.

## 📚 Documentation

- [Local Setup Guide](docs/SETUP.md)
- [GCP Deployment Guide](docs/DEPLOYMENT.md)
- [API Reference](docs/API.md)
- [Architecture Overview](docs/ARCHITECTURE.md)

## 🛠️ Configuration

All services use environment-based configuration:
- `config/dev.env.example` - Development settings
- `config/prod.env.example` - Production settings

See [Configuration Guide](docs/CONFIG.md) for details.

## 📊 Monitoring & Logging

- Cloud Logging integration for all services
- Vertex AI monitoring for LLM calls
- Custom metrics for retrieval quality

## 🔒 Security

- Secret management via Google Secret Manager
- CORS configuration for API access
- Request validation and rate limiting
- Secure credential handling in CI/CD

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

## 🆘 Support

- Issues: [GitHub Issues](../../issues)
- Discussions: [GitHub Discussions](../../discussions)
