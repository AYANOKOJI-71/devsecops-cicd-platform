# Security Policy

This is a portfolio reference project. Do not report real secrets, potentially exploitable details, or sensitive data through public issues. Use the author’s GitHub contact route instead.

The project’s security posture is based on least privilege, immutable release artifacts, vulnerability and misconfiguration scanning, protected production deployment, and short-lived cloud credentials. The workflow configuration must never be changed to print secrets, assume wildcard AWS roles, or deploy from an unreviewed pull request.

If a secret is accidentally committed, immediately revoke or rotate it at the provider, remove it from the current source tree, invalidate any affected artifact, and review workflow logs. Removing a value from a Git commit alone does not make it safe.
