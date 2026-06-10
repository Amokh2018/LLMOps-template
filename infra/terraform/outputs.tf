output "project_id" {
  description = "GCP Project ID"
  value       = var.project_id
}

output "region" {
  description = "GCP Region"
  value       = var.region
}

output "service_account_email" {
  description = "Email of RAG service account"
  value       = google_service_account.rag_service.email
}

output "service_account_id" {
  description = "ID of RAG service account"
  value       = google_service_account.rag_service.unique_id
}

output "gcs_bucket_name" {
  description = "Name of GCS bucket for documents"
  value       = google_storage_bucket.documents.name
}

output "gcs_bucket_url" {
  description = "URL of GCS bucket"
  value       = "gs://${google_storage_bucket.documents.name}"
}

output "environment" {
  description = "Environment name"
  value       = var.environment
}
