"""HTTP presentation adapter for TutorDesk."""

from typing import Literal

from fastapi import APIRouter, FastAPI, Response, status
from pydantic import BaseModel

from tutordesk.readiness import HealthProbe, PostgresHealthProbe

HealthState = Literal["ok", "unavailable"]


class ComponentHealth(BaseModel):
    """Readiness of the processes behind the public application origin."""

    api: Literal["ok"]
    database: HealthState


class HealthStatus(BaseModel):
    """Public health response."""

    status: HealthState
    components: ComponentHealth


def create_app(*, health_probe: HealthProbe | None = None) -> FastAPI:
    """Create the FastAPI presentation adapter."""
    app = FastAPI(title="TutorDesk API", version="0.1.0")
    api = APIRouter(prefix="/api/v1")
    dependency_probe = health_probe or PostgresHealthProbe()

    @api.get("/health", response_model=HealthStatus, tags=["operations"])
    async def health(response: Response) -> HealthStatus:
        database_status: HealthState = (
            "ok" if await dependency_probe.is_ready() else "unavailable"
        )
        if database_status == "unavailable":
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

        return HealthStatus(
            status=database_status,
            components=ComponentHealth(api="ok", database=database_status),
        )

    app.include_router(api)
    return app


app = create_app()
