"""HTTP presentation adapter for TutorDesk."""

from typing import Literal

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel


class HealthStatus(BaseModel):
    """Public health response."""

    status: Literal["ok"]


def create_app() -> FastAPI:
    """Create the FastAPI presentation adapter."""
    app = FastAPI(title="TutorDesk API", version="0.1.0")
    api = APIRouter(prefix="/api/v1")

    @api.get("/health", response_model=HealthStatus, tags=["operations"])
    async def health() -> HealthStatus:
        return HealthStatus(status="ok")

    app.include_router(api)
    return app


app = create_app()
