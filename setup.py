from setuptools import setup, find_packages
from pathlib import Path

here = Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

# Single-source version import (no full package import to avoid side-effects)
version_ns = {}
exec((here / "rcpchgrowth" / "_version.py").read_text(encoding="utf-8"), version_ns)

setup(
    name="rcpchgrowth",
    version=version_ns["__version__"],
    description="SDS and Centile calculations for UK Growth Data",
    long_description=long_description,
    url="https://github.com/rcpch/digital-growth-charts/blob/master/README.md",
    author="@eatyourpeas, @marcusbaw, @statist7, RCPCH Incubator",
    author_email="incubator@rcpch.ac.uk",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
    ],
    keywords="growth charts, anthropometry, SDS, centile, UK-WHO, UK90, Trisomy 21 (UK), Trisomy 21 (AAP), Turner, CDC",
    packages=find_packages(),
    python_requires=">3.8",
    install_requires=["python-dateutil", "scipy"],
    extras_require={
        "notebook": [
            "pandas>=1.5",
            "matplotlib>=3.7",
            "jupyterlab",
            "ipykernel",
        ]
    },
    include_package_data=True,
    project_urls={
        "Bug Reports": "https://github.com/rcpch/rcpchgrowth-python/issues",
        "API management": "https://dev.rcpch.ac.uk",
        "Source": "https://github.com/rcpch/rcpchgrowth-python",
    },
)
