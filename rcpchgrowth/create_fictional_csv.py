from datetime import datetime, timedelta
from .global_functions import measurement_from_sds
from importlib import resources
from pathlib import Path

def generate_csv():
    """
    Generate a fictional CSV file with child growth data.
    """
    data_directory = resources.files("rcpchgrowth")

    data_path = Path(
        data_directory, "random_dates.csv") 

    import pandas as pd
    df = pd.read_csv(data_path)
    df['birth_date'] = pd.to_datetime(df['start_date'], format='%Y-%m-%d')
    df['observation_date'] = pd.to_datetime(df['start_date']) + pd.to_timedelta(df['age_days'], unit='days')
    df['observation_value'] = df['age_days'].apply(
        lambda age_days: measurement_from_sds(
            sex="male",
            reference="who", 
            measurement_method="height", 
            requested_sds=1.5, 
            age=age_days / 365.25
        )
    )
    df['sex'] = 1  # This assigns 1 to every row in the sex column
    df['measurement_method'] = "height"  # This assigns "height" to every row

    # Save to CSV (removed duplicate DataFrame creation)
    df.to_csv('fictional_child_growth_data.csv', index=False)