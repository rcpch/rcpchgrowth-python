"""
Tests for `return_correlation()`'s out-of-domain error handling.

Fixes GitHub issue #51 ("Returning Errors rather that raising them"), for
its `dynamic_growth.py` occurrences - found by a full-package sweep for the
`return <SomeException>(...)` anti-pattern after the reporter's original
UK-WHO example was fixed separately.

`return_correlation()` is root-exported (`rcpchgrowth.return_correlation`)
and **returns** an `Exception` instance, rather than raising it, for a
requested age outside the correlation matrix's domain (over 53 weeks, or
over 12 months):

    >>> return_correlation(t1=60, t2=5, time_interval="weeks")
    Exception('Data only available below 53 weeks of age')

This module is labelled experimental and not for clinical use, but the
function is still public API surface, and its one internal caller,
`create_thrive_line()` (also root-exported), demonstrates exactly the harm
issue #51 describes: it uses the return value directly in arithmetic
(`conditional_weight_gain()` computes `r**2`), so an out-of-range request
crashes with a confusing, unrelated error far from the real cause:

    >>> create_thrive_line(t=[3, 15], z1=0.0, sex="male", target_centile=50.0)
    TypeError: unsupported operand type(s) for *: 'float' and 'Exception'

instead of a clear message naming the actual problem (a requested age
outside the correlation matrix's domain).
"""

import pytest

from rcpchgrowth import create_thrive_line
from rcpchgrowth.dynamic_growth import return_correlation


def test_return_correlation_raises_above_the_weekly_ceiling():
    with pytest.raises(ValueError, match="only available below 53 weeks"):
        return_correlation(t1=60, t2=5, time_interval="weeks")


def test_return_correlation_raises_above_the_monthly_ceiling():
    with pytest.raises(ValueError, match="only available below 12 months"):
        return_correlation(t1=15, t2=5, time_interval="months")


@pytest.mark.parametrize(
    "t1,t2,time_interval",
    [(60, 5, "weeks"), (5, 60, "weeks"), (15, 5, "months"), (5, 15, "months")],
)
def test_return_correlation_does_not_return_an_exception_instance(t1, t2, time_interval):
    with pytest.raises(ValueError):
        result = return_correlation(t1=t1, t2=t2, time_interval=time_interval)
        assert not isinstance(result, BaseException), (
            f"return_correlation({t1}, {t2}, {time_interval!r}) returned an "
            f"exception instance instead of raising: {result!r}"
        )


def test_return_correlation_still_works_for_a_valid_request():
    # Baseline: the fix must not change in-domain behaviour.
    result = return_correlation(t1=3, t2=4, time_interval="months")
    assert isinstance(result, float)
    assert result == pytest.approx(0.941324764)


def test_create_thrive_line_raises_a_clear_error_for_an_out_of_range_age_instead_of_crashing():
    # End-to-end regression test for the real caller: before the fix, this
    # raised a confusing TypeError from deep inside conditional_weight_gain
    # ("unsupported operand type(s) for *: 'float' and 'Exception'"). After
    # the fix, the actual cause is raised directly.
    with pytest.raises(ValueError, match="only available below 12 months"):
        create_thrive_line(t=[3, 15], z1=0.0, sex="male", target_centile=50.0)
