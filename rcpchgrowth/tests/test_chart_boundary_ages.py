"""Regression tests for valid gestational boundary points in UK-WHO charts."""

from datetime import date

import pytest

from rcpchgrowth import Measurement
from rcpchgrowth.chart_functions import create_chart
from rcpchgrowth.constants import (
    BMI,
    FORTY_TWO_WEEKS_GESTATION,
    HEAD_CIRCUMFERENCE,
    HEIGHT,
    TWENTY_FIVE_WEEKS_GESTATION,
    TWENTY_THREE_WEEKS_GESTATION,
    TWENTY_TWO_WEEKS_GESTATION,
    UK90_CHILD,
    UK90_PRETERM,
    UK_WHO,
    UK_WHO_CHILD,
    UK_WHO_INFANT,
    WEIGHT,
)


@pytest.mark.parametrize(
    ("measurement_method", "component", "expected_first_age"),
    [
        (WEIGHT, UK90_PRETERM, TWENTY_THREE_WEEKS_GESTATION),
        (HEAD_CIRCUMFERENCE, UK90_PRETERM, TWENTY_THREE_WEEKS_GESTATION),
        (HEIGHT, UK90_PRETERM, TWENTY_FIVE_WEEKS_GESTATION),
        # UK90 has no preterm BMI values; this seam point is sourced from WHO.
        (BMI, UK_WHO_INFANT, FORTY_TWO_WEEKS_GESTATION),
    ],
)
def test_chart_includes_first_valid_gestational_boundary(
    measurement_method,
    component,
    expected_first_age,
):
    chart = create_chart(
        reference=UK_WHO,
        measurement_method=measurement_method,
        sex="female",
    )
    component_data = next(item[component] for item in chart if component in item)
    first_centile = component_data["female"][measurement_method][0]["data"]

    assert first_centile[0]["x"] == round(expected_first_age, 4)


@pytest.mark.parametrize("sex", ["female", "male"])
@pytest.mark.parametrize("measurement_method", [HEIGHT, WEIGHT, HEAD_CIRCUMFERENCE, BMI])
def test_both_uk_who_chart_components_include_age_four(measurement_method, sex):
    chart = create_chart(
        reference=UK_WHO,
        measurement_method=measurement_method,
        sex=sex,
    )
    younger_data = next(
        item[UK_WHO_CHILD] for item in chart if UK_WHO_CHILD in item
    )[sex][measurement_method][0]["data"]
    older_data = next(item[UK90_CHILD] for item in chart if UK90_CHILD in item)[
        sex
    ][measurement_method][0]["data"]

    assert younger_data[-1]["x"] == 4
    assert younger_data[-1]["y"] is not None
    assert older_data[0]["x"] == 4
    assert older_data[0]["y"] is not None


def test_observation_below_reference_floor_remains_plottable_without_sds():
    measurement = Measurement(
        birth_date=date(2026, 1, 1),
        observation_date=date(2026, 1, 1),
        measurement_method=WEIGHT,
        observation_value=0.5,
        reference=UK_WHO,
        sex="female",
        gestation_weeks=22,
    ).measurement
    point = measurement["plottable_data"]["centile_data"][
        "corrected_decimal_age_data"
    ]

    assert point["x"] == TWENTY_TWO_WEEKS_GESTATION
    assert point["y"] == 0.5
    assert point["sds"] is None
    assert point["centile"] is None
    assert point["observation_value_error"] == (
        "There is no UK90 reference data below 23 weeks gestation"
    )
