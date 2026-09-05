# Open queries

## R1 - Thrive-line public contract

**Status: blocks completion of R1.**

Should `create_thrive_lines(target_centile, sex)` return a stable JSON-serializable collection of centile and thrive-line coordinates, leaving rendering to clients, or should it retain its historical matplotlib side effect behind an optional dependency? Returning data is the recommended option and matches the architecture discussed in issue #15, but the return shape would become a new public compatibility contract.

What is the clinically supported initial scope and independent validation source for these trajectories? The current implementation has no authoritative vectors, ends at 11 rather than 12 months, produces a malformed non-monotonic sequence in `create_thrive_line`, and clips falling and rising trajectories asymmetrically. The recommended scope is explicitly experimental UK-WHO weight data until independently reviewed vectors define the supported target centiles, age endpoint, line spacing, and clipping behavior.

## QA - Exact preterm chart boundaries

**Status: blocks final completion claims for R20 and R21, but not other work.**

PR #101 contains the existing fix for exact 23-, 25-, and 42-week chart boundaries. Should that PR be merged before this QA branch is made ready for review, or should its commit be incorporated into this branch? Until one path lands, this branch will preserve the known omission as characterization and keep R20/R21 marked in progress.

## R24 - Release policy settings

**Status: resolved for R24.**

The automated cascade can require release PRs to be merged with a merge commit and can reject other merge strategies at runtime. Should GitHub repository settings also disable rebase and squash merging for release branches, or is workflow enforcement sufficient?

Existing releases prove that PyPI Trusted Publishing accepts `.github/workflows/python-publish.yml` without a GitHub environment. The implementation will preserve that workflow identity. Confirm whether a protected `pypi` environment should be introduced later; adding one requires updating PyPI's trusted-publisher configuration and any required environment reviewer would add a second human intervention after merge.

R24 enforces same-repository release branches and merge commits at runtime, so repository-wide disabling of squash and rebase remains optional defence in depth rather than a release prerequisite. It preserves the existing environment-free Trusted Publishing identity; introducing a protected `pypi` environment remains a separate coordinated policy change because it requires updating PyPI and could add another human action after merge.
