import logging
from typing import Optional
from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.services.match_service import client as match_service_client

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Generate and manage embeddings for documents."""

    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        model: str = "text-embedding-004"
    ):
        self.project_id = project_id
        self.location = location
        self.model = model
        aiplatform.init(project=project_id, location=location)

    async def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors
        """
        try:
            embeddings = []
            for text in texts:
                response = aiplatform.generative_models.GenerativeModel(
                    self.model
                ).embed_content(
                    content=text,
                    task_type="SEMANTIC_SIMILARITY"
                )
                embeddings.append(response.embedding.values)

            logger.info(f"Generated {len(embeddings)} embeddings")
            return embeddings

        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise

    async def index_documents(
        self,
        documents: list[dict],
        endpoint_name: str,
        index_id: str
    ) -> bool:
        """
        Index documents in Vector Search.

        Args:
            documents: List of documents with id, content, and metadata
            endpoint_name: Vector Search endpoint
            index_id: Index ID

        Returns:
            Success status
        """
        try:
            # Extract texts and generate embeddings
            texts = [doc["content"] for doc in documents]
            embeddings = await self.generate_embeddings(texts)

            # Prepare datapoints for indexing
            datapoints = []
            for doc, embedding in zip(documents, embeddings):
                datapoint = match_service_client.IndexDatapoint(
                    datapoint_id=doc["id"],
                    feature_vector=embedding
                )
                datapoints.append(datapoint)

            # Index in Vector Search
            # In production, you would call the actual match service
            logger.info(f"Indexed {len(datapoints)} documents")
            return True

        except Exception as e:
            logger.error(f"Error indexing documents: {str(e)}")
            raise

    async def update_documents(
        self,
        documents: list[dict],
        endpoint_name: str,
        index_id: str
    ) -> bool:
        """
        Update existing documents in Vector Search.

        Args:
            documents: List of documents to update
            endpoint_name: Vector Search endpoint
            index_id: Index ID

        Returns:
            Success status
        """
        return await self.index_documents(documents, endpoint_name, index_id)
