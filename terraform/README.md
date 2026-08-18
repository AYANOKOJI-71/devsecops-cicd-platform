# AWS Delivery Foundation

This Terraform module creates the supply-chain resources that are safe to express without committing credentials: an immutable Amazon ECR repository with scan-on-push and cleanup controls, a GitHub OIDC provider (unless an existing provider ARN is supplied), and a GitHub Actions IAM role.

The trust policy accepts a single explicit GitHub OIDC `sub` claim. The default corresponds to the repository’s protected `production` environment, not a wildcard branch or organization. When a pre-existing EKS cluster name is supplied, the module creates an EKS access entry associated with the Kubernetes group `devsecops-deployers`. The Kubernetes manifests bind that group only to deployment actions in the application namespace.

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform fmt -check -recursive
terraform validate
terraform plan
```

An actual `apply` requires an AWS account and is deliberately not part of the GitHub pipeline. Configure a protected GitHub environment named `production`, restrict it to the `main` branch, require a reviewer, and set `AWS_REGION`, `AWS_ROLE_TO_ASSUME`, and `EKS_CLUSTER_NAME` as environment variables before enabling the manual deployment workflow.

For repositories created after July 15, 2026 or configured for immutable GitHub OIDC subject claims, update `github_subject` to the exact claim format shown by GitHub before applying this module. See `docs/research-notes.md` for the official references.
