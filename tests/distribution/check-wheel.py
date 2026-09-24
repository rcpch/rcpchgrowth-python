#!/usr/bin/env python3
"""Validate the exact wheel structure needed by runtime consumers."""

import sys
from email.parser import Parser
from pathlib import Path
from zipfile import ZipFile

REQUIRED_PYTHON_FILES = {
    "rcpchgrowth/__init__.py",
    "rcpchgrowth/_build_info.py",
}
RUNTIME_RESOURCES = {
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
REQUIRED_FILES = REQUIRED_PYTHON_FILES | RUNTIME_RESOURCES


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
    package_resources = {
        name
        for name in members
        if name.startswith("rcpchgrowth/")
        and not name.endswith((".py", "/"))
    }
    unexpected_resources = sorted(package_resources - RUNTIME_RESOURCES)
    forbidden = sorted(
        name
        for name in members
        if "__pycache__" in name
        or name.endswith((".pyc", ".pyo"))
        or "notebooks" in Path(name).parts
        or name.startswith("rcpchgrowth/tests/")
        or "fenton" in name.casefold()
    )
    assert not missing, f"Required runtime files missing from wheel: {missing}"
    assert not unexpected_resources, (
        f"Unapproved package resources found in wheel: {unexpected_resources}"
    )
    assert not forbidden, f"Forbidden files found in wheel: {forbidden}"
    assert metadata["Name"] == "rcpchgrowth"
    assert metadata["Version"]
    assert wheel.name.startswith(f"rcpchgrowth-{metadata['Version']}-"), (
        f"Wheel filename and metadata version differ: {wheel.name}, {metadata['Version']}"
    )
    print(
        f"Validated {wheel.name}: rcpchgrowth {metadata['Version']}, {len(members)} files"
    )


if __name__ == "__main__":
    main()
