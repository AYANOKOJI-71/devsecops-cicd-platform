# Initial Security-Gate Remediation

The first public workflow run identified three independent configuration issues. The fixes below preserve the security controls rather than silencing their findings.

| Finding | Root cause | Remediation |
| --- | --- | --- |
| Trivy filesystem misconfiguration | The deployment identity could write Kubernetes Services and NetworkPolicies as part of applying the whole manifest collection. | The deployment workflow now performs an image-only rollout. Its namespace Role can observe and patch only the named `delivery-api` Deployment. Platform manifests remain an administrator-controlled bootstrap operation. |
| Trivy container vulnerabilities | The moving `python:3.12-slim` tag inherited high-severity Debian packages with available fixes. | The Dockerfile now uses Docker’s explicitly published `python:3.12.14-slim-trixie` base variant and refreshes available Debian security updates during the image build. The container scan still fails on high or critical findings. [1] |
| CodeQL workflow failure | CodeQL analysis completed, but GitHub Code Scanning is not enabled for this private repository, so GitHub rejected result uploads. | The CodeQL workflow explicitly grants `actions: read` for workflow metadata and runs in supported analysis-only mode with SARIF and database uploads disabled. [2] |

The repository’s static validator enforces the rollout-only Kubernetes permissions, the absence of arbitrary `kubectl apply` in the production workflow, the explicit base-image tag, and CodeQL’s required workflow-read permission. This makes the remediation reviewable and prevents accidental regression.

## References

[1] [Docker Official Image — Python](https://hub.docker.com/_/python)

[2] [GitHub Docs — Private repository CodeQL enablement](https://docs.github.com/en/code-security/reference/code-scanning/troubleshoot-analysis-errors/private-repository-enablement)
