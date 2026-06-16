FROM python:3.12-slim

# Environment hygiene
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# System deps (slim image minimal; add build-essential if future compiled deps needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    gfortran \
    libopenblas-dev \
    pkg-config \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy metadata first for build cache
COPY pyproject.toml README.md ./
COPY requirements.txt ./

# Copy the full source (needed for editable install)
COPY rcpchgrowth rcpchgrowth

# Upgrade build tooling, install the package (with notebook extras) editable,
# and install dev/test deps. Notebook extras (jupyterlab, ipykernel, pandas,
# matplotlib) and runtime deps (python-dateutil, scipy) come from pyproject.toml.
RUN pip install --upgrade pip setuptools wheel \
 && pip install -e .[notebook] \
 && pip install -r requirements.txt \
 && python -m ipykernel install --name rcpchgrowth --display-name 'rcpchgrowth' --sys-prefix

# Bring in notebooks only after package install so they are never considered for package discovery
COPY notebooks notebooks

# Expose Jupyter port
EXPOSE 8888

# Helpful default: open bash; docker-compose can override with jupyter lab
CMD ["bash"]