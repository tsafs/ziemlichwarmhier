```skill
---
name: pipeline-job
description: Add a new Python data pipeline job with fixtures, pytest tests, Docker container, and GitHub Actions stub. Use when creating data processing pipelines for station data, ERA5-Land, or HYRAS processing.
---

# Pipeline Job Skill

## Purpose

Create a new Python data pipeline job that processes weather/climate data. Covers: Python script, pytest with local fixtures, Dockerfile, entrypoint script, and GitHub Actions workflow stub.

## Prerequisites

Gather context:

```
Subagent 1: "Read jobs/ directory structure. List all job directories and their contents."
Subagent 2: "Read jobs/job-update-daily-station-data/src/ — all Python files."
Subagent 3: "Read jobs/job-update-daily-station-data/Dockerfile and entrypoint.sh."
Subagent 4: "Read analysis/utilities/upload_to_s3.py and download_from_s3.py."
Subagent 5: "Read pyproject.toml. Return: dependencies and project config."
Subagent 6: "Read .github/workflows/ — list all workflow YAML files."
```

## Architecture

```
jobs/job-<name>/
├── Dockerfile
├── DOCKER_README.md
├── entrypoint.sh
└── src/
    ├── main.py               # Entry point
    ├── <pipeline_step>.py    # Processing logic
    └── ...

analysis/tests/
├── conftest.py               # Shared fixtures
├── fixtures/
│   └── <job>/
│       ├── input_sample.csv
│       └── expected_output.csv
└── test_<job>.py             # pytest tests
```

## Implementation Steps

### Step 1: Create Pipeline Script

**Location**: `jobs/job-<name>/src/main.py`

```python
#!/usr/bin/env python3
"""
<Job description>

Processes <data source> and outputs <result>.
Designed to run in Docker container triggered by GitHub Actions.
"""

import os
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def process_data(input_path: Path, output_path: Path) -> None:
    """
    Core processing logic.

    Args:
        input_path: Path to input CSV/NetCDF
        output_path: Path to write processed output
    """
    logger.info(f"Processing {input_path} → {output_path}")

    # Read input
    # ... processing logic ...
    # Write output

    logger.info(f"Done. Output: {output_path}")


def main() -> None:
    input_dir = Path(os.environ.get("INPUT_DIR", "/data/input"))
    output_dir = Path(os.environ.get("OUTPUT_DIR", "/data/output"))

    if not input_dir.exists():
        logger.error(f"Input directory not found: {input_dir}")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    for input_file in sorted(input_dir.glob("*.csv")):
        output_file = output_dir / input_file.name
        process_data(input_file, output_file)


if __name__ == "__main__":
    main()
```

### Step 2: Create Processing Module (if needed)

**Location**: `jobs/job-<name>/src/<step>.py` or reuse from `analysis/`

```python
"""
<Step description>

Reusable processing function that can be tested independently.
"""

import csv
from pathlib import Path
from typing import Iterator


def parse_input(path: Path) -> Iterator[dict]:
    """Parse CSV input into records."""
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield {
                "date": row["date"],
                "value": float(row["value"]) if row.get("value") else None,
            }


def transform(records: Iterator[dict]) -> list[dict]:
    """Apply transformation to records."""
    return [
        {**r, "value_transformed": r["value"] * 1.0 if r["value"] is not None else None}
        for r in records
    ]


def write_output(records: list[dict], path: Path) -> None:
    """Write processed records to CSV."""
    if not records:
        return
    fieldnames = list(records[0].keys())
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
```

### Step 3: Create Test Fixtures

**Location**: `analysis/tests/fixtures/<job>/`

Input fixture — `input_sample.csv`:
```csv
date,stationId,value
2024-01-01,00044,5.2
2024-06-15,00044,22.8
2024-12-31,00044,-1.3
```

Expected output — `expected_output.csv`:
```csv
date,stationId,value,value_transformed
2024-01-01,00044,5.2,5.2
2024-06-15,00044,22.8,22.8
2024-12-31,00044,-1.3,-1.3
```

### Step 4: Write pytest Tests

**Location**: `analysis/tests/test_<job>.py`

```python
import csv
import pytest
from pathlib import Path

# Adjust import path based on job location
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "jobs" / "job-<name>" / "src"))

from main import process_data  # noqa: E402


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "<job>"


@pytest.fixture
def input_file():
    return FIXTURE_DIR / "input_sample.csv"


@pytest.fixture
def expected_output():
    return FIXTURE_DIR / "expected_output.csv"


@pytest.fixture
def tmp_output(tmp_path):
    return tmp_path / "output.csv"


