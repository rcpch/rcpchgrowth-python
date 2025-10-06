"""
Handles WHO reference data selection
"""

# standard imports
import json
from importlib import resources
from pathlib import Path
import pandas as pd

# rcpch imports
from .constants import *

"""
birth_date: date of birth
observation_date: date of observation
sex: sex (string, MALE or FEMALE)
decimal_age: chronological, decimal
corrected_age: corrected for prematurity, decimal
measurement_method: height, weight, bmi, ofc (decimal)
observation: value (float)
gestation_weeks: gestational age(weeks), integer
gestation_days: supplementary days of gestation
lms: L, M or S
reference: reference data
"""

# load the reference data
data_directory = resources.files("rcpchgrowth.data_tables")
who_data_directory = data_directory.joinpath("who")

data_path = Path(
    who_data_directory, "who_infants.json")  # 2 weeks to 2 years
with open(data_path) as json_file:
    WHO_INFANTS_DATA = json.load(json_file)
    json_file.close()

data_path = Path(
    who_data_directory, "who_children.json")  # 2 years to 5 years
with open(data_path) as json_file:
    WHO_CHILD_DATA = json.load(json_file)
    json_file.close()

data_path = Path(
    who_data_directory, "who_2007_children.json")  # 5 years to 19 years
with open(data_path) as json_file:
    WHO_2007_DATA = json.load(json_file)
    json_file.close()

# public functions


def reference_data_absent(
    age: float,
    measurement_method: str,
    sex: str
):
    """
    Helper function.
    Returns boolean
    Tests presence of valid reference data for a given measurement request

    Reference data is not complete for all ages/sexes/measurements.
     - Length data is not available until 25 weeks gestation, though weight date is available from 23 weeks
     - There is only BMI reference data from 2 weeks of age to aged 20y
     - Head circumference reference data is available from 23 weeks gestation to 17y in girls and 18y in boys
     - lowest threshold is 23 weeks, upper threshold is 20y
    """

    if age < ZERO_YEARS:  # lower threshold of WHO data
        return True, "WHO data does not exist below term."

    if age > NINETEEN_YEARS:  # upper threshold of UK90 data
        return True, "WHO data does not exist above 19 years."

    if measurement_method == WEIGHT and age > TEN_YEARS:
        return True, "WHO weight data does not exist in children over 10 y of age."
    
    if measurement_method == HEAD_CIRCUMFERENCE and age > FIVE_YEARS:
        return True, "WHO head circumference data does not exist in children over 5 y of age."

    else:
        return False, ""


def who_reference(
    age: float,
    default_youngest_reference: bool = False
) -> json:
    """
    The purpose of this function is to choose the correct reference for calculation.
    The WHO standard.
    - WHO_INFANTS reference runs from 0 weeks to 2 y
    - WHO_CHILD_DATA runs from 2 years to 5 years (also stored as WHO_2006_CHILD)
    - WHO_2007_CHILD then resumes from 5 years to 19 years
    The function return the appropriate reference file as json
    """

    if age <= WHO_2006_REFERENCE_UPPER_THRESHOLD:  # 5.00 years and below
        # Children up to and including 5 years are measured using WHO 2006 data
        if (age == 2.0 and default_youngest_reference) or age < WHO_CHILD_LOWER_THRESHOLD: # 2.0 years
            # If default_youngest_reference is True, the younger reference is used to calculate values
            # This is specifically for the overlap between WHO 2006 lying and standing in centile curve generation
            # WHO 2006 reference is used for children below 2 years or those who are 2 years old and default_youngest_reference is True
            return WHO_INFANTS_DATA
        elif age <= WHO_2006_REFERENCE_UPPER_THRESHOLD: # 5.00 years
            if age <= WHO_2006_REFERENCE_UPPER_THRESHOLD and default_youngest_reference: # 5.00 years
                return WHO_CHILD_DATA
            else:
                return WHO_2007_DATA
        return WHO_CHILD_DATA
        
    elif age <= WHO_2007_REFERENCE_UPPER_THRESHOLD:
        # All children over 5 years and above are measured using WHO 2007 child data
        if default_youngest_reference:
            return WHO_CHILD_DATA
        return WHO_2007_DATA

    else:
        raise LookupError("There are no WHO reference data above the age of 19 years.")


