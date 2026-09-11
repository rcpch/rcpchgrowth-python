"""Integrity contract for the primary UK-WHO clinical validation fixture."""

import hashlib
import json
from pathlib import Path

FIXTURE_PATH = Path(__file__).with_name("sds_age_validation_2021_refactored_2026.json")
DEPRECATED_FIXTURE_PATH = Path(__file__).with_name(
    "sds_age_validation_2021_deprecated.json"
)
EXPECTED_SHA256 = "e269b3ff4312bca76563eb8adc7d0e9941b655077d11888b34522c3ffe2f6c84"
EXPECTED_DEPRECATED_SHA256 = (
    "f50c8b8757bd21da2108a07f91bb6855c8f39c1728cbe9eb3b5d210d7f7d3bac"
)
EXPECTED_FIELDS = {
    "birth_date",
    "chronological_age",
    "chronological_sds",
    "corrected_age",
    "corrected_sds",
    "gestation_days",
    "gestation_weeks",
    "measurement_method",
    "observation_date",
    "observation_value",
    "sex",
}


def test_primary_uk_who_fixture_has_expected_count_and_checksum():
    fixture_bytes = FIXTURE_PATH.read_bytes()
    cases = json.loads(fixture_bytes)

    assert len(cases) == 3984
    assert hashlib.sha256(fixture_bytes).hexdigest() == EXPECTED_SHA256


def test_every_primary_uk_who_fixture_case_has_the_complete_schema():
    cases = json.loads(FIXTURE_PATH.read_bytes())

    assert all(set(case) == EXPECTED_FIELDS for case in cases)


def test_deprecated_uk_who_fixture_is_preserved_unchanged():
    fixture_bytes = DEPRECATED_FIXTURE_PATH.read_bytes()

    assert len(json.loads(fixture_bytes)) == 4002
    assert hashlib.sha256(fixture_bytes).hexdigest() == EXPECTED_DEPRECATED_SHA256