def test_process_data_produces_expected_output(input_file, expected_output, tmp_output):
    """Golden test: process fixture input and compare to expected output."""
    process_data(input_file, tmp_output)

    assert tmp_output.exists(), "Output file was not created"

    with open(tmp_output) as actual, open(expected_output) as expected:
        actual_rows = list(csv.DictReader(actual))
        expected_rows = list(csv.DictReader(expected))

    assert len(actual_rows) == len(expected_rows), (
        f"Row count mismatch: {len(actual_rows)} vs {len(expected_rows)}"
    )

    for i, (a, e) in enumerate(zip(actual_rows, expected_rows)):
        assert a == e, f"Row {i} mismatch: {a} vs {e}"


def test_process_data_handles_empty_input(tmp_path):
    """Process an empty CSV (header only) without crashing."""
    empty_input = tmp_path / "empty.csv"
    empty_input.write_text("date,stationId,value\n")
    output = tmp_path / "output.csv"

    process_data(empty_input, output)
    # Should either produce empty output or header-only file


def test_process_data_missing_input_raises(tmp_path):
    """Non-existent input should raise or log error."""
    with pytest.raises((FileNotFoundError, SystemExit)):
        process_data(tmp_path / "nonexistent.csv", tmp_path / "out.csv")
```

### Step 5: Add conftest.py (if not exists)

**Location**: `analysis/tests/conftest.py`

```python
"""Shared pytest fixtures for analysis pipeline tests."""

import os
import pytest
from pathlib import Path
from unittest.mock import patch

FIXTURE_BASE = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixture_dir():
    """Base fixture directory."""
    return FIXTURE_BASE


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """Block all network access in tests by default."""
    import socket
    monkeypatch.setattr(socket, "socket", lambda *a, **kw: (_ for _ in ()).throw(
        RuntimeError("Tests must not make network calls. Use fixtures instead.")
    ))


@pytest.fixture
def mock_s3(tmp_path):
    """Mock S3 upload/download to use local tmp directory."""
    with patch.dict(os.environ, {
        "AWS_ACCESS_KEY_ID": "test",
        "AWS_SECRET_ACCESS_KEY": "test",
        "S3_ENDPOINT_URL": "http://localhost:9000",
        "S3_BUCKET_NAME": "test-bucket",
    }):
        yield tmp_path
```

### Step 6: Create Dockerfile

**Location**: `jobs/job-<name>/Dockerfile`

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install system deps if needed (e.g., for netCDF4)
# RUN apt-get update && apt-get install -y --no-install-recommends libhdf5-dev && rm -rf /var/lib/apt/lists/*

COPY src/ ./src/
COPY entrypoint.sh ./

RUN pip install --no-cache-dir requests numpy pandas

RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
```

### Step 7: Create Entrypoint

**Location**: `jobs/job-<name>/entrypoint.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "=== Starting <job-name> ==="
echo "Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

cd /app

python src/main.py

echo "=== Completed <job-name> ==="
```

### Step 8: Create GitHub Actions Workflow Stub

**Location**: `.github/workflows/docker-build-job-<name>.yml`

```yaml
name: Build and push <job-name>

on:
  push:
    branches: [main]
    paths:
      - 'jobs/job-<name>/**'

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4

      - name: Log in to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          context: jobs/job-<name>
          push: true
          tags: ghcr.io/${{ github.repository }}:<tag>-latest
```

## Run Commands

```bash
# Run tests
cd /path/to/repo && python -m pytest analysis/tests/test_<job>.py -v

# Run with coverage
python -m pytest analysis/tests/ --cov=jobs/job-<name>/src --cov-report=term-missing

# Build Docker image locally
docker build -t job-<name>:local jobs/job-<name>/

# Test Docker image
docker run --rm -v $(pwd)/analysis/tests/fixtures/<job>:/data/input -v /tmp/output:/data/output job-<name>:local
```

## Failure Modes & Self-Correction

| Failure | Cause | Fix |
|---------|-------|-----|
| `ModuleNotFoundError` in test | Wrong `sys.path.insert` | Adjust path to `jobs/job-<name>/src` |
| `no_network` fixture blocks test | Test makes HTTP call | Mock the HTTP call or use fixture file |
| Golden output mismatch | Processing logic changed | Update `expected_output.csv` after review |
| Docker build fails | Missing system dependency | Add to `apt-get install` in Dockerfile |
| Entrypoint permission denied | Missing `chmod +x` | Add `RUN chmod +x entrypoint.sh` in Dockerfile |

## Checklist

- [ ] `main.py` with `process_data()` function
- [ ] Processing module with testable pure functions
- [ ] Input fixture CSV in `analysis/tests/fixtures/<job>/`
- [ ] Expected output golden CSV
- [ ] pytest tests: golden comparison, empty input, missing input
- [ ] `conftest.py` with `no_network` fixture
- [ ] Dockerfile builds successfully
- [ ] `entrypoint.sh` runs pipeline
- [ ] GitHub Actions workflow stub created
- [ ] `pytest` passes with no network access
```
