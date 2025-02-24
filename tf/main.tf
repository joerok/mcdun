terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 4.60.0"
    }
  }
}

# Configure the Google Cloud provider
provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

# Create a service account
resource "google_service_account" "github_actions_service_account" {
  account_id   = var.service_account_id_prefix
  display_name = "GitHub Actions Service Account"
  project      = var.gcp_project_id
}

# Grant the service account storage admin permissions
resource "google_project_iam_member" "service_account_storage_admin" {
  project = var.gcp_project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.github_actions_service_account.email}"
}

# Create a Workload Identity Pool
resource "google_iam_workload_identity_pool" "github_actions_pool" {
  workload_identity_pool_id = var.workload_identity_pool_id
  display_name              = "GitHub Actions Identity Pool"
  description               = "Pool for GitHub Actions to access Google Cloud"
  project                   = var.gcp_project_id
}

# Create a Workload Identity Provider (GitHub)
resource "google_iam_workload_identity_pool_provider" "github_actions_provider" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.github_actions_pool.workload_identity_pool_id
  workload_identity_pool_provider_id = var.workload_identity_provider_id
  display_name                       = "GitHub Actions Provider"
  description                        = "Provider for GitHub Actions Workload Identity"
  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "attribute.actor" = "assertion.actor"
    "attribute.repository" = "assertion.repository"
    "attribute.repository_owner" = "assertion.repository_owner"
  }
  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }

  project = var.gcp_project_id
  attribute_condition = "attribute.repository == assertion.repository && attribute.repository_owner == assertion.repository_owner"

}

# IAM binding to allow the pool to impersonate the service account
resource "google_service_account_iam_member" "sa_impersonate_binding" {
  service_account_id = google_service_account.github_actions_service_account.name
  role               = "roles/iam.workloadIdentityUser"
  member = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github_actions_pool.name}/attribute.repository_owner/${var.github_repo_owner}"
}

# Enable the IAM Credentials API
resource "google_project_service" "iamcredentials" {
  project = var.gcp_project_id
  service = "iamcredentials.googleapis.com"

  disable_dependent_services = false
  disable_on_destroy         = false
}

# Output variables for GitHub Actions
output "gcp_workload_identity_provider" {
  value       = "projects/${var.gcp_project_id}/locations/global/workloadIdentityPools/${var.workload_identity_pool_id}/providers/${var.workload_identity_provider_id}"
  description = "The full name of the Workload Identity Provider"
}

output "gcp_service_account_email" {
  value       = google_service_account.github_actions_service_account.email
  description = "The email of the service account"
}