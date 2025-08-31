# standard imports
from datetime import datetime
import json
import os
from pprint import pprint
import pandas as pd

# third-party imports
import pytest

# rcpch imports
from rcpchgrowth import Measurement, who_z_for_measurement
from rcpchgrowth.constants import HEIGHT, WEIGHT, BMI

# the ACCURACY constant defines the accuracy of the test comparisons
# owing to variations in statistical calculations it's impossible to get exact
# agreement between R and Python, so our statistician feels we can set a tolerance
# within which we will accept a result as correct.
ACCURACY = 1e-2

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
            
            failed_assertions = []
            processed_rows = 0
            
            for i, row in enumerate(rows):
                try:
                    # Skip rows with missing critical data
                    if pd.isna(row.get('birth_date')) or pd.isna(row.get('observation_date')):
                        continue
                        
                    if pd.isna(row.get('sex')):
                        continue
                    
                    processed_rows += 1
                    
                    # Height measurement
                    height_value = row["clenhei"] if preschool_age else row["height"]
                    if pd.notna(height_value):
                        height_measurement_object = Measurement(
                            measurement_method="height",
                            observation_value=height_value,
                            birth_date=datetime.strptime(row["birth_date"], "%Y-%m-%d"),
                            observation_date=datetime.strptime(row["observation_date"], "%Y-%m-%d"),
                            sex=row["sex"],
                            reference="who"
                        ).measurement
                        # assert int(row['age_days']) == (row['observation_date'] - row['birth_date']).days, f"Row {i} - Age days mismatch: {row['age_days']} vs calculated {(row['observation_date'] - row['birth_date']).days}"

                    # Weight measurement (only if weight is not NaN)
                    if pd.notna(row.get('weight')):
                        weight_measurement_object = Measurement(
                            measurement_method="weight",
                            observation_value=row["weight"],
                            birth_date=datetime.strptime(row["birth_date"], "%Y-%m-%d"),
                            observation_date=datetime.strptime(row["observation_date"], "%Y-%m-%d"),
                            sex=row["sex"],
                            reference="who"
                        ).measurement
                    
                    # OFC measurement (only if ofc is not NaN)
                    if pd.notna(row.get('ofc')):
                        ofc_measurement_object = Measurement(
                            measurement_method="ofc",
                            observation_value=row["ofc"],
                            birth_date=datetime.strptime(row["birth_date"], "%Y-%m-%d"),
                            observation_date=datetime.strptime(row["observation_date"], "%Y-%m-%d"),
                            sex=row["sex"],
                            reference="who"
                        ).measurement
                    
                    # BMI measurement (only if cbmi is not NaN)
                    if pd.notna(row.get('cbmi')):
                        bmi_measurement_object = Measurement(
                            measurement_method="bmi",
                            observation_value=row["cbmi"],
                            birth_date=datetime.strptime(row["birth_date"], "%Y-%m-%d"),
                            observation_date=datetime.strptime(row["observation_date"], "%Y-%m-%d"),
                            sex=row["sex"],
                            reference="who"
                        ).measurement
                    
                    height_z = Measurement(
                        measurement_method=HEIGHT,
                        observation_value=row["clenhei"] if preschool_age else row["height"],
                        birth_date=datetime.strptime(row["birth_date"], "%Y-%m-%d"),
                        observation_date=datetime.strptime(row["observation_date"], "%Y-%m-%d"),
                        sex=row["sex"],
                        reference="who",
                    ).measurement["measurement_calculated_values"]["chronological_sds"]
                    if pd.notna(row.get('weight')):
                        weight_z = Measurement(
                            measurement_method=WEIGHT,
                            observation_value=row["weight"],
                            birth_date=datetime.strptime(row["birth_date"], "%Y-%m-%d"),
                            observation_date=datetime.strptime(row["observation_date"], "%Y-%m-%d"),
                            sex=row["sex"],
                            reference="who",
                        ).measurement["measurement_calculated_values"]["chronological_sds"]
                    if pd.notna(row.get('ofc')):
                        ofc_z = Measurement(
                            measurement_method="ofc",
                            observation_value=row["ofc"],
                            birth_date=datetime.strptime(row["birth_date"], "%Y-%m-%d"),
                            observation_date=datetime.strptime(row["observation_date"], "%Y-%m-%d"),
                            sex=row["sex"],
                            reference="who",
                        ).measurement["measurement_calculated_values"]["chronological_sds"]
                    if pd.notna(row.get('cbmi')):
                        bmi_z = Measurement(
                            measurement_method=BMI,
                            observation_value=row["cbmi"],
                            birth_date=datetime.strptime(row["birth_date"], "%Y-%m-%d"),
                            observation_date=datetime.strptime(row["observation_date"], "%Y-%m-%d"),
                            sex=row["sex"],
                            reference="who",
                        ).measurement["measurement_calculated_values"]["chronological_sds"]
                    

                    
                    # Assertions - collect failures instead of stopping
                    if preschool_age:
                        if pd.notna(height_value) and pd.notna(row.get('zlen')):
                            try:
                                assert height_measurement_object["measurement_calculated_values"]['chronological_sds'] == pytest.approx(row['zlen'], abs=ACCURACY
                                ), f"Row {i} - RCPCH: height of {height_value} in {row['sex']} of age {round(row['age_days']/365.25, 4)} ({row['age_days']} d) expected SDS of {row['zlen']} but got {height_measurement_object['measurement_calculated_values']['chronological_sds']}"
                                assert height_z == pytest.approx(
                                    row['zlen'], abs=ACCURACY
                                ), f"Row {i} - WHO: height of {height_value} in {row['sex']} of age {round(row['age_days']/365.25, 4)} ({row['age_days']} d) expected SDS of {row['zlen']} but got {height_measurement_object['measurement_calculated_values']['chronological_sds']}"
                            except AssertionError as e:
                                failed_assertions.append(str(e))
                                
                        if pd.notna(row.get('weight')) and pd.notna(row.get('zwei')):
                            try:
                                assert round(weight_measurement_object["measurement_calculated_values"]['chronological_sds'],2) == pytest.approx(
                                    row['zwei'], abs=ACCURACY
                                ), f"Row {i} - RCPCH: Weight of {row['weight']} in {row['sex']} of age {round(row['age_days']/365.25, 2)} ({row['age_days']} d) expected SDS of {row['zwei']} but got {weight_measurement_object['measurement_calculated_values']['chronological_sds']}"
                                assert weight_z == pytest.approx(
                                    row['zwei'], abs=ACCURACY
                                ), f"Row {i} - WHO: Weight of {row['weight']} in {row['sex']} of age {round(row['age_days']/365.25, 2)} ({row['age_days']} d) expected SDS of {row['zwei']} but got {weight_measurement_object['measurement_calculated_values']['chronological_sds']}"
                            except AssertionError as e:
                                failed_assertions.append(str(e))
                                
                        if pd.notna(row.get('ofc')) and pd.notna(row.get('zhc')):
                            try:
                                assert round(ofc_measurement_object["measurement_calculated_values"]['chronological_sds'],2) == pytest.approx(
                                    row['zhc'], abs=ACCURACY
                                ), f"Row {i} - RCPCH: OFC of {row['ofc']} in {row['sex']} of age {round(row['age_days']/365.25, 2)} ({row['age_days']} d) expected SDS of {row['zhc']} but got {ofc_measurement_object['measurement_calculated_values']['chronological_sds']}"
                                assert ofc_z == pytest.approx(
                                    row['zhc'], abs=ACCURACY
                                ), f"Row {i} - WHO: OFC of {row['ofc']} in {row['sex']} of age {round(row['age_days']/365.25, 2)} ({row['age_days']} d) expected SDS of {row['zhc']} but got {ofc_measurement_object['measurement_calculated_values']['chronological_sds']}"
                            except AssertionError as e:
                                failed_assertions.append(str(e))
                                
                        if pd.notna(row.get('cbmi')) and pd.notna(row.get('zbmi')):
                            try:
                                assert round(bmi_measurement_object["measurement_calculated_values"]['chronological_sds'],2) == pytest.approx(
                                    row['zbmi'], abs=ACCURACY
                                ), f"Row {i} - RCPCH: BMI of {row['cbmi']} in {row['sex']} of age {round(row['age_days']/365.25, 2)} ({row['age_days']} d) expected SDS of {row['zbmi']} but got {bmi_measurement_object['measurement_calculated_values']['chronological_sds']}"
                                assert bmi_z == pytest.approx(
                                    row['zbmi'], abs=ACCURACY
                                ), f"Row {i} - WHO: BMI of {row['cbmi']} in {row['sex']} of age {round(row['age_days']/365.25, 2)} ({row['age_days']} d) expected SDS of {row['zbmi']} but got {bmi_measurement_object['measurement_calculated_values']['chronological_sds']}"
                            except AssertionError as e:
                                failed_assertions.append(str(e))
                                
                    elif school_age:
                        # Similar pattern for school age...
                        if pd.notna(height_value) and pd.notna(row.get('zhfa')):
                            try:
                                assert height_z == pytest.approx(
                                    row['zhfa'], abs=ACCURACY
                                ), f"Row {i} - WHO: height of {height_value} in {row['sex']} of age {round(row['age_in_months']* 30.4375,2)} ({row['age_in_months']} mo) expected SDS of {row['zhfa']} but got {height_z}"
                            except AssertionError as e:
                                failed_assertions.append(str(e))
                        if pd.notna(row.get('weight')) and pd.notna(row.get('zwfa')):
                            try:
                                assert weight_z == pytest.approx(
                                    row['zwfa'], abs=ACCURACY
                                ), f"Row {i} - WHO: Weight of {row['weight']} in {row['sex']} of age {round(row['age_in_months']* 30.4375,2)} ({row['age_in_months']} mo) expected SDS of {row['zwfa']} but got {weight_z}"
                            except AssertionError as e:
                                failed_assertions.append(str(e))
                                
                except Exception as e:
                    failed_assertions.append(f"Row {i} - Exception: {str(e)}, {row}")
                    continue
            
            # Report summary
            print(f"File: {filename} - Processed {processed_rows} out of {len(rows)} rows")
            
            # If there were failures, report them all at once
            if failed_assertions:
                failure_summary = f"File {filename} of length {len(rows)} had {len(failed_assertions)} failures:\n" + "\n".join(failed_assertions[:10])  # Show first 10 failures
                if len(failed_assertions) > 10:
                    failure_summary += f"\n... and {len(failed_assertions) - 10} more failures"
                pytest.fail(failure_summary)
                
        except FileNotFoundError:
            pytest.skip(f"File {filename} not found")