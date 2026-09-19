"""TutorDesk disposable Source Processing worker entrypoint."""

from typing import NoReturn

from tutordesk.entrypoints._pending import unavailable


def main() -> NoReturn:
    """Fail explicitly until the Source Processing worker is implemented."""
    unavailable("Source Processing worker")
