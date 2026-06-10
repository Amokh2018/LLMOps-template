from pydantic import BaseModel, Field
from typing import Optional


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000, description="User query")
    top_k: Optional[int] = Field(default=5, ge=1, le=20, description="Number of documents to retrieve")
    threshold: Optional[float] = Field(default=0.7, ge=0.0, le=1.0, description="Similarity threshold")


class RetrievedDocument(BaseModel):
    id: str = Field(..., description="Document ID")
    content: str = Field(..., description="Document content")
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Similarity score")
    metadata: Optional[dict] = Field(default=None, description="Additional document metadata")


class RAGResponse(BaseModel):
    query: str = Field(..., description="Original query")
    response: str = Field(..., description="Generated response from Gemini")
    retrieved_documents: list[RetrievedDocument] = Field(..., description="Retrieved context documents")
    model_used: str = Field(..., description="Model used for generation")


class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
