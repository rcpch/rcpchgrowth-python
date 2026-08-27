"""Tests for ownership of the two-year WHO chart overlap."""

import pytest

from rcpchgrowth.chart_functions import create_chart
from rcpchgrowth.constants import (
    BMI,
    HEAD_CIRCUMFERENCE,
    HEIGHT,
    UK_WHO,
    UK_WHO_INFANT,
    WEIGHT,
    WHO,
    WHO_2006_INFANT,
)


@pytest.mark.parametrize(
    ("reference", "component"),
    [
        (UK_WHO, UK_WHO_INFANT),
        (WHO, WHO_2006_INFANT),
    ],
)
@pytest.mark.parametrize("sex", ["female", "male"])
@pytest.mark.parametrize("measurement_method", [HEIGHT, WEIGHT, HEAD_CIRCUMFERENCE, BMI])
def test_younger_who_chart_component_includes_age_two(
    reference,
    component,
    sex,
    measurement_method,
):
    chart = create_chart(
        reference=reference,
        measurement_method=measurement_method,
        sex=sex,
    )
    component_data = next(item[component] for item in chart if component in item)
    first_centile = component_data[sex][measurement_method][0]["data"]

    assert first_centile[-1]["x"] == 2
