# WHO test data summary

This folder contains reference and generated datasets used to validate WHO growth calculations.

## Dataset inventory

Row counts below include header rows.

| Dataset | Rows | Purpose |
|---|---:|---|
| `random_dates.csv` | 1001 | Base random date pairs and age-in-days values used as input for fixture generation workflows. |
| `who_validation_data.csv` | 1001 | Main WHO validation fixture for measurement-to-SDS checks across methods, ages, and sexes. |
| `who_under2_gold_192.csv` | 193 | Deterministic under-2 gold-standard dataset generated from the `anthro` R package (192 cases + header). |
| `random_ages/random_dates_0_to_4.csv` | 1001 | Random date ranges focused on 0 to 4 years. |
| `random_ages/random_dates_4_to_18.csv` | 1001 | Random date ranges focused on 4 to 18 years. |
| `random_ages/fictional_child_growth_data.csv` | 1001 | Synthetic child growth records used for integration-style test data preparation. |
| `who_chart_precalculated_centiles.py` | n/a | Pre-calculated WHO centile arrays used by chart/centile tests. |

## Why `who_under2_gold_192.csv` has 192 cases

The under-2 gold-standard file is intentionally a balanced matrix:

- 2 sexes (male, female)
- 4 WHO under-2 methods (`length`, `weight`, `bmi`, `ofc`)
- 8 age anchors in days (`0`, `14`, `42`, `91`, `183`, `365`, `730`, `731`)
- 3 SDS targets (`-2`, `0`, `+2`)

Total:

- `2 x 4 x 8 x 3 = 192`

This design gives deterministic, reproducible coverage while keeping the file small enough to debug quickly.

## Design rationale

- Covers all under-2 WHO measurement methods.
- Uses symmetric SDS anchors around the median to exercise low, central, and high regions.
- Includes clinically meaningful infant milestones (birth, 2 weeks, 6 weeks, 3 months, 6 months, 12 months, 24 months).
- Includes a boundary probe at day 731 (just over 2 years) to expose edge behavior near method/reference transitions.

## Provenance

`who_under2_gold_192.csv` was generated from the local `anthro` R package using inverse LMS measurement generation for fixed SDS inputs, then moved into this folder for Python-side tests.

Key columns in this file:

- `sex`, `sex_label`
- `measurement_method`
- `age_days`, `age_months`, `age_years`
- `requested_z`
- `observation_value`
- `measurement_precision`
- `correct_extreme`