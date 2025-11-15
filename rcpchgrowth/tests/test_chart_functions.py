import pytest
from rcpchgrowth.global_functions import *
from .who_test_data.who_chart_precalculated_centiles import *


UNDER_FIVES_SERIES = [
    # Girls weight-for-age 0-5y
    ("WHO_GIRL_WEIGHT_UNDER_FIVE_50", WHO_GIRL_WEIGHT_UNDER_FIVE_50, "female", "weight", 0),
    ("WHO_GIRL_WEIGHT_UNDER_FIVE_25", WHO_GIRL_WEIGHT_UNDER_FIVE_25, "female", "weight", -0.67),
    ("WHO_GIRL_WEIGHT_UNDER_FIVE_10", WHO_GIRL_WEIGHT_UNDER_FIVE_10, "female", "weight", -1.28),
    ("WHO_GIRL_WEIGHT_UNDER_FIVE_5",  WHO_GIRL_WEIGHT_UNDER_FIVE_5,  "female", "weight", -1.64),
    # Girls BMI-for-age 0-5y
    ("WHO_GIRL_BMI_UNDER_FIVE_50", WHO_GIRL_BMI_UNDER_FIVE_50, "female", "bmi", 0),
    ("WHO_GIRL_BMI_UNDER_FIVE_99", WHO_GIRL_BMI_UNDER_FIVE_99, "female", "bmi", 2.33),
    ("WHO_GIRL_BMI_UNDER_FIVE_999", WHO_GIRL_BMI_UNDER_FIVE_999, "female", "bmi", 3.0903),
    ("WHO_GIRL_BMI_UNDER_FIVE_1", WHO_GIRL_BMI_UNDER_FIVE_1, "female", "bmi", -2.33),
    ("WHO_GIRL_BMI_UNDER_FIVE_001", WHO_GIRL_BMI_UNDER_FIVE_001, "female", "bmi", -3.0903),
    # Girls length-for-age 0-5y
    ("WHO_GIRL_LENGTH_UNDER_FIVE_01", WHO_GIRL_LENGTH_UNDER_FIVE_01, "female", "height", -3.0903),
    ("WHO_GIRL_LENGTH_UNDER_FIVE_1", WHO_GIRL_LENGTH_UNDER_FIVE_1, "female", "height", -2.33),
    ("WHO_GIRL_LENGTH_UNDER_FIVE_15", WHO_GIRL_LENGTH_UNDER_FIVE_15, "female", "height", -1.036),
    ("WHO_GIRL_LENGTH_UNDER_FIVE_25", WHO_GIRL_LENGTH_UNDER_FIVE_25, "female", "height", -0.67),
    ("WHO_GIRL_LENGTH_UNDER_FIVE_50", WHO_GIRL_LENGTH_UNDER_FIVE_50, "female", "height", 0),
    ("WHO_GIRL_LENGTH_UNDER_FIVE_75", WHO_GIRL_LENGTH_UNDER_FIVE_75, "female", "height", 0.67),
    ("WHO_GIRL_LENGTH_UNDER_FIVE_85", WHO_GIRL_LENGTH_UNDER_FIVE_85, "female", "height", 1.036),
    ("WHO_GIRL_LENGTH_UNDER_FIVE_99", WHO_GIRL_LENGTH_UNDER_FIVE_99, "female", "height", 2.33),
    ("WHO_GIRL_LENGTH_UNDER_FIVE_999", WHO_GIRL_LENGTH_UNDER_FIVE_999, "female", "height", 3.0903),
    # Girls OFC-for-age 0-5y
    ("WHO_GIRL_OFC_UNDER_FIVE_01", WHO_GIRL_OFC_UNDER_FIVE_01, "female", "ofc", -3.0903),
    ("WHO_GIRL_OFC_UNDER_FIVE_1", WHO_GIRL_OFC_UNDER_FIVE_1, "female", "ofc", -2.33),
    ("WHO_GIRL_OFC_UNDER_FIVE_15", WHO_GIRL_OFC_UNDER_FIVE_15, "female", "ofc", -1.036),
    ("WHO_GIRL_OFC_UNDER_FIVE_25", WHO_GIRL_OFC_UNDER_FIVE_25, "female", "ofc", -0.67),
    ("WHO_GIRL_OFC_UNDER_FIVE_50", WHO_GIRL_OFC_UNDER_FIVE_50, "female", "ofc", 0),
    ("WHO_GIRL_OFC_UNDER_FIVE_75", WHO_GIRL_OFC_UNDER_FIVE_75, "female", "ofc", 0.67),
    ("WHO_GIRL_OFC_UNDER_FIVE_85", WHO_GIRL_OFC_UNDER_FIVE_85, "female", "ofc", 1.036),
    ("WHO_GIRL_OFC_UNDER_FIVE_99", WHO_GIRL_OFC_UNDER_FIVE_99, "female", "ofc", 2.33),
    ("WHO_GIRL_OFC_UNDER_FIVE_999", WHO_GIRL_OFC_UNDER_FIVE_999, "female", "ofc", 3.0903),

    # Boys weight-for-age 0-5y
    ("WHO_BOY_WEIGHT_UNDER_FIVE_01", WHO_BOY_WEIGHT_UNDER_FIVE_01, "male", "weight", -3.0903),
    ("WHO_BOY_WEIGHT_UNDER_FIVE_1", WHO_BOY_WEIGHT_UNDER_FIVE_1, "male", "weight", -2.33),
    ("WHO_BOY_WEIGHT_UNDER_FIVE_15", WHO_BOY_WEIGHT_UNDER_FIVE_15, "male", "weight", -1.036),
    ("WHO_BOY_WEIGHT_UNDER_FIVE_25", WHO_BOY_WEIGHT_UNDER_FIVE_25, "male", "weight", -0.67),
    ("WHO_BOY_WEIGHT_UNDER_FIVE_50", WHO_BOY_WEIGHT_UNDER_FIVE_50, "male", "weight", 0),
    ("WHO_BOY_WEIGHT_UNDER_FIVE_75", WHO_BOY_WEIGHT_UNDER_FIVE_75, "male", "weight", 0.67),
    ("WHO_BOY_WEIGHT_UNDER_FIVE_85", WHO_BOY_WEIGHT_UNDER_FIVE_85, "male", "weight", 1.036),
    ("WHO_BOY_WEIGHT_UNDER_FIVE_99", WHO_BOY_WEIGHT_UNDER_FIVE_99, "male", "weight", 2.33),
    ("WHO_BOY_WEIGHT_UNDER_FIVE_999", WHO_BOY_WEIGHT_UNDER_FIVE_999, "male", "weight", 3.0903),
    # Boys length-for-age 0-5y
    ("WHO_BOY_LENGTH_UNDER_FIVE_01", WHO_BOY_LENGTH_UNDER_FIVE_01, "male", "height", -3.0903),
    ("WHO_BOY_LENGTH_UNDER_FIVE_1", WHO_BOY_LENGTH_UNDER_FIVE_1, "male", "height", -2.33),
    ("WHO_BOY_LENGTH_UNDER_FIVE_15", WHO_BOY_LENGTH_UNDER_FIVE_15, "male", "height", -1.036),
    ("WHO_BOY_LENGTH_UNDER_FIVE_25", WHO_BOY_LENGTH_UNDER_FIVE_25, "male", "height", -0.67),
    ("WHO_BOY_LENGTH_UNDER_FIVE_50", WHO_BOY_LENGTH_UNDER_FIVE_50, "male", "height", 0),
    ("WHO_BOY_LENGTH_UNDER_FIVE_75", WHO_BOY_LENGTH_UNDER_FIVE_75, "male", "height", 0.67),
    ("WHO_BOY_LENGTH_UNDER_FIVE_85", WHO_BOY_LENGTH_UNDER_FIVE_85, "male", "height", 1.036),
    ("WHO_BOY_LENGTH_UNDER_FIVE_99", WHO_BOY_LENGTH_UNDER_FIVE_99, "male", "height", 2.33),
    ("WHO_BOY_LENGTH_UNDER_FIVE_999", WHO_BOY_LENGTH_UNDER_FIVE_999, "male", "height", 3.0903),
    # Boys BMI-for-age 0-5y
    ("WHO_BOY_BMI_UNDER_FIVE_01", WHO_BOY_BMI_UNDER_FIVE_01, "male", "bmi", -3.0903),
    ("WHO_BOY_BMI_UNDER_FIVE_1", WHO_BOY_BMI_UNDER_FIVE_1, "male", "bmi", -2.33),
    ("WHO_BOY_BMI_UNDER_FIVE_15", WHO_BOY_BMI_UNDER_FIVE_15, "male", "bmi", -1.036),
    ("WHO_BOY_BMI_UNDER_FIVE_25", WHO_BOY_BMI_UNDER_FIVE_25, "male", "bmi", -0.67),
    ("WHO_BOY_BMI_UNDER_FIVE_50", WHO_BOY_BMI_UNDER_FIVE_50, "male", "bmi", 0),
    ("WHO_BOY_BMI_UNDER_FIVE_75", WHO_BOY_BMI_UNDER_FIVE_75, "male", "bmi", 0.67),
    ("WHO_BOY_BMI_UNDER_FIVE_85", WHO_BOY_BMI_UNDER_FIVE_85, "male", "bmi", 1.036),
    ("WHO_BOY_BMI_UNDER_FIVE_99", WHO_BOY_BMI_UNDER_FIVE_99, "male", "bmi", 2.33),
    ("WHO_BOY_BMI_UNDER_FIVE_999", WHO_BOY_BMI_UNDER_FIVE_999, "male", "bmi", 3.0903),
    # Boys OFC-for-age 0-5y
    ("WHO_BOY_OFC_UNDER_FIVE_01", WHO_BOY_OFC_UNDER_FIVE_01, "male", "ofc", -3.0903),
    ("WHO_BOY_OFC_UNDER_FIVE_1", WHO_BOY_OFC_UNDER_FIVE_1, "male", "ofc", -2.33),
    ("WHO_BOY_OFC_UNDER_FIVE_15", WHO_BOY_OFC_UNDER_FIVE_15, "male", "ofc", -1.036),
    ("WHO_BOY_OFC_UNDER_FIVE_25", WHO_BOY_OFC_UNDER_FIVE_25, "male", "ofc", -0.67),
    ("WHO_BOY_OFC_UNDER_FIVE_50", WHO_BOY_OFC_UNDER_FIVE_50, "male", "ofc", 0),
    ("WHO_BOY_OFC_UNDER_FIVE_75", WHO_BOY_OFC_UNDER_FIVE_75, "male", "ofc", 0.67),
    ("WHO_BOY_OFC_UNDER_FIVE_85", WHO_BOY_OFC_UNDER_FIVE_85, "male", "ofc", 1.036),
    ("WHO_BOY_OFC_UNDER_FIVE_99", WHO_BOY_OFC_UNDER_FIVE_99, "male", "ofc", 2.33),
    ("WHO_BOY_OFC_UNDER_FIVE_999", WHO_BOY_OFC_UNDER_FIVE_999, "male", "ofc", 3.0903),
]

