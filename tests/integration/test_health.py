import pytest
from fastapi.testclient import TestClient

from tutordesk.http import create_app
from tutordesk.readiness import HealthProbe


class StubHealthProbe:
    def __init__(self, *, ready: bool) -> None:
        self._ready = ready

    async def is_ready(self) -> bool:
        return self._ready


@pytest.mark.integration
def test_health_endpoint_reports_the_server_is_ready() -> None:
    probe: HealthProbe = StubHealthProbe(ready=True)

    with TestClient(create_app(health_probe=probe)) as client:
        response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "components": {"api": "ok", "database": "ok"},
    }


@pytest.mark.integration
def test_health_endpoint_reports_a_sanitized_database_failure() -> None:
    probe: HealthProbe = StubHealthProbe(ready=False)

    with TestClient(create_app(health_probe=probe)) as client:
        response = client.get("/api/v1/health")

    assert response.status_code == 503
    assert response.json() == {
        "status": "unavailable",
        "components": {"api": "ok", "database": "unavailable"},
    }
