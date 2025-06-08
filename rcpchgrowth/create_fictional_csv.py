from .global_functions import measurement_from_sds
from importlib import resources
from pathlib import Path

def measurement_for_reference(reference: str, measurement_method: str, age_days: int, sds: float, sex: str):

    meets_threshold = False
    
    if reference == "who":
        
        if measurement_method == "weight":
            if age_days < 365.25 * 10:
                meets_threshold = True
        elif measurement_method == "ofc":
            if age_days <= 365.25 * 5:
                meets_threshold = True
        elif measurement_method in ["height", "bmi"]:
            meets_threshold = True
        
        return measurement_from_sds(
                sex=sex,
                reference=reference, 
                measurement_method=measurement_method, 
                requested_sds=sds, 
                age=age_days / 365.25
            ) if meets_threshold else None


def generate_csv(sds, reference: str = "who", age_group: str = "preschool"):
    """
    Generate a fictional CSV file with child growth data.
    """
    data_directory = resources.files("rcpchgrowth")

    zero_to_four_data_path = Path(
        data_directory, "tests/who_test_data/random_ages/random_dates_0_to_4.csv")
    four_to_nineteen_data_path = Path(
        data_directory, "tests/who_test_data/random_ages/random_dates_4_to_18.csv")

    import pandas as pd
    all_data = []
    for sex in ['male', 'female']:
        df = pd.read_csv(zero_to_four_data_path if age_group == "preschool" else four_to_nineteen_data_path)
        df["sex"] = sex
        df['birth_date'] = pd.to_datetime(df['start_date'], format='%Y-%m-%d')
        df['observation_date'] = pd.to_datetime(df['start_date']) + pd.to_timedelta(df['age_days'], unit='days')
        for new_col in ['height', 'weight', 'ofc']:
            df[new_col] = df['age_days'].apply(
                lambda age_days: measurement_for_reference(
                    reference=reference,
                    measurement_method=new_col,
                    age_days=age_days,
                    sex=sex,
                    sds=sds
                )
            )
        all_data.append(df)

    final_df = pd.concat(all_data, ignore_index=True)

    # Save to CSV (removed duplicate DataFrame creation)
    final_df.to_csv(f'rcpchgrowth/tests/who_test_data/{age_group}_{reference}_{sds}.csv', index=False)

def create_csvs():
    """
    Create CSV files for different combinations of SDS, measurement method, sex, and reference.
    """
    sds_values = [-3, -2, -1, 1, 2, 3]
    for sds in sds_values:
        for age_group in ["preschool", "schoolage"]:
                generate_csv(sds, reference="who", age_group=age_group)

def create_random_dates_csv(num_rows=100, start_date='2010-01-01', start_age_days=0, end_age_days=3650):
    """
    Create a CSV file with random dates for testing.
    """
    import pandas as pd
    from datetime import datetime, timedelta
    import random

    start_date = datetime(2010, 1, 1)
    
    random_age_days = [random.randint(start_age_days, end_age_days) for _ in range(num_rows)]

    data = {
        'start_date': [start_date +  timedelta(days=days) for days in random_age_days],
        'age_days': random_age_days
    }

    df = pd.DataFrame(data)
    df.to_csv(f'rcpchgrowth/tests/random_dates_{int(start_age_days/365)}_to_{int(end_age_days/365)}.csv', index=False)