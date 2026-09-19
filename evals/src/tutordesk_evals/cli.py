"""Command-line entrypoint for deterministic evaluation checks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from tutordesk_evals.catalog import SUPPORTED_LANGUAGES, load_fixture_catalog


def main() -> None:
    """Validate the evaluation catalog and summarize its language coverage."""
    parser = argparse.ArgumentParser(description="Validate TutorDesk evaluation fixtures")
    parser.add_argument("catalog", type=Path, help="UTF-8 JSON Lines fixture catalog")
    args = parser.parse_args()

    fixtures = load_fixture_catalog(args.catalog)
    languages = sorted({fixture.language for fixture in fixtures})
    missing = SUPPORTED_LANGUAGES.difference(languages)
    if missing:
        parser.error(f"catalog is missing required languages: {', '.join(sorted(missing))}")

    print(json.dumps({"fixtures": len(fixtures), "languages": languages}))
