# WHO Reference Implementation

Transition from UK-WHO version of WHO (where LMS values are weekly or monthly) to WHO published version of reference data where  LMS values exist for every day of life 0-5y.

## Overview

This pull request transitions the rcpchgrowth-python library from using the UK-WHO version of the WHO reference (published 2006) 0-4y to the newer WHO reference with daily LMS values (0-5 years). This represents a significant improvement in data quality and eliminates the need for interpolation.

## Historical Context

### UK-WHO Reference (2006)

The UK-WHO reference is a **hybrid reference** combining:

* **WHO data** for ages 0-4 years

* **UK90 data** for ages 4-23 years

The WHO dataset used in the UK-WHO reference (published 2006) provided Lambda, Mu, and Sigma (LMS) values at **discrete time intervals**:

* **Weekly intervals** from birth to 3 months

* **Monthly intervals** from 3 months to 4 years

This discrete interval approach meant that when a measurement was taken at an age that fell between published intervals, the library had to **interpolate** the LMS values. Interpolation introduces:

* Computational complexity

* Potential for rounding errors

* Approximation rather than exact reference values

* Variability depending on interpolation method (we use **cubic interpolation**)

### WHO Daily Reference Data

Subsequently, the World Health Organization produced an enhanced dataset with **LMS values for each day of life** from 0-5 years. This dataset:

* Provides exact LMS values for every age in the 0-5 year range

* Eliminates the need for interpolation

* Increases precision and accuracy

* Simplifies calculation logic

This in effect has pushed the interpolation step down a layer into the reference data, removing the need for it in the application layer.

## Rationale for This Change

### 1. **Improved Accuracy**

Replacing interpolated values with direct daily LMS values eliminates approximation error and provides more precise growth assessment.

### 2. **Simplified Code**

Removing interpolation logic reduces code complexity, making the calculation more maintainable and easier to understand.

### 3. **Alignment with WHO Standards**

Using the latest WHO data aligns the library with the WHO standard.

### 4. **Better Coverage**

The daily LMS values provide exact values for all ages 0-5 years, whereas the previous discrete intervals sometimes required extrapolation or approximation at boundaries.

### 5. **Reduced Computational Cost**

Eliminating interpolation calculations may improve performance, particularly for batch processing of measurements.

## Implementation Details

### What Changed

* **Test fixture**: Replaced the original `sds_age_validation_2021.json` calculations (generated from WHO weekly and monthly LMS values from UK-WHO) with `sds_age_validation_2021_refactored_2026` and renamed the original file to `sds_age_validation_2021_deprecated.json`. The new file is identical to the old file but removes 18 items that failed with the new implementation (using daily WHO values instead of the older reference). A summary of the differences is found in [LIVE_DATASET_FAILED_TESTS_SUMMARY.md](LIVE_DATASET_FAILED_TESTS_SUMMARY.md)

* **Reference data**: Updated LMS tables in `rcpchgrowth/data_tables/` to use WHO daily values

* **Calculation logic**: This is actually unchanged, but the existing methodology was always to look for exact matches before running interpolation steps. Since there are always matches with daily LMS values, the interpolation steps will always be skipped for the under 5s where the WHO standard is used.

### Test Results

During the transition from the deprecated (interpolated) fixture to the new (daily) fixture:

* **3984 test cases** pass with the new WHO daily reference data

* **18 test cases** from the old fixture failed when run against the new reference

* These 18 cases are concentrated in **preterm and early infant assessment** (before 0.5 years, mostly 27-44 weeks gestation)

* See [LIVE_DATASET_FAILED_TESTS_SUMMARY.md](LIVE_DATASET_FAILED_TESTS_SUMMARY.md) for detailed analysis

* These failures represent expected behavioral differences between the two reference systems, not bugs (see comparison by @timcole above of the LMS values between the two)

The failures in preterm assessment are likely due to:

* The fact that WHO use **linear** interpolation to generate their LMS values, not **cubic** (I make that assumption, but that is what they do in their published application code)

* The UK-WHO use 2 weeks of life as their lower limit when interpolating values, not 0 which introduces differences at this threshold (see above).

### Under-2y anthro gold dataset experiment

As an additional validation exercise, we compared requested SDS values from `who_under2_gold_192.csv` (generated via `anthro_measurements`) against SDS recalculated by this Python package for all 192 under-2 rows.

* **Headline max absolute difference**: `1.0980290423567851e-06`

* **Headline min signed difference**: `-1.0980290423567851e-06`

* **Headline max signed difference**: `7.938643615812424e-07`

