# `s/`

The `s/` directory contains convenience scripts that standardise repeated development and release processes for this repository.

## Development

- `s/up` - start the development container in the background.
- `s/down` - stop the container while preserving its image.
- `s/rebuild` - remove and rebuild the local container image, then start it.
- `s/build` - build the development container image.
- `s/logs [-f]` - show container logs, optionally following them.
- `s/shell` - open an interactive shell in the running container.
- `s/python` - open a Python REPL in the running container.
- `s/notebook` - start JupyterLab and open it in a browser.
- `s/test [pytest arguments]` - start the container if needed and run pytest.
- `s/test --running [pytest arguments]` - run pytest in an already-running container.
- `s/lint [Ruff arguments]` - run the adopted blocking Ruff rules in the development container.
- `s/lint --audit` - report the broader proposed Ruff rule set without failing.
- `s/test-wheel [wheel path]` - build or accept a wheel, inspect it, install it outside the source tree, and run package smoke tests.
- `s/test-downstream-wheel <wheel> <server commit>` - test an exact wheel against an immutable compatible server revision.
- `s/remove-containers-and-images` - stop the Compose stack and remove locally built images.

## Optional Release Preparation

`s/version++` is the optional, canonical automation for preparing a version bump. It requires a clean local `live` branch identical to `origin/live`, runs the complete test suite, updates `pyproject.toml` and `CITATION.cff`, validates the package build, creates `chore(release): vX.Y.Z` on a release branch, pushes it, and opens a PR to `live`.

- `s/version++` - prepare a patch bump.
- `s/version++ patch` - prepare a patch bump explicitly.
- `s/version++ minor` - prepare a minor bump.
- `s/version++ major` - prepare a major bump.
- `s/version++ minor --dry-run` - preview the proposed version and workflow without changing anything.

The script does not tag or publish. Review CI and merge the release PR using a merge commit; that merge is the final human release action. `.github/workflows/release-on-merge.yml` then validates the same-repository PR, its permitted files, supported version bump, synchronized metadata, and exact two-parent merge commit before creating or reusing the annotated tag and GitHub Release. It invokes `.github/workflows/python-publish.yml` to test and build once, then publishes the verified commit-stamped artifacts from the top-level workflow so PyPI Trusted Publishing and attestations use the supported workflow identity.

To exercise the complete validation, Python 3.10-3.13 test matrix, build, and artifact checks without creating a tag, GitHub Release, or PyPI publication, manually run the `Release merged version PR` workflow with the number of a merged release PR. Leave `recover_pypi_publication` disabled for this dry run. Enable it only to recover a validated release whose automatic PyPI upload failed; the workflow then verifies or reuses the existing tag and GitHub Release before rebuilding and publishing the exact merge commit. Use a release PR whose exact commit satisfies the current quality gates.
