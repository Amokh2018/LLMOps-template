import asyncio
import logging
from config import settings
from documents import DocumentProcessor
from embeddings import EmbeddingService
from pythonjsonlogger import jsonlogger

# Configure logging
logger = logging.getLogger()
logger.setLevel(settings.log_level)

logHandler = logging.StreamHandler()
if settings.enable_cloud_logging:
    from google.cloud import logging as cloud_logging
    client = cloud_logging.Client()
    client.setup_logging()
else:
    formatter = jsonlogger.JsonFormatter()
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)


async def ingest_documents():
    """Main ingestion pipeline."""
    try:
        logger.info("Starting document ingestion pipeline")

        # Initialize services
        doc_processor = DocumentProcessor(
            project_id=settings.gcp_project_id,
            bucket_name=settings.gcs_bucket
        )

        embedding_service = EmbeddingService(
            project_id=settings.gcp_project_id,
            location=settings.vertex_ai_location,
            model=settings.embedding_model
        )

        # Load documents from GCS
        logger.info(f"Loading documents from gs://{settings.gcs_bucket}/{settings.gcs_ingestion_prefix}")
        all_chunks = []

        for doc_id, content in doc_processor.load_documents_from_gcs(
            settings.gcs_ingestion_prefix
        ):
            # Process document into chunks
            chunks = doc_processor.process_document(
                doc_id=doc_id,
                content=content,
                chunk_size=settings.chunk_size,
                overlap=settings.chunk_overlap
            )
            all_chunks.extend(chunks)
            logger.info(f"Processed {doc_id} into {len(chunks)} chunks")

        # Index chunks
        if all_chunks:
            logger.info(f"Indexing {len(all_chunks)} chunks")
            await embedding_service.index_documents(
                documents=all_chunks,
                endpoint_name=settings.vector_store_endpoint,
                index_id=settings.vector_store_index_id
            )
            logger.info("Ingestion pipeline completed successfully")
        else:
            logger.warning("No documents found to ingest")

    except Exception as e:
        logger.error(f"Ingestion pipeline failed: {str(e)}")
        raise


async def main():
    """Entry point for the ingestion service."""
    await ingest_documents()


if __name__ == "__main__":
    asyncio.run(main())
