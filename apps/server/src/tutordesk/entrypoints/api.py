"""TutorDesk API process entrypoint."""

import os

import uvicorn


def main() -> None:
    """Run the API adapter for local development."""
    uvicorn.run(
        "tutordesk.http:app",
        access_log=False,
        host=os.getenv("TUTORDESK_API_HOST", "127.0.0.1"),
        port=int(os.getenv("TUTORDESK_API_PORT", "8000")),
    )
