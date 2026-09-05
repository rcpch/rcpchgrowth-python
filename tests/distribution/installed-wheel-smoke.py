#!/usr/bin/env python3
"""Exercise every runtime data family from an installed wheel."""

import os
from datetime import date, timedelta
from importlib.metadata import version
from pathlib import Path

import rcpchgrowth
from rcpchgrowth._build_info import COMMIT

REFERENCE_CASES = {
    "uk-who": ("female", 5.0),
    "who": ("male", 1.0),
    "cdc": ("male", 10.0),
    "turners-syndrome": ("female", 10.0),
    "trisomy-21": ("female", 5.0),
    "trisomy-21-aap": ("female", 5.0),
}
SERVER_ROOT_IMPORTS = {
    "Measurement",
    "centile",
    "chronological_calendar_age",
    "corrected_decimal_age",
    "create_chart",
    "generate_fictional_child_data",
    "lower_and_upper_limits_of_expected_height_z",
    "measurement_from_sds",
    "mid_parental_height_z",
    "sds_for_measurement",
}


def main() -> None:
    module_path = Path(rcpchgrowth.__file__).resolve()
    assert "site-packages" in module_path.parts, module_path
    assert rcpchgrowth.__version__ == version("rcpchgrowth")
    if expected_commit := os.environ.get("EXPECTED_COMMIT"):
        assert COMMIT == expected_commit
    assert all(hasattr(rcpchgrowth, name) for name in SERVER_ROOT_IMPORTS)

    birth_date = date(2015, 1, 1)
    for reference, (sex, age) in REFERENCE_CASES.items():
        measurement = rcpchgrowth.Measurement(
            birth_date=birth_date,
            observation_date=birth_date + timedelta(days=age * 365.25),
            measurement_method="height",
            observation_value=110.0,
            reference=reference,
            sex=sex,
        ).measurement
        assert measurement["provenance"]["growth_reference"] == reference
        assert (
            measurement["provenance"]["calculation_engine"]["version"]
            == rcpchgrowth.__version__
        )
        assert (
            measurement["measurement_calculated_values"]["chronological_sds"]
            is not None
        )
        chart = rcpchgrowth.create_chart(
            reference=reference,
            centile_format=[50],
            measurement_method="height",
            sex=sex,
        )
        assert chart and any(next(iter(component.values())) for component in chart)

    assert isinstance(rcpchgrowth.return_correlation(3, 4, "months"), float)
    assert isinstance(rcpchgrowth.return_correlation(3, 4, "weeks"), float)
    print(f"Installed-wheel smoke passed for {version('rcpchgrowth')} at {module_path}")


if __name__ == "__main__":
    main()
