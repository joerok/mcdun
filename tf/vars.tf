variable "gcp_project_id" {
  type        = string
  description = "The Google Cloud Project ID"
}

variable "gcp_region" {
  type        = string
  description = "The Google Cloud region"
  default     = "us-central1"
}

variable "service_account_id_prefix" {
  type        = string
  description = "Prefix for the service account ID"
  default     = "github-actions-sa"
}

variable "workload_identity_pool_id" {
  type        = string
  description = "The ID for the Workload Identity Pool"
  default     = "github-actions-pool"
}

variable "workload_identity_provider_id" {
  type        = string
  description = "The ID for the Workload Identity Pool Provider"
  default     = "github-actions-provider"
}

variable "github_repo_owner" {
  type        = string
  description = "The GitHub repository owner (leave blank for organization-level access)"
  default     = "joerok"
}
