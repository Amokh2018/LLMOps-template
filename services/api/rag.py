import logging
from typing import Optional
from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.services.match_service import client as match_service_client
from .models import RetrievedDocument, RAGResponse
from .config import settings

logger = logging.getLogger(__name__)


class RAGService:
    def __init__(self):
        self.project_id = settings.gcp_project_id
        self.location = settings.vertex_ai_location
        self.model_name = settings.gemini_model
        self.index_id = settings.vector_store_index_id
        self.endpoint_name = settings.vector_store_endpoint

        aiplatform.init(project=self.project_id, location=self.location)
        self.generative_model = aiplatform.generative_models.GenerativeModel(self.model_name)

    async def retrieve_documents(
        self,
        query: str,
        top_k: int = 5,
        threshold: float = 0.7
    ) -> list[RetrievedDocument]:
        """Retrieve relevant documents from vector store using semantic search."""
        try:
            embedding_response = aiplatform.generative_models.GenerativeModel(
                "text-embedding-004"
            ).embed_content(
                content=query,
                task_type="SEMANTIC_SIMILARITY"
            )

            query_embedding = embedding_response.embedding.values

            match_request = match_service_client.FindNeighborsRequest(
                index_endpoint=self.endpoint_name,
                deployed_index_id=self.index_id,
                queries=[
                    match_service_client.FindNeighborsRequest.Query(
                        data_point=match_service_client.IndexDatapoint(
                            feature_vector=query_embedding
                        ),
                        neighbor_count=top_k
                    )
                ]
            )

            # In real implementation, you'd call the match service
            # For now, this is a placeholder structure
            documents = []
            logger.info(f"Retrieved {len(documents)} documents for query: {query[:50]}...")
            return documents

        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            raise

    async def generate_response(
        self,
        query: str,
        context_documents: list[RetrievedDocument]
    ) -> str:
        """Generate response using Gemini with retrieved context."""
        try:
            # Prepare context from retrieved documents
            context = "\n\n".join([
                f"Document {doc.id} (similarity: {doc.similarity_score:.2f}):\n{doc.content}"
                for doc in context_documents
            ])

            prompt = f"""You are a helpful AI assistant. Answer the following question based on the provided context.

Context:
{context}

Question: {query}

Answer:"""

            response = self.generative_model.generate_content(prompt)
            return response.text

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise

    async def answer_query(
        self,
        query: str,
        top_k: int = 5,
        threshold: float = 0.7
    ) -> RAGResponse:
        """Complete RAG pipeline: retrieve and generate."""
        try:
            # Retrieve relevant documents
            documents = await self.retrieve_documents(
                query=query,
                top_k=top_k,
                threshold=threshold
            )

            # Generate response
            response_text = await self.generate_response(query, documents)

            return RAGResponse(
                query=query,
                response=response_text,
                retrieved_documents=documents,
                model_used=self.model_name
            )

        except Exception as e:
            logger.error(f"Error in RAG pipeline: {str(e)}")
            raise
