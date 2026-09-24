#!/usr/bin/env python3
"""Validate source distribution structure and package contents."""

import sys
from email.parser import Parser
from pathlib import Path
from runpy import run_path
from tarfile import open as open_tar


WHEEL_CHECKER = Path(__file__).with_name("check-wheel.py")
WHEEL_POLICY = run_path(str(WHEEL_CHECKER))
RUNTIME_RESOURCES = WHEEL_POLICY["RUNTIME_RESOURCES"]
REQUIRED_FILES = WHEEL_POLICY["REQUIRED_FILES"] | {
    "LICENSE",
    "README.md",
    "pyproject.toml",
}
ALLOWED_BUILD_METADATA = {
    "PKG-INFO",
    "rcpchgrowth.egg-info/PKG-INFO",
    "rcpchgrowth.egg-info/SOURCES.txt",
    "rcpchgrowth.egg-info/dependency_links.txt",
    "rcpchgrowth.egg-info/requires.txt",
    "rcpchgrowth.egg-info/top_level.txt",
    "setup.cfg",
}


def main() -> None:
    sdist = Path(sys.argv[1]).resolve()
    if not sdist.is_file() or not sdist.name.endswith(".tar.gz"):
        raise SystemExit(f"Not a source distribution: {sdist}")

    with open_tar(sdist, "r:gz") as archive:
        file_members = {member.name: member for member in archive if member.isfile()}
        roots = {Path(name).parts[0] for name in file_members}
        if len(roots) != 1:
            raise AssertionError(f"Expected one sdist root, found {sorted(roots)}")
        root = roots.pop()
        metadata_name = f"{root}/PKG-INFO"
        if metadata_name not in file_members:
            raise AssertionError(f"Missing sdist metadata: {metadata_name}")
        metadata_file = archive.extractfile(file_members[metadata_name])
        assert metadata_file is not None
        metadata = Parser().parsestr(metadata_file.read().decode())

    members = {name.removeprefix(f"{root}/") for name in file_members}
    missing = sorted(REQUIRED_FILES - members)
    unexpected_resources = sorted(
        name
        for name in members
        if not name.endswith(".py")
        and name not in REQUIRED_FILES
        and name not in ALLOWED_BUILD_METADATA
    )
    forbidden = sorted(
        name
        for name in members
        if "__pycache__" in name
        or name.endswith((".pyc", ".pyo"))
        or "notebooks" in Path(name).parts
        or name.startswith("rcpchgrowth/tests/")
        or "fenton" in name.casefold()
    )
    assert not missing, f"Required files missing from sdist: {missing}"
    assert not unexpected_resources, (
        f"Unapproved package resources found in sdist: {unexpected_resources}"
    )
    assert not forbidden, f"Forbidden files found in sdist: {forbidden}"
    assert metadata["Name"] == "rcpchgrowth"
    assert metadata["Version"]
    expected_name = f"rcpchgrowth-{metadata['Version']}.tar.gz"
    expected_root = f"rcpchgrowth-{metadata['Version']}"
    assert root == expected_root, (
        f"Source distribution root and metadata version differ: "
        f"{root}, {metadata['Version']}"
    )
    assert sdist.name == expected_name, (
        f"Source distribution filename and metadata version differ: "
        f"{sdist.name}, {metadata['Version']}"
    )
    print(
        f"Validated {sdist.name}: rcpchgrowth {metadata['Version']}, "
        f"{len(members)} files"
    )


if __name__ == "__main__":
    main()
