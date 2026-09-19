import pytest
from fastapi.testclient import TestClient

from tutordesk.http import create_app


@pytest.mark.integration
def test_health_endpoint_reports_the_server_is_ready() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
