import logging
from typing import Optional, Iterator
from google.cloud import storage
from pathlib import Path

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Handle document loading and chunking."""

    def __init__(self, project_id: str, bucket_name: str):
        self.project_id = project_id
        self.bucket_name = bucket_name
        self.storage_client = storage.Client(project=project_id)

    def load_documents_from_gcs(self, prefix: str) -> Iterator[tuple[str, str]]:
        """
        Load documents from GCS bucket.

        Yields:
            Tuple of (document_id, content)
        """
        bucket = self.storage_client.bucket(self.bucket_name)
        blobs = bucket.list_blobs(prefix=prefix)

        for blob in blobs:
            try:
                content = blob.download_as_string().decode("utf-8")
                yield (blob.name, content)
                logger.info(f"Loaded document: {blob.name}")
            except Exception as e:
                logger.error(f"Error loading {blob.name}: {str(e)}")
                continue

    def chunk_text(
        self,
        text: str,
        chunk_size: int = 1000,
        overlap: int = 100
    ) -> list[str]:
        """
        Split text into overlapping chunks.

        Args:
            text: Text to chunk
            chunk_size: Size of each chunk
            overlap: Overlap between chunks

        Returns:
            List of text chunks
        """
        chunks = []
        start = 0

        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append(text[start:end])

            # Move start position, accounting for overlap
            start = end - overlap if end < len(text) else len(text)

        return chunks

    def process_document(
        self,
        doc_id: str,
        content: str,
        chunk_size: int = 1000,
        overlap: int = 100
    ) -> list[dict]:
        """
        Process a single document into chunks with metadata.

        Args:
            doc_id: Document identifier
            content: Document content
            chunk_size: Size of chunks
            overlap: Overlap between chunks

        Returns:
            List of chunks with metadata
        """
        chunks = self.chunk_text(content, chunk_size, overlap)

        processed_chunks = []
        for idx, chunk in enumerate(chunks):
            processed_chunks.append({
                "id": f"{doc_id}:chunk_{idx}",
                "content": chunk,
                "document_id": doc_id,
                "chunk_index": idx,
                "total_chunks": len(chunks),
                "metadata": {
                    "source": doc_id,
                    "chunk": idx
                }
            })

        return processed_chunks
