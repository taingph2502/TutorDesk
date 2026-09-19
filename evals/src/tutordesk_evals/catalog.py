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


def load_fixture_catalog(path: Path) -> tuple[EvaluationFixture, ...]:
    """Load and validate a UTF-8 JSON Lines evaluation catalog."""
    fixtures: list[EvaluationFixture] = []
    seen_ids: set[str] = set()

    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue

        raw: object = json.loads(line)
        if not isinstance(raw, dict):
            raise ValueError(f"{path}:{line_number}: fixture must be an object")
        record = cast(dict[str, object], raw)

        fixture_id = _required_string(record, "id", path, line_number)
        prompt = _required_string(record, "prompt", path, line_number)
        language_value = _required_string(record, "language", path, line_number)
        if language_value not in SUPPORTED_LANGUAGES:
            raise ValueError(f"{path}:{line_number}: unsupported language {language_value!r}")
        language = cast(SupportedLanguage, language_value)

        terms_value = record.get("expected_terms")
        if not isinstance(terms_value, list) or not terms_value:
            raise ValueError(f"{path}:{line_number}: expected_terms must be a non-empty list")
        terms = cast(list[object], terms_value)
        expected_terms = tuple(_non_empty_term(term, path, line_number) for term in terms)

        if fixture_id in seen_ids:
            raise ValueError(f"{path}:{line_number}: duplicate fixture id {fixture_id!r}")
        seen_ids.add(fixture_id)
        fixtures.append(EvaluationFixture(fixture_id, language, prompt, expected_terms))

    if not fixtures:
        raise ValueError(f"{path}: fixture catalog is empty")
    return tuple(fixtures)


def _required_string(
    record: dict[str, object], key: str, path: Path, line_number: int
) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{path}:{line_number}: {key} must be a non-empty string")
    return value


def _non_empty_term(value: object, path: Path, line_number: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{path}:{line_number}: expected terms must be non-empty strings")
    return value
