# Pre-cleanup baseline

This baseline implements the evidence record required by R17 before mechanical maintenance changes. It was recorded on 2026-09-03 from the tree committed with this document, after rebasing the R16-R23 quality-gate implementation onto `v4.6.2`.

## Environment

- Container runtime: Python 3.13.13
- Test runner: pytest 9.1.1
- Full command: `s/test --running -q -rs`
- Result: 145239 collected, 145239 passed, 0 skipped, 0 failed in 167.84 seconds

## Fixture integrity

The primary UK-WHO fixture `rcpchgrowth/tests/sds_age_validation_2021_refactored_2026.json` contains 3984 cases. Its SHA-256 digest is `e269b3ff4312bca76563eb8adc7d0e9941b655077d11888b34522c3ffe2f6c84`. `test_fixture_integrity.py` enforces the count, digest, and complete field set without changing the fixture.

## Focused commands

- Calculation pipeline: `s/test --running rcpchgrowth/tests/test_global_functions.py rcpchgrowth/tests/test_uk_who.py -q`
- Measurement response contract: `s/test --running rcpchgrowth/tests/test_measurement_contract.py rcpchgrowth/tests/test_provenance.py -q`
- Chart generation: `s/test --running rcpchgrowth/tests/test_chart_functions.py rcpchgrowth/tests/test_chart_age_grids.py rcpchgrowth/tests/test_chart_age_two_overlap.py -q -rs`
- Source-package imports and fixture integrity: `s/test --running rcpchgrowth/tests/test_public_api_contract.py rcpchgrowth/tests/test_fixture_integrity.py -q`
- Adopted Ruff checks: `s/lint --running`
- Broader non-blocking Ruff audit: `s/lint --running --audit`
- Installed-wheel contract: `s/test-wheel`
- Complete supported suite: `s/test --running -q -rs`

## Downstream compatibility

The downstream runner was exercised with `digital-growth-charts-server` PR #280 commit `6918e3b8152963345f4c0996e7bd52bacf904583` and the published `rcpchgrowth` 4.6.0 wheel. The server suite passed 1066 tests with one documented skip, and both pinned React profiles passed all 47 assertions. This verifies the runner at those exact revisions, not against PR #280's moving head or the current candidate parcel. Repeat the gate with a commit-stamped candidate wheel against PR #280's immutable merge commit after it adopts the canonical engine identifier.
