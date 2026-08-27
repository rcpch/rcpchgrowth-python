"""
Regression tests for an operator-precedence bug in the CDC/WHO gestational
correction guard in `Measurement.__calculate_ages()`.

Bug found by inspection, confirmed interactively:

    if self.reference == CDC or self.reference == WHO and self.corrected_decimal_age is not None:
        if (self.corrected_decimal_age >= 2 and gestation_weeks < 37) or ...

`and` binds tighter than `or`, so this parses as:

    self.reference == CDC or (self.reference == WHO and self.corrected_decimal_age is not None)

The `is not None` guard is therefore only ever applied on the WHO branch.
For `reference == CDC`, the block is entered unconditionally, regardless of
whether `self.corrected_decimal_age` is `None`.

The comment directly above the line ("if reference is CDC or WHO, we must
treat >37 week infants as term...") describes behaviour intended to apply
identically to both references, so this is a missing-parentheses defect,
not a deliberate asymmetry.

Confirmed reachable: constructing a CDC-reference `Measurement` where
`corrected_decimal_age()` internally raises (the one documented case is an
observation date before the birth date) leaves `self.corrected_decimal_age`
as `None` via the surrounding try/except - see measurement.py's
`__calculate_ages()`. The buggy guard then still enters the block for CDC,
and the inner `None >= 2` comparison raises an **unhandled TypeError** that
propagates straight out of the `Measurement()` constructor, because the
call site (`__init__`) does not wrap `__calculate_ages()` in a try/except.

By contrast, the same invalid input under `uk-who` (a reference unaffected
by this block entirely) and under `who` (correctly guarded by the `and`)
both degrade gracefully: `corrected_decimal_age` is set to `None` and a
human-readable `corrected_decimal_age_error` string is returned instead.
CDC should behave the same way.
"""

from datetime import date

import pytest

from rcpchgrowth import Measurement

# An observation date before the birth date is the one documented trigger
# for corrected_decimal_age() to raise internally, per its own docstring
# and the "Birth date cannot be after the date of observation." message.
BIRTH_DATE = date(2020, 1, 1)
OBSERVATION_DATE_BEFORE_BIRTH = date(2019, 1, 1)


@pytest.mark.parametrize("reference", ["uk-who", "who", "cdc"])
def test_measurement_does_not_crash_when_corrected_age_calculation_fails(reference):
    # This must never raise. Every reference should degrade gracefully to
    # corrected_decimal_age=None with a descriptive error, exactly as
    # uk-who and who already do.
    measurement = Measurement(
        birth_date=BIRTH_DATE,
        observation_date=OBSERVATION_DATE_BEFORE_BIRTH,
        measurement_method="height",
        observation_value=50.0,
        reference=reference,
        sex="male",
    ).measurement

    dates = measurement["measurement_dates"]
    assert dates["corrected_decimal_age"] is None
    assert dates["corrected_decimal_age_error"] is not None
    assert "cannot be after" in dates["corrected_decimal_age_error"]


def test_cdc_and_who_behave_identically_for_the_same_invalid_input():
    # Belt-and-braces: the two references sharing this correction block
    # must produce the same graceful outcome for the same bad input,
    # since the guard is meant to treat them identically.
    common = dict(
        birth_date=BIRTH_DATE,
        observation_date=OBSERVATION_DATE_BEFORE_BIRTH,
        measurement_method="height",
        observation_value=50.0,
        sex="male",
    )
    cdc_result = Measurement(reference="cdc", **common).measurement
    who_result = Measurement(reference="who", **common).measurement

    assert (
        cdc_result["measurement_dates"]["corrected_decimal_age"]
        == who_result["measurement_dates"]["corrected_decimal_age"]
        == None
    )
