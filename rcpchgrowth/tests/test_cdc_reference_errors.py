"""
Tests for `cdc_reference()`'s and `cdc_lms_array_for_measurement_and_sex()`'s
out-of-domain error handling.

Fixes GitHub issue #51 ("Returning Errors rather that raising them"), for
its CDC-module occurrences. The reporter's original complaint concerned the
UK-WHO module's identical anti-pattern (fixed separately, see
test_uk_who_reference_errors.py); this file addresses the same class of
defect found by a follow-up sweep of the whole package for
`return <SomeException>(...)`.

Two occurrences, structurally similar to the UK-WHO case but with a
different reachability profile:

1. `cdc_reference()` **returns** a `ValueError` instance (does not raise)
   for an age above the CDC upper threshold (20 years):

       >>> cdc_reference(age=25, measurement_method="height")
       ValueError('There is no CDC reference data above the age of 20 years.')

   This is currently masked at the one real caller,
   `cdc_lms_array_for_measurement_and_sex()`, by a second, independent
   check (`reference_data_absent()`) whose upper threshold happens to
   exactly match (`CDC_UPPER_THRESHOLD == TWENTY_YEARS == 20.0`), so the
   caller still raises `LookupError` overall for this specific boundary -
   the same masking pattern as the original UK-WHO bug.

2. The caller's own `except: return LookupError(...)` clause has the
   identical anti-pattern, and - unlike the UK-WHO case - it is **already
   directly reachable today**, because `reference_data_absent()` is called
   before the try/except, but does not independently catch the specific
   threshold that `cdc_reference()`'s *correctly-raising* branch protects
   (`FENTON_LOWER_THRESHOLD`, ~22 weeks gestation, a stricter/lower bound
   than `reference_data_absent()`'s own `age < 0` check). For an age below
   `FENTON_LOWER_THRESHOLD`, `cdc_reference()` correctly raises
   `ValueError`, the caller's bare `except:` catches it, and then
   **returns** (not raises) a generic `LookupError` instance - confirmed
   live:

       >>> cdc_lms_array_for_measurement_and_sex(age=-0.5, measurement_method="height", sex="male")
       LookupError('There is no CDC reference for the age supplied.')  # returned, not raised

   This is exactly the failure mode issue #51's reporter described:
   invalid input is silently handed back as an exception *object* rather
   than raised, and a caller doing arithmetic or a lookup on the result
   (as `sds_for_measurement()`'s `fetch_lms()` -> `nearest_lowest_index()`
   does, iterating the "array") gets a confusing, unrelated error far from
   the actual cause.
"""

import pytest

from rcpchgrowth.cdc import cdc_reference, cdc_lms_array_for_measurement_and_sex
from rcpchgrowth.constants.reference_constants import FENTON_LOWER_THRESHOLD


def test_cdc_reference_raises_above_the_age_ceiling():
    with pytest.raises(ValueError, match="no CDC reference data above the age of 20 years"):
        cdc_reference(age=25, measurement_method="height")


def test_cdc_reference_does_not_return_an_exception_instance():
    for out_of_range_age in (21, 25, 100):
        with pytest.raises(ValueError):
            result = cdc_reference(age=out_of_range_age, measurement_method="height")
            assert not isinstance(result, BaseException), (
                f"cdc_reference({out_of_range_age}) returned an exception "
                f"instance instead of raising: {result!r}"
            )


def test_cdc_lms_array_raises_for_age_above_the_ceiling():
    # Before the fix, reference_data_absent()'s independent >20y check
    # happened to raise correctly regardless of the bug in cdc_reference()
    # itself, using its own message text ("CDC data does not exist above 20
    # years."). After the fix, cdc_reference() raises immediately with its
    # own, more specific message, and reference_data_absent() is never
    # reached for this case - a deliberate consequence of fixing the
    # except-clause anti-pattern below, matching the same fix applied to
    # the UK-WHO module.
    with pytest.raises(LookupError, match="above the age of 20 years"):
        cdc_lms_array_for_measurement_and_sex(age=25, measurement_method="height", sex="male")


@pytest.mark.parametrize("out_of_range_age", [FENTON_LOWER_THRESHOLD - 0.01, -0.5, -1.0])
def test_cdc_lms_array_raises_for_age_below_the_fenton_floor(out_of_range_age):
    # Live, currently-reachable case: no independent check masks this one.
    with pytest.raises(LookupError) as excinfo:
        result = cdc_lms_array_for_measurement_and_sex(
            age=out_of_range_age, measurement_method="height", sex="male"
        )
        assert not isinstance(result, BaseException), (
            f"cdc_lms_array_for_measurement_and_sex({out_of_range_age}) "
            f"returned an exception instance instead of raising: {result!r}"
        )
    assert "reference data" in str(excinfo.value)
    assert excinfo.value.__cause__ is not None, "LookupError should chain the original ValueError"
