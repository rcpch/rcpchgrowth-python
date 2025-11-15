FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies if needed
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Copy requirements and setup files first for better layer caching
COPY requirements.txt setup.py MANIFEST.in README.md ./

# Install development dependencies
RUN pip install -r requirements.txt

# Copy the package source code
COPY rcpchgrowth/ ./rcpchgrowth/

# Install the package in editable/development mode
RUN pip install -e .

# Keep container running and allow interactive use
CMD ["/bin/bash"]