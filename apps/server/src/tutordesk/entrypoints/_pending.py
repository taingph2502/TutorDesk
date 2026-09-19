"""Explicit failures for process entrypoints not implemented by the scaffold."""

from typing import NoReturn


def unavailable(process_name: str) -> NoReturn:
    """Exit with an actionable message instead of pretending a process started."""
    raise SystemExit(
        f"The {process_name} entrypoint is scaffolded but not implemented in Milestone 0 yet."
    )
