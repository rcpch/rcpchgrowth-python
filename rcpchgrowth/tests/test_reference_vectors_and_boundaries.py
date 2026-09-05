"""Characterization vectors and boundaries for the supported references."""

import math

import pytest

from rcpchgrowth import cdc, trisomy_21_aap, uk_who, who
from rcpchgrowth.constants import (
    BMI,
    CDC,
    FEMALE,
    FORTY_TWO_WEEKS_GESTATION,
    HEAD_CIRCUMFERENCE,
    HEIGHT,
    MALE,
    TWENTY_THREE_WEEKS_GESTATION,
    TRISOMY_21,
    TRISOMY_21_AAP,
    TURNERS,
    UK_WHO,
    WEIGHT,
    WHO,
)
from rcpchgrowth.constants.reference_constants import WHO_2006_REFERENCE_UPPER_THRESHOLD
from rcpchgrowth.global_functions import measurement_from_sds, sds_for_measurement


@pytest.mark.parametrize(
    ("reference", "age", "method", "sex", "sds", "expected"),
    [
        pytest.param(TURNERS, 10, HEIGHT, FEMALE, 0, 119.45, id="turner-height"),
        pytest.param(TRISOMY_21, 0, HEIGHT, MALE, 0, 49.50236, id="trisomy-21-height"),
        pytest.param(
            TRISOMY_21_AAP,
            0,
            WEIGHT,
            MALE,
            0,
            3.177,
            id="trisomy-21-aap-weight",
        ),
        pytest.param(
            CDC,
            0,
            HEAD_CIRCUMFERENCE,
            FEMALE,
            0,
            34.7115617,
            id="cdc-infant-ofc",
        ),
        pytest.param(
            CDC,
            2,
            BMI,
            MALE,
            2.326347874,
            21.10122398,
            id="cdc-extended-bmi-p99",
        ),
    ],
)
def test_published_reference_vectors(reference, age, method, sex, sds, expected):
    """Values are literal LMS-table vectors from Lyon et al. (1985), Styles et al. (ADC 2002), Zemel et al. (Pediatrics 2015), and the CDC/NCHS tables. CDC sources: https://www.cdc.gov/growthcharts/cdc-data-files.htm and https://www.cdc.gov/growthcharts/extended-bmi-data-files.htm. The p99 value is independently evaluated from the age-24-month male LMS row and sigma using the published extended-BMI equation."""
    assert measurement_from_sds(reference, sds, method, sex, age) == pytest.approx(
        expected, abs=1e-4
    )
    assert sds_for_measurement(reference, age, method, expected, sex) == pytest.approx(
        sds, abs=1e-4
    )


@pytest.mark.parametrize(
    ("reference", "valid_age", "invalid_age", "method", "sex", "message"),
    [
        (UK_WHO, 20, math.nextafter(20, math.inf), HEIGHT, MALE, "above the age of 20 years"),
        (WHO, 19, math.nextafter(19, math.inf), HEIGHT, MALE, "above 19 years"),
        (CDC, 20, math.nextafter(20, math.inf), HEIGHT, MALE, "above the age of 20 years"),
        (TURNERS, 20, math.nextafter(20, math.inf), HEIGHT, FEMALE, "above 20 years"),
        (TRISOMY_21, 20, math.nextafter(20, math.inf), HEIGHT, MALE, "over the age of 20y"),
        (TRISOMY_21_AAP, 20, math.nextafter(20, math.inf), HEIGHT, MALE, "over the age of 20y"),
    ],
)
def test_every_reference_includes_its_upper_boundary_and_rejects_above_it(
    reference, valid_age, invalid_age, method, sex, message
):
    assert measurement_from_sds(reference, 0, method, sex, valid_age) is not None
    with pytest.raises(LookupError, match=message):
        measurement_from_sds(reference, 0, method, sex, invalid_age)


@pytest.mark.parametrize(
    ("reference", "valid_age", "invalid_age", "method", "sex", "message"),
    [
        (UK_WHO, TWENTY_THREE_WEEKS_GESTATION, math.nextafter(TWENTY_THREE_WEEKS_GESTATION, -math.inf), WEIGHT, MALE, "below 23 weeks gestation"),
        (WHO, 0, math.nextafter(0, -math.inf), HEIGHT, MALE, "below term"),
        (CDC, 0, math.nextafter(0, -math.inf), HEIGHT, MALE, "below 40 weeks"),
        (TURNERS, 1, math.nextafter(1, -math.inf), HEIGHT, FEMALE, "below 1 year"),
        (TRISOMY_21, 0, math.nextafter(0, -math.inf), HEIGHT, MALE, "below 40 weeks"),
        (TRISOMY_21_AAP, 0, math.nextafter(0, -math.inf), WEIGHT, MALE, "below 40 weeks"),
    ],
)
def test_every_reference_includes_its_lower_boundary_and_rejects_below_it(
    reference, valid_age, invalid_age, method, sex, message
):
    assert measurement_from_sds(reference, 0, method, sex, valid_age) is not None
    with pytest.raises(LookupError, match=message):
        measurement_from_sds(reference, 0, method, sex, invalid_age)


