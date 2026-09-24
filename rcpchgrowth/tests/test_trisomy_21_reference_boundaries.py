import math

import pytest

from rcpchgrowth.constants import BMI, FEMALE, MALE, TRISOMY_21
from rcpchgrowth.global_functions import sds_for_measurement


@pytest.mark.parametrize("sex", [MALE, FEMALE])
@pytest.mark.parametrize("age", [18.83, 18.92])
def test_trisomy_21_bmi_accepts_final_source_ages(sex, age):
    result = sds_for_measurement(
        reference=TRISOMY_21,
        age=age,
        measurement_method=BMI,
        observation_value=25.0,
        sex=sex,
    )

    assert math.isfinite(result)


@pytest.mark.parametrize("sex", [MALE, FEMALE])
def test_trisomy_21_bmi_rejects_age_after_last_source_age(sex):
    with pytest.raises(
        LookupError, match=r"Trisomy BMI reference data does not exist > 18\.92 y\."
    ):
        sds_for_measurement(
            reference=TRISOMY_21,
            age=math.nextafter(18.92, math.inf),
            measurement_method=BMI,
            observation_value=25.0,
            sex=sex,
        )
