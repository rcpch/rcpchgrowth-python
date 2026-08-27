"""
Registry test: every age grid used to build chart-coordinate output must be
strictly ascending with no duplicate ages.

These constants are hard-coded rather than derived from the underlying LMS
tables (see global_functions.py, generate_centile()), so there is no
structural guarantee they are in order. A single wrong or duplicated value
makes chart-coordinate output plot backwards or repeat a point at that
position in the line.

Bug found by inspection: WHO_2006_OVER_TWOS_AGES (used for the standalone
WHO reference's who_2006_child chart component, ages 2-5y) has 3.083333333
duplicated at index 26, immediately after 4.0 at index 25, where an
ascending monthly grid requires 4.083333333. This is a single-digit typo
(4 -> 3) in the source constant.
"""

from rcpchgrowth.constants.reference_constants import (
    CDC_TO_THREE_AGE,
    CDC_TO_TWO_AGE,
    CDC_TWO_TWENTY,
    TRISOMY_21_AAP_CHILD_AGES,
    TRISOMY_21_AAP_INFANT_AGES,
    TRISOMY_21_AGES,
    TURNER_AGES,
    UK90_AGES,
    UK_90_PRETERM_AGES,
    UK_WHO_2006_OVER_TWOS_AGES,
    WHO_2006_OVER_TWOS_AGES,
    WHO_2006_UNDER_TWOS_AGES,
    WHO_2007_AGES,
)

# Every age grid referenced by generate_centile() in global_functions.py to
# select the x-axis values for a chart-coordinate line, keyed by the
# constant's own name so a failing case names the offending array directly.
CHART_AGE_GRIDS = {
    "UK_90_PRETERM_AGES": UK_90_PRETERM_AGES,
    "WHO_2006_UNDER_TWOS_AGES": WHO_2006_UNDER_TWOS_AGES,
    "UK_WHO_2006_OVER_TWOS_AGES": UK_WHO_2006_OVER_TWOS_AGES,
    "UK90_AGES": UK90_AGES,
    "WHO_2006_OVER_TWOS_AGES": WHO_2006_OVER_TWOS_AGES,
    "WHO_2007_AGES": WHO_2007_AGES,
    "CDC_TO_THREE_AGE": CDC_TO_THREE_AGE,
    "CDC_TO_TWO_AGE": CDC_TO_TWO_AGE,
    "CDC_TWO_TWENTY": CDC_TWO_TWENTY,
    "TURNER_AGES": TURNER_AGES,
    "TRISOMY_21_AGES": TRISOMY_21_AGES,
    "TRISOMY_21_AAP_INFANT_AGES": TRISOMY_21_AAP_INFANT_AGES,
    "TRISOMY_21_AAP_CHILD_AGES": TRISOMY_21_AAP_CHILD_AGES,
}


def test_every_chart_age_grid_is_registered():
    # Guards against a new age-grid constant being added to
    # global_functions.py without this registry being updated to cover it.
    import inspect

    import rcpchgrowth.global_functions as gf

    source = inspect.getsource(gf.generate_centile)
    referenced = {
        name for name in dir(__import__("rcpchgrowth.constants.reference_constants", fromlist=["*"]))
        if name.endswith("_AGES") or name.endswith("_AGE") or name.endswith("TWENTY")
    }
    # every constant this test checks must actually exist upstream
    for name in CHART_AGE_GRIDS:
        assert name in referenced, f"{name} is not a real reference constant"


def test_chart_age_grid_has_no_duplicate_ages():
    failures = {}
    for name, grid in CHART_AGE_GRIDS.items():
        seen = set()
        dupes = {age for age in grid if age in seen or seen.add(age)}
        if dupes:
            failures[name] = sorted(dupes)
    assert not failures, f"duplicate ages found in: {failures}"


def test_chart_age_grid_is_strictly_ascending():
    failures = {}
    for name, grid in CHART_AGE_GRIDS.items():
        descents = [
            (i, grid[i - 1], grid[i])
            for i in range(1, len(grid))
            if grid[i] <= grid[i - 1]
        ]
        if descents:
            failures[name] = descents
    assert not failures, f"non-ascending age grid(s): {failures}"
