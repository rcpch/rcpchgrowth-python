from .age_advice_strings import comment_prematurity_correction
from .bmi_functions import bmi_from_height_weight, weight_for_bmi_height
from .cdc import select_reference_data_for_cdc_chart
from .centile_bands import centile_band_for_centile
from .chart_functions import create_chart
from .constants import *  # noqa: F401,F403
from .date_calculations import chronological_decimal_age, corrected_decimal_age, chronological_calendar_age, estimated_date_delivery, corrected_gestational_age
from .dynamic_growth import create_thrive_line, return_correlation, create_thrive_lines, velocity, acceleration
from .global_functions import centile, sds_for_measurement, measurement_from_sds, percentage_median_bmi, measurement_for_z, cubic_interpolation, linear_interpolation
from .fictional_child import generate_fictional_child_data
from .measurement import Measurement
from .mid_parental_height import mid_parental_height, mid_parental_height_z, expected_height_z_from_mid_parental_height_z, lower_and_upper_limits_of_expected_height_z
from .trisomy_21 import select_reference_data_for_trisomy_21
from .trisomy_21_aap import select_reference_data_for_trisomy_21_aap
from .turner import select_reference_data_for_turner
from .uk_who import select_reference_data_for_uk_who_chart

# Version
try:
    from importlib import metadata as _md
    __version__ = _md.version("rcpchgrowth")
except Exception:
    import pathlib, sys
    _root = pathlib.Path(__file__).resolve().parent.parent
    _pyproj = _root / "pyproject.toml"
    _ver = "0.0.0+unknown"
    if _pyproj.is_file():
        try:
            if sys.version_info >= (3, 11):
                import tomllib
            else:
                import tomli as tomllib  # type: ignore
            with _pyproj.open("rb") as f:
                _data = tomllib.load(f)
            _ver = _data.get("project", {}).get("version", _ver)
        except Exception:
            pass
    __version__ = _ver