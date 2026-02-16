---
goal: Phase 6 - Nightly Job Orchestration Implementation
version: 1.0
date_created: 2026-02-16
last_updated: 2026-02-16
owner: Sebastian
status: 'Planned'
tags: [phase-6, jobs, docker, github-actions, automation, pipeline]
---

# Introduction

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

This phase implements the automated job orchestration for the ERA5 climate visualization pipeline. It creates Docker-based jobs that run as scheduled GitHub Actions workflows to keep the climate data and tiles up to date.

**Key outputs:**
- Daily job: Check for new ERA5 data and process new months
- Monthly job: Regenerate all tiles for the completed month
- Yearly job: Recalculate all metrics for the completed year
- GitHub Actions workflows for scheduling
- Failure notification system
- Runbook for manual operations

## 1. Requirements & Constraints

### From Master Plan

- **REQ-007**: Support monthly data updates via nightly pipeline
- **NFR-005**: Data pipeline completes nightly < 60 minutes
- **CON-004**: Maximum GitHub Actions runtime: 6 hours (free tier)

### Phase-Specific Requirements

- **REQ-P6-001**: Daily job checks for new ERA5 data and processes if available
- **REQ-P6-002**: Monthly job regenerates tiles for previous complete month on 1st
- **REQ-P6-003**: Yearly job recalculates all metrics on January 15
- **REQ-P6-004**: All jobs must be runnable locally via Docker for debugging
- **REQ-P6-005**: Jobs must validate environment variables before processing
- **REQ-P6-006**: Automatic failure notification via GitHub Issues
- **REQ-P6-007**: Job logs must be accessible for debugging
- **REQ-P6-008**: Jobs must be idempotent (safe to re-run)

### Constraints

- **CON-P6-001**: GitHub Actions free tier limits: 2000 minutes/month, 6 hour max per job
- **CON-P6-002**: Docker images should be < 1GB for fast pull times
- **CON-P6-003**: Secrets must not be exposed in logs or error messages
- **CON-P6-004**: ERA5 data has ~5 day publication delay

## 2. Implementation Steps

### Implementation Phase 6.1: Daily Job

- GOAL-P6-001: Create daily ERA5 processing job

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P6-001 | Create `jobs/job-era5-daily/Dockerfile` | | |
| TASK-P6-002 | Create `jobs/job-era5-daily/entrypoint.sh` with env validation | | |
| TASK-P6-003 | Create `jobs/job-era5-daily/src/process_daily.py` orchestrator | | |
| TASK-P6-004 | Implement new data detection logic (check CDS availability) | | |
| TASK-P6-005 | Integrate Phase 3-4 modules (fetch, interpolate, mask, tiles) | | |
| TASK-P6-006 | Add comprehensive logging and progress reporting | | |
| TASK-P6-007 | Write local test script for job execution | | |

### Implementation Phase 6.2: Monthly Job

- GOAL-P6-002: Create monthly tile regeneration job

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P6-008 | Create `jobs/job-era5-monthly/Dockerfile` | | |
| TASK-P6-009 | Create `jobs/job-era5-monthly/entrypoint.sh` | | |
| TASK-P6-010 | Create `jobs/job-era5-monthly/src/process_monthly.py` | | |
| TASK-P6-011 | Implement full month reprocessing for data corrections | | |
| TASK-P6-012 | Add tile count verification after generation | | |
| TASK-P6-013 | Write local test script | | |

### Implementation Phase 6.3: Yearly Job

- GOAL-P6-003: Create yearly metrics recalculation job

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P6-014 | Create `jobs/job-era5-yearly/Dockerfile` | | |
| TASK-P6-015 | Create `jobs/job-era5-yearly/entrypoint.sh` | | |
| TASK-P6-016 | Create `jobs/job-era5-yearly/src/process_yearly.py` | | |
| TASK-P6-017 | Integrate Phase 5 metrics modules | | |
| TASK-P6-018 | Implement full year metrics calculation | | |
| TASK-P6-019 | Add JSON export and upload | | |
| TASK-P6-020 | Write local test script | | |

### Implementation Phase 6.4: GitHub Actions Workflows

- GOAL-P6-004: Create scheduled GitHub Actions workflows

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P6-021 | Create `.github/workflows/era5-daily-pipeline.yml` | | |
| TASK-P6-022 | Create `.github/workflows/era5-monthly-pipeline.yml` | | |
| TASK-P6-023 | Create `.github/workflows/era5-yearly-pipeline.yml` | | |
| TASK-P6-024 | Configure cron schedules for each workflow | | |
| TASK-P6-025 | Add workflow_dispatch for manual triggers | | |
| TASK-P6-026 | Configure environment secrets in repository | | |

### Implementation Phase 6.5: Notifications & Monitoring

- GOAL-P6-005: Implement failure notifications and monitoring

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P6-027 | Implement GitHub Issue creation on failure | | |
| TASK-P6-028 | Add pipeline success notification (optional Slack/Discord) | | |
| TASK-P6-029 | Create monitoring dashboard or status page concept | | |
| TASK-P6-030 | Document alerting thresholds and escalation | | |