OVER_FIVES_SERIES = [
    # Girls weight 5-10y
    ("WHO_GIRL_WEIGHT_OVER_FIVE_50", WHO_GIRL_WEIGHT_OVER_FIVE_50, "female", "weight", 0),
    ("WHO_GIRL_WEIGHT_OVER_FIVE_75", WHO_GIRL_WEIGHT_OVER_FIVE_75, "female", "weight", 0.67),
    ("WHO_GIRL_WEIGHT_OVER_FIVE_85", WHO_GIRL_WEIGHT_OVER_FIVE_85, "female", "weight", 1.04),
    ("WHO_GIRL_WEIGHT_OVER_FIVE_97", WHO_GIRL_WEIGHT_OVER_FIVE_97, "female", "weight", 1.88),
    # Girls height 5-19y
    # ("WHO_GIRL_LENGTH_OVER_FIVE_01", WHO_GIRL_LENGTH_OVER_FIVE_01, "female", "height", -3.0903),
    # ("WHO_GIRL_LENGTH_OVER_FIVE_1", WHO_GIRL_LENGTH_OVER_FIVE_1, "female", "height", -2.33),
    # ("WHO_GIRL_LENGTH_OVER_FIVE_15", WHO_GIRL_LENGTH_OVER_FIVE_15, "female", "height", -1.036),
    # ("WHO_GIRL_LENGTH_OVER_FIVE_25", WHO_GIRL_LENGTH_OVER_FIVE_25, "female", "height", -0.67),
    # ("WHO_GIRL_LENGTH_OVER_FIVE_50", WHO_GIRL_LENGTH_OVER_FIVE_50, "female", "height", 0),
    # ("WHO_GIRL_LENGTH_OVER_FIVE_75", WHO_GIRL_LENGTH_OVER_FIVE_75, "female", "height", 0.67),
    # ("WHO_GIRL_LENGTH_OVER_FIVE_85", WHO_GIRL_LENGTH_OVER_FIVE_85, "female", "height", 1.036),
    # ("WHO_GIRL_LENGTH_OVER_FIVE_99", WHO_GIRL_LENGTH_OVER_FIVE_99, "female", "height", 2.33),
    # ("WHO_GIRL_LENGTH_OVER_FIVE_999", WHO_GIRL_LENGTH_OVER_FIVE_999, "female", "height", 3.0903),

    # Girls bmi 5-19y
    # ("WHO_GIRL_BMI_OVER_FIVE_01", WHO_GIRL_BMI_OVER_FIVE_01, "female", "bmi", -3.0903),
    # ("WHO_GIRL_BMI_OVER_FIVE_1", WHO_GIRL_BMI_OVER_FIVE_1, "female", "bmi", -2.33),
    # ("WHO_GIRL_BMI_OVER_FIVE_25", WHO_GIRL_BMI_OVER_FIVE_25, "female", "bmi", -0.67),
    # ("WHO_GIRL_BMI_OVER_FIVE_50", WHO_GIRL_BMI_OVER_FIVE_50, "female", "bmi", 0),
    # ("WHO_GIRL_BMI_OVER_FIVE_75", WHO_GIRL_BMI_OVER_FIVE_75, "female", "bmi", 0.67),
    # ("WHO_GIRL_BMI_OVER_FIVE_85", WHO_GIRL_BMI_OVER_FIVE_85, "female", "bmi", 1.036),
    # ("WHO_GIRL_BMI_OVER_FIVE_99", WHO_GIRL_BMI_OVER_FIVE_99, "female", "bmi", 2.33),
    # ("WHO_GIRL_BMI_OVER_FIVE_999", WHO_GIRL_BMI_OVER_FIVE_999, "female", "bmi", 3.0903),

    # Boys length 5-19y
    ("WHO_BOY_LENGTH_OVER_FIVE_01", WHO_BOY_LENGTH_OVER_FIVE_01, "male", "height", -3.0903),
    ("WHO_BOY_LENGTH_OVER_FIVE_1", WHO_BOY_LENGTH_OVER_FIVE_1, "male", "height", -2.33),
    ("WHO_BOY_LENGTH_OVER_FIVE_25", WHO_BOY_LENGTH_OVER_FIVE_25, "male", "height", -0.67),
    ("WHO_BOY_LENGTH_OVER_FIVE_50", WHO_BOY_LENGTH_OVER_FIVE_50, "male", "height", 0),
    ("WHO_BOY_LENGTH_OVER_FIVE_75", WHO_BOY_LENGTH_OVER_FIVE_75, "male", "height", 0.67),
    ("WHO_BOY_LENGTH_OVER_FIVE_85", WHO_BOY_LENGTH_OVER_FIVE_85, "male", "height", 1.036),
    ("WHO_BOY_LENGTH_OVER_FIVE_99", WHO_BOY_LENGTH_OVER_FIVE_99, "male", "height", 2.33),
    ("WHO_BOY_LENGTH_OVER_FIVE_999", WHO_BOY_LENGTH_OVER_FIVE_999, "male", "height", 3.0903),
    
    # Boys weight 5-10y
    ("WHO_BOY_WEIGHT_OVER_FIVE_01", WHO_BOY_WEIGHT_OVER_FIVE_01, "male", "weight", -3.0903),
    ("WHO_BOY_WEIGHT_OVER_FIVE_1", WHO_BOY_WEIGHT_OVER_FIVE_1, "male", "weight", -2.33),
    ("WHO_BOY_WEIGHT_OVER_FIVE_25", WHO_BOY_WEIGHT_OVER_FIVE_25, "male", "weight", -0.67),
    ("WHO_BOY_WEIGHT_OVER_FIVE_50", WHO_BOY_WEIGHT_OVER_FIVE_50, "male", "weight", 0),
    ("WHO_BOY_WEIGHT_OVER_FIVE_75", WHO_BOY_WEIGHT_OVER_FIVE_75, "male", "weight", 0.67),
    ("WHO_BOY_WEIGHT_OVER_FIVE_85", WHO_BOY_WEIGHT_OVER_FIVE_85, "male", "weight", 1.036),
    ("WHO_BOY_WEIGHT_OVER_FIVE_99", WHO_BOY_WEIGHT_OVER_FIVE_99, "male", "weight", 2.33),
    ("WHO_BOY_WEIGHT_OVER_FIVE_999", WHO_BOY_WEIGHT_OVER_FIVE_999, "male", "weight", 3.0903),
    
    # # Boys bmi 5-19y
    # ("WHO_BOY_BMI_OVER_FIVE_01", WHO_BOY_BMI_OVER_FIVE_01, "male", "bmi", -3.0903),
    # ("WHO_BOY_BMI_OVER_FIVE_1", WHO_BOY_BMI_OVER_FIVE_1, "male", "bmi", -2.33),
    # ("WHO_BOY_BMI_OVER_FIVE_25", WHO_BOY_BMI_OVER_FIVE_25, "male", "bmi", -0.67),
    # ("WHO_BOY_BMI_OVER_FIVE_50", WHO_BOY_BMI_OVER_FIVE_50, "male", "bmi", 0),
    # ("WHO_BOY_BMI_OVER_FIVE_75", WHO_BOY_BMI_OVER_FIVE_75, "male", "bmi", 0.67),
    # ("WHO_BOY_BMI_OVER_FIVE_85", WHO_BOY_BMI_OVER_FIVE_85, "male", "bmi", 1.036),
    # ("WHO_BOY_BMI_OVER_FIVE_99", WHO_BOY_BMI_OVER_FIVE_99, "male", "bmi", 2.33),
    # ("WHO_BOY_BMI_OVER_FIVE_999", WHO_BOY_BMI_OVER_FIVE_999, "male", "bmi", 3.0903),
]

