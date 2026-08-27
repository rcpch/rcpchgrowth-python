"""
Tests for `uk_who_reference()`'s out-of-domain error handling.

Bug found by inspection and confirmed interactively: for an age outside the
UK90/WHO/UK-WHO domain (below 23 weeks gestation, or above 20 years),
`uk_who_reference()` **returns** a `ValueError` instance rather than
**raising** it:

    >>> uk_who_reference(age=-10)
    ValueError('There is no UK90 reference data below 23 weeks gestation')
    >>> type(uk_who_reference(age=-10))
    <class 'ValueError'>

This violates ordinary Python exception semantics: a caller doing
`result = uk_who_reference(age)` gets back an exception *object* it is not
expecting to check for, and a `try/except:` wrapped around the call (as in
`uk_who_lms_array_for_measurement_and_sex()`) never fires, because nothing
was actually raised.

The only current caller, `uk_who_lms_array_for_measurement_and_sex()`,
happens to be shielded from the immediate consequence of this by a second,
independent check (`reference_data_absent()`) whose thresholds happen to
exactly match `uk_who_reference()`'s, so out-of-range ages still correctly
raise `LookupError` overall - but only via that second check, and only by
coincidence of matching thresholds with no test enforcing they stay in
sync. `uk_who_reference()` itself has no leading underscore and is freely
importable, so any other or future caller relying on ordinary exception
semantics would be silently handed the wrong thing.

**Important second-order effect, discovered while fixing this:** the same
caller's `except:` clause around the call to `uk_who_reference()` has the
identical anti-pattern - `return LookupError(...)` instead of
`raise LookupError(...)` - and was previously *unreachable*, because
`uk_who_reference()` never actually raised anything for that `except:` to
catch. Making `uk_who_reference()` raise correctly therefore makes this
second bug newly reachable, and it must be fixed in the same change or an
out-of-range age would regress from "raises a specific LookupError" to
"silently returns a generic LookupError object". See
`test_uk_who_lms_array_for_measurement_and_sex_raises_for_out_of_range_age`
below, which is the end-to-end test that caught this.
"""

import pytest

from rcpchgrowth.uk_who import uk_who_reference, uk_who_lms_array_for_measurement_and_sex


def test_uk_who_reference_raises_below_the_gestation_floor():
    with pytest.raises(ValueError, match="no UK90 reference data below 23 weeks gestation"):
        uk_who_reference(age=-10)


def test_uk_who_reference_raises_above_the_age_ceiling():
    with pytest.raises(ValueError, match="no UK90 reference data above the age of 20 years"):
        uk_who_reference(age=25)


def test_uk_who_reference_does_not_return_an_exception_instance():
    # A stronger, type-based check independent of the two tests above:
    # whatever the boundary and message wording, an out-of-domain call must
    # never yield a value where `isinstance(value, BaseException)` is true,
    # because that is the specific shape of this defect.
    for out_of_range_age in (-10, -1, 21, 100):
        with pytest.raises(ValueError):
            result = uk_who_reference(age=out_of_range_age)
            # if we get here, the function returned rather than raised
            assert not isinstance(result, BaseException), (
                f"uk_who_reference({out_of_range_age}) returned an exception "
                f"instance instead of raising: {result!r}"
            )


@pytest.mark.parametrize(
    "out_of_range_age,expected_message_fragment",
    [
        (-10, "below 23 weeks gestation"),
        (25, "above the age of 20 years"),
        (100, "above the age of 20 years"),
    ],
)
def test_uk_who_lms_array_for_measurement_and_sex_raises_for_out_of_range_age(
    out_of_range_age, expected_message_fragment
):
    # End-to-end regression test for the second-order effect documented
    # above: the one real caller of uk_who_reference() must still correctly
    # *raise* LookupError for an out-of-range age, not silently return a
    # LookupError instance - and it must preserve uk_who_reference()'s
    # specific message (which boundary was crossed) rather than falling
    # back to a generic "no reference for the age supplied" string. Before
    # any of these fixes, the specific message reached the caller only by
    # accident, via a second, independent check (reference_data_absent())
    # whose thresholds happened to match; that path is now bypassed
    # entirely because uk_who_reference() raises immediately, so the
    # specific message must be carried across deliberately.
    with pytest.raises(LookupError) as excinfo:
        result = uk_who_lms_array_for_measurement_and_sex(
            age=out_of_range_age,
            measurement_method="height",
            sex="male",
        )
        assert not isinstance(result, BaseException), (
            f"uk_who_lms_array_for_measurement_and_sex({out_of_range_age}) "
            f"returned an exception instance instead of raising: {result!r}"
        )
    assert expected_message_fragment in str(excinfo.value)
    assert excinfo.value.__cause__ is not None, "LookupError should chain the original ValueError"