### Implementation Phase 6.6: Documentation & Testing

- GOAL-P6-006: Complete documentation and testing

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P6-031 | Create `documentation/deployment/runbook.md` | | |
| TASK-P6-032 | Document manual job execution procedures | | |
| TASK-P6-033 | Document recovery procedures for failures | | |
| TASK-P6-034 | Create job testing checklist | | |
| TASK-P6-035 | Test all workflows with manual dispatch | | |

## 3. Alternatives

- **ALT-P6-001**: **Kubernetes CronJobs instead of GitHub Actions**
  - More powerful, persistent storage
  - Rejected: Adds infrastructure cost (~€20/month), GitHub Actions free for public repos

- **ALT-P6-002**: **Single unified job instead of daily/monthly/yearly**
  - Simpler configuration
  - Rejected: Different schedules, different resource requirements, harder to debug

- **ALT-P6-003**: **AWS Lambda for serverless execution**
  - No container management
  - Rejected: 15-minute timeout limit insufficient, cold starts problematic

- **ALT-P6-004**: **Self-hosted runner on Hetzner VPS**
  - More control, no time limits
  - Rejected: Adds €5/month cost, management overhead; only needed if jobs exceed 6 hours

## 4. Dependencies

### Phase Dependencies

- **DEP-P6-001**: Phase 2 (Infrastructure) - S3 credentials and bucket configured
- **DEP-P6-002**: Phase 3 (ERA5 Pipeline) - all processing modules
- **DEP-P6-003**: Phase 4 (Tile Generation) - tile generation modules
- **DEP-P6-004**: Phase 5 (Metrics) - metrics calculation modules

### External Dependencies

- **DEP-P6-005**: GitHub Actions enabled for repository
- **DEP-P6-006**: CDS API key configured as repository secret
- **DEP-P6-007**: Hetzner S3 credentials configured as repository secrets

### Required Repository Secrets

| Secret Name | Description |
|-------------|-------------|
| `CDS_API_KEY` | Copernicus CDS API key |
| `R2_ACCESS_KEY` | Hetzner Object Storage access key |
| `R2_SECRET_KEY` | Hetzner Object Storage secret key |
| `R2_ENDPOINT_URL` | Hetzner S3 endpoint URL |
| `BUCKET_NAME` | Target bucket name |

## 5. Files

### New Files

| File ID | Path | Action | Description |
|---------|------|--------|-------------|
| FILE-P6-001 | `jobs/job-era5-daily/Dockerfile` | NEW | Daily job Docker image |
| FILE-P6-002 | `jobs/job-era5-daily/entrypoint.sh` | NEW | Daily job entrypoint |
| FILE-P6-003 | `jobs/job-era5-daily/src/process_daily.py` | NEW | Daily orchestrator |
| FILE-P6-004 | `jobs/job-era5-daily/src/check_new_data.py` | NEW | Data availability checker |
| FILE-P6-005 | `jobs/job-era5-daily/requirements.txt` | NEW | Python dependencies |
| FILE-P6-006 | `jobs/job-era5-daily/DOCKER_README.md` | NEW | Job documentation |
| FILE-P6-007 | `jobs/job-era5-monthly/Dockerfile` | NEW | Monthly job Docker image |
| FILE-P6-008 | `jobs/job-era5-monthly/entrypoint.sh` | NEW | Monthly job entrypoint |
| FILE-P6-009 | `jobs/job-era5-monthly/src/process_monthly.py` | NEW | Monthly orchestrator |
| FILE-P6-010 | `jobs/job-era5-monthly/requirements.txt` | NEW | Python dependencies |
| FILE-P6-011 | `jobs/job-era5-yearly/Dockerfile` | NEW | Yearly job Docker image |
| FILE-P6-012 | `jobs/job-era5-yearly/entrypoint.sh` | NEW | Yearly job entrypoint |
| FILE-P6-013 | `jobs/job-era5-yearly/src/process_yearly.py` | NEW | Yearly orchestrator |
| FILE-P6-014 | `jobs/job-era5-yearly/requirements.txt` | NEW | Python dependencies |
| FILE-P6-015 | `.github/workflows/era5-daily-pipeline.yml` | NEW | Daily schedule |
| FILE-P6-016 | `.github/workflows/era5-monthly-pipeline.yml` | NEW | Monthly schedule |
| FILE-P6-017 | `.github/workflows/era5-yearly-pipeline.yml` | NEW | Yearly schedule |
| FILE-P6-018 | `.github/workflows/build-era5-jobs.yml` | NEW | Docker image builder |
| FILE-P6-019 | `documentation/deployment/runbook.md` | NEW | Operations runbook |

## 6. Testing

### Job Tests

