"""
Regression test for hazard rcpch/digital-growth-charts-documentation#178:
`chronological_percentage_median_bmi` was computed from `corrected_age`
instead of `chronological_age` in `Measurement.__calculate_ages()`.

    chronological_percentage_median_bmi = percentage_median_bmi(
        reference=reference,
        age=corrected_age,          # <-- should be chronological_age
        actual_bmi=observation_value,
        sex=sex
    )

Because the field immediately above it (`corrected_percentage_median_bmi`)
correctly uses `corrected_age`, the two fields returned an identical value
for every BMI measurement, silently mislabelling the corrected-age result
as chronological. This is invisible whenever corrected and chronological
age happen to coincide (term birth, or a reference that resets/stops
correction), which is why it was not caught by the existing fixture-based
tests, and why this test uses a preterm child under UK-WHO specifically -
the reference where gestational correction is retained throughout, so the
two ages differ at every age for any gestation other than exactly 40+0.
"""

from datetime import date

import pytest

from rcpchgrowth import Measurement
from rcpchgrowth.global_functions import percentage_median_bmi

# 28+0 weeks gestation (12 weeks preterm), observed at chronological age 3.0
# years under UK-WHO, where correction is retained well beyond 2 years -
# so corrected and chronological age differ throughout.
BIRTH_DATE = date(2020, 1, 1)
OBSERVATION_DATE = date(2023, 1, 1)
GESTATION_WEEKS = 28
GESTATION_DAYS = 0
OBSERVATION_VALUE = 15.5
SEX = "male"
REFERENCE = "uk-who"


def _measurement_calculated_values():
    measurement = Measurement(
        sex=SEX,
        birth_date=BIRTH_DATE,
        observation_date=OBSERVATION_DATE,
        measurement_method="bmi",
        observation_value=OBSERVATION_VALUE,
        gestation_weeks=GESTATION_WEEKS,
        gestation_days=GESTATION_DAYS,
        reference=REFERENCE,
    ).measurement
    return measurement["measurement_dates"], measurement["measurement_calculated_values"]


def test_corrected_and_chronological_ages_differ_for_this_fixture():
    # Sanity check on the fixture itself: this test is only meaningful if
    # corrected and chronological age genuinely differ.
    dates, _ = _measurement_calculated_values()
    assert dates["corrected_decimal_age"] != pytest.approx(
        dates["chronological_decimal_age"], abs=1e-6
    )


def test_chronological_percentage_median_bmi_uses_chronological_age():
    dates, values = _measurement_calculated_values()

    expected_chronological = percentage_median_bmi(
        reference=REFERENCE,
        age=dates["chronological_decimal_age"],
        actual_bmi=OBSERVATION_VALUE,
        sex=SEX,
    )
    expected_corrected = percentage_median_bmi(
        reference=REFERENCE,
        age=dates["corrected_decimal_age"],
        actual_bmi=OBSERVATION_VALUE,
        sex=SEX,
    )

    assert values["chronological_percentage_median_bmi"] == pytest.approx(
        expected_chronological
    )
    assert values["corrected_percentage_median_bmi"] == pytest.approx(
        expected_corrected
    )

    # The two fields must differ here - this is the assertion the previous
    # code could never fail, because both fields used age=corrected_age.
    assert values["chronological_percentage_median_bmi"] != pytest.approx(
        values["corrected_percentage_median_bmi"]
    )
