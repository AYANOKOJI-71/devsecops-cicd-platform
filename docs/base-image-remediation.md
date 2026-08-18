# Base Image Remediation Note

The initial image security scan reported high-severity operating-system packages inherited from the moving `python:3.12-slim` base. The remediation uses the explicit Python 3.12 Debian Trixie slim variant, which Docker’s Official Image documentation currently publishes as `3.12.14-slim-trixie` and `3.12-slim-trixie`. Making the Debian release explicit improves traceability and avoids silently changing distribution families when a generic tag moves. [1]

The CI security gate remains responsible for rejecting newly discovered high- or critical-severity vulnerabilities. This source-selection change does not suppress the image scan or lower its failure threshold.

## Reference

[1] [Docker Official Image — Python](https://hub.docker.com/_/python)
