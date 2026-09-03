"""Direct characterization of dynamic chart output for every public reference."""

import pytest

from rcpchgrowth.chart_functions import create_chart
from rcpchgrowth.constants import (
    BMI,
    CDC,
    FEMALE,
    HEIGHT,
    MALE,
    REFERENCES,
    TRISOMY_21,
    TRISOMY_21_AAP,
    TURNERS,
    UK_WHO,
    WHO,
)

CHART_CASES = [
    pytest.param(
        UK_WHO,
        HEIGHT,
        MALE,
        [
            # The nominal 25-week grid value is fractionally below the exact
            # validation threshold, so the first emitted height point is 26 weeks.
            ("uk90_preterm", -0.2683, 0.0383),
            ("uk_who_infant", 0.0383, 2),
            ("uk_who_child", 2, 4),
            ("uk90_child", 4, 20),
        ],
        id="uk-who",
    ),
    pytest.param(
        WHO,
        HEIGHT,
        MALE,
        [
            ("who_2006_infant", 0.0383, 2),
            ("who_2006_child", 2, 5),
            ("who_2007_child", 5, 19),
        ],
        id="who",
    ),
    pytest.param(
        CDC,
        BMI,
        MALE,
        [
            ("fenton", None, None),
            ("cdc_infant", None, None),
            ("cdc_child", 2, 20),
        ],
        id="cdc-bmi",
    ),
    pytest.param(
        TURNERS,
        HEIGHT,
        FEMALE,
        [(TURNERS, 1, 20)],
        id="turner",
    ),
    pytest.param(
        TRISOMY_21,
        HEIGHT,
        MALE,
        [(TRISOMY_21, 0, 20)],
        id="trisomy-21",
    ),
    pytest.param(
        TRISOMY_21_AAP,
        HEIGHT,
        MALE,
        [
            ("trisomy_21_aap_infant", 0.0833, 3),
            ("trisomy_21_aap_child", 3, 20),
        ],
        id="trisomy-21-aap",
    ),
]


def test_every_public_reference_has_a_dynamic_chart_contract():
    assert {case.values[0] for case in CHART_CASES} == set(REFERENCES)


@pytest.mark.parametrize(("reference", "method", "sex", "components"), CHART_CASES)
def test_chart_structure_series_and_age_domains(reference, method, sex, components):
    chart = create_chart(reference, [50], method, sex)

    assert [next(iter(component)) for component in chart] == [
        name for name, _, _ in components
    ]
    for component, (name, first_age, last_age) in zip(
        chart, components, strict=True
    ):
        series = component[name][sex]
        assert list(series) == [method]
        assert len(series[method]) == 1
        centile = series[method][0]
        assert centile["sds"] == 0
        assert centile["centile"] == 50

        points = centile["data"]
        if first_age is None:
            # Fenton is unavailable and CDC has no infant BMI table. The builder
            # intentionally preserves both component slots as empty series.
            assert points == []
            continue

        assert points[0]["x"] == first_age
        assert points[-1]["x"] == last_age
        assert all(set(point) == {"l", "x", "y"} for point in points)
        assert all(point["l"] == 50 for point in points)
        assert all(point["y"] is not None for point in points)


@pytest.mark.parametrize(
    ("reference", "method", "sex", "component", "age", "expected"),
    [
        pytest.param(UK_WHO, HEIGHT, MALE, "uk90_child", 4, 102.49, id="uk-who"),
        # Age two is clamped to the infant table's authoritative day-730 row.
        pytest.param(WHO, HEIGHT, MALE, "who_2006_infant", 2, 87.8018, id="who"),
        pytest.param(TURNERS, HEIGHT, FEMALE, TURNERS, 10, 119.45, id="turner"),
        pytest.param(
            TRISOMY_21,
            HEIGHT,
            MALE,
            TRISOMY_21,
            0,
            49.50236,
            id="trisomy-21",
        ),
        pytest.param(
            TRISOMY_21_AAP,
            HEIGHT,
            MALE,
            "trisomy_21_aap_infant",
            0.0833,
            52.632,
            id="trisomy-21-aap-infant",
        ),
        pytest.param(
            TRISOMY_21_AAP,
            HEIGHT,
            MALE,
            "trisomy_21_aap_child",
            3,
            87.222,
            id="trisomy-21-aap-child",
        ),
        pytest.param(CDC, BMI, MALE, "cdc_child", 2, 16.57502768, id="cdc"),
    ],
)
def test_chart_representative_source_table_coordinates(
    reference, method, sex, component, age, expected
):
    """Median coordinates are literal rows from the UK90, WHO, Lyon 1985, Styles 2002, Zemel 2015, and CDC LMS source tables."""
    chart = create_chart(reference, [50], method, sex)
    points = next(item[component] for item in chart if component in item)[sex][method][
        0
    ]["data"]
    point = next(point for point in points if point["x"] == age)
    assert point["y"] == pytest.approx(expected, abs=1e-4)


def test_aap_chart_includes_both_age_three_height_coordinates():
    """Both AAP component slots plot age three through the infant-owned calculation path; the source tables happen to have the same median there."""
    chart = create_chart(TRISOMY_21_AAP, [50], HEIGHT, MALE)
    infant = chart[0]["trisomy_21_aap_infant"][MALE][HEIGHT][0]["data"]
    child = chart[1]["trisomy_21_aap_child"][MALE][HEIGHT][0]["data"]
    assert infant[-1]["x"] == child[0]["x"] == 3
    assert infant[-1]["y"] == child[0]["y"] == pytest.approx(87.222)
