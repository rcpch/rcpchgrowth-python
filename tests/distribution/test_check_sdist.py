import io
import subprocess
import sys
from pathlib import Path
from runpy import run_path
from tarfile import TarInfo, open as open_tar


SCRIPT = Path(__file__).with_name("check-sdist.py")
REQUIRED_FILES = run_path(str(SCRIPT))["REQUIRED_FILES"]


def make_sdist(tmp_path, *, version="4.6.2", omitted=None, extra=()):
    sdist = tmp_path / f"rcpchgrowth-{version}.tar.gz"
    root = f"rcpchgrowth-{version}"
    members = REQUIRED_FILES - ({omitted} if omitted else set())
    with open_tar(sdist, "w:gz") as archive:
        for name in members:
            info = TarInfo(f"{root}/{name}")
            info.size = 0
            archive.addfile(info, io.BytesIO())
        metadata = f"Name: rcpchgrowth\nVersion: {version}\n".encode()
        info = TarInfo(f"{root}/PKG-INFO")
        info.size = len(metadata)
        archive.addfile(info, io.BytesIO(metadata))
        for name in extra:
            info = TarInfo(f"{root}/{name}")
            info.size = 0
            archive.addfile(info, io.BytesIO())
    return sdist


def check(sdist):
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(sdist)],
        capture_output=True,
        check=False,
        text=True,
    )


def test_accepts_minimal_valid_sdist(tmp_path):
    result = check(make_sdist(tmp_path))
    assert result.returncode == 0, result.stderr


def test_rejects_missing_runtime_resource(tmp_path):
    missing = "rcpchgrowth/data_tables/who/who_infants.json"
    result = check(make_sdist(tmp_path, omitted=missing))
    assert result.returncode != 0
    assert missing in result.stderr


def test_rejects_unapproved_package_resource(tmp_path):
    extra = "rcpchgrowth/data_tables/source/reference.csv"
    result = check(make_sdist(tmp_path, extra=(extra,)))
    assert result.returncode != 0
    assert extra in result.stderr


def test_rejects_unapproved_top_level_resource(tmp_path):
    extra = "references/source-publication.pdf"
    result = check(make_sdist(tmp_path, extra=(extra,)))
    assert result.returncode != 0
    assert extra in result.stderr


def test_rejects_fenton_path_case_insensitively(tmp_path):
    extra = "reference/FENTON-paper.pdf"
    result = check(make_sdist(tmp_path, extra=(extra,)))
    assert result.returncode != 0
    assert extra in result.stderr
