# standard imports
from datetime import datetime
import json
import os
from pprint import pprint
import pandas as pd

# third-party imports
import pytest

# rcpch imports
from rcpchgrowth import Measurement
from rcpchgrowth.constants import HEIGHT, WEIGHT, BMI

# the ACCURACY constant defines the accuracy of the test comparisons
# owing to variations in statistical calculations it's impossible to get exact
# agreement between R and Python, so our statistician feels we can set a tolerance
# within which we will accept a result as correct.
ACCURACY = 1e-3

# NOTE: The aggregated CSV-wide test was removed in favor of per-row parametrized
# tests below. Per-row tests give one pytest item per CSV row so test runners
# (and CI) show a dot for each row.


# --- Per-row parametrized tests --------------------------------------------
# Create a parametrized test so pytest reports one test (dot) per CSV row.
CSV_PATH = (
    os.path.abspath(os.path.dirname(__file__))
    + "/who_test_data/who_validation_data.csv"
)
validation_params = []
validation_ids = []
if os.path.exists(CSV_PATH):
    import math

    vdf = pd.read_csv(CSV_PATH)
    for idx, r in vdf.iterrows():
        mth = r.get("measurement_method")
        obs = r.get("observation_value")
        if pd.isna(mth) or pd.isna(obs):
            continue
        # include minimal fields to avoid large param objects
        validation_params.append(
            (
                int(idx),
                str(mth),
                float(obs),
                str(r.get("start_date")),
                str(r.get("end_date")),
                r.get("sex"),
                r.get("requested_z"),
            )
        )
        validation_ids.append(f"row-{idx}-{mth}")


UNDER2_CSV_PATH = (
    os.path.abspath(os.path.dirname(__file__))
    + "/who_test_data/who_under2_gold_192.csv"
)
under2_params = []
under2_ids = []
if os.path.exists(UNDER2_CSV_PATH):
    udf = pd.read_csv(UNDER2_CSV_PATH)
    for idx, r in udf.iterrows():
        mth = r.get("measurement_method")
        obs = r.get("observation_value")
        age_days = r.get("age_days")
        sex_val = r.get("sex")
        requested_z = r.get("requested_z")

        if (
            pd.isna(mth)
            or pd.isna(obs)
            or pd.isna(age_days)
            or pd.isna(sex_val)
            or pd.isna(requested_z)
        ):
            continue

        under2_params.append(
            (
                int(idx),
                str(mth),
                float(obs),
                int(age_days),
                int(sex_val),
                float(requested_z),
            )
        )
        under2_ids.append(f"under2-row-{idx}-{mth}-d{int(age_days)}")


@pytest.mark.parametrize("row_param", validation_params, ids=validation_ids)
def test_validation_csv_row(row_param):
    """Per-row validation: one pytest test per CSV row so failures/passes are shown individually."""
    idx, mth, obs, start_date, end_date, sex_val, requested_z = row_param

    # map methods
    if mth == "length":
        mm = HEIGHT
    elif mth == "weight":
        mm = WEIGHT
    elif mth == "bmi":
        mm = BMI
    elif mth in ("headc", "headcirc"):
        mm = "ofc"
    else:
        pytest.skip(f"Unknown method {mth} for row {idx}")

    # parse dates
    try:
        bd = datetime.strptime(start_date, "%Y-%m-%d")
        od = datetime.strptime(end_date, "%Y-%m-%d")
    except Exception:
        pytest.skip(f"Invalid dates for row {idx}")

    # normalize sex
    if pd.isna(sex_val):
        pytest.skip(f"Missing sex for row {idx}")
    try:
        if isinstance(sex_val, (int, float)):
            sex = (
                "male"
                if int(sex_val) == 1
                else "female" if int(sex_val) == 2 else str(sex_val)
            )
        else:
            s = str(sex_val).strip().lower()
            if s in ("1", "m", "male", "man", "boy"):
                sex = "male"
            elif s in ("2", "f", "female", "woman", "girl"):
                sex = "female"
            else:
                sex = s
    except Exception:
        sex = str(sex_val)

    meas = Measurement(
        measurement_method=mm,
        observation_value=float(obs),
        birth_date=bd,
        observation_date=od,
        sex=sex,
        reference="who",
    )
    sds = meas.measurement.get("measurement_calculated_values", {}).get(
        "chronological_sds"
    )

    assert sds == pytest.approx(float(requested_z), abs=ACCURACY)


@pytest.mark.parametrize("row_param", under2_params, ids=under2_ids)
def test_under2_gold_csv_row(row_param):
    """Per-row under-2 gold validation against anthro-generated observations."""
    idx, mth, obs, age_days, sex_val, requested_z = row_param

    if mth == "length":
        mm = HEIGHT
    elif mth == "weight":
        mm = WEIGHT
    elif mth == "bmi":
        mm = BMI
    elif mth in ("headc", "headcirc", "ofc"):
        mm = "ofc"
    else:
        pytest.skip(f"Unknown method {mth} for under2 row {idx}")

    if sex_val == 1:
        sex = "male"
    elif sex_val == 2:
        sex = "female"
    else:
        pytest.skip(f"Unknown sex value {sex_val} for under2 row {idx}")

    # Build deterministic dates from age-in-days so we can validate age-dependent SDS.
    birth_date = datetime(2000, 1, 1)
    observation_date = birth_date + pd.Timedelta(days=int(age_days))

    meas = Measurement(
        measurement_method=mm,
        observation_value=float(obs),
        birth_date=birth_date,
        observation_date=observation_date,
        sex=sex,
        reference="who",
    )
    sds = meas.measurement.get("measurement_calculated_values", {}).get(
        "chronological_sds"
    )

    assert sds == pytest.approx(float(requested_z), abs=ACCURACY)
