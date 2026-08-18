"""Contract tests for the operational endpoints."""

from fastapi.testclient import TestClient

from app.main import APP_NAME, APP_VERSION, ENVIRONMENT, app

client = TestClient(app)


def assert_status_response(response, expected_status: str) -> None:
    """Assert fields deliberately exposed by the non-sensitive status contract."""

    assert response.status_code == 200
    payload = response.json()
    assert payload["service"] == APP_NAME
    assert payload["status"] == expected_status
    assert payload["environment"] == ENVIRONMENT
    assert payload["version"] == APP_VERSION
    assert payload["checked_at"].endswith("Z") or "+00:00" in payload["checked_at"]


def test_health_check_reports_healthy_state() -> None:
    """Kubernetes liveness probes should receive a stable success response."""

    assert_status_response(client.get("/healthz"), "healthy")


def test_readiness_check_reports_ready_state() -> None:
    """Kubernetes readiness probes should receive a stable success response."""

    assert_status_response(client.get("/readyz"), "ready")


def test_version_check_exposes_release_metadata() -> None:
    """Operational verification should reveal build metadata but no secrets."""

    assert_status_response(client.get("/version"), "running")
