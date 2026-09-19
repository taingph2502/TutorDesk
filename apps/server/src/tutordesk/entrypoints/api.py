"""TutorDesk API process entrypoint."""

import uvicorn


def main() -> None:
    """Run the API adapter for local development."""
    uvicorn.run("tutordesk.http:app", host="127.0.0.1", port=8000)
