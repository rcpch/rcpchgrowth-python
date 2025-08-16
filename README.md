# RCPCHGrowth Python library

## Calculations for children's measurements against UK and international growth references.

[![PyPI version](https://img.shields.io/pypi/v/rcpchgrowth.svg?style=flat-square&labelColor=%2311a7f2&color=%230d0d58)](https://pypi.org/project/rcpchgrowth/)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg?style=flat-square&labelColor=%2311a7f2&color=%230d0d58)](https://www.gnu.org/licenses/agpl-3.0)
[![Binder](https://img.shields.io/badge/Binder-Launch?style=flat-square&labelColor=%2311a7f2&color=%230d0d58&logo=binder&logoColor=white)](https://mybinder.org/v2/gh/rcpch/rcpchgrowth-python/live?labpath=notebooks%2FQuickstart.ipynb)
[![Codespaces](https://img.shields.io/badge/Codespaces-Open_in_Cloud?style=flat-square&labelColor=%2311a7f2&color=%230d0d58&logo=github&logoColor=white)](https://codespaces.new/rcpch/rcpchgrowth-python?quickstart=1)

Please go to <https://growth.rcpch.ac.uk/products/python-library/> for full documentation.

Issues can be raised here <https://github.com/rcpch/rcpchgrowth-python/issues>

---

## Installation

### Docker

If you want to avoid setting up docker environments, there are shortcut scripts the create a dockerized environment with RCPCHGrowth already installed.

First ensure the folders have the correct permissions:

```bash
chmod +x s/dev
```

To generate a container which will launch the notebooks in a browser and allow local dev ( with hot reload)

```bash
s/dev
```

### Minimal installation (assuming you have a python virtual env setup)

```bash
pip install rcpchgrowth
```

With notebook & package dependencies:

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
- `AdditionalFunctions.ipynb` - exposes some of the date and calculation functions for more in-depth exploration
- `ExperimentalFunctions.ipynb` - exposes functions that are in development and more experimental

## Data handling / privacy

<table>
<tr>
  <td width="6" style="background:#2311a7f2;"></td>
  <td>
    <strong>Data handling & privacy</strong><br>
    <strong>Never commit identifiable patient data.</strong><br>
    • Keep raw identifiable data outside version control (secure, access‑controlled).<br>
    • De‑identify before analysis (remove names, NHS numbers, full DOB; date‑shift if required).<br>
    • Do not push raw exports to forks, PRs or gists.<br>
    • Use <code>ResearchTemplate.ipynb</code> for generating de‑identified derived outputs.<br>
    <em>If in doubt, stop and seek local information governance guidance.</em>
  </td>
</tr>
</table>


---

## Contributing

See issues list and please open discussions before large changes.

---

Copyright © Royal College of Paediatrics and Child Health
