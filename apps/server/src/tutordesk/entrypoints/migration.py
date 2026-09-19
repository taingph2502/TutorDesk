"""TutorDesk migration process entrypoint."""

from typing import NoReturn

from tutordesk.entrypoints._pending import unavailable


def main() -> NoReturn:
    """Fail explicitly until the migration runtime is implemented."""
    unavailable("migration")
