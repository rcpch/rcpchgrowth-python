"""Build-time revision metadata.

`COMMIT` is deliberately `"unknown"` in checked-out source, editable installs,
and any build that has not been stamped. The PyPI publish workflow
(`.github/workflows/python-publish.yml`) overwrites this file with the
release commit SHA immediately before building the distribution, so that
released wheels/sdists report a real value via `Measurement.measurement`
provenance.
"""

COMMIT = "unknown"
