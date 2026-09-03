#!/usr/bin/env python3
"""Validate the minimum wheel structure needed by runtime consumers."""

import sys
from email.parser import Parser
from pathlib import Path
from zipfile import ZipFile

REQUIRED_FILES = {
    "rcpchgrowth/__init__.py",
    "rcpchgrowth/_build_info.py",
    "rcpchgrowth/data_tables/cdc2-20.json",
    "rcpchgrowth/data_tables/cdc_infants.json",
    "rcpchgrowth/data_tables/trisomy_21.json",
    "rcpchgrowth/data_tables/trisomy_21_aap_children.json",
    "rcpchgrowth/data_tables/trisomy_21_aap_infants.json",
    "rcpchgrowth/data_tables/turner.json",
    "rcpchgrowth/data_tables/uk90_child.json",
    "rcpchgrowth/data_tables/uk90_preterm.json",
    "rcpchgrowth/data_tables/uk90_term.json",
    "rcpchgrowth/data_tables/uk_who_weight_correlation_matrices/weight_correlation_by_month.json",
    "rcpchgrowth/data_tables/uk_who_weight_correlation_matrices/weight_correlation_by_week.json",
    "rcpchgrowth/data_tables/who/pre_2025/who_infants.json",
    "rcpchgrowth/data_tables/who/who_2007_children.json",
    "rcpchgrowth/data_tables/who/who_children.json",
    "rcpchgrowth/data_tables/who/who_infants.json",
}


def main() -> None:
    wheel = Path(sys.argv[1]).resolve()
    if not wheel.is_file() or wheel.suffix != ".whl":
        raise SystemExit(f"Not a wheel: {wheel}")

    with ZipFile(wheel) as archive:
        members = set(archive.namelist())
        metadata_names = [
            name for name in members if name.endswith(".dist-info/METADATA")
        ]
        if len(metadata_names) != 1:
            raise AssertionError(f"Expected one METADATA file, found {metadata_names}")
        metadata = Parser().parsestr(archive.read(metadata_names[0]).decode())

    missing = sorted(REQUIRED_FILES - members)
    forbidden = sorted(
        name
        for name in members
        if "__pycache__" in name
        or name.endswith((".pyc", ".pyo"))
        or name.startswith("notebooks/")
    )
    assert not missing, f"Required runtime files missing from wheel: {missing}"
    assert not forbidden, f"Generated or notebook files found in wheel: {forbidden}"
    assert metadata["Name"] == "rcpchgrowth"
    assert metadata["Version"]
    print(
        f"Validated {wheel.name}: rcpchgrowth {metadata['Version']}, {len(members)} files"
    )


if __name__ == "__main__":
    main()
