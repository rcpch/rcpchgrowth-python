"""
Tests for `generate_fictional_child_data`.

These tests cover the new `start_chronological_age_interval_type` and
`end_age_interval_type` parameters. The contract being verified is:

    Calling the function with a quantity expressed in a non-year unit
    (days / weeks / months) must produce the same output as calling the
    function with the equivalent decimal-year quantity (i.e. the unit
    conversion is performed internally and does not perturb the result).

Because `generate_fictional_child_data` is deterministic when `noise=False`
and `drift=False`, the two calls should produce byte-for-byte identical
measurement arrays.
"""

import pytest

from rcpchgrowth import generate_fictional_child_data


# Conversion factors mirroring the implementation in `fictional_child.py`.
DAYS_PER_YEAR = 365.25
WEEKS_PER_YEAR = 52
MONTHS_PER_YEAR = 12


def _measurement_signature(measurement):
    """
    Reduces a Measurement dict to the fields that depend on age / SDS.

    `generate_fictional_child_data` rounds the raw observation value and
    derives everything else from age and SDS, so this tuple is sufficient
    to detect any divergence between two calls.
    """
    dates = measurement["measurement_dates"]
    return (
        dates["chronological_decimal_age"],
        dates["corrected_decimal_age"],
        measurement["child_observation_value"]["observation_value"],
        measurement["measurement_calculated_values"]["chronological_sds"],
    )


def _signatures(measurements):
    return [_measurement_signature(m) for m in measurements]


# Common kwargs shared by every call below. We disable noise (random) and
# drift so the output is fully deterministic.
COMMON_KWARGS = dict(
    measurement_method="height",
    sex="male",
    gestation_weeks=40,
    gestation_days=0,
    measurement_interval_type="months",
    measurement_interval_number=6,
    start_sds=0,
    drift=False,
    noise=False,
)


# ---------------------------------------------------------------------------
# Equivalence: supplying interval units == supplying pre-converted years
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "interval_type, factor",
    [
        ("days", DAYS_PER_YEAR),
        ("d", DAYS_PER_YEAR),
        ("day", DAYS_PER_YEAR),
        ("weeks", WEEKS_PER_YEAR),
        ("w", WEEKS_PER_YEAR),
        ("week", WEEKS_PER_YEAR),
        ("months", MONTHS_PER_YEAR),
        ("m", MONTHS_PER_YEAR),
        ("month", MONTHS_PER_YEAR),
        ("years", 1),
        ("y", 1),
        ("year", 1),
    ],
)
def test_start_age_interval_type_matches_manual_conversion(interval_type, factor):
    """
    `start_chronological_age_interval_type` should produce identical output
    to passing the equivalent decimal-year value as `start_chronological_age`.
    """
    raw_start = 2  # 2 of whatever unit
    expected_start_years = raw_start / factor

    with_units = generate_fictional_child_data(
        **COMMON_KWARGS,
        start_chronological_age=raw_start,
        start_chronological_age_interval_type=interval_type,
        end_age=4,
        end_age_interval_type="years",
    )
    with_years = generate_fictional_child_data(
        **COMMON_KWARGS,
        start_chronological_age=expected_start_years,
        start_chronological_age_interval_type="years",
        end_age=4,
        end_age_interval_type="years",
    )

    assert _signatures(with_units) == _signatures(with_years)


@pytest.mark.parametrize(
    "interval_type, factor",
    [
        ("days", DAYS_PER_YEAR),
        ("d", DAYS_PER_YEAR),
        ("day", DAYS_PER_YEAR),
        ("weeks", WEEKS_PER_YEAR),
        ("w", WEEKS_PER_YEAR),
        ("week", WEEKS_PER_YEAR),
        ("months", MONTHS_PER_YEAR),
        ("m", MONTHS_PER_YEAR),
        ("month", MONTHS_PER_YEAR),
        ("years", 1),
        ("y", 1),
        ("year", 1),
    ],
)
def test_end_age_interval_type_matches_manual_conversion(interval_type, factor):
    """
    `end_age_interval_type` should produce identical output to passing the
    equivalent decimal-year value as `end_age`.
    """
    raw_end = 4  # 4 of whatever unit
    expected_end_years = raw_end / factor

    with_units = generate_fictional_child_data(
        **COMMON_KWARGS,
        start_chronological_age=0,
        start_chronological_age_interval_type="years",
        end_age=raw_end,
        end_age_interval_type=interval_type,
    )
    with_years = generate_fictional_child_data(
        **COMMON_KWARGS,
        start_chronological_age=0,
        start_chronological_age_interval_type="years",
        end_age=expected_end_years,
        end_age_interval_type="years",
    )

    assert _signatures(with_units) == _signatures(with_years)


def test_both_interval_types_combined():
    """
    When both start and end ages are supplied in non-year units, the result
    should still match the equivalent call with both expressed in years.
    """
    start_days = 365          # ~1 year
    end_months = 24           # 2 years

    with_units = generate_fictional_child_data(
        **COMMON_KWARGS,
        start_chronological_age=start_days,
        start_chronological_age_interval_type="days",
        end_age=end_months,
        end_age_interval_type="months",
    )
    with_years = generate_fictional_child_data(
        **COMMON_KWARGS,
        start_chronological_age=start_days / DAYS_PER_YEAR,
        start_chronological_age_interval_type="years",
        end_age=end_months / MONTHS_PER_YEAR,
        end_age_interval_type="years",
    )

    assert _signatures(with_units) == _signatures(with_years)


# ---------------------------------------------------------------------------
# Backward compatibility
# ---------------------------------------------------------------------------

def test_defaults_match_years():
    """
    Omitting the new parameters must behave identically to explicitly
    passing 'years' for both, preserving backward compatibility.
    """
    omitted = generate_fictional_child_data(
        **COMMON_KWARGS,
        start_chronological_age=1.0,
        end_age=3.0,
    )
    explicit = generate_fictional_child_data(
        **COMMON_KWARGS,
        start_chronological_age=1.0,
        start_chronological_age_interval_type="years",
        end_age=3.0,
        end_age_interval_type="years",
    )

    assert _signatures(omitted) == _signatures(explicit)


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

def test_invalid_start_interval_type_raises():
    with pytest.raises(ValueError):
        generate_fictional_child_data(
            **COMMON_KWARGS,
            start_chronological_age=1,
            start_chronological_age_interval_type="fortnights",
        )


def test_invalid_end_interval_type_raises():
    with pytest.raises(ValueError):
        generate_fictional_child_data(
            **COMMON_KWARGS,
            end_age=2,
            end_age_interval_type="fortnights",
        )
