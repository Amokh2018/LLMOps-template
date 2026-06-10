terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable required APIs
resource "google_project_service" "aiplatform" {
  project = var.project_id
  service = "aiplatform.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "run" {
  project = var.project_id
  service = "run.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "storage" {
  project = var.project_id
  service = "storage.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "logging" {
  project = var.project_id
  service = "logging.googleapis.com"
  disable_on_destroy = false
}

# Service Account for RAG services
resource "google_service_account" "rag_service" {
  account_id   = "rag-service"
  display_name = "RAG Service Account"
  project      = var.project_id
}

# IAM bindings for service account
resource "google_project_iam_member" "rag_aiplatform" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.rag_service.email}"
}

resource "google_project_iam_member" "rag_storage" {
  project = var.project_id
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.rag_service.email}"
}

resource "google_project_iam_member" "rag_logging" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.rag_service.email}"
}

# GCS bucket for documents
resource "google_storage_bucket" "documents" {
  project  = var.project_id
  name     = var.gcs_bucket_name
  location = var.region

  uniform_bucket_level_access = true

  lifecycle {
    prevent_destroy = true
  }
}

# Cloud Logging bucket
resource "google_logging_project_bucket_config" "default" {
  count      = var.enable_monitoring ? 1 : 0
  project    = var.project_id
  location   = var.region
  bucket_id  = "rag-logs"
  retention_days = 30
}

# Vector Search Index (placeholder - requires manual configuration in Vertex AI console)
# In production, you would configure this through the Vertex AI API or console
output "vector_index_note" {
  value = <<-EOT
    Note: Vector Search Index needs to be created manually in Vertex AI console.
    Index name: ${var.vector_index_name}
    Dimension: ${var.vector_dimensions}
    Distance type: COSINE_DISTANCE
  EOT
}
