"""Semantic contract tests for the complete ``Measurement.measurement`` result."""

from datetime import date
from numbers import Real

import pytest

from rcpchgrowth import Measurement

TOP_LEVEL_KEYS = {
    "birth_data",
    "bone_age",
    "child_observation_value",
    "events_data",
    "measurement_calculated_values",
    "measurement_dates",
    "plottable_data",
    "provenance",
}
BIRTH_DATA_KEYS = {
    "birth_date",
    "estimated_date_delivery",
    "estimated_date_delivery_string",
    "gestation_days",
    "gestation_weeks",
    "sex",
}
MEASUREMENT_DATE_KEYS = {
    "observation_date",
    "chronological_decimal_age",
    "corrected_decimal_age",
    "chronological_calendar_age",
    "corrected_calendar_age",
    "corrected_gestational_age",
    "comments",
    "corrected_decimal_age_error",
    "chronological_decimal_age_error",
}
COMMENT_KEYS = {
    "clinician_corrected_decimal_age_comment",
    "lay_corrected_decimal_age_comment",
    "clinician_chronological_decimal_age_comment",
    "lay_chronological_decimal_age_comment",
}
CALCULATED_VALUE_KEYS = {
    "corrected_sds",
    "corrected_centile",
    "corrected_centile_band",
    "chronological_sds",
    "chronological_centile",
    "chronological_centile_band",
    "corrected_measurement_error",
    "chronological_measurement_error",
    "corrected_percentage_median_bmi",
    "chronological_percentage_median_bmi",
}
BONE_AGE_KEYS = {
    "bone_age",
    "bone_age_type",
    "bone_age_sds",
    "bone_age_centile",
    "bone_age_text",
}
CENTILE_POINT_KEYS = {
    "x",
    "y",
    "b",
    "centile",
    "sds",
    "events_text",
    "bone_age_label",
    "bone_age_type",
    "bone_age_sds",
    "bone_age_centile",
    "observation_error",
    "age_type",
    "calendar_age",
    "lay_comment",
    "clinician_comment",
    "age_error",
    "centile_band",
    "observation_value_error",
}
SDS_POINT_KEYS = CENTILE_POINT_KEYS - {"sds", "observation_error"}


def make_measurement(**overrides):
    values = {
        "birth_date": date(2020, 1, 1),
        "observation_date": date(2021, 1, 1),
        "measurement_method": "height",
        "observation_value": 75.0,
        "reference": "uk-who",
        "sex": "female",
    }
    values.update(overrides)
    return Measurement(**values).measurement


def assert_complete_measurement_shape(measurement):
    assert set(measurement) == TOP_LEVEL_KEYS
    assert set(measurement["provenance"]) == {
        "growth_reference",
        "calculation_engine",
    }
    assert set(measurement["provenance"]["calculation_engine"]) == {
        "name",
        "version",
        "commit",
    }
    assert set(measurement["birth_data"]) == BIRTH_DATA_KEYS
    assert set(measurement["measurement_dates"]) == MEASUREMENT_DATE_KEYS
    assert set(measurement["measurement_dates"]["corrected_gestational_age"]) == {
        "corrected_gestation_weeks",
        "corrected_gestation_days",
    }
    assert set(measurement["measurement_dates"]["comments"]) == COMMENT_KEYS
    assert set(measurement["child_observation_value"]) == {
        "measurement_method",
        "observation_value",
        "observation_value_error",
    }
    assert set(measurement["measurement_calculated_values"]) == CALCULATED_VALUE_KEYS
    assert set(measurement["plottable_data"]) == {"centile_data", "sds_data"}
    assert set(measurement["bone_age"]) == BONE_AGE_KEYS
    assert set(measurement["events_data"]) == {"events_text"}

    for data_kind, point_keys in (
        ("centile_data", CENTILE_POINT_KEYS),
        ("sds_data", SDS_POINT_KEYS),
    ):
        plot_data = measurement["plottable_data"][data_kind]
        assert set(plot_data) == {
            "chronological_decimal_age_data",
            "corrected_decimal_age_data",
        }
        assert set(plot_data["chronological_decimal_age_data"]) == point_keys
        assert set(plot_data["corrected_decimal_age_data"]) == point_keys | {
            "corrected_gestational_age"
        }


