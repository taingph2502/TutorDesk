"""Versioned evaluation-fixture catalog loading."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, cast

type SupportedLanguage = Literal["en", "vi"]
SUPPORTED_LANGUAGES = frozenset({"en", "vi"})


@dataclass(frozen=True, slots=True)
class EvaluationFixture:
    """One deterministic evaluation input and its coarse expectations."""

    id: str
    language: SupportedLanguage
    prompt: str
    expected_terms: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class FixtureLocation:
    """Human-readable location of one fixture record."""

    path: Path
    line_number: int

    def error(self, message: str) -> ValueError:
        return ValueError(f"{self.path}:{self.line_number}: {message}")


def load_fixture_catalog(path: Path) -> tuple[EvaluationFixture, ...]:
    """Load and validate a UTF-8 JSON Lines evaluation catalog."""
    fixtures: list[EvaluationFixture] = []
    seen_ids: set[str] = set()

    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue

        location = FixtureLocation(path, line_number)
        raw: object = json.loads(line)
        if not isinstance(raw, dict):
            raise location.error("fixture must be an object")
        record = cast(dict[str, object], raw)

        fixture_id = _required_field(record, "id", location)
        prompt = _required_field(record, "prompt", location)
        language_value = _required_field(record, "language", location)
        if language_value not in SUPPORTED_LANGUAGES:
            raise location.error(f"unsupported language {language_value!r}")
        language = cast(SupportedLanguage, language_value)

        terms_value = record.get("expected_terms")
        if not isinstance(terms_value, list) or not terms_value:
            raise location.error("expected_terms must be a non-empty list")
        terms = cast(list[object], terms_value)
        expected_terms = tuple(
            _non_empty_string(term, "expected terms", location) for term in terms
        )

        if fixture_id in seen_ids:
            raise location.error(f"duplicate fixture id {fixture_id!r}")
        seen_ids.add(fixture_id)
        fixtures.append(EvaluationFixture(fixture_id, language, prompt, expected_terms))

    if not fixtures:
        raise ValueError(f"{path}: fixture catalog is empty")
    return tuple(fixtures)


def _required_field(
    record: dict[str, object], key: str, location: FixtureLocation
) -> str:
    return _non_empty_string(record.get(key), key, location)


def _non_empty_string(value: object, description: str, location: FixtureLocation) -> str:
    if not isinstance(value, str) or not value.strip():
        raise location.error(f"{description} must be a non-empty string")
    return value
