locals {
  ecr_repository_name       = "${var.project_name}-${var.environment}"
  oidc_provider_arn         = coalesce(var.existing_github_oidc_provider_arn, try(aws_iam_openid_connect_provider.github[0].arn, null))
  github_oidc_provider_url  = "token.actions.githubusercontent.com"
}

resource "aws_ecr_repository" "delivery_api" {
  name                 = local.ecr_repository_name
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }
}

resource "aws_ecr_lifecycle_policy" "delivery_api" {
  repository = aws_ecr_repository.delivery_api.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep the 30 most recent tagged releases"
        selection = {
          tagStatus   = "tagged"
          tagPrefixList = ["v", "sha-"]
          countType   = "imageCountMoreThan"
          countNumber = 30
        }
        action = { type = "expire" }
      },
      {
        rulePriority = 2
        description  = "Remove untagged layers after seven days"
        selection = {
          tagStatus   = "untagged"
          countType   = "sinceImagePushed"
          countUnit   = "days"
          countNumber = 7
        }
        action = { type = "expire" }
      }
    ]
  })
}

resource "aws_iam_openid_connect_provider" "github" {
  count = var.existing_github_oidc_provider_arn == null ? 1 : 0

  url            = "https://${local.github_oidc_provider_url}"
  client_id_list = ["sts.amazonaws.com"]
}

data "aws_iam_policy_document" "github_oidc_assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [local.oidc_provider_arn]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:sub"
      values   = [var.github_subject]
    }
  }
}

resource "aws_iam_role" "github_actions_deployer" {
  name               = "${var.project_name}-${var.environment}-github-actions"
  assume_role_policy = data.aws_iam_policy_document.github_oidc_assume_role.json
  max_session_duration = 3600
}

data "aws_iam_policy_document" "github_actions_deployer" {
  statement {
    sid       = "EcrAuthorization"
    effect    = "Allow"
    actions   = ["ecr:GetAuthorizationToken"]
    resources = ["*"]
  }

  statement {
    sid    = "EcrPushToApplicationRepository"
    effect = "Allow"
    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:CompleteLayerUpload",
      "ecr:InitiateLayerUpload",
      "ecr:PutImage",
      "ecr:UploadLayerPart"
    ]
    resources = [aws_ecr_repository.delivery_api.arn]
  }

  dynamic "statement" {
    for_each = var.eks_cluster_name == null ? [] : [var.eks_cluster_name]
    content {
      sid       = "ReadTargetCluster"
      effect    = "Allow"
      actions   = ["eks:DescribeCluster"]
      resources = ["arn:aws:eks:${var.aws_region}:*:cluster/${statement.value}"]
    }
  }
}

resource "aws_iam_role_policy" "github_actions_deployer" {
  name   = "${var.project_name}-${var.environment}-delivery"
  role   = aws_iam_role.github_actions_deployer.id
  policy = data.aws_iam_policy_document.github_actions_deployer.json
}

resource "aws_eks_access_entry" "github_actions_deployer" {
  count = var.eks_cluster_name == null ? 0 : 1

  cluster_name      = var.eks_cluster_name
  principal_arn     = aws_iam_role.github_actions_deployer.arn
  type              = "STANDARD"
  kubernetes_groups = ["devsecops-deployers"]
}
