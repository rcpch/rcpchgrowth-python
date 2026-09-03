import subprocess
import sys
from pathlib import Path
from runpy import run_path
from zipfile import ZipFile


SCRIPT = Path(__file__).with_name("check-wheel.py")
REQUIRED_FILES = run_path(str(SCRIPT))["REQUIRED_FILES"]


def make_wheel(tmp_path, *, version="4.6.2", omitted=None, extra=()):
    wheel = tmp_path / f"rcpchgrowth-{version}-py3-none-any.whl"
    members = REQUIRED_FILES - ({omitted} if omitted else set())
    with ZipFile(wheel, "w") as archive:
        for name in members:
            archive.writestr(name, "")
        archive.writestr(
            f"rcpchgrowth-{version}.dist-info/METADATA",
            f"Name: rcpchgrowth\nVersion: {version}\n",
        )
        for name in extra:
            archive.writestr(name, "")
    return wheel


def check(wheel):
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(wheel)],
        capture_output=True,
        check=False,
        text=True,
    )


def test_accepts_minimal_valid_wheel(tmp_path):
    result = check(make_wheel(tmp_path))
    assert result.returncode == 0, result.stderr


def test_rejects_missing_runtime_resource(tmp_path):
    missing = "rcpchgrowth/data_tables/who/who_infants.json"
    result = check(make_wheel(tmp_path, omitted=missing))
    assert result.returncode != 0
    assert missing in result.stderr


def test_rejects_nested_notebook_content(tmp_path):
    result = check(make_wheel(tmp_path, extra=("rcpchgrowth/notebooks/demo.ipynb",)))
    assert result.returncode != 0
    assert "demo.ipynb" in result.stderr


def test_rejects_filename_metadata_version_mismatch(tmp_path):
    wheel = make_wheel(tmp_path)
    mismatched = wheel.with_name("rcpchgrowth-4.6.1-py3-none-any.whl")
    wheel.rename(mismatched)
    result = check(mismatched)
    assert result.returncode != 0
    assert "filename and metadata version differ" in result.stderr


def test_rejects_multiple_metadata_files(tmp_path):
    wheel = make_wheel(tmp_path)
    with ZipFile(wheel, "a") as archive:
        archive.writestr("other-1.0.dist-info/METADATA", "Name: other\nVersion: 1.0\n")
    result = check(wheel)
    assert result.returncode != 0
    assert "Expected one METADATA file" in result.stderr
