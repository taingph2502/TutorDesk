"""Readiness probes for private deployment dependencies."""

import os
from pathlib import Path
from typing import Protocol

import psycopg


class HealthProbe(Protocol):
    """Boundary used by the HTTP adapter to inspect a private dependency."""

    async def is_ready(self) -> bool:
        """Return whether the dependency can serve application traffic."""
        ...


class PostgresHealthProbe:
    """Check PostgreSQL readiness without exposing connection failures."""

    def __init__(self, database_url: str | None = None) -> None:
        self._database_url = database_url or os.getenv("TUTORDESK_DATABASE_URL")

    async def is_ready(self) -> bool:
        try:
            connection = await self._connect()
            async with connection, connection.cursor() as cursor:
                await cursor.execute("SELECT 1")
                return await cursor.fetchone() == (1,)
        except (OSError, psycopg.Error):
            return False

    async def _connect(self) -> psycopg.AsyncConnection[tuple[object, ...]]:
        if self._database_url is not None:
            return await psycopg.AsyncConnection.connect(
                self._database_url,
                connect_timeout=2,
            )

        password_file = os.getenv("TUTORDESK_DATABASE_PASSWORD_FILE")
        if password_file is None:
            raise OSError("database password file is not configured")

        password = Path(password_file).read_text(encoding="utf-8").strip()
        return await psycopg.AsyncConnection.connect(
            host=os.getenv("TUTORDESK_DATABASE_HOST", "127.0.0.1"),
            port=int(os.getenv("TUTORDESK_DATABASE_PORT", "5432")),
            dbname=os.getenv("TUTORDESK_DATABASE_NAME", "tutordesk"),
            user=os.getenv("TUTORDESK_DATABASE_USER", "tutordesk"),
            password=password,
            connect_timeout=2,
        )
