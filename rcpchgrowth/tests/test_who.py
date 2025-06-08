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

filenames = [
    "preschool_who_-1.csv",
    "preschool_who_-2.csv",
    "preschool_who_-3.csv",
    "preschool_who_1.csv",
    "preschool_who_2.csv",
    "preschool_who_3.csv",
    "schoolage_who_-1.csv",
    "schoolage_who_-2.csv",
    "schoolage_who_-3.csv",
    "schoolage_who_1.csv",
    "schoolage_who_2.csv",
    "schoolage_who_3.csv"
]

def load_valid_data_set(filename):
    """
    Loads in the testing data from JSON file
    """
    df = pd.read_csv(os.path.abspath(os.path.dirname(__file__)) + "/who_test_data/anthro_files/" + filename)
    return df.to_dict('records')

@pytest.mark.parametrize("filename", filenames)
class TestWHOData:
    def test_measurement_class_who_data_by_file(self, filename):
        """
        Test all rows in a specific file
        """
        try:
            rows = load_valid_data_set(filename)

            preschool_age = "preschool" in filename
            school_age = "schoolage" in filename
            
            for i, row in enumerate(rows):
                height_measurement_object = Measurement(
                    measurement_method="height",
                    observation_value=row["clenhei"] if preschool_age else row["height"],
                    birth_date=datetime.strptime(row["birth_date"], "%Y-%m-%d"),
                    observation_date=datetime.strptime(row["observation_date"], "%Y-%m-%d"),
                    sex=row["sex"],
                    reference="who"
                ).measurement
                
                weight_measurement_object = Measurement(
                    measurement_method="weight",
                    observation_value=row["weight"],
                    birth_date=datetime.strptime(row["birth_date"], "%Y-%m-%d"),
                    observation_date=datetime.strptime(row["observation_date"], "%Y-%m-%d"),
                    sex=row["sex"],
                    reference="who"
                ).measurement
                
                ofc_measurement_object = Measurement(
                    measurement_method="ofc",
                    observation_value=row["ofc"],
                    birth_date=datetime.strptime(row["birth_date"], "%Y-%m-%d"),
                    observation_date=datetime.strptime(row["observation_date"], "%Y-%m-%d"),
                    sex=row["sex"],
                    reference="who"
                ).measurement
                
                bmi_measurement_object = Measurement(
                    measurement_method="bmi",
                    observation_value=row["cbmi"],
                    birth_date=datetime.strptime(row["birth_date"], "%Y-%m-%d"),
                    observation_date=datetime.strptime(row["observation_date"], "%Y-%m-%d"),
                    sex=row["sex"],
                    reference="who"
                ).measurement
                
                if preschool_age:
                    assert round(height_measurement_object["measurement_calculated_values"]['chronological_sds'], 2) == pytest.approx(
                        row['zlen'], abs=ACCURACY
                    ), f"Row {i} - height of {row['clenhei']} in {row['sex']} of age {round(row['age_days']/365.25, 2)} ({row['age_days']} d) expected SDS of {row['zlen']} but got {height_measurement_object['measurement_calculated_values']['chronological_sds']}"
                    assert round(weight_measurement_object["measurement_calculated_values"]['chronological_sds'],2) == pytest.approx(
                        row['zwei'], abs=ACCURACY
                    ), f"Row {i} - Weight of {row['weight']} in {row['sex']} of age {round(row['age_days']/365.25, 2)} ({row['age_days']} d) expected SDS of {row['zwei']} but got {weight_measurement_object['measurement_calculated_values']['chronological_sds']}"
                    assert round(ofc_measurement_object["measurement_calculated_values"]['chronological_sds'],2) == pytest.approx(
                        row['zhc'], abs=ACCURACY
                    ), f"Row {i} - OFC of {row['ofc']} in {row['sex']} of age {round(row['age_days']/365.25, 2)} ({row['age_days']} d) expected SDS of {row['zhc']} but got {ofc_measurement_object['measurement_calculated_values']['chronological_sds']}"
                    assert round(bmi_measurement_object["measurement_calculated_values"]['chronological_sds'],2) == pytest.approx(
                        row['zbmi'], abs=ACCURACY
                    ), f"Row {i} - BMI of {row['cbmi']} in {row['sex']} of age {round(row['age_days']/365.25, 2)} ({row['age_days']} d) expected SDS of {row['zbmi']} but got {bmi_measurement_object['measurement_calculated_values']['chronological_sds']}"
                elif school_age:
                    assert round(height_measurement_object["measurement_calculated_values"]['chronological_sds'],2) == pytest.approx(
                        row['zhfa'], abs=ACCURACY
                    ), f"Row {i} - height of {row['height']} in {row['sex']} of age {round(row['age_in_months']/12,2)} ({row['age_in_months']} mo) expected SDS of {row['zhfa']} but got {height_measurement_object['measurement_calculated_values']['chronological_sds']}"
                    if not pd.isna(row['weight']): # Only check weight if it is not NaN
                        assert round(weight_measurement_object["measurement_calculated_values"]['chronological_sds'],2) == pytest.approx(
                            row['zwfa'], abs=ACCURACY
                        ), f"Row {i} - Weight of {row['weight']} in {row['sex']} of age {round(row['age_in_months']/12,2)} ({row['age_in_months']} mo) expected SDS of {row['zwfa']} but got {weight_measurement_object['measurement_calculated_values']['chronological_sds']}"
                    if pd.notna(row['cbmi']):
                        assert round(bmi_measurement_object["measurement_calculated_values"]['chronological_sds'],2) == pytest.approx(
                            row['zbfa'], abs=ACCURACY
                        ), f"Row {i} - BMI of {row['cbmi']} in {row['sex']} of age {round(row['age_in_months']/12,2)} ({row['age_in_months']} mo) expected SDS of {row['zbfa']} but got {bmi_measurement_object['measurement_calculated_values']['chronological_sds']}"
                    
        except FileNotFoundError:
            pytest.skip(f"File {filename} not found")