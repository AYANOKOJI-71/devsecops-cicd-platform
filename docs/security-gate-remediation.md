# Initial Security-Gate Remediation

The first public workflow run identified three independent configuration issues. The fixes below preserve the security controls rather than silencing their findings.

| Finding | Root cause | Remediation |
| --- | --- | --- |
| Trivy filesystem misconfiguration | The deployment identity could write Kubernetes Services and NetworkPolicies as part of applying the whole manifest collection. | The deployment workflow now performs an image-only rollout. Its namespace Role can observe and patch only the named `delivery-api` Deployment. Platform manifests remain an administrator-controlled bootstrap operation. |
| Trivy container vulnerabilities | The moving `python:3.12-slim` tag inherited high-severity Debian packages with available fixes. | The Dockerfile now uses Docker’s explicitly published `python:3.12.14-slim-trixie` base variant. The container scan still fails on high or critical findings. [1] |
| CodeQL workflow failure | CodeQL analysis completed, but the workflow token lacked the read access needed to retrieve workflow-run metadata during post-processing. | The CodeQL workflow now explicitly grants `actions: read`, alongside the existing minimum `contents: read` and `security-events: write` permissions. [2] |

The repository’s static validator enforces the rollout-only Kubernetes permissions, the absence of arbitrary `kubectl apply` in the production workflow, the explicit base-image tag, and CodeQL’s required workflow-read permission. This makes the remediation reviewable and prevents accidental regression.

## References

[1] [Docker Official Image — Python](https://hub.docker.com/_/python)

[2] [GitHub Docs — Workflow syntax: permissions](https://docs.github.com/actions/writing-workflows/workflow-syntax-for-github-actions#permissions)

