variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "vector_index_name" {
  description = "Name of the Vector Search index"
  type        = string
  default     = "rag-documents"
}

variable "vector_dimensions" {
  description = "Dimension of embedding vectors"
  type        = number
  default     = 768
}

variable "api_service_name" {
  description = "Cloud Run service name for API"
  type        = string
  default     = "api-service"
}

variable "ingestion_job_name" {
  description = "Cloud Run job name for ingestion"
  type        = string
  default     = "ingestion-pipeline"
}

variable "gcs_bucket_name" {
  description = "GCS bucket for documents"
  type        = string
}

variable "enable_monitoring" {
  description = "Enable Cloud Monitoring and Logging"
  type        = bool
  default     = true
}
