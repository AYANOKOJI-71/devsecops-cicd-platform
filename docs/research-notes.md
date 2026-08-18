# Security Design Research Notes

This implementation uses an offline, portfolio-ready delivery path. The following official guidance informed the future cloud-deployment gate and workflow security model.

| Source | Applied design decision |
| --- | --- |
| [GitHub: Configuring OpenID Connect in AWS](https://docs.github.com/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services) | The deployment workflow requests `id-token: write` only in the deployment job and assumes a short-lived AWS role rather than storing long-lived AWS keys. The trust policy restricts the GitHub OIDC `sub` claim to the repository environment. |
| [GitHub: Security hardening for GitHub Actions](https://docs.github.com/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions) | Workflows use minimum `GITHUB_TOKEN` permissions, keep secrets out of source, avoid privileged pull-request triggers, and use a protected deployment environment for production access. |
| [AWS IAM: Create an OIDC identity provider](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_create_oidc.html) | The future Terraform module provisions GitHub's OIDC provider and an IAM role whose identity policy is limited to the required ECR and EKS deployment actions. |

These notes are implementation guidance, not deployed credentials. The repository deliberately contains no cloud-account ID, AWS role ARN, secret value, cluster endpoint, or live Terraform state.

## Trivy Supply-Chain Decision

In March 2026, Aqua disclosed compromised Trivy and Trivy Action releases. Aqua’s incident guidance identified Trivy `v0.69.3` as a safe recovery release, while the current official release page lists `v0.74.0` as the latest release. The security workflow therefore uses the `v0.74.0` container image **by immutable SHA-256 digest**, rather than a mutable tag or the affected GitHub Action. [Aqua incident update](https://www.aquasec.com/blog/trivy-supply-chain-attack-what-you-need-to-know/) · [Trivy releases](https://github.com/aquasecurity/trivy/releases)

## Test Client Compatibility

Current Starlette guidance identifies `httpx2` as the supported dependency for `TestClient`; plain `httpx` remains supported but is deprecated. The development dependency therefore uses `httpx2` to keep the FastAPI contract tests free of the upstream warning. [Starlette TestClient documentation](https://starlette.dev/testclient/) · [FastAPI discussion](https://github.com/fastapi/fastapi/discussions/15742)
