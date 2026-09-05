#!/usr/bin/env python3
"""Validate that a merged release PR is safe to publish."""

import argparse
import json
import re
import subprocess
from datetime import date
from pathlib import Path


ALLOWED_FILES = {"CITATION.cff", "pyproject.toml"}
SHA_PATTERN = re.compile(r"[0-9a-f]{40}")
VERSION_PATTERN = re.compile(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)")


def fail(message):
    raise ValueError(message)


def git(repo, *arguments):
    return subprocess.run(
        ["git", *arguments],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def toml_value(contents, section, key):
    current_section = None
    for line in contents.splitlines():
        section_match = re.fullmatch(r"\s*\[([^]]+)]\s*", line)
        if section_match:
            current_section = section_match.group(1)
            continue
        if current_section == section:
            value_match = re.fullmatch(
                rf'\s*{re.escape(key)}\s*=\s*"([^"]+)"\s*(?:#.*)?', line
            )
            if value_match:
                return value_match.group(1)
    fail(f"Missing {key!r} in [{section}]")


def citation_value(contents, key):
    match = re.search(rf"^{re.escape(key)}:\s*['\"]?([^'\"\s]+)['\"]?\s*$", contents, re.MULTILINE)
    if not match:
        fail(f"Missing {key!r} in CITATION.cff")
    return match.group(1)


def parse_version(value):
    match = VERSION_PATTERN.fullmatch(value)
    if not match:
        fail(f"Version is not supported semantic version X.Y.Z: {value!r}")
    return tuple(int(part) for part in match.groups())


def bump_kind(previous, release):
    old = parse_version(previous)
    new = parse_version(release)
    supported = {
        (old[0], old[1], old[2] + 1): "patch",
        (old[0], old[1] + 1, 0): "minor",
        (old[0] + 1, 0, 0): "major",
    }
    if new not in supported:
        fail(f"Unsupported version bump: {previous} -> {release}")
    return supported[new]


def validate_metadata(pyproject, citation, expected_version):
    versions = {
        "project.version": toml_value(pyproject, "project", "version"),
        "tool.bumpversion.current_version": toml_value(
            pyproject, "tool.bumpversion", "current_version"
        ),
        "CITATION.cff version": citation_value(citation, "version"),
    }
    mismatches = {name: value for name, value in versions.items() if value != expected_version}
    if mismatches:
        fail(f"Release metadata is not synchronized to {expected_version}: {mismatches}")
    release_date = citation_value(citation, "date-released")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", release_date):
        fail(f"CITATION.cff date-released is not YYYY-MM-DD: {release_date!r}")
    try:
        date.fromisoformat(release_date)
    except ValueError:
        fail(f"CITATION.cff date-released is not a valid date: {release_date!r}")
    return release_date


def validate_pr(pr, files, repository):
    if not pr.get("merged"):
        fail("Release PR is not merged")
    if pr.get("base", {}).get("ref") != "live":
        fail("Release PR does not target live")
    if pr.get("head", {}).get("repo", {}).get("full_name") != repository:
        fail("Release PR must originate in the same repository")

    head_ref = pr.get("head", {}).get("ref", "")
    branch_match = re.fullmatch(r"release/v(.+)", head_ref)
    if not branch_match:
        fail(f"Invalid release branch: {head_ref!r}")
    version = branch_match.group(1)
    parse_version(version)
    if pr.get("title") != f"chore(release): v{version}":
        fail("Release PR title does not match its version")

    changed_files = {item.get("filename") for item in files}
    if changed_files != ALLOWED_FILES or len(files) != len(ALLOWED_FILES):
        fail(
            "Release PR must change exactly pyproject.toml and CITATION.cff; "
            f"found {sorted(str(item) for item in changed_files)}"
        )

    merge_sha = pr.get("merge_commit_sha", "")
    base_sha = pr.get("base", {}).get("sha", "")
    head_sha = pr.get("head", {}).get("sha", "")
    for name, value in (("merge", merge_sha), ("base", base_sha), ("head", head_sha)):
        if not SHA_PATTERN.fullmatch(value):
            fail(f"PR has an invalid {name} commit SHA")
    return version, merge_sha, base_sha, head_sha


def validate_repository(repo, merge_sha, base_sha, head_sha, version):
    head = git(repo, "rev-parse", "HEAD")
    if head != merge_sha:
        fail(f"Checked-out commit {head} is not PR merge commit {merge_sha}")

    commit = git(repo, "rev-list", "--parents", "-n", "1", merge_sha).split()
    if len(commit) != 3:
        fail("Release PR must use a two-parent merge commit")
    if commit[1:] != [base_sha, head_sha]:
        fail("Merge commit parents do not match the PR base and head commits")

    pyproject = git(repo, "show", f"{merge_sha}:pyproject.toml")
    citation = git(repo, "show", f"{merge_sha}:CITATION.cff")
    release_date = validate_metadata(pyproject, citation, version)
    previous_pyproject = git(repo, "show", f"{base_sha}:pyproject.toml")
    previous_version = toml_value(previous_pyproject, "project", "version")
    kind = bump_kind(previous_version, version)
    return previous_version, kind, release_date


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pr-json", type=Path, required=True)
    parser.add_argument("--files-json", type=Path, required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--github-output", type=Path)
    args = parser.parse_args()

    pr = json.loads(args.pr_json.read_text())
    files = json.loads(args.files_json.read_text())
    version, merge_sha, base_sha, head_sha = validate_pr(pr, files, args.repository)
    previous_version, kind, release_date = validate_repository(
        args.repo, merge_sha, base_sha, head_sha, version
    )
    result = {
        "base_sha": base_sha,
        "bump": kind,
        "merge_sha": merge_sha,
        "previous_version": previous_version,
        "release_date": release_date,
        "tag": f"v{version}",
        "version": version,
    }
    if args.github_output:
        with args.github_output.open("a") as output:
            for name, value in result.items():
                output.write(f"{name}={value}\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
