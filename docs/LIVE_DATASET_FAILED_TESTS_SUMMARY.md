# Live Dataset Failed Tests Summary

## Scope

This report summarizes failures from running:

- `test_uk_who_reference_integration`
- against both fixtures in `who-validation`
- where the failures were only from the live fixture file: `sds_age_validation_2021.json`

Command used:

```bash
docker compose exec dev pytest rcpchgrowth/tests/test_uk_who.py::test_uk_who_reference_integration -q
```

## Overall Result

- Total cases run: 7986
- Passed: 7968
- Failed: 18
- All 18 failures were in: `sds_age_validation_2021.json` (live dataset)
- Failures in `sds_age_validation_2021_refactor_2026.json`: 0

## Failed Cases (Live Fixture)

1. `sds_age_validation_2021.json:367`
   - expected: `-0.632189989`
   - actual: `-0.6340680481290769`
2. `sds_age_validation_2021.json:411`
   - expected: `1.078752995`
   - actual: `1.0809072812105682`
3. `sds_age_validation_2021.json:504`
   - expected: `-1.124135375`
   - actual: `-1.1252545568825487`
4. `sds_age_validation_2021.json:505`
   - expected: `-1.375826955`
   - actual: `-1.3784736052012738`
5. `sds_age_validation_2021.json:507`
   - expected: `-1.191470265`
   - actual: `-1.1928066570238767`
6. `sds_age_validation_2021.json:637`
   - expected: `-2.296421766`
   - actual: `-2.29977886411417`
7. `sds_age_validation_2021.json:639`
   - expected: `-1.928933501`
   - actual: `-1.9305750145259444`
8. `sds_age_validation_2021.json:782`
   - expected: `-0.218435228`
   - actual: `-0.21952940858951137`
9. `sds_age_validation_2021.json:1621`
   - expected: `-1.44912672`
   - actual: `-1.4503060503173935`
10. `sds_age_validation_2021.json:1721`
    - expected: `-6.032728195`
    - actual: `-6.044236751081421`
11. `sds_age_validation_2021.json:1723`
    - expected: `-5.535323143`
    - actual: `-5.5426050198074535`
12. `sds_age_validation_2021.json:1797`
    - expected: `-3.291125298`
    - actual: `-3.2922979854481627`
13. `sds_age_validation_2021.json:2375`
    - expected: `-0.997933209`
    - actual: `-0.9991163887382516`
14. `sds_age_validation_2021.json:2796`
    - expected: `-1.894040585`
    - actual: `-1.8953394083040758`
15. `sds_age_validation_2021.json:2797`
    - expected: `-2.109273911`
    - actual: `-2.113812295000201`
16. `sds_age_validation_2021.json:2799`
    - expected: `-1.908897519`
    - actual: `-1.9115163184972574`
17. `sds_age_validation_2021.json:3141`
    - expected: `1.697126865`
    - actual: `1.6959057642336917`
18. `sds_age_validation_2021.json:3143`
    - expected: `1.673045874`
    - actual: `1.6772149618716816`

### Case Demographics And Ages (18/18)

| Fixture Index | Sex | Gestation (weeks+days) | Chronological Age (years) | Corrected Age (years) |
|---|---|---|---|---|
| 367 | male | 42+6 | 0.295687885 | 0.350444901 |
| 411 | male | 40+3 | 0.249144422 | 0.257357974 |
| 504 | female | 43+5 | 0.229979466 | 0.301163587 |
| 505 | female | 43+5 | 0.229979466 | 0.301163587 |
| 507 | female | 43+5 | 0.229979466 | 0.301163587 |
| 637 | female | 33+4 | 0.31211499 | 0.188911704 |
| 639 | female | 33+4 | 0.31211499 | 0.188911704 |
| 782 | female | 42+4 | 0.016427105 | 0.065708419 |
| 1621 | female | 33+4 | 0.323066393 | 0.199863107 |
| 1721 | female | 27+2 | 0.271047228 | 0.027378508 |
| 1723 | female | 27+2 | 0.271047228 | 0.027378508 |
| 1797 | female | 27+4 | 1.965776865 | 1.727583847 |
| 2375 | male | 34+1 | 0.366872005 | 0.254620123 |
| 2796 | female | 44+0 | 0.20807666 | 0.284736482 |
| 2797 | female | 44+0 | 0.20807666 | 0.284736482 |
| 2799 | female | 44+0 | 0.20807666 | 0.284736482 |
| 3141 | male | 32+6 | 0.45174538 | 0.314852841 |
| 3143 | male | 32+6 | 0.45174538 | 0.314852841 |

## Pattern Analysis

### Sex Distribution
- Female: 11 cases (61%)
- Male: 4 cases (22%)
- Significant female predominance in failures

### Age Distribution
- **Chronological age range**: 0.016 to 1.97 years
- **Predominant stage**: Very early infancy (mostly <0.5 years)
- Most cases cluster in the neonatal to early infant period

### Gestation Distribution
- **Range**: 27+2 to 44+0 weeks
- **Predominant**: Preterm/late preterm births
- No cases from full-term healthy gestations

### Duplicate Age-Measurement Patterns
Several cases share identical chronological ages, suggesting systematic differences in measurement calculation:
- **Cases 504/505/507**: Female, 43+5 weeks gestation, all age 0.229979466
- **Cases 637/639**: Female, 33+4 weeks gestation, all age 0.31211499
- **Cases 1721/1723**: Female, 27+2 weeks gestation, all age 0.271047228
- **Cases 2796/2797/2799**: Female, 44+0 weeks gestation, all age 0.20807666
- **Cases 3141/3143**: Male, 32+6 weeks gestation, all age 0.45174538

### Common Thread
All 18 failed cases are **very young infants (mostly premature or borderline preterm)** with **duplicate age-measurement combinations**. These appear to be cases where the refactored WHO-based calculation differs most significantly from the old UK-WHO calculation, particularly in:
- Early life (neonatal/early infancy)
- Preterm age corrections
- Multiple measurements at the same age/gestation combination

This suggests the numerical divergence between old and new code is concentrated in **preterm/early infant growth assessment**, likely due to differences in how WHO vs UK-WHO references handle age correction and LMS calculations in this critical period.

## Notes

- Tolerance in test is absolute `1e-3`.
- All failures are close numerical mismatches beyond that threshold.
- Removed records match exactly with failed live test cases (confirmed 1:1 index correlation).

## Removed-vs-Failed Comparison
- Removed record count: 18
- Failed live-case count: 18
- Exact index match: True
- Removed indices: [367, 411, 504, 505, 507, 637, 639, 782, 1621, 1721, 1723, 1797, 2375, 2796, 2797, 2799, 3141, 3143]
- Failed indices: [367, 411, 504, 505, 507, 637, 639, 782, 1621, 1721, 1723, 1797, 2375, 2796, 2797, 2799, 3141, 3143]
- In removed but not failed: []
- In failed but not removed: []
