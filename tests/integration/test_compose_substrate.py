import json
import os
import subprocess
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import pytest

REPOSITORY_ROOT = Path(__file__).parents[2]
COMPOSE_FILE = REPOSITORY_ROOT / "infra" / "compose" / "compose.yaml"
COMPOSE_SMOKE_ENABLED = os.getenv("TUTORDESK_COMPOSE_SMOKE") == "1"

pytestmark = [
    pytest.mark.integration,
    pytest.mark.compose,
    pytest.mark.skipif(
        not COMPOSE_SMOKE_ENABLED,
        reason="set TUTORDESK_COMPOSE_SMOKE=1 to exercise the Docker Compose substrate",
    ),
]


def load_compose_model() -> dict[str, Any]:
    result = subprocess.run(
        ["docker", "compose", "-f", str(COMPOSE_FILE), "config", "--format", "json"],
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        env={**os.environ, "TUTORDESK_DATABASE_PASSWORD": "compose-contract-only"},
        text=True,
    )
    return json.loads(result.stdout)


def test_compose_exposes_one_loopback_origin_and_keeps_dependencies_private() -> None:
    model = load_compose_model()
    services = model["services"]

    assert set(services) == {"api", "database", "web"}
    assert services["web"]["ports"] == [
        {
            "name": "workspace",
            "mode": "ingress",
            "target": 3000,
            "published": "3000",
            "protocol": "tcp",
            "host_ip": "127.0.0.1",
        }
    ]
    assert "ports" not in services["api"]
    assert "ports" not in services["database"]
    assert model["networks"]["data"]["internal"] is True

    for service in services.values():
        assert service["healthcheck"]
        assert service["restart"] == "unless-stopped"


def test_containerized_workspace_and_health_share_the_loopback_origin() -> None:
    with (
        urllib.request.urlopen("http://127.0.0.1:3000/", timeout=5) as workspace,
        urllib.request.urlopen(
            "http://127.0.0.1:3000/api/v1/health", timeout=5
        ) as health,
    ):
        workspace_body = workspace.read().decode()
        health_body = json.load(health)

    assert workspace.status == 200
    assert "TutorDesk" in workspace_body
    assert health.status == 200
    assert health_body == {
        "status": "ok",
        "components": {"api": "ok", "database": "ok"},
    }


def test_health_exposes_database_failure_and_recovers_after_restart() -> None:
    compose_command = ["docker", "compose", "-f", str(COMPOSE_FILE)]
    subprocess.run(
        [*compose_command, "stop", "database"],
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    try:
        try:
            with urllib.request.urlopen(
                "http://127.0.0.1:3000/api/v1/health", timeout=15
            ) as response:
                failure_status = response.status
                failure_body = json.load(response)
        except urllib.error.HTTPError as response:
            failure_status = response.status
            failure_body = json.load(response)

        assert failure_status == 503
        assert failure_body == {
            "status": "unavailable",
            "components": {"api": "ok", "database": "unavailable"},
        }
    finally:
        subprocess.run(
            [*compose_command, "start", "database"],
            cwd=REPOSITORY_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            [*compose_command, "up", "--wait"],
            cwd=REPOSITORY_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

    with urllib.request.urlopen(
        "http://127.0.0.1:3000/api/v1/health", timeout=5
    ) as response:
        assert response.status == 200
