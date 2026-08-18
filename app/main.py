"""Minimal API used to demonstrate secure CI/CD delivery controls."""

from datetime import UTC, datetime
from os import getenv

from fastapi import FastAPI, status
from pydantic import BaseModel

APP_NAME = "delivery-api"
APP_VERSION = getenv("APP_VERSION", "0.1.0")
ENVIRONMENT = getenv("APP_ENVIRONMENT", "development")

app = FastAPI(
    title="DevSecOps Delivery API",
    version=APP_VERSION,
    description="A minimal service delivered through a security-gated pipeline.",
    docs_url=None,
    redoc_url=None,
)


class ServiceStatus(BaseModel):
    """A safe, non-sensitive representation of the service state."""

    service: str
    status: str
    environment: str
    version: str
    checked_at: datetime


def service_status(state: str) -> ServiceStatus:
    """Return a timestamped status response without exposing runtime secrets."""

    return ServiceStatus(
        service=APP_NAME,
        status=state,
        environment=ENVIRONMENT,
        version=APP_VERSION,
        checked_at=datetime.now(UTC),
    )


@app.get("/healthz", response_model=ServiceStatus, status_code=status.HTTP_200_OK)
def health_check() -> ServiceStatus:
    """Liveness endpoint used by the container and Kubernetes probes."""

    return service_status("healthy")


@app.get("/readyz", response_model=ServiceStatus, status_code=status.HTTP_200_OK)
def readiness_check() -> ServiceStatus:
    """Readiness endpoint kept independent from optional downstream services."""

    return service_status("ready")


@app.get("/version", response_model=ServiceStatus, status_code=status.HTTP_200_OK)
def version_check() -> ServiceStatus:
    """Expose release metadata needed for operational verification."""

    return service_status("running")
