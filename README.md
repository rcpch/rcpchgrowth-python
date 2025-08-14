# RCPCH Digital Growth Python library

[![PyPI version](https://img.shields.io/pypi/v/rcpchgrowth.svg)](https://pypi.org/project/rcpchgrowth/)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/rcpch/rcpchgrowth-python/live?labpath=notebooks%2FQuickstart.ipynb)
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/rcpch/rcpchgrowth-python?quickstart=1)

Please go to <https://growth.rcpch.ac.uk/products/python-library/> for full documentation.

Issues can be raised here <https://github.com/rcpch/rcpchgrowth-python/issues>

---

## Installation

Minimal (algorithm only):

```bash
pip install rcpchgrowth
```

With notebook & plotting convenience dependencies:

```bash
pip install "rcpchgrowth[notebook]"
```

The `notebook` extra currently pulls in: `pandas`, `matplotlib`, `jupyterlab`, `ipykernel`.

To verify versions inside a Jupyter session:

```python
import rcpchgrowth, pandas as pd, sys
print(rcpchgrowth.__version__, pd.__version__, sys.version)
```

## Example notebooks

Example notebooks live in `notebooks/`:

- `Quickstart.ipynb` – single measurement, small batch, simple plot.
- `ResearchTemplate.ipynb` – structured workflow for batch CSV processing (ages, SDS, centiles, quality flags, export).

### Launch options

- Binder badge above opens the Quickstart notebook (branch `live`). Binder builds from this repo's `requirements.txt`; to add notebook extras inside Binder run:

  ```bash
  pip install "rcpchgrowth[notebook]"
  ```

- Codespaces badge launches a ready cloud dev environment; open the notebooks folder afterwards.

## Data handling / privacy

Do NOT place identifiable patient data in a public fork or commit history. De‑identify and keep raw data outside version control. The research template includes guidance for exporting enriched results safely.

## Basic usage (programmatic)

```python
from datetime import date
from rcpchgrowth import Measurement

sex = 'F'
dob = date(2022, 6, 15)
md  = date(2024, 2, 1)
weight_kg = 12.3

measurement = Measurement(birth_date=dob, measurement_method='weight', observation_date=md, observation_value=weight_kg, reference='uk-who', gestation_weeks=40, gestation_days=0).measurement

# Extracting the results from the measurement dictionary

# Calculated ages
chronological_age_decimal_years = measurement['measurement_dates']["chronological_decimal_age"]
corrected_age_decimal_years = measurement['measurement_dates']["corrected_decimal_age"]
chronological_calendar_age = measurement['measurement_dates']["chronological_calendar_age"] # returns age as readable text in years, months, weeks and days
corrected_calendar_age = measurement['measurement_dates']["corrected_calendar_age"] # returns age as readable text in years, months, weeks and days
# This returns corrected gestational age in weeks if the baby was premature and is not yet term.
corrected_gestational_age = measurement['measurement_dates']["corrected_gestational_age"]["corrected_gestation_weeks"]
corrected_gestational_age = measurement['measurement_dates']["corrected_gestational_age"]["corrected_gestation_days"]

# calculated SDS and centiles
corrected_weight_sds = measurement["measurement_calculated_values"]["corrected_sds"]
corrected_weight_centile = measurement["measurement_calculated_values"]["corrected_centile"]
chronological_weight_sds = measurement["measurement_calculated_values"]["chronological_sds"]
chronological_weight_centile = measurement["measurement_calculated_values"]["chronological_centile"]

print(f"Age (decimal years): {chronological_age_decimal_years:.3f}")
print(f"Weight: {weight_kg} kg | SDS: {corrected_weight_sds:.2f} | Centile: {corrected_weight_centile:.1f}")
```

---

## Contributing

See issues list and please open discussions before large changes.

---

Copyright © Royal College of Paediatrics and Child Health
