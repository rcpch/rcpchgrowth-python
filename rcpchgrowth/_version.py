__all__ = ["__version__"]

try:
	from importlib.metadata import version as _meta_version
except ImportError:  # Python <3.8 fallback not needed, but kept minimal
	from importlib_metadata import version as _meta_version  # type: ignore

try:
	__version__ = _meta_version("rcpchgrowth")
except Exception:
	__version__ = "0.0.0+unknown"