def test_successful_measurement_has_complete_typed_structure_and_values():
    measurement = make_measurement(
        events_text=["Growth review"],
        bone_age=1.2,
        bone_age_type="greulich-pyle",
        bone_age_sds=0.3,
        bone_age_centile=61.8,
        bone_age_text="Concordant bone age",
    )

    assert_complete_measurement_shape(measurement)
    assert measurement["provenance"]["growth_reference"] == "uk-who"
    assert (
        measurement["provenance"]["calculation_engine"]["name"]
        == "rcpch/rcpchgrowth-python"
    )
    assert all(
        isinstance(measurement["provenance"]["calculation_engine"][key], str)
        and measurement["provenance"]["calculation_engine"][key]
        for key in ("version", "commit")
    )
    assert measurement["birth_data"] == {
        "birth_date": date(2020, 1, 1),
        "gestation_weeks": 40,
        "gestation_days": 0,
        "estimated_date_delivery": date(2020, 1, 1),
        "estimated_date_delivery_string": "Wed 01 January, 2020",
        "sex": "female",
    }
    dates = measurement["measurement_dates"]
    assert isinstance(dates["chronological_decimal_age"], float)
    assert dates["chronological_decimal_age"] == pytest.approx(1.0020533881)
    assert dates["corrected_decimal_age"] == dates["chronological_decimal_age"]
    assert dates["corrected_decimal_age_error"] is None
    assert dates["chronological_decimal_age_error"] is None

    calculated = measurement["measurement_calculated_values"]
    assert calculated["corrected_sds"] == pytest.approx(0.3706868165)
    assert calculated["chronological_sds"] == pytest.approx(0.3706868165)
    assert calculated["corrected_centile"] == pytest.approx(64.4564594609)
    assert calculated["chronological_centile"] == pytest.approx(64.4564594609)
    assert all(
        isinstance(calculated[key], Real)
        for key in (
            "corrected_sds",
            "chronological_sds",
            "corrected_centile",
            "chronological_centile",
        )
    )
    assert calculated["corrected_measurement_error"] is None
    assert calculated["chronological_measurement_error"] is None
    assert calculated["corrected_percentage_median_bmi"] is None
    assert calculated["chronological_percentage_median_bmi"] is None
    assert measurement["bone_age"] == {
        "bone_age": 1.2,
        "bone_age_type": "greulich-pyle",
        "bone_age_sds": 0.3,
        "bone_age_centile": 61.8,
        "bone_age_text": "Concordant bone age",
    }
    assert measurement["events_data"] == {"events_text": ["Growth review"]}

    centile_data = measurement["plottable_data"]["centile_data"]
    sds_data = measurement["plottable_data"]["sds_data"]
    for age_type, expected_age_type in (
        ("chronological_decimal_age_data", "chronological_age"),
        ("corrected_decimal_age_data", "corrected_age"),
    ):
        assert centile_data[age_type]["age_type"] == expected_age_type
        assert centile_data[age_type]["y"] == 75.0
        assert centile_data[age_type]["b"] == 1.2
        assert centile_data[age_type]["events_text"] == ["Growth review"]
        assert sds_data[age_type]["y"] == pytest.approx(0.3706868165)


def test_preterm_measurement_distinguishes_corrected_and_chronological_results():
    measurement = make_measurement(
        observation_date=date(2020, 7, 1),
        measurement_method="weight",
        observation_value=6.5,
        sex="male",
        gestation_weeks=32,
        events_text=["review"],
    )

    assert_complete_measurement_shape(measurement)
    dates = measurement["measurement_dates"]
    assert dates["chronological_decimal_age"] == pytest.approx(0.4982888433)
    assert dates["corrected_decimal_age"] == pytest.approx(0.3449691992)
    assert dates["corrected_calendar_age"] == "4 months and 5 days"
    assert "32+0 weeks" in dates["comments"]["lay_corrected_decimal_age_comment"]

    calculated = measurement["measurement_calculated_values"]
    assert calculated["chronological_sds"] == pytest.approx(-1.7874654372)
    assert calculated["corrected_sds"] == pytest.approx(-0.7524570442)
    assert calculated["chronological_centile"] == pytest.approx(3.6931146757)
    assert calculated["corrected_centile"] == pytest.approx(22.5888126476)
    assert measurement["events_data"]["events_text"] == ["review"]


def test_out_of_range_measurement_retains_shape_and_reports_both_age_errors():
    measurement = make_measurement(
        birth_date=date(2000, 1, 1),
        observation_date=date(2025, 1, 1),
        observation_value=170.0,
    )

    assert_complete_measurement_shape(measurement)
    expected_error = "There is no UK90 reference data above the age of 20 years."
    assert (
        measurement["child_observation_value"]["observation_value_error"]
        == expected_error
    )
    calculated = measurement["measurement_calculated_values"]
    assert calculated["corrected_measurement_error"] == expected_error
    assert calculated["chronological_measurement_error"] == expected_error
    assert all(
        calculated[key] is None
        for key in (
            "corrected_sds",
            "corrected_centile",
            "corrected_centile_band",
            "chronological_sds",
            "chronological_centile",
            "chronological_centile_band",
        )
    )
    centile_data = measurement["plottable_data"]["centile_data"]
    assert (
        centile_data["corrected_decimal_age_data"]["observation_error"]
        == expected_error
    )
    assert (
        centile_data["chronological_decimal_age_data"]["observation_error"]
        == expected_error
    )


def test_invalid_observation_is_flagged_but_current_calculations_are_retained():
    measurement = make_measurement(observation_value=1.0)

    assert_complete_measurement_shape(measurement)
    expected_error = "Height/length must be passed in cm, not metres"
    assert (
        measurement["child_observation_value"]["observation_value_error"]
        == expected_error
    )
    calculated = measurement["measurement_calculated_values"]
    assert calculated["corrected_sds"] == pytest.approx(-28.3556975398)
    assert calculated["chronological_sds"] == pytest.approx(-28.3556975398)
    assert calculated["corrected_measurement_error"] is None
    assert calculated["chronological_measurement_error"] is None
    centile_data = measurement["plottable_data"]["centile_data"]
    assert (
        centile_data["corrected_decimal_age_data"]["observation_error"]
        == expected_error
    )
    assert (
        centile_data["chronological_decimal_age_data"]["observation_error"]
        == expected_error
    )


def test_invalid_dates_retain_complete_shape_and_suppress_calculations():
    measurement = make_measurement(
        observation_date=date(2019, 1, 1), observation_value=50.0
    )

    assert_complete_measurement_shape(measurement)
    dates = measurement["measurement_dates"]
    assert dates["corrected_decimal_age"] is None
    assert dates["corrected_decimal_age_error"] == (
        "Birth date cannot be after the date of observation."
    )
    calculated = measurement["measurement_calculated_values"]
    assert calculated["corrected_measurement_error"] == (
        "Dates error. Calculations impossible."
    )
    assert calculated["chronological_measurement_error"] == (
        "Dates error. Calculations impossible."
    )
    assert calculated["corrected_sds"] is None
    assert calculated["chronological_sds"] is None
