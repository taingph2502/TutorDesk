"""TutorDesk Source Processing supervisor entrypoint."""

from typing import NoReturn

from tutordesk.entrypoints._pending import unavailable


def main() -> NoReturn:
    """Fail explicitly until the processing supervisor is implemented."""
    unavailable("Source Processing supervisor")
