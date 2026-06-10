from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # GCP
    gcp_project_id: str
    gcp_region: str = "us-central1"
    vertex_ai_location: str = "us-central1"

    # Cloud Storage
    gcs_bucket: str
    gcs_ingestion_prefix: str = "documents/"
    gcs_processed_prefix: str = "processed/"

    # Vector Store
    vector_store_index_id: str
    vector_store_endpoint: str

    # Database
    db_type: str = "firestore"

    # Processing
    chunk_size: int = 1000
    chunk_overlap: int = 100
    embedding_model: str = "text-embedding-004"

    # Logging
    log_level: str = "INFO"
    enable_cloud_logging: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