@pytest.mark.parametrize(
    ("reference", "valid_age", "invalid_age", "method", "sex", "message"),
    [
        (
            UK_WHO,
            FORTY_TWO_WEEKS_GESTATION,
            FORTY_TWO_WEEKS_GESTATION - 0.0001,
            BMI,
            MALE,
            "below 2 weeks",
        ),
        (UK_WHO, 17, 17.0001, HEAD_CIRCUMFERENCE, FEMALE, "girls over 17"),
        (WHO, 10, 10.0001, WEIGHT, MALE, "weight data"),
        (
            WHO,
            WHO_2006_REFERENCE_UPPER_THRESHOLD,
            WHO_2006_REFERENCE_UPPER_THRESHOLD + 0.0001,
            HEAD_CIRCUMFERENCE,
            MALE,
            "head circumference",
        ),
        (CDC, 2, 1.9999, BMI, MALE, "BMI below 2 years"),
        (CDC, 3, 3.0001, HEAD_CIRCUMFERENCE, MALE, "head circumference above 3 years"),
        (TRISOMY_21, 18.82, 18.8201, BMI, MALE, "BMI reference data"),
        (TRISOMY_21, 18, 18.0001, HEAD_CIRCUMFERENCE, MALE, "head circumference"),
        (TRISOMY_21_AAP, 0.083333333, 0.0829, HEIGHT, MALE, "below 1 month"),
        (TRISOMY_21_AAP, 2, 1.9999, BMI, MALE, "below 2 years"),
    ],
)
def test_measurement_specific_boundaries(
    reference, valid_age, invalid_age, method, sex, message
):
    assert measurement_from_sds(reference, 0, method, sex, valid_age) is not None
    with pytest.raises(LookupError, match=message):
        measurement_from_sds(reference, 0, method, sex, invalid_age)


@pytest.mark.parametrize(
    ("method", "sex", "message"),
    [
        (WEIGHT, FEMALE, "no reference data for weight"),
        (HEIGHT, MALE, "only affects girls"),
    ],
)
def test_turner_rejects_unsupported_measurements_and_sex(method, sex, message):
    with pytest.raises(LookupError, match=message):
        measurement_from_sds(TURNERS, 0, method, sex, 10)


def test_aap_one_month_cutoff_matches_first_height_lms_row():
    invalid, _ = trisomy_21_aap.reference_data_absent(0.083, HEIGHT, MALE)
    assert invalid is True
    with pytest.raises(LookupError, match="below 1 month"):
        measurement_from_sds(TRISOMY_21_AAP, 0, HEIGHT, MALE, 0.083)


def test_uk_who_exact_handover_ownership():
    assert uk_who.uk_who_reference(FORTY_TWO_WEEKS_GESTATION) is uk_who.WHO_INFANTS_DATA
    assert (
        uk_who.uk_who_reference(FORTY_TWO_WEEKS_GESTATION, True)
        is uk_who.UK90_PRETERM_DATA
    )
    assert uk_who.uk_who_reference(2) is uk_who.WHO_CHILD_DATA
    assert uk_who.uk_who_reference(2, True) is uk_who.WHO_INFANTS_DATA
    assert uk_who.uk_who_reference(4) is uk_who.UK90_CHILD_DATA
    assert uk_who.uk_who_reference(4, True) is uk_who.WHO_CHILD_DATA


def test_who_exact_handover_ownership():
    assert who.who_reference(2) is who.WHO_CHILD_DATA
    assert who.who_reference(2, True) is who.WHO_INFANTS_DATA
    assert who.who_reference(WHO_2006_REFERENCE_UPPER_THRESHOLD) is who.WHO_CHILD_DATA
    assert (
        who.who_reference(WHO_2006_REFERENCE_UPPER_THRESHOLD + 0.0001)
        is who.WHO_2007_DATA
    )


def test_cdc_exact_handover_and_ofc_ownership():
    assert cdc.cdc_reference(2, HEIGHT) is cdc.CDC_CHILD_DATA
    assert cdc.cdc_reference(2, HEIGHT, True) is cdc.WHO_INFANTS_DATA
    assert cdc.cdc_reference(3, HEAD_CIRCUMFERENCE) is cdc.CDC_INFANT_DATA
    assert cdc.cdc_reference(3.0001, HEIGHT) is cdc.CDC_CHILD_DATA


def test_aap_age_three_overlap_is_measurement_specific():
    """At age three AAP height/weight stay infant-owned, OFC can select either table, and BMI is child-only."""
    select = trisomy_21_aap.trisomy_21_aap_lms_array_for_measurement_and_sex
    infant = trisomy_21_aap.TRISOMY_21_AAP_INFANT_DATA["measurement"]
    child = trisomy_21_aap.TRISOMY_21_AAP_CHILD_DATA["measurement"]
    assert select(HEIGHT, MALE, 3) is infant[HEIGHT][MALE]
    assert select(HEAD_CIRCUMFERENCE, MALE, 3) is child[HEAD_CIRCUMFERENCE][MALE]
    assert select(HEAD_CIRCUMFERENCE, MALE, 3, True) is infant[HEAD_CIRCUMFERENCE][MALE]
    assert select(BMI, MALE, 3) is child[BMI][MALE]
