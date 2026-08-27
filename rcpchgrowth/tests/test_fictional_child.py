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
# drift so the output is fully deterministic. `measurement_interval_type` and
# `measurement_interval_number` are intentionally omitted so individual tests
# can override them without colliding with **COMMON_KWARGS.
COMMON_KWARGS = dict(
    measurement_method="height",
    sex="male",
    gestation_weeks=40,
    gestation_days=0,
    start_sds=0,
    drift=False,
    noise=False,
)

# Default measurement interval used by the equivalence tests: 6 months.
DEFAULT_INTERVAL = dict(
    measurement_interval_type="months",
    measurement_interval_number=6,
)


# ---------------------------------------------------------------------------
# Equivalence: supplying interval units == supplying pre-converted years
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "interval_type, raw_value, factor",
    [
        ("days", 730, DAYS_PER_YEAR),     # ~2 years
        ("d", 730, DAYS_PER_YEAR),
        ("day", 730, DAYS_PER_YEAR),
        ("weeks", 104, WEEKS_PER_YEAR),    # 2 years
        ("w", 104, WEEKS_PER_YEAR),
        ("week", 104, WEEKS_PER_YEAR),
        ("months", 24, MONTHS_PER_YEAR),   # 2 years
        ("m", 24, MONTHS_PER_YEAR),
        ("month", 24, MONTHS_PER_YEAR),
        ("years", 2, 1),
        ("y", 2, 1),
        ("year", 2, 1),
    ],
)
def test_start_age_interval_type_matches_manual_conversion(interval_type, raw_value, factor):
    """
    `start_chronological_age_interval_type` should produce identical output
    to passing the equivalent decimal-year value as `start_chronological_age`.
    """
    expected_start_years = raw_value / factor

    with_units = generate_fictional_child_data(
        **COMMON_KWARGS,
        **DEFAULT_INTERVAL,
        start_chronological_age=raw_value,
        start_chronological_age_interval_type=interval_type,
        end_age=4,
        end_age_interval_type="years",
    )
    with_years = generate_fictional_child_data(
        **COMMON_KWARGS,
        **DEFAULT_INTERVAL,
        start_chronological_age=expected_start_years,
        start_chronological_age_interval_type="years",
        end_age=4,
        end_age_interval_type="years",
    )

    assert _signatures(with_units) == _signatures(with_years)


@pytest.mark.parametrize(
    "interval_type, raw_value, factor",
    [
        ("days", 1461, DAYS_PER_YEAR),    # ~4 years
        ("d", 1461, DAYS_PER_YEAR),
        ("day", 1461, DAYS_PER_YEAR),
        ("weeks", 208, WEEKS_PER_YEAR),   # 4 years
        ("w", 208, WEEKS_PER_YEAR),
        ("week", 208, WEEKS_PER_YEAR),
        ("months", 48, MONTHS_PER_YEAR),   # 4 years
        ("m", 48, MONTHS_PER_YEAR),
        ("month", 48, MONTHS_PER_YEAR),
        ("years", 4, 1),
        ("y", 4, 1),
        ("year", 4, 1),
    ],
)
def test_end_age_interval_type_matches_manual_conversion(interval_type, raw_value, factor):
    """
    `end_age_interval_type` should produce identical output to passing the
    equivalent decimal-year value as `end_age`.
    """
    expected_end_years = raw_value / factor

    with_units = generate_fictional_child_data(
        **COMMON_KWARGS,
        **DEFAULT_INTERVAL,
        start_chronological_age=0,
        start_chronological_age_interval_type="years",
        end_age=raw_value,
        end_age_interval_type=interval_type,
    )
    with_years = generate_fictional_child_data(
        **COMMON_KWARGS,
        **DEFAULT_INTERVAL,
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
        **DEFAULT_INTERVAL,
        start_chronological_age=start_days,
        start_chronological_age_interval_type="days",
        end_age=end_months,
        end_age_interval_type="months",
    )
    with_years = generate_fictional_child_data(
        **COMMON_KWARGS,
        **DEFAULT_INTERVAL,
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
        **DEFAULT_INTERVAL,
        start_chronological_age=1.0,
        end_age=3.0,
    )
    explicit = generate_fictional_child_data(
        **COMMON_KWARGS,
        **DEFAULT_INTERVAL,
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
            **DEFAULT_INTERVAL,
            start_chronological_age=1,
            start_chronological_age_interval_type="fortnights",
        )


def test_invalid_end_interval_type_raises():
    with pytest.raises(ValueError):
        generate_fictional_child_data(
            **COMMON_KWARGS,
            **DEFAULT_INTERVAL,
            end_age=2,
            end_age_interval_type="fortnights",
        )


# ---------------------------------------------------------------------------
# Range validation
# ---------------------------------------------------------------------------

def test_start_age_greater_than_end_age_raises():
    with pytest.raises(ValueError, match="end_age .* must be greater than"):
        generate_fictional_child_data(
            **COMMON_KWARGS,
            **DEFAULT_INTERVAL,
            start_chronological_age=3,
            start_chronological_age_interval_type="years",
            end_age=1,
            end_age_interval_type="years",
        )


def test_start_age_equal_to_end_age_raises():
    with pytest.raises(ValueError, match="end_age .* must be greater than"):
        generate_fictional_child_data(
            **COMMON_KWARGS,
            **DEFAULT_INTERVAL,
            start_chronological_age=2,
            start_chronological_age_interval_type="years",
            end_age=2,
            end_age_interval_type="years",
        )


def test_range_smaller_than_measurement_interval_raises():
    # 1-month span, 6-month interval -> no measurements possible
    with pytest.raises(ValueError, match="smaller than the measurement interval"):
        generate_fictional_child_data(
            **COMMON_KWARGS,
            start_chronological_age=0,
            start_chronological_age_interval_type="years",
            end_age=1,
            end_age_interval_type="months",
            measurement_interval_type="months",
            measurement_interval_number=6,
        )


def test_non_positive_measurement_interval_number_raises():
    with pytest.raises(ValueError, match="measurement_interval_number must be a positive value"):
        generate_fictional_child_data(
            **COMMON_KWARGS,
            measurement_interval_type="months",
            measurement_interval_number=0,
        )