def who_lms_array_for_measurement_and_sex(
    age: float,
    measurement_method: str,
    sex: str,
    default_youngest_reference: bool = False
) -> list:

    # selects the correct lms data array from the patchwork of references that make up WHO
    invalid_data, data_error = reference_data_absent(
        age=age,
        measurement_method=measurement_method,
        sex=sex)
    
    if invalid_data:
        raise LookupError(data_error)
    else:
        selected_reference = who_reference(
            age=age,
            default_youngest_reference=default_youngest_reference
        )
        return selected_reference["measurement"][measurement_method][sex]


def select_reference_data_for_who_chart(
    who_reference_name: str, 
    measurement_method: str, 
    sex: str,
    default_youngest_reference: bool = False):

    # takes a who_reference name (see parameter constants), measurement_method and sex to return
    # reference data

    if who_reference_name == WHO_2006_INFANT:
        try:
            who_infants_reference = who_lms_array_for_measurement_and_sex(
                age=0.04,
                measurement_method=measurement_method,
                sex=sex,
                default_youngest_reference=default_youngest_reference 
            )
        except:
            who_infants_reference = []
        return who_infants_reference
    elif who_reference_name == WHO_2006_CHILD:
        try:
            who_2006_children_reference = who_lms_array_for_measurement_and_sex(
                age=3.0,
                measurement_method=measurement_method,
                sex=sex,
                default_youngest_reference=default_youngest_reference # should never need younger reference in this calculation
            )
        except:
            who_2006_children_reference = []
        return who_2006_children_reference
    elif who_reference_name == WHO_2007_CHILD:
        try:
            who_2007_children_reference = who_lms_array_for_measurement_and_sex(
                age=6.0,
                measurement_method=measurement_method,
                sex=sex,
                default_youngest_reference=default_youngest_reference
            )
        except:
            who_2007_children_reference = []
        return who_2007_children_reference
    else:
        raise LookupError(
            f"No data found for {measurement_method} in {sex}s in {who_reference_name}")

def who_csv_reference_data_for_age_and_sex(age_days: float, sex: str, measurement_method: str) -> pd.DataFrame:
    """
    Load WHO CSV for given age band, sex, and measurement from rcpchgrowth/data_tables/who/pre_2025/.
    Filenames:
      who_2006_{measurement}_{sex}.csv   (<=5y)
      who_2007_{measurement}_{sex}.csv   (>5y; not available for OFC)
    """
    if age_days < 0:
        raise ValueError("Age cannot be negative")

    sex_key = str(sex).strip().lower()          # "male" | "female"
    meas_key = str(measurement_method).strip().lower()

    # Map common aliases -> filename token
    meas_token = {
        "head_circumference": "ofc",
        "hc": "ofc",
        "ofc": "ofc",
        "height": "height",
        "length": "height",   # if your files use 'height' for all
        "weight": "weight",
        "bmi": "bmi",
    }.get(meas_key, meas_key)

    if age_days <= 1826:  # <=5 years
        base = "who_2006"
    else:
        if meas_token == "ofc":
            raise ValueError("Head circumference data is not available for children over 5 years of age.")
        base = "who_2007"

    filename = f"{base}_{meas_token}_{sex_key}.csv"

    # CSV source directory (pre_2025)
    csv_dir = data_directory.joinpath("who", "csv")
    csv_traversable = csv_dir.joinpath(filename)

    with resources.as_file(csv_traversable) as p:
        pth = Path(p)
        if not pth.exists():
            raise FileNotFoundError(f"CSV not found: {pth}")
        return pd.read_csv(pth)