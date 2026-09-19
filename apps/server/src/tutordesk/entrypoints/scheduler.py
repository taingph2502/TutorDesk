"""TutorDesk scheduler process entrypoint."""

from typing import NoReturn

from tutordesk.entrypoints._pending import unavailable


def main() -> NoReturn:
    """Fail explicitly until the scheduler runtime is implemented."""
    unavailable("scheduler")
