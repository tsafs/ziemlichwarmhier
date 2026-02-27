#!/usr/bin/env python3
"""
process_daily.py - Daily ERA5 pipeline orchestrator.

Determines which months in the last 3 months need processing (ERA5-Land has a
~5-day publication delay), then for each unprocessed month:
  1. Fetch monthly ERA5-Land data
  2. Apply Germany land mask
  3. Calculate temperature anomaly vs 1961-1990 reference climatology
  4. Export anomaly GeoTIFF
  5. Generate map tiles
  6. Upload tiles to S3
  7. Validate tile coverage

Environment variables:
  CDS_API_KEY       - Copernicus CDS API key (required)
  ACCESS_KEY        - S3 access key (required)
  SECRET_KEY        - S3 secret key (required)
  ENDPOINT_URL      - S3 endpoint URL (required)
  BUCKET_NAME       - S3 bucket name (required)
  FORCE_REPROCESS   - Set to "true" to skip idempotency check and reprocess (optional)
  CLIMATE_DATA_PROVIDER - Override provider id (optional, defaults to "era5-land")
"""

import json
import logging
import os
import sys
from datetime import date, timedelta
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

from analysis.era5.providers import get_provider
from analysis.era5.fetch_era5_data import (
    fetch_monthly_data,
    fetch_reference_climatology,
    load_era5_data,
)
from analysis.era5.apply_land_mask import apply_germany_land_mask
from analysis.era5.calculate_anomalies import calculate_monthly_anomaly, export_anomaly_geotiff
from analysis.tiles.generate_tiles import generate_tiles_for_geotiff
from analysis.tiles.upload_tiles import upload_tiles_from_env
from analysis.tiles.validate_tiles import validate_tile_coverage

from check_new_data import check_era5_data_available

# ---------------------------------------------------------------------------
# Logging setup – structured JSON output
# ---------------------------------------------------------------------------

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "time": self.formatTime(record, "%Y-%m-%dT%H:%M:%SZ"),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload)


def setup_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(handler)


logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# S3 helpers
# ---------------------------------------------------------------------------

def _s3_client():
    return boto3.client(
        "s3",
        endpoint_url=os.environ["ENDPOINT_URL"],
        aws_access_key_id=os.environ["ACCESS_KEY"],
        aws_secret_access_key=os.environ["SECRET_KEY"],
    )


def tiles_exist_in_s3(year: int, month: int, bucket: str) -> bool:
    """Return True if at least one tile already exists for the given month."""
    prefix = f"tiles/{year}/{month:02d}/"
    client = _s3_client()
    try:
        response = client.list_objects_v2(Bucket=bucket, Prefix=prefix, MaxKeys=1)
        return bool(response.get("Contents"))
    except ClientError as exc:
        logger.warning("S3 list_objects failed: %s", exc)
        return False


# ---------------------------------------------------------------------------
# Months to process
# ---------------------------------------------------------------------------

def months_to_process() -> list[tuple[int, int]]:
    """
    Return list of (year, month) tuples for the last 3 months (excluding current
    incomplete month) that have published ERA5-Land data.
    """
    today = date.today()
    # Start from the month before the current one, go back 3 months total
    candidates = []
    for offset in range(1, 4):
        first_of_month = date(today.year, today.month, 1)
        # subtract offset months
        target = first_of_month - timedelta(days=offset * 31)
        target = date(target.year, target.month, 1)
        candidates.append((target.year, target.month))
    return candidates


# ---------------------------------------------------------------------------
# Per-month pipeline
# ---------------------------------------------------------------------------

def process_month(
    year: int,
    month: int,
    provider,
    data_dir: Path,
    output_dir: Path,
    reference_ds,
    force: bool,
    bucket: str,
) -> bool:
    """
    Run the full pipeline for a single year/month.
    Returns True on success, False on failure.
    """
    log_ctx = {"year": year, "month": month}

    # Idempotency check
    if not force and tiles_exist_in_s3(year, month, bucket):
        logger.info("Tiles already exist in S3, skipping", extra=log_ctx)
        return True

    logger.info("Checking CDS data availability", extra=log_ctx)
    if not check_era5_data_available(year, month):
        logger.info("ERA5 data not yet available for this month, skipping", extra=log_ctx)
        return True

    try:
        # 1. Fetch
        logger.info("Fetching monthly ERA5 data", extra=log_ctx)
        raw_path = fetch_monthly_data(provider, year, month, data_dir, force=force)

        # 2. Load + land mask
        logger.info("Loading dataset and applying land mask", extra=log_ctx)
        ds = load_era5_data(raw_path)
        ds_masked = apply_germany_land_mask(ds, provider)

        # 3. Anomaly
        logger.info("Calculating temperature anomaly", extra=log_ctx)
        anomaly_ds = calculate_monthly_anomaly(ds_masked, reference_ds, year, month)

        # 4. Export GeoTIFF
        geotiff_path = output_dir / f"anomaly_{year}_{month:02d}.tif"
        logger.info("Exporting GeoTIFF to %s", geotiff_path, extra=log_ctx)
        export_anomaly_geotiff(anomaly_ds, geotiff_path)

        # 5. Generate tiles
        tile_dir = output_dir / "tiles" / f"{year}" / f"{month:02d}"
        logger.info("Generating map tiles", extra=log_ctx)
        tile_count = generate_tiles_for_geotiff(geotiff_path, tile_dir, year, month)
        logger.info("Generated %d tiles", tile_count, extra=log_ctx)

        # 6. Upload tiles
        logger.info("Uploading tiles to S3", extra=log_ctx)
        uploaded = upload_tiles_from_env(tile_dir, year, month)
        logger.info("Uploaded %d tiles", uploaded, extra=log_ctx)

        # 7. Validate
        logger.info("Validating tile coverage", extra=log_ctx)
        result = validate_tile_coverage(tile_dir, year, month)
        if not result.is_valid:
            logger.error("Tile validation failed: %s", result, extra=log_ctx)
            return False

        logger.info("Month processed successfully", extra=log_ctx)
        return True

    except Exception as exc:
        logger.exception("Unhandled error processing month: %s", exc, extra=log_ctx)
        return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    setup_logging()
    logger.info("ERA5 daily pipeline starting")

    force = os.environ.get("FORCE_REPROCESS", "").lower() == "true"
    bucket = os.environ["BUCKET_NAME"]

    data_dir = Path("/app/data/era5")
    output_dir = Path("/app/output")
    data_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Initialising provider")
    try:
        provider = get_provider()
    except Exception as exc:
        logger.error("Failed to initialise provider: %s", exc)
        return 1

    # Fetch reference climatology once
    logger.info("Fetching reference climatology")
    try:
        ref_path = fetch_reference_climatology(provider, data_dir)
        reference_ds = load_era5_data(ref_path, convert_temperature=False)
    except Exception as exc:
        logger.error("Failed to fetch reference climatology: %s", exc)
        return 1

    months = months_to_process()
    logger.info("Months to check: %s", months)

    failures = []
    for year, month in months:
        success = process_month(
            year, month, provider, data_dir, output_dir, reference_ds, force, bucket
        )
        if not success:
            failures.append((year, month))

    if failures:
        logger.error("Pipeline completed with failures: %s", failures)
        return 1

    logger.info("ERA5 daily pipeline finished successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
