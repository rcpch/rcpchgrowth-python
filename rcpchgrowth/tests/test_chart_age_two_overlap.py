"""Tests for both sides of the two-year WHO chart overlap."""

import pytest

from rcpchgrowth.chart_functions import create_chart
from rcpchgrowth.constants import (
    BMI,
    HEAD_CIRCUMFERENCE,
    HEIGHT,
    UK_WHO,
    UK_WHO_CHILD,
    UK_WHO_INFANT,
    WEIGHT,
    WHO,
    WHO_2006_CHILD,
    WHO_2006_INFANT,
)
from rcpchgrowth.global_functions import (
    measurement_from_sds,
    percentage_median_bmi,
    sds_for_measurement,
)


@pytest.mark.parametrize(
    ("reference", "younger_component", "older_component"),
    [
        (UK_WHO, UK_WHO_INFANT, UK_WHO_CHILD),
        (WHO, WHO_2006_INFANT, WHO_2006_CHILD),
    ],
)
@pytest.mark.parametrize("sex", ["female", "male"])
@pytest.mark.parametrize("measurement_method", [HEIGHT, WEIGHT, HEAD_CIRCUMFERENCE, BMI])
def test_both_who_chart_components_include_age_two(
    reference,
    younger_component,
    older_component,
    sex,
    measurement_method,
):
    chart = create_chart(
        reference=reference,
        measurement_method=measurement_method,
        sex=sex,
    )
    younger_data = next(
        item[younger_component] for item in chart if younger_component in item
    )[sex][measurement_method][0]["data"]
    older_data = next(
        item[older_component] for item in chart if older_component in item
    )[sex][measurement_method][0]["data"]

    assert younger_data[-1]["x"] == 2
    assert younger_data[-1]["y"] is not None
    assert older_data[0]["x"] == 2
    assert older_data[0]["y"] is not None


@pytest.mark.parametrize("reference", [UK_WHO, WHO])
@pytest.mark.parametrize("sex", ["female", "male"])
@pytest.mark.parametrize("measurement_method", [HEIGHT, WEIGHT, HEAD_CIRCUMFERENCE, BMI])
def test_age_two_measurement_calculation_defaults_to_older_reference(
    reference,
    sex,
    measurement_method,
):
    median = measurement_from_sds(
        reference=reference,
        requested_sds=0,
        measurement_method=measurement_method,
        sex=sex,
        age=2,
    )

    assert median is not None
    assert sds_for_measurement(
        reference=reference,
        age=2,
        measurement_method=measurement_method,
        observation_value=median,
        sex=sex,
    ) == pytest.approx(0, abs=1e-4)


@pytest.mark.parametrize("reference", [UK_WHO, WHO])
@pytest.mark.parametrize("sex", ["female", "male"])
def test_age_two_percentage_median_bmi_uses_older_reference(reference, sex):
    median = measurement_from_sds(
        reference=reference,
        requested_sds=0,
        measurement_method=BMI,
        sex=sex,
        age=2,
    )

    assert percentage_median_bmi(
        reference=reference,
        age=2,
        actual_bmi=median,
        sex=sex,
    ) == pytest.approx(100, abs=1e-3)


@pytest.mark.parametrize("reference", [UK_WHO, WHO])
@pytest.mark.parametrize("sex", ["female", "male"])
def test_age_two_length_exceeds_standing_height(reference, sex):
    length = measurement_from_sds(
        reference=reference,
        requested_sds=0,
        measurement_method=HEIGHT,
        sex=sex,
        age=2,
        default_youngest_reference=True,
    )
    height = measurement_from_sds(
        reference=reference,
        requested_sds=0,
        measurement_method=HEIGHT,
        sex=sex,
        age=2,
    )

    assert length > height
