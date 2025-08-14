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
COPY rcpchgrowth/_version.py rcpchgrowth/_version.py

# Copy the full source (needed for editable install)
COPY rcpchgrowth rcpchgrowth

# Upgrade pip/setuptools/wheel first
RUN pip install --upgrade pip setuptools wheel

# Install runtime + notebook deps first (ensures wheels pulled before editable wiring)
RUN pip install python-dateutil scipy pandas matplotlib jupyterlab ipykernel

# Install dev/test tools
RUN pip install -r requirements.txt

# Finally perform editable install (should be fast now; minimal build isolation work)
RUN pip install -e . || (echo '--- Editable install failed; running pip debug ---' && python -m pip debug && exit 1)

# Bring in notebooks only after package install so they are never considered for package discovery
COPY notebooks notebooks

# Expose Jupyter port
EXPOSE 8888

# Helpful default: open bash; docker-compose can override with jupyter lab
CMD ["bash"]