# AGENTS.md - Guidance for AI/LLM Development

This document provides context and guidance for AI agents, LLMs, and automated tools working on the rcpchgrowth-python repository.

## Project Overview

**rcpchgrowth-python** is a Python library for calculating children's growth measurements against UK and international growth references.

### WHO reference migration (completed)

The library previously derived WHO reference L, M, S values by cubic interpolation against a sparse (weekly/monthly) table. [PR #80](https://github.com/rcpch/rcpchgrowth-python/pull/80) replaced this with WHO's officially-published per-day LMS table, aligning with WHO's own `anthro`/`anthroplus` reference implementation. This merged into `live` as part of the 4.5.x releases; there is no separate `who-validation` branch any more. See the [WHO Reference Implementation](https://growth.rcpch.ac.uk/developer/who-reference-implementation/) page in the documentation site for what changed and why, including the 18 fixture cases whose expected values changed in the transition.

Note: this repository does not keep project documentation. Developer, clinician, integrator and researcher docs live in the separate [digital-growth-charts-documentation](https://github.com/rcpch/digital-growth-charts-documentation) repository, published at [growth.rcpch.ac.uk](https://growth.rcpch.ac.uk).

## Development Workflow

### Container-Based Development

The project uses Docker for a consistent development environment. Always use the convenience scripts in the `s/` folder:

```bash
s/up          # Start container
s/notebook    # Launch JupyterLab
s/test        # Run pytest (auto-starts container if needed)
s/test --running  # Run pytest in already-running container
s/shell       # Interactive bash in container
s/down        # Stop container
```

**Key Point**: The container runs JupyterLab in the background, enabling both interactive notebook development AND command-line test execution simultaneously.

## Testing Strategy

### Test Fixtures

**Standard fixture** (new):

- `rcpchgrowth/tests/sds_age_validation_2021_refactored_2026.json` - 3984 test cases generated from WHO data
- All tests pass against this fixture
- This is the current/target state

**Deprecated fixture** (old):

- `rcpchgrowth/tests/sds_age_validation_2021_deprecated.json` - 4002 test cases from live branch
- 18 test cases removed during transition (see the [WHO Reference Implementation](https://growth.rcpch.ac.uk/developer/who-reference-implementation/) page)
- Kept for regression testing if needed

WHO dataset details:

- `rcpchgrowth/tests/who_test_data/README.md` - Inventory of WHO test files and rationale for `who_under2_gold_192.csv`

### Running Tests

```bash
# Run the UK-WHO integration suite
s/test rcpchgrowth/tests/test_uk_who.py -v

# Run all tests
s/test

# In an already-running container
s/test --running rcpchgrowth/tests/ -v
```

## Key Code Locations

| Component | Location |
|-----------|----------|
| Main library | `rcpchgrowth/` |
| Measurement calculation | `rcpchgrowth/measurement.py` |
| Tests | `rcpchgrowth/tests/` |
| Test data | `rcpchgrowth/tests/sds_age_validation_2021_refactored_2026.json` |
| Reference data | `rcpchgrowth/data_tables/` |
| Documentation | Separate repo: [digital-growth-charts-documentation](https://github.com/rcpch/digital-growth-charts-documentation) ([growth.rcpch.ac.uk](https://growth.rcpch.ac.uk)) |

## Important Considerations for LLM Development

### Test Fixture Strategy

The test fixture is **fixed and finite** (3984 cases). When modifying calculation logic:

1. Run tests to identify failures
2. Analyze whether failures are expected (intentional algorithm changes) or bugs
3. Do NOT modify test fixtures without explicit user direction
4. Document any intentional test failures in PR comments

### Preterm/Early Infant Focus

The 18 removed test cases (from the WHO reference migration) were concentrated in:

- Very early infancy (mostly <0.5 years)
- Preterm/late preterm births (27+2 to 44+0 weeks gestation)
- 61% female cases with duplicate age-measurement combinations

This indicates **largest numerical divergence between UK-WHO and WHO occurs in preterm/early infant assessment**. When debugging calculation differences, prioritize these scenarios.

### Reference Data

WHO reference data is loaded from `rcpchgrowth/data_tables/`:

- LMS values (Lambda, Mu, Sigma) stored as JSON
- Age-corrected calculations for preterm infants (up to 2 years)
- Different handling vs. UK-WHO; be cautious with age correction logic

### Git Branch Context

- **live** (main production branch) - the WHO reference migration is merged here; releases are cut from `live`
- The `who-validation` branch has been retired - do not target it
- Do not push directly to `live`; open a PR for review

## Documentation for Developers

- [WHO Reference Implementation](https://growth.rcpch.ac.uk/developer/who-reference-implementation/) - the WHO daily-LMS migration, the BMI direction asymmetry, the 5-year boundary, and the 18 removed fixture cases
- [README.md](README.md) - Installation and quick-start (human-focused, but useful context)

## Common Tasks

### Adding a New Feature

1. Write test cases in `rcpchgrowth/tests/`
2. Implement feature in appropriate module
3. Run `s/test` to validate
4. If test fixture needs updating, document justification

### Debugging a Test Failure

1. Check if it's a known issue in the [WHO Reference Implementation](https://growth.rcpch.ac.uk/developer/who-reference-implementation/) page
2. Run specific test with `-v` flag for full output
3. Inspect test fixture data for the failing case
4. Compare old vs. new calculation if transitioning between reference systems

### Environment Issues

If container fails to start or tests don't run:

1. `s/down` then `s/up` to restart
2. Check `docker compose logs` for errors
3. Verify pytest installed: `s/test --running --version`
4. See docker-compose.yml for setup command

## Contact & Issues

- Issues: https://github.com/rcpch/rcpchgrowth-python/issues
- Repository: https://github.com/rcpch/rcpchgrowth-python
- Documentation: https://growth.rcpch.ac.uk/products/python-library/