| Test ID | Description | Method |
|---------|-------------|--------|
| TEST-P6-001 | Daily job Dockerfile builds successfully | `docker build` |
| TEST-P6-002 | Daily job starts with all required env vars | Local Docker run |
| TEST-P6-003 | Daily job fails gracefully with missing env vars | Local Docker run |
| TEST-P6-004 | Daily job completes within 60 minutes | Timed local run |
| TEST-P6-005 | Monthly job processes full month | Local Docker run |
| TEST-P6-006 | Yearly job calculates all metrics | Local Docker run |
| TEST-P6-007 | GitHub Actions workflow YAML is valid | `actionlint` |
| TEST-P6-008 | Workflow manual dispatch works | GitHub UI test |

### Integration Tests

| Test ID | Description | Method |
|---------|-------------|--------|
| TEST-P6-009 | End-to-end: fetch → tiles → upload | Full pipeline run |
| TEST-P6-010 | Tiles accessible after upload | HTTP request test |
| TEST-P6-011 | Failure notification creates issue | Simulate failure |

## 7. Risks & Assumptions

### Risks

| Risk ID | Description | Probability | Impact | Mitigation |
|---------|-------------|-------------|--------|------------|
| RISK-P6-001 | GitHub Actions minutes exhausted | Low | High | Monitor usage, optimize job duration |
| RISK-P6-002 | Job exceeds 6-hour limit | Low | Medium | Split into smaller jobs, use matrix |
| RISK-P6-003 | CDS API down during scheduled run | Medium | Low | Retry next day, manual trigger |
| RISK-P6-004 | Failed upload leaves incomplete data | Medium | Medium | Atomic upload with verification |
| RISK-P6-005 | Secret exposed in error logs | Low | High | Sanitize error messages, audit logs |

### Assumptions

- **ASSUMPTION-P6-001**: GitHub Actions free tier sufficient (2000 min/month)
- **ASSUMPTION-P6-002**: ERA5 data typically available within 5 days of month end
- **ASSUMPTION-P6-003**: Pipeline duration < 60 minutes for daily job
- **ASSUMPTION-P6-004**: Repository remains public (free Actions minutes)
- **ASSUMPTION-P6-005**: Hetzner S3 API stable and compatible with boto3

## 8. Multi-Agent Execution Notes

### Execution Order

**Sequential tasks:**
1. TASK-P6-001 → TASK-P6-007 (Daily job)
2. TASK-P6-008 → TASK-P6-013 (Monthly job)
3. TASK-P6-014 → TASK-P6-020 (Yearly job)
4. TASK-P6-021 → TASK-P6-026 (GitHub Actions)
5. TASK-P6-027 → TASK-P6-035 (Monitoring & docs)

**Parallel opportunities:**
- Daily, monthly, yearly jobs can be developed in parallel
- Workflows can be developed in parallel with jobs

### Agent Context Requirements

Each agent session needs:
- This phase plan document
- Phase 3-5 module APIs (function signatures)
- Existing job patterns from `jobs/job-update-10min-station-data/`
- GitHub Actions workflow syntax reference

### Validation Checkpoints

- **After Phase 6.1**: Daily job builds and runs locally with mock data
- **After Phase 6.2**: Monthly job builds and runs locally
- **After Phase 6.3**: Yearly job builds and runs locally
- **After Phase 6.4**: All workflows pass `actionlint` validation
- **After Phase 6.5**: Test failure creates GitHub issue
- **After Phase 6.6**: All documentation reviewed

