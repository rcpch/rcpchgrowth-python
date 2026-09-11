import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[2]
SCRIPT = ROOT / ".github/scripts/validate-release.py"
SPEC = importlib.util.spec_from_file_location("validate_release", SCRIPT)
VALIDATE_RELEASE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATE_RELEASE)


def run_git(repo, *arguments):
    return subprocess.run(
        ["git", *arguments],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def metadata(version):
    return (
        f'[project]\nversion = "{version}"\n\n'
        f'[tool.bumpversion]\ncurrent_version = "{version}"\n',
        f"version: {version}\ndate-released: 2026-09-03\n",
    )


def make_merged_release(tmp_path, previous="4.6.1", release="4.6.2"):
    repo = tmp_path / "repo"
    repo.mkdir()
    run_git(repo, "init", "-b", "live")
    run_git(repo, "config", "user.name", "Release Test")
    run_git(repo, "config", "user.email", "release@example.invalid")
    run_git(repo, "config", "commit.gpgsign", "false")
    pyproject, citation = metadata(previous)
    (repo / "pyproject.toml").write_text(pyproject)
    (repo / "CITATION.cff").write_text(citation)
    run_git(repo, "add", "pyproject.toml", "CITATION.cff")
    run_git(repo, "commit", "-m", "initial")
    base_sha = run_git(repo, "rev-parse", "HEAD")

    run_git(repo, "switch", "-c", f"release/v{release}")
    pyproject, citation = metadata(release)
    (repo / "pyproject.toml").write_text(pyproject)
    (repo / "CITATION.cff").write_text(citation)
    run_git(repo, "commit", "-am", f"chore(release): v{release}")
    head_sha = run_git(repo, "rev-parse", "HEAD")
    run_git(repo, "switch", "live")
    run_git(repo, "merge", "--no-ff", f"release/v{release}", "-m", "merge release")
    merge_sha = run_git(repo, "rev-parse", "HEAD")
    return repo, base_sha, head_sha, merge_sha


@pytest.mark.parametrize(
    ("previous", "release", "expected"),
    [
        ("4.6.1", "4.6.2", "patch"),
        ("4.6.2", "4.7.0", "minor"),
        ("4.6.2", "5.0.0", "major"),
    ],
)
def test_supported_semver_bumps(previous, release, expected):
    assert VALIDATE_RELEASE.bump_kind(previous, release) == expected


@pytest.mark.parametrize("release", ["4.6.4", "4.7.1", "5.1.0", "4.6.1"])
def test_rejects_unsupported_semver_bumps(release):
    with pytest.raises(ValueError, match="Unsupported version bump"):
        VALIDATE_RELEASE.bump_kind("4.6.2", release)


def test_rejects_release_pr_with_any_other_file():
    pr = {
        "merged": True,
        "base": {"ref": "live", "sha": "a" * 40},
        "head": {
            "ref": "release/v4.6.2",
            "sha": "b" * 40,
            "repo": {"full_name": "rcpch/rcpchgrowth-python"},
        },
        "merge_commit_sha": "c" * 40,
        "title": "chore(release): v4.6.2",
    }
    files = [
        {"filename": "pyproject.toml"},
        {"filename": "CITATION.cff"},
        {"filename": "rcpchgrowth/__init__.py"},
    ]
    with pytest.raises(ValueError, match="must change exactly"):
        VALIDATE_RELEASE.validate_pr(pr, files, "rcpch/rcpchgrowth-python")


def test_cli_validates_exact_merge_commit_and_writes_outputs(tmp_path):
    repo, base_sha, head_sha, merge_sha = make_merged_release(tmp_path)
    pr = {
        "merged": True,
        "base": {"ref": "live", "sha": base_sha},
        "head": {
            "ref": "release/v4.6.2",
            "sha": head_sha,
            "repo": {"full_name": "rcpch/rcpchgrowth-python"},
        },
        "merge_commit_sha": merge_sha,
        "title": "chore(release): v4.6.2",
    }
    pr_json = tmp_path / "pr.json"
    files_json = tmp_path / "files.json"
    output = tmp_path / "output"
    pr_json.write_text(json.dumps(pr))
    files_json.write_text(
        json.dumps(
            [{"filename": "pyproject.toml"}, {"filename": "CITATION.cff"}]
        )
    )

    result = subprocess.run(
        [
            sys.executable,
            SCRIPT,
            "--pr-json",
            pr_json,
            "--files-json",
            files_json,
            "--repository",
            "rcpch/rcpchgrowth-python",
            "--repo",
            repo,
            "--github-output",
            output,
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert json.loads(result.stdout)["merge_sha"] == merge_sha
    assert "tag=v4.6.2" in output.read_text().splitlines()
    assert "bump=patch" in output.read_text().splitlines()


def test_rejects_non_merge_commit(tmp_path):
    repo, base_sha, head_sha, _ = make_merged_release(tmp_path)
    with pytest.raises(ValueError, match="Checked-out commit"):
        VALIDATE_RELEASE.validate_repository(
            repo, head_sha, base_sha, head_sha, "4.6.2"
        )


def test_rejects_non_calendar_release_date():
    pyproject, _ = metadata("4.6.2")
    citation = "version: 4.6.2\ndate-released: 20260903\n"
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        VALIDATE_RELEASE.validate_metadata(pyproject, citation, "4.6.2")
