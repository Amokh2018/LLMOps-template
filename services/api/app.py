import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pythonjsonlogger import jsonlogger

from .config import settings
from .models import QueryRequest, HealthResponse, RAGResponse
from .rag import RAGService

# Configure JSON logging
logger = logging.getLogger()
logger.setLevel(settings.api_log_level)

# Add JSON formatter if running in production
if os.getenv("ENVIRONMENT", "development") == "production":
    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter()
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
else:
    logging.basicConfig(level=settings.api_log_level)

# Initialize RAG service
rag_service: RAGService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global rag_service
    rag_service = RAGService()
    logger.info("RAG service initialized")
    yield
    logger.info("Shutting down RAG service")


# Create FastAPI app
app = FastAPI(
    title="RAG API",
    description="Retrieval-Augmented Generation API with Gemini and Vertex AI",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0"
    )


@app.post("/query", response_model=RAGResponse)
async def query(request: QueryRequest):
    """
    Process a query using RAG pipeline.

    Args:
        request: QueryRequest containing the user's question

    Returns:
        RAGResponse with generated answer and context documents
    """
    try:
        if rag_service is None:
            raise HTTPException(
                status_code=503,
                detail="RAG service not initialized"
            )

        response = await rag_service.answer_query(
            query=request.query,
            top_k=request.top_k or settings.retrieval_top_k,
            threshold=request.threshold or settings.retrieval_distance_threshold
        )
        return response

    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error processing query"
        )


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "RAG API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "query": "/query",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level=settings.api_log_level.lower()
    )
