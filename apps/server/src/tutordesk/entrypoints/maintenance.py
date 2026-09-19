"""TutorDesk maintenance process entrypoint."""

from typing import NoReturn

from tutordesk.entrypoints._pending import unavailable


def main() -> NoReturn:
    """Fail explicitly until the maintenance runtime is implemented."""
    unavailable("maintenance")
