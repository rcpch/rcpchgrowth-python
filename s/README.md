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

The script does not tag or publish. After the release PR is merged, it prints a runbook containing commands that resolve the PR's exact merge commit and create the GitHub Release from that commit. The release event triggers the existing PyPI workflow; the runbook also provides links for checking GitHub Actions, PyPI, and Zenodo.

This is a project-specific exception to the house-style CI auto-tag cascade. The existing publisher is intentionally triggered by a manually reviewed GitHub Release, so the post-merge tag and Release remain explicit runbook steps until the publishing workflow is migrated to an auto-tag and `workflow_call` design.
