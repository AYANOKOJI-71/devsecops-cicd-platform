variable "aws_region" {
  description = "AWS region for the ECR repository and optional EKS access entry."
  type        = string
  default     = "ap-southeast-1"
}

variable "project_name" {
  description = "Lowercase project identifier used in cloud resource names."
  type        = string
  default     = "devsecops-cicd-platform"

  validation {
    condition     = can(regex("^[a-z0-9-]{3,40}$", var.project_name))
    error_message = "project_name must contain 3-40 lowercase letters, numbers, or hyphens."
  }
}

variable "environment" {
  description = "Protected deployment environment represented by this module."
  type        = string
  default     = "production"
}

variable "github_repository" {
  description = "GitHub owner/repository trusted to assume the OIDC deployment role."
  type        = string
  default     = "AYANOKOJI-71/devsecops-cicd-platform"
}

variable "github_subject" {
  description = "Exact GitHub OIDC subject claim trusted by AWS. Update if immutable subject claims are enabled."
  type        = string
  default     = "repo:AYANOKOJI-71/devsecops-cicd-platform:environment:production"
}

variable "existing_github_oidc_provider_arn" {
  description = "Optional existing GitHub OIDC provider ARN. Leave null to create one."
  type        = string
  default     = null
  nullable    = true
}

variable "eks_cluster_name" {
  description = "Optional pre-existing EKS cluster name. When set, Terraform creates a namespace-scoped access entry."
  type        = string
  default     = null
  nullable    = true
}