_POINT_CASES = [
    (series_name, age_days, expected_weight, sex, method, sds)
    for series_name, values, sex, method, sds in UNDER_FIVES_SERIES
    for age_days, expected_weight in enumerate(values)
]

_POINT_CASES_OVER_FIVES = [
    (series_name, age_months, expected_observation_value, sex, method, sds)
    for series_name, values, sex, method, sds in OVER_FIVES_SERIES
    for age_months, expected_observation_value in enumerate(values)
]

@pytest.mark.parametrize(
    "series_name,age_days,expected_weight,sex,measurement_method,requested_sds",
    _POINT_CASES
)
def test_who_under_fives(series_name, age_days, expected_weight, sex, measurement_method, requested_sds):
    ACCURACY = 1e-3
    age_years = round(age_days / 365.25, 4)
    print(f"Testing {series_name} day {age_days} ({age_years:.4f} years)")
    if age_years > 5.00:
        pytest.skip("Skipping under-five test for age > 5 years")
    measurement = measurement_from_sds(
        reference='who',
        requested_sds=requested_sds,
        measurement_method=measurement_method,
        sex=sex,
        age=age_years,
        default_youngest_reference=True
    )
    assert measurement == pytest.approx(expected_weight, rel=ACCURACY), (
        f"{series_name} day {age_days}: expected {expected_weight} got {measurement} for {requested_sds} in {sex} and {measurement_method} at {age_years:.3f} years"
    )

@pytest.mark.parametrize(
    "series_name,age_months,expected_observation_value,sex,measurement_method,requested_sds",
    _POINT_CASES_OVER_FIVES
)
def test_who_over_fives(series_name, age_months, expected_observation_value, sex, measurement_method, requested_sds):
    ACCURACY = 1e-3
    age_years = 5 + round(age_months / 12, 4)
    measurement = measurement_from_sds(
        reference='who',
        requested_sds=requested_sds,
        measurement_method=measurement_method,
        sex=sex,
        age=age_years,
        default_youngest_reference=True if age_years >= 5 else False # if we are charting over fives, we do use under-five reference at aged 5 years
    )
    assert measurement == pytest.approx(expected_observation_value, rel=ACCURACY), (
        f"{series_name} month {age_months}: expected {expected_observation_value} got {measurement} for {requested_sds} in {sex} and {measurement_method} at {age_years:.2f} years"
    )