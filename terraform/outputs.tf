output "ecr_repository_url" {
  description = "Repository URL for images that pass the CI security gates."
  value       = aws_ecr_repository.delivery_api.repository_url
}

output "github_actions_role_arn" {
  description = "Set this as the AWS_ROLE_TO_ASSUME production environment variable in GitHub."
  value       = aws_iam_role.github_actions_deployer.arn
}

output "github_oidc_provider_arn" {
  description = "GitHub OIDC provider trusted by the deployment role."
  value       = local.oidc_provider_arn
}
