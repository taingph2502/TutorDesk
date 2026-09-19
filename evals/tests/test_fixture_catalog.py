from pathlib import Path

import pytest

from tutordesk.evals.catalog import load_fixture_catalog

FIXTURE_CATALOG = Path(__file__).parents[1] / "fixtures" / "smoke.jsonl"


@pytest.mark.unit
def test_smoke_catalog_covers_english_and_vietnamese() -> None:
    fixtures = load_fixture_catalog(FIXTURE_CATALOG)

    assert {fixture.language for fixture in fixtures} == {"en", "vi"}
    assert all(fixture.prompt and fixture.expected_terms for fixture in fixtures)
