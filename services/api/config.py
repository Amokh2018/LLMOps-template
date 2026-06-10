from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # GCP
    gcp_project_id: str
    gcp_region: str = "us-central1"
    vertex_ai_location: str = "us-central1"

    # Models
    gemini_model: str = "gemini-1.5-pro"

    # Vector Store
    vector_store_index_id: str
    vector_store_endpoint: str

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_log_level: str = "INFO"
    cors_origins: str = "http://localhost:3000,http://localhost:8000"

    # Retrieval
    retrieval_top_k: int = 5
    retrieval_distance_threshold: float = 0.7

    # Database
    db_type: str = "firestore"

    # Monitoring
    enable_cloud_logging: bool = False
    enable_cloud_trace: bool = False

    # Rate limiting
    rate_limit_requests_per_minute: int = 100

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]


settings = Settings()
