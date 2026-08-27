"""Tests for calculation-reference provenance on Measurement results.

Safety driver: hazard rcpch/digital-growth-charts-documentation#174 records a
case where chart curves and a measurement result used different growth
references. This is step 1 of the mitigation chain
(rcpch/rcpchgrowth-python#37): every Measurement result must carry the
growth reference, and the identity of the calculation engine that produced
it, so downstream consumers can detect a mismatch.
"""

# standard imports
from datetime import date, timedelta

# third-party imports
import pytest

# rcpch imports
from rcpchgrowth import Measurement, generate_fictional_child_data
from rcpchgrowth.constants import REFERENCES

BIRTH_DATE = date(2015, 1, 1)


def observation_date_for_age(age_years: float) -> date:
    return BIRTH_DATE + timedelta(days=age_years * 365.25)


# One measurement per public reference, chosen to fall inside that
# reference's valid age range and (for Turner) the correct sex, so every
# case produces a real calculated result rather than an error path.
REFERENCE_CASES = {
    "uk-who": {"sex": "female", "age_years": 5.0},
    "trisomy-21": {"sex": "female", "age_years": 5.0},
    "trisomy-21-aap": {"sex": "female", "age_years": 5.0},
    "turners-syndrome": {"sex": "female", "age_years": 10.0},
    "cdc": {"sex": "male", "age_years": 10.0},
    "who": {"sex": "male", "age_years": 1.0},
}


def test_all_six_public_references_are_covered_by_this_test():
    # Guards against REFERENCE_CASES silently drifting out of sync with the
    # canonical public vocabulary if a new reference is ever added.
    assert set(REFERENCE_CASES.keys()) == set(REFERENCES)


@pytest.mark.parametrize("reference", REFERENCES)
def test_provenance_growth_reference_matches_the_selected_reference(reference):
    case = REFERENCE_CASES[reference]

    measurement = Measurement(
        birth_date=BIRTH_DATE,
        observation_date=observation_date_for_age(case["age_years"]),
        measurement_method="height",
        observation_value=110.0,
        reference=reference,
        sex=case["sex"],
    ).measurement

    assert measurement["provenance"]["growth_reference"] == reference


@pytest.mark.parametrize("reference", REFERENCES)
def test_provenance_calculation_engine_is_always_present(reference):
    case = REFERENCE_CASES[reference]

    measurement = Measurement(
        birth_date=BIRTH_DATE,
        observation_date=observation_date_for_age(case["age_years"]),
        measurement_method="height",
        observation_value=110.0,
        reference=reference,
        sex=case["sex"],
    ).measurement

    engine = measurement["provenance"]["calculation_engine"]
    assert engine["name"] == "rcpchgrowth"
    assert isinstance(engine["version"], str) and engine["version"] != ""
    assert isinstance(engine["commit"], str) and engine["commit"] != ""


def test_trisomy_21_and_trisomy_21_aap_provenance_are_distinguishable():
    common = {
        "birth_date": BIRTH_DATE,
        "observation_date": observation_date_for_age(5.0),
        "measurement_method": "height",
        "observation_value": 100.0,
        "sex": "female",
    }

    trisomy_21 = Measurement(reference="trisomy-21", **common).measurement
    trisomy_21_aap = Measurement(reference="trisomy-21-aap", **common).measurement

    assert trisomy_21["provenance"]["growth_reference"] == "trisomy-21"
    assert trisomy_21_aap["provenance"]["growth_reference"] == "trisomy-21-aap"
    assert (
        trisomy_21["provenance"]["growth_reference"]
        != trisomy_21_aap["provenance"]["growth_reference"]
    )


def test_turners_syndrome_provenance_retains_canonical_spelling():
    measurement = Measurement(
        birth_date=BIRTH_DATE,
        observation_date=observation_date_for_age(10.0),
        measurement_method="height",
        observation_value=120.0,
        reference="turners-syndrome",
        sex="female",
    ).measurement

    assert measurement["provenance"]["growth_reference"] == "turners-syndrome"


def test_provenance_is_present_when_numerical_result_is_unavailable():
    # A dates error (observation before birth) makes SDS/centile calculation
    # impossible, but a Measurement result is still returned. Provenance must
    # survive this early-return path too.
    measurement = Measurement(
        birth_date=BIRTH_DATE,
        observation_date=BIRTH_DATE - timedelta(days=1),
        measurement_method="height",
        observation_value=50.0,
        reference="uk-who",
        sex="female",
    ).measurement

    assert measurement["measurement_calculated_values"]["corrected_sds"] is None
    assert measurement["provenance"]["growth_reference"] == "uk-who"


@pytest.mark.parametrize("reference", REFERENCES)
def test_fictional_child_measurements_carry_provenance(reference):
    case = REFERENCE_CASES[reference]

    measurements = generate_fictional_child_data(
        measurement_method="height",
        sex=case["sex"],
        start_chronological_age=max(case["age_years"] - 1, 0.0),
        end_age=case["age_years"] + 1,
        measurement_interval_number=6,
        measurement_interval_type="months",
        reference=reference,
    )

    assert len(measurements) > 0
    for measurement in measurements:
        assert measurement["provenance"]["growth_reference"] == reference
        assert measurement["provenance"]["calculation_engine"]["name"] == "rcpchgrowth"
