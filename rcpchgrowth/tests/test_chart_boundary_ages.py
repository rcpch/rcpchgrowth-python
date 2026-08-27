"""Regression tests for valid gestational boundary points in UK-WHO charts."""

import pytest

from rcpchgrowth.chart_functions import create_chart
from rcpchgrowth.constants import (
    BMI,
    FORTY_TWO_WEEKS_GESTATION,
    HEAD_CIRCUMFERENCE,
    HEIGHT,
    TWENTY_FIVE_WEEKS_GESTATION,
    TWENTY_THREE_WEEKS_GESTATION,
    UK90_PRETERM,
    UK_WHO,
    UK_WHO_INFANT,
    WEIGHT,
)


@pytest.mark.parametrize(
    ("measurement_method", "component", "expected_first_age"),
    [
        (WEIGHT, UK90_PRETERM, TWENTY_THREE_WEEKS_GESTATION),
        (HEAD_CIRCUMFERENCE, UK90_PRETERM, TWENTY_THREE_WEEKS_GESTATION),
        (HEIGHT, UK90_PRETERM, TWENTY_FIVE_WEEKS_GESTATION),
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