This is substantially tighter than the accepted tolerance of `1e-3` and supports practical numerical equivalence for the scenarios covered by this under-2 matrix.

## WHO Chart Functions: Centile Curve Validation

### Overview

In addition to the SDS-from-measurement tests described above, the chart function tests in [rcpchgrowth/tests/test_chart_functions.py](../rcpchgrowth/tests/test_chart_functions.py) validate the **inverse direction**: given a requested SDS, what measurement value is produced? The gold standard for these tests is the centile curve data published directly by the WHO on its website:

* **Under 5 years**: [WHO Child Growth Standards](https://www.who.int/tools/child-growth-standards)
* **Over 5 years**: [WHO Growth Reference 5–19 years](https://www.who.int/tools/growth-reference-data-for-5to19-years)

These published tables list the exact measurement value expected at each centile line for each age point. By testing that `measurement_from_sds()` reproduces those values within a relative tolerance of `1e-3`, we confirm that the chart centile curves rendered by this library match what WHO itself publishes.

### Coverage

| Age range | Measurement methods | Sexes | SDS values tested | Test count |
|-----------|-------------------|-------|-------------------|------------|
| 0–5 years (`test_who_under_fives`) | weight, height, BMI, OFC | male, female | ±3.0903, ±2.33, ±1.036, ±0.67, 0, +0.67, +1.036, +2.33, +3.0903 | ~97,000 |
| 5–19 years (`test_who_over_fives`) | weight (5–10y only), height, BMI | male, female | ±3.0903, ±2.33, ±1.036, ±0.67, 0, +0.67, +1.036, +2.33, +3.0903 | ~26,000 |

Total parametrized test items: **123,061**.

### Direction and the BMI Asymmetry

It is important to note that these chart function tests exercise the **SDS → measurement** direction only. This direction uses the standard inverse-LMS formula throughout:

$$x = M \cdot (1 + L \cdot S \cdot z)^{1/L}$$

**However**, the WHO specifies a different rule when going **measurement → SDS** for extreme BMI values (i.e. z > +3 or z < −3). In that direction, WHO uses a **percentage of the 95th centile** method as a correction for the extreme tails:

* The SD3+ value is adjusted so that the distance between SD2 and SD3 is used to extrapolate linearly beyond SD3, rather than applying the standard LMS formula directly.
* This correction is documented in the WHO computation guide: [https://cdn.who.int/media/docs/default-source/child-growth/growth-reference-5-19-years/computation.pdf](https://cdn.who.int/media/docs/default-source/child-growth/growth-reference-5-19-years/computation.pdf)

**This correction is deliberately NOT applied in the SDS → measurement direction.** The WHO published centile curve values themselves do not apply this adjustment; they use pure inverse-LMS. Therefore, to ensure consistency with the WHO published chart curves, `measurement_from_sds()` does the same. The commented-out code in `global_functions.py` preserves the discarded implementation for reference.

The asymmetry is therefore intentional and correct:

| Direction | Extreme BMI rule applied? |
|-----------|--------------------------|
| Measurement → SDS (`Measurement` class, `sds_for_measurement`) | Yes — percentage-of-95th-centile correction |
| SDS → measurement (`measurement_from_sds`, chart generation) | No — pure inverse-LMS, matching WHO published curve values |

## Discrepancy at the WHO 2006/2007 5-Year Boundary

### Observation

There is a small but reproducible discontinuity in the WHO reference data at the 5-year boundary between the two WHO packages. This has been reported as [WorldHealthOrganization/anthro#64](https://github.com/WorldHealthOrganization/anthro/issues/64) (filed by the RCPCH team; no response from WHO maintainers at the time of writing).

**LMS values for boys height at the boundary**:

| Source | Age point | L | M | S |
|--------|-----------|---|---|---|
| `anthro` (WHO 2006) | 1826 days | 1 | 109.9593 | 0.04214 |
| `anthroplus` (WHO 2007) | 60 months | 1 | 109.7265 | 0.04156 |

The difference in the median (M) is **~0.23 cm**, which is small but non-trivial for a centile chart.

### Root Cause

The [published WHO 2007 growth reference PDF tables](https://cdn.who.int/media/docs/default-source/child-growth/growth-reference-5-19-years/height-for-age-(5-19-years)/hfa-boys-5-19years-per.pdf) actually begin at **61 months**, not 60 months. The `anthroplus` 60-month entry therefore does not appear to represent an empirical data point from the WHO 2007 study — it looks like a backwards-interpolated or extended value added for continuity purposes, and does not precisely match what you would obtain by linearly extrapolating from the `anthro` 1826-day values.

### How This Library Handles It

The `who_reference()` function in `who.py` uses the constant `WHO_2006_REFERENCE_UPPER_THRESHOLD = 1856 / 365.25` (~61 months, 5.079 years) as the cutoff:

* **Ages ≤ 1856 days** → `WHO_CHILD_DATA` (from `anthro`, WHO 2006)
* **Ages > 1856 days** → `WHO_2007_DATA` (from `anthroplus`, WHO 2007)

This means that at exactly 5.0 years (1826.25 days / 60 months) the library uses the **anthro WHO 2006 value** (M = 109.9593 for boys height), not the anthroplus 60-month value. This choice aligns with where the WHO 2007 published tables themselves start (61 months), and avoids using the ambiguous/interpolated `anthroplus` row at 60 months.

The practical consequence is that there is **no discontinuity in this library's output** at exactly 5 years — the transition happens at ~61 months where both the underlying data and the published tables are well-defined.

## Backward Compatibility

### API Level

The API remains unchanged. Existing code using the library will continue to work without modification.

### Numerical Results

Numerical results will differ from the UK-WHO reference for some measurements, particularly in:

* Early infancy (0-6 months)

* Preterm and late preterm infants (27-44 weeks gestation)

* The extent of difference varies by age and measurement type

These differences reflect the differences arising from interpolation between the WHO approach (which uses **linear** interpolation) and the UK-WHO approach (which uses **cubic**). These differences in the early ages possibly reflect the boundaries where interpolation starts from (42 weeks in UK-WHO and 0 y in WHO). The maximum difference between the SDS derived from each method is 0.011508556081421. This is beyond the test tolerance previously accepted in the UK-WHO implementation of `1e-3`. The rationale though is to align with WHO where this excursion is acceptable.

## Data Sources & Implementation

The WHO reference data in this library is sourced from two WHO R packages:

### **WHO anthro package** (0-5 years)

* **Repository**: [WorldHealthOrganization/anthro](https://github.com/WorldHealthOrganization/anthro)

* **Branch used**: `z-to-measurement` (RCPCH fork with inverse-LMS functions)

* **Coverage**: Children from birth to 5 years (0-1826 days)

* **Data precision**: Daily LMS values (no interpolation required)

* **Measures**: Length/height, weight, weight-for-length, BMI, head circumference

### **WHO anthroplus package** (5-19 years)

* **Repository**: [WorldHealthOrganization/anthroplus](https://github.com/WorldHealthOrganization/anthroplus)

* **Branch used**: `precision` (RCPCH fork with enhanced z-score precision control)

* **Coverage**: Children and adolescents 5-19 years (61-228 months)

* **Data precision**: Age-specific LMS values

* **Measures**: Height, weight, BMI, head circumference

### **RCPCH Modifications**

Both packages have RCPCH-maintained branches that add:

* `z_precision` parameter to control z-score decimal precision

* `anthro_measurements` / `anthroplus_measurements` inverse-LMS functions to compute measurements from requested z-scores

* Enhanced extreme value handling with `correct_extreme` parameter

* See [who-validation repository](https://github.com/rcpch/who-validation) for validation approach and helper functions

## Documentation

For more information, see:

* [AGENTS.md](../AGENTS.md) --- Development workflow and testing strategy

* [LIVE_DATASET_FAILED_TESTS_SUMMARY.md](LIVE_DATASET_FAILED_TESTS_SUMMARY.md) --- Detailed analysis of the 18 failed test cases

* [README.md](../README.md) --- Installation and quick start

## Publication References

* **UK-WHO Reference**: Cole TJ, Freeman JV, Preece MA. British 1990, British 1990r and British 1990sd reference curves for body mass index; and power derived references for weight, height and body mass index in children and adolescents. Eur J Clin Nutr. 1995;49(2):119-126.

* **WHO Growth Standards 2006**: WHO Multicentre Growth Reference Study Group. WHO Child Growth Standards: Length/height-for-age, weight-for-age, weight-for-length, weight-for-height and body mass index-for-age. Geneva: WHO; 2006. Available: [https://www.who.int/tools/child-growth-standards](https://www.who.int/tools/child-growth-standards)

* **WHO Growth Reference 2007** (5-19 years): de Onis M, Onyango AW, Borghi E, et al. Development of a WHO growth reference for school-aged children and adolescents. Bull World Health Organ. 2007;85(9):660-667. Available: [https://www.who.int/publications/i/item/9789241563369](https://www.who.int/publications/i/item/9789241563369)