## 9. Related Specifications / Further Reading

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Actions Cron Syntax](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#schedule)
- [Docker Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- Existing job pattern: `jobs/job-update-10min-station-data/`
- Master Plan: `plan/botox/era5-germany-climate-visualization-1.md`

## 10. Code Reference

### 10.1 Daily Job Dockerfile

**File**: `jobs/job-era5-daily/Dockerfile`

```dockerfile
FROM python:3.13-slim

# Set environment
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install system dependencies for NetCDF and GDAL
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgdal-dev \
    libnetcdf-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY jobs/job-era5-daily/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy job source
COPY jobs/job-era5-daily/src ./src/

# Copy shared analysis modules
COPY analysis/era5/*.py ./src/era5/
COPY analysis/tiles/*.py ./src/tiles/
COPY analysis/utilities/upload_to_s3.py ./src/

# Create necessary __init__.py files
RUN touch ./src/era5/__init__.py ./src/tiles/__init__.py

# Copy entrypoint
COPY jobs/job-era5-daily/entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

# Create data directories
RUN mkdir -p ./data/raw ./data/interpolated ./data/masked ./data/anomalies ./data/tiles

# Default command
ENTRYPOINT ["./entrypoint.sh"]
```

### 10.2 Daily Job Entrypoint

**File**: `jobs/job-era5-daily/entrypoint.sh`

```bash
#!/bin/bash
set -e

echo "=========================================="
echo "ERA5 Daily Pipeline"
echo "Started: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "=========================================="

# Required environment variables
required_vars=(
    "CDS_API_KEY"
    "ACCESS_KEY"
    "SECRET_KEY"
    "BUCKET_NAME"
    "ENDPOINT_URL"
)

# Validate environment variables
echo ""
echo "Validating environment variables..."
missing_vars=()
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    else
        # Log presence without value (security)
        echo "  ✓ $var is set"
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo ""
    echo "ERROR: Missing required environment variables:"
    for var in "${missing_vars[@]}"; do
        echo "  ✗ $var"
    done
    exit 1
fi

# Set up CDS API credentials
echo ""
echo "Configuring CDS API..."
mkdir -p ~/.cdsapi
echo "url: https://cds.climate.copernicus.eu/api/v2" > ~/.cdsapirc
echo "key: $CDS_API_KEY" >> ~/.cdsapirc

# Run the pipeline
echo ""
echo "Starting ERA5 processing pipeline..."
python src/process_daily.py

# Report completion
echo ""
echo "=========================================="
echo "ERA5 Daily Pipeline Complete"
echo "Finished: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "=========================================="
```

### 10.3 Daily Job Orchestrator

**File**: `jobs/job-era5-daily/src/process_daily.py`

```python
#!/usr/bin/env python3
"""
ERA5 Daily Pipeline Orchestrator.

Checks for new ERA5-Land data and processes any new months available.
Runs daily but only performs work when new data is detected.
"""

import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Set up module paths
sys.path.insert(0, str(Path(__file__).parent))

from era5.fetch_era5_data import fetch_monthly_data, load_era5_data
from era5.interpolate_to_grid import interpolate_to_1km
from era5.apply_land_mask import apply_germany_land_mask
from era5.calculate_anomalies import calculate_monthly_anomaly
from tiles.generate_tiles import generate_tiles_for_geotiff
from tiles.upload_tiles import upload_tiles_for_month

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('era5-daily')


def get_target_month():
    """Calculate the target month for processing.
    
    ERA5-Land data is typically available ~5 days after month end.
    Target the previous complete month.
    
    Returns:
        Tuple of (year, month)
    """
    today = datetime.utcnow()
    
    # Go to first of current month, then back one day to get previous month
    first_of_month = today.replace(day=1)
    last_month = first_of_month - timedelta(days=1)
    
    return last_month.year, last_month.month


def check_already_processed(year: int, month: int) -> bool:
    """Check if month already processed by checking S3.
    
    Args:
        year: Year to check
        month: Month to check
        
    Returns:
        True if already processed
    """
    # For now, always process. Could check S3 for existing tiles.
    # In production, implement S3 listing check
    return False


def run_pipeline(year: int, month: int):
    """Run the full processing pipeline for a month.
    
    Args:
        year: Target year
        month: Target month (1-12)
    """
    logger.info(f"Processing ERA5-Land data for {year}-{month:02d}")
    
    # Define paths
    base_dir = Path('./data')
    raw_dir = base_dir / 'raw'
    interp_dir = base_dir / 'interpolated'
    masked_dir = base_dir / 'masked'
    anomaly_dir = base_dir / 'anomalies'
    tiles_dir = base_dir / 'tiles'
    
    # Step 1: Fetch ERA5-Land data
    logger.info("Step 1/5: Fetching ERA5-Land data...")
    try:
        raw_path = fetch_monthly_data(year, month, raw_dir)
        logger.info(f"  Downloaded: {raw_path}")
    except Exception as e:
        logger.error(f"  Failed to fetch data: {e}")
        raise
    
    # Step 2: Interpolate to 1km grid
    logger.info("Step 2/5: Interpolating to 1km grid...")
    try:
        interp_path = interpolate_to_1km(raw_path, interp_dir)
        logger.info(f"  Interpolated: {interp_path}")
    except Exception as e:
        logger.error(f"  Interpolation failed: {e}")
        raise
    
    # Step 3: Apply land mask
    logger.info("Step 3/5: Applying Germany land mask...")
    try:
        masked_path = apply_germany_land_mask(interp_path, masked_dir)
        logger.info(f"  Masked: {masked_path}")
    except Exception as e:
        logger.error(f"  Land mask failed: {e}")
        raise
    
    # Step 4: Calculate anomaly
    logger.info("Step 4/5: Calculating temperature anomaly...")
    try:
        anomaly_path = calculate_monthly_anomaly(masked_path, year, month, anomaly_dir)
        logger.info(f"  Anomaly: {anomaly_path}")
    except Exception as e:
        logger.error(f"  Anomaly calculation failed: {e}")
        raise
    
    # Step 5: Generate and upload tiles
    logger.info("Step 5/5: Generating and uploading tiles...")
    try:
        stats = generate_tiles_for_geotiff(anomaly_path, tiles_dir, year, month)
        logger.info(f"  Generated: {stats['total_tiles']} tiles ({stats['total_bytes'] / 1024 / 1024:.1f} MB)")
        
        bucket = os.environ.get('BUCKET_NAME')
        endpoint = os.environ.get('ENDPOINT_URL')
        
        upload_stats = upload_tiles_for_month(tiles_dir, bucket, year, month, endpoint)
        logger.info(f"  Uploaded: {upload_stats['success']}/{upload_stats['total']} tiles")
        
        if upload_stats['failed'] > 0:
            logger.warning(f"  Failed uploads: {upload_stats['failed']}")
            
    except Exception as e:
        logger.error(f"  Tile generation/upload failed: {e}")
        raise
    
    logger.info(f"Pipeline complete for {year}-{month:02d}")


def main():
    """Main entry point for daily pipeline."""
    logger.info("ERA5 Daily Pipeline starting...")
    
    # Get target month
    year, month = get_target_month()
    logger.info(f"Target month: {year}-{month:02d}")
    
    # Check if already processed
    if check_already_processed(year, month):
        logger.info(f"Month {year}-{month:02d} already processed. Skipping.")
        return
    
    # Run pipeline
    try:
        run_pipeline(year, month)
        logger.info("Pipeline completed successfully!")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
```

### 10.4 Daily Job Requirements

**File**: `jobs/job-era5-daily/requirements.txt`

```
# ERA5 data processing
cdsapi>=0.7.0
xarray>=2025.6.1
netCDF4>=1.7.2
scipy>=1.14.0

# Geospatial processing
rasterio>=1.4.0
geopandas>=1.0.0
shapely>=2.0.0

# Tile generation
Pillow>=10.0.0
mercantile>=1.2.0

# Storage upload
boto3>=1.38.0

# Utilities
numpy>=2.3.0
tqdm>=4.67.0
requests>=2.32.0
```

### 10.5 Monthly Job Orchestrator

**File**: `jobs/job-era5-monthly/src/process_monthly.py`

```python
#!/usr/bin/env python3
"""
ERA5 Monthly Pipeline Orchestrator.

Regenerates all tiles for the previous complete month.
This handles any data corrections from CDS.
"""

import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from era5.fetch_era5_data import fetch_monthly_data
from era5.interpolate_to_grid import interpolate_to_1km
from era5.apply_land_mask import apply_germany_land_mask
from era5.calculate_anomalies import calculate_monthly_anomaly
from tiles.generate_tiles import generate_tiles_for_geotiff
from tiles.upload_tiles import upload_tiles_for_month
from tiles.validate_tiles import validate_tile_directory

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger('era5-monthly')


def get_target_month():
    """Get the previous complete month."""
    today = datetime.utcnow()
    first_of_month = today.replace(day=1)
    last_month = first_of_month - timedelta(days=1)
    return last_month.year, last_month.month


def run_full_month_pipeline(year: int, month: int):
    """Run complete pipeline for a month with validation."""
    logger.info(f"Full month reprocessing for {year}-{month:02d}")
    
    base_dir = Path('./data')
    
    # Force re-download (might have corrections)
    logger.info("Fetching ERA5-Land data (force download)...")
    raw_path = fetch_monthly_data(year, month, base_dir / 'raw', force_download=True)
    
    # Process
    logger.info("Interpolating...")
    interp_path = interpolate_to_1km(raw_path, base_dir / 'interpolated')
    
    logger.info("Applying land mask...")
    masked_path = apply_germany_land_mask(interp_path, base_dir / 'masked')
    
    logger.info("Calculating anomaly...")
    anomaly_path = calculate_monthly_anomaly(masked_path, year, month, base_dir / 'anomalies')
    
    # Generate tiles
    logger.info("Generating tiles...")
    tiles_dir = base_dir / 'tiles'
    stats = generate_tiles_for_geotiff(anomaly_path, tiles_dir, year, month)
    logger.info(f"Generated {stats['total_tiles']} tiles")
    
    # Validate tiles before upload
    logger.info("Validating tiles...")
    validation = validate_tile_directory(tiles_dir, year, month)
    
    if not validation['valid']:
        logger.error(f"Tile validation failed: {validation}")
        raise RuntimeError("Tile validation failed")
    
    logger.info(f"Validation passed: {validation['tiles_per_zoom']}")
    
    # Upload
    logger.info("Uploading tiles...")
    bucket = os.environ.get('BUCKET_NAME')
    endpoint = os.environ.get('ENDPOINT_URL')
    
    upload_stats = upload_tiles_for_month(tiles_dir, bucket, year, month, endpoint)
    
    if upload_stats['failed'] > 0:
        logger.error(f"Upload had {upload_stats['failed']} failures")
        raise RuntimeError(f"Upload incomplete: {upload_stats['failed']} failures")
    
    logger.info(f"Upload complete: {upload_stats['success']} tiles")


def main():
    """Main entry point."""
    logger.info("ERA5 Monthly Pipeline starting...")
    
    year, month = get_target_month()
    logger.info(f"Target month: {year}-{month:02d}")
    
    try:
        run_full_month_pipeline(year, month)
        logger.info("Monthly pipeline completed successfully!")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Monthly pipeline failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
```

### 10.6 Yearly Job Orchestrator

**File**: `jobs/job-era5-yearly/src/process_yearly.py`

```python
#!/usr/bin/env python3
"""
ERA5 Yearly Pipeline Orchestrator.

Recalculates all metrics for the completed year and exports to JSON.
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from metrics.calculate_annual_anomaly import calculate_annual_anomaly, calculate_reference_climatology
from metrics.calculate_warming_rate import calculate_warming_rate
from metrics.calculate_seasonal_warming import calculate_seasonal_warming
from metrics.calculate_threshold_days import calculate_threshold_days
from metrics.calculate_comfortable_days import calculate_comfortable_days
from metrics.aggregate_metrics import load_city_list, aggregate_to_cities, aggregate_to_country
from metrics.export_metrics import export_germany_metrics, export_all_city_metrics
from upload_to_s3 import upload_file

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger('era5-yearly')


def get_target_year():
    """Get the previous complete year."""
    today = datetime.utcnow()
    return today.year - 1


def calculate_all_metrics(ds, year: int) -> dict:
    """Calculate all metrics for a year.
    
    Args:
        ds: Dataset with temperature data
        year: Target year
        
    Returns:
        LocationMetrics dictionary
    """
    calculated_at = datetime.utcnow().isoformat() + 'Z'
    
    # Calculate each metric
    logger.info("  Calculating annual anomaly...")
    annual_anomaly = calculate_annual_anomaly(ds, year)
    
    logger.info("  Calculating warming rate...")
    warming_rate = calculate_warming_rate(ds)
    
    logger.info("  Calculating seasonal warming...")
    seasonal_warming = calculate_seasonal_warming(ds, year)
    
    logger.info("  Calculating threshold days...")
    threshold_days = calculate_threshold_days(ds, year)
    
    logger.info("  Calculating comfortable days...")
    comfortable_days = calculate_comfortable_days(ds, year)
    
    # Record days would need daily records database
    # Placeholder for now
    record_days = {
        'total': 0,
        'hot': 0,
        'cold': 0,
        'year': year,
    }
    
    return {
        'calculatedAt': calculated_at,
        'annualAnomaly': annual_anomaly,
        'warmingRate': warming_rate,
        'recordDays': record_days,
        'seasonalWarming': seasonal_warming,
        'thresholdDays': threshold_days,
        'comfortableDays': comfortable_days,
    }


def run_yearly_pipeline(year: int):
    """Run full yearly metrics calculation."""
    import xarray as xr
    
    base_dir = Path('./data')
    output_dir = base_dir / 'metrics'
    
    # Load historical data (all years)
    logger.info(f"Loading ERA5 data for metrics calculation...")
    # In production, this would load from a consolidated data file
    # For now, placeholder
    ds = xr.open_dataset(base_dir / 'historical' / 'era5_land_germany.nc')
    
    # Calculate Germany-level metrics
    logger.info("Calculating Germany-level metrics...")
    germany_metrics = calculate_all_metrics(ds, year)
    
    # Export Germany metrics
    logger.info("Exporting Germany metrics...")
    germany_path = export_germany_metrics(germany_metrics, output_dir)
    
    # Calculate city-level metrics
    logger.info("Calculating city-level metrics...")
    cities = load_city_list(Path('frontend/public/german_cities_p5000.csv'))
    
    city_metrics = {}
    for _, city in cities.iterrows():
        try:
            # Select nearest grid point for city
            city_ds = ds.sel(
                latitude=city['latitude'],
                longitude=city['longitude'],
                method='nearest'
            )
            city_metrics[city['name']] = calculate_all_metrics(city_ds, year)
        except Exception as e:
            logger.warning(f"Failed to calculate metrics for {city['name']}: {e}")
    
    logger.info(f"Calculated metrics for {len(city_metrics)} cities")
    
    # Export city metrics
    logger.info("Exporting city metrics...")
    city_paths = export_all_city_metrics(city_metrics, output_dir)
    
    # Upload to S3
    logger.info("Uploading metrics to S3...")
    bucket = os.environ.get('BUCKET_NAME')
    endpoint = os.environ.get('ENDPOINT_URL')
    region = os.environ.get('REGION', 'eu-central-1')
    
    # Upload Germany
    upload_file(str(germany_path), bucket, region, endpoint, directory='metrics')
    
    # Upload cities
    for city_name, path in city_paths.items():
        upload_file(str(path), bucket, region, endpoint, directory='metrics/cities')
    
    logger.info("Upload complete!")


def main():
    """Main entry point."""
    logger.info("ERA5 Yearly Pipeline starting...")
    
    year = get_target_year()
    logger.info(f"Target year: {year}")
    
    try:
        run_yearly_pipeline(year)
        logger.info("Yearly pipeline completed successfully!")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Yearly pipeline failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
```

### 10.7 GitHub Actions Daily Workflow

**File**: `.github/workflows/era5-daily-pipeline.yml`

```yaml
name: ERA5 Daily Pipeline

on:
  schedule:
    # Run at 06:00 UTC daily
    # ERA5-Land data typically available ~5 days after month end
    - cron: '0 6 * * *'
  workflow_dispatch:
    # Allow manual trigger
    inputs:
      force_run:
        description: 'Force run even if data already processed'
        type: boolean
        default: false

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository_owner }}/era5-daily

jobs:
  run-pipeline:
    runs-on: ubuntu-latest
    timeout-minutes: 120  # 2 hour max
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          pip install -r jobs/job-era5-daily/requirements.txt
      
      - name: Set up CDS API
        run: |
          mkdir -p ~/.cdsapi
          echo "url: https://cds.climate.copernicus.eu/api/v2" > ~/.cdsapirc
          echo "key: ${{ secrets.CDS_API_KEY }}" >> ~/.cdsapirc
      
      - name: Run ERA5 daily pipeline
        env:
          CDS_API_KEY: ${{ secrets.CDS_API_KEY }}
          ACCESS_KEY: ${{ secrets.R2_ACCESS_KEY }}
          SECRET_KEY: ${{ secrets.R2_SECRET_KEY }}
          BUCKET_NAME: ${{ vars.BUCKET_NAME || 'era5-climate-tiles' }}
          ENDPOINT_URL: ${{ secrets.R2_ENDPOINT_URL }}
        run: |
          cd jobs/job-era5-daily
          python src/process_daily.py
      
      - name: Upload logs as artifact
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: pipeline-logs-${{ github.run_id }}
          path: |
            jobs/job-era5-daily/data/
            !jobs/job-era5-daily/data/**/*.nc
          retention-days: 7
      
      - name: Notify on failure
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            const title = `ERA5 Daily Pipeline Failed - ${new Date().toISOString().split('T')[0]}`;
            const body = `
            ## Pipeline Failure Report
            
            **Workflow Run:** [${context.runId}](${context.serverUrl}/${context.repo.owner}/${context.repo.repo}/actions/runs/${context.runId})
            **Triggered by:** ${context.eventName}
            **Branch:** ${context.ref}
            **Commit:** ${context.sha.substring(0, 7)}
            
            Please investigate the logs and retry if needed.
            `;
            
            await github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: title,
              body: body,
              labels: ['pipeline-failure', 'automated', 'era5']
            });
```

### 10.8 GitHub Actions Monthly Workflow

**File**: `.github/workflows/era5-monthly-pipeline.yml`

```yaml
name: ERA5 Monthly Pipeline

on:
  schedule:
    # Run on 1st of each month at 08:00 UTC
    - cron: '0 8 1 * *'
  workflow_dispatch:
    inputs:
      year:
        description: 'Year to process (default: previous month)'
        type: number
        required: false
      month:
        description: 'Month to process (1-12, default: previous month)'
        type: number
        required: false

jobs:
  run-pipeline:
    runs-on: ubuntu-latest
    timeout-minutes: 180  # 3 hour max
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          pip install -r jobs/job-era5-monthly/requirements.txt
      
      - name: Run ERA5 monthly pipeline
        env:
          CDS_API_KEY: ${{ secrets.CDS_API_KEY }}
          ACCESS_KEY: ${{ secrets.R2_ACCESS_KEY }}
          SECRET_KEY: ${{ secrets.R2_SECRET_KEY }}
          BUCKET_NAME: ${{ vars.BUCKET_NAME || 'era5-climate-tiles' }}
          ENDPOINT_URL: ${{ secrets.R2_ENDPOINT_URL }}
          TARGET_YEAR: ${{ github.event.inputs.year || '' }}
          TARGET_MONTH: ${{ github.event.inputs.month || '' }}
        run: |
          cd jobs/job-era5-monthly
          python src/process_monthly.py
      
      - name: Notify on failure
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            const title = `ERA5 Monthly Pipeline Failed - ${new Date().toISOString().split('T')[0]}`;
            await github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: title,
              body: `Monthly pipeline failed. [View run](${context.serverUrl}/${context.repo.owner}/${context.repo.repo}/actions/runs/${context.runId})`,
              labels: ['pipeline-failure', 'automated', 'era5']
            });
```

### 10.9 GitHub Actions Yearly Workflow

**File**: `.github/workflows/era5-yearly-pipeline.yml`

```yaml
name: ERA5 Yearly Pipeline

on:
  schedule:
    # Run on January 15 at 10:00 UTC
    # Gives time for December data to be available
    - cron: '0 10 15 1 *'
  workflow_dispatch:
    inputs:
      year:
        description: 'Year to process (default: previous year)'
        type: number
        required: false

jobs:
  run-pipeline:
    runs-on: ubuntu-latest
    timeout-minutes: 360  # 6 hour max (GitHub limit)
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          pip install -r jobs/job-era5-yearly/requirements.txt
      
      - name: Run ERA5 yearly pipeline
        env:
          CDS_API_KEY: ${{ secrets.CDS_API_KEY }}
          ACCESS_KEY: ${{ secrets.R2_ACCESS_KEY }}
          SECRET_KEY: ${{ secrets.R2_SECRET_KEY }}
          BUCKET_NAME: ${{ vars.BUCKET_NAME || 'era5-climate-tiles' }}
          ENDPOINT_URL: ${{ secrets.R2_ENDPOINT_URL }}
          TARGET_YEAR: ${{ github.event.inputs.year || '' }}
        run: |
          cd jobs/job-era5-yearly
          python src/process_yearly.py
      
      - name: Notify on failure
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            const title = `ERA5 Yearly Pipeline Failed - ${new Date().getFullYear()}`;
            await github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: title,
              body: `Yearly metrics calculation failed. [View run](${context.serverUrl}/${context.repo.owner}/${context.repo.repo}/actions/runs/${context.runId})`,
              labels: ['pipeline-failure', 'automated', 'era5', 'high-priority']
            });
```

### 10.10 Operations Runbook

**File**: `documentation/deployment/runbook.md`

```markdown
# ERA5 Climate Pipeline Operations Runbook

## Overview

This runbook describes operational procedures for the ERA5 climate visualization pipeline.

## Scheduled Jobs

| Job | Schedule | Duration | Purpose |
|-----|----------|----------|---------|
| Daily | 06:00 UTC daily | ~30 min | Process new monthly data |
| Monthly | 08:00 UTC, 1st | ~2 hours | Full month reprocessing |
| Yearly | 10:00 UTC, Jan 15 | ~4 hours | Recalculate all metrics |

## Manual Job Execution

### Trigger via GitHub Actions

1. Go to Actions tab in repository
2. Select workflow (era5-daily-pipeline, etc.)
3. Click "Run workflow"
4. Optionally specify parameters (year, month)
5. Click "Run workflow" button

### Run Locally via Docker

```bash
# Build image
docker build -t era5-daily -f jobs/job-era5-daily/Dockerfile .

# Run with environment variables
docker run \
  -e CDS_API_KEY="your-key" \
  -e ACCESS_KEY="your-access-key" \
  -e SECRET_KEY="your-secret-key" \
  -e BUCKET_NAME="era5-climate-tiles" \
  -e ENDPOINT_URL="https://fsn1.your-objectstorage.com" \
  era5-daily
```

## Common Issues & Resolutions

### Issue: CDS API Timeout

**Symptoms:** Job fails with "Connection timeout" or "Read timeout"

**Resolution:**
1. Check CDS status: https://cds.climate.copernicus.eu/
2. If CDS is down, wait and retry
3. If persistent, increase timeout in `fetch_era5_data.py`
4. Manual retry: Trigger workflow_dispatch

### Issue: Upload Failures

**Symptoms:** "Upload failed" errors in logs

**Resolution:**
1. Verify S3 credentials are valid
2. Check Hetzner status page
3. Verify bucket exists and is accessible
4. Re-run job - it will skip already-processed data

### Issue: Tile Validation Failure

**Symptoms:** "Tile validation failed" error

**Resolution:**
1. Check tile counts in validation output
2. Verify GeoTIFF was created correctly
3. Check disk space in runner
4. If persistent, investigate interpolation step

### Issue: GitHub Actions Minutes Exhausted

**Symptoms:** Workflows queued but not running

**Resolution:**
1. Check usage in Settings → Billing
2. Cancel non-essential runs
3. Consider larger runner with shorter duration
4. Wait for monthly reset

## Recovery Procedures

### Regenerate Tiles for a Month

```bash
# Via GitHub Actions
workflow_dispatch with year=XXXX, month=XX

# Or locally
python jobs/job-era5-monthly/src/process_monthly.py --year 2024 --month 6
```

### Regenerate All Metrics

```bash
# Via GitHub Actions
workflow_dispatch on era5-yearly-pipeline

# Or locally
python jobs/job-era5-yearly/src/process_yearly.py --year 2024
```

### Full Data Refresh

If all data needs regeneration (e.g., after algorithm change):

1. Update code with changes
2. Clear S3 bucket tiles: `aws s3 rm s3://bucket/tiles/ --recursive`
3. Run yearly job for each year
4. Verify tiles accessible

## Monitoring

### Check Job Status

- GitHub Actions: Repository → Actions tab
- Recent failures: Filter by "failure" status

### Verify Data Freshness

1. Check latest tile timestamps in S3
2. Verify metrics JSON `generatedAt` field
3. Compare to expected update date (last month's data)

### Alert Channels

- GitHub Issues: Automatic on failure (label: pipeline-failure)
- Email: Via GitHub notification settings

## Contacts

- Repository Maintainer: @tsafs
- Infrastructure: Hetzner (Object Storage)
- Data Source: Copernicus CDS
```
