#!/usr/bin/env python3
"""
process_monthly.py - Monthly ERA5 pipeline orchestrator.

Runs on the 1st of each month (via cron) to fully process the previous complete
month: fetch ERA5-Land data, apply land mask, compute anomaly, generate tiles,
upload to S3, and validate coverage.

Environment variables:
  CDS_API_KEY       - Copernicus CDS API key (required)
  ACCESS_KEY        - S3 access key (required)
  SECRET_KEY        - S3 secret key (required)
  ENDPOINT_URL      - S3 endpoint URL (required)
  BUCKET_NAME       - S3 bucket name (required)
  TARGET_YEAR       - Override year (optional, for manual runs)
  TARGET_MONTH      - Override month (optional, for manual runs)
  FORCE_REPROCESS   - Set to "true" to skip idempotency check (optional)
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
# Target month resolution
# ---------------------------------------------------------------------------

def resolve_target_month() -> tuple[int, int]:
    """
    Return (year, month) for the month to process.

    Precedence:
      1. TARGET_YEAR + TARGET_MONTH env vars (manual override)
      2. Previous calendar month (default when run on 1st of current month)
    """
    env_year = os.environ.get("TARGET_YEAR")
    env_month = os.environ.get("TARGET_MONTH")

    if env_year and env_month:
        return int(env_year), int(env_month)

    today = date.today()
    first_of_month = date(today.year, today.month, 1)
    previous = first_of_month - timedelta(days=1)  # last day of previous month
    return previous.year, previous.month


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    setup_logging()
    logger.info("ERA5 monthly pipeline starting")

    force = os.environ.get("FORCE_REPROCESS", "").lower() == "true"
    bucket = os.environ["BUCKET_NAME"]

    data_dir = Path("/app/data/era5")
    output_dir = Path("/app/output")
    data_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    year, month = resolve_target_month()
    logger.info("Target month: %04d-%02d", year, month)

    # Idempotency check
    if not force and tiles_exist_in_s3(year, month, bucket):
        logger.info("Tiles already exist in S3 for %04d-%02d; nothing to do", year, month)
        return 0

    logger.info("Initialising provider")
    try:
        provider = get_provider()
    except Exception as exc:
        logger.error("Failed to initialise provider: %s", exc)
        return 1

    try:
        # Fetch reference climatology
        logger.info("Fetching reference climatology")
        ref_path = fetch_reference_climatology(provider, data_dir)
        reference_ds = load_era5_data(ref_path, convert_temperature=False)

        # 1. Fetch monthly data
        logger.info("Fetching monthly ERA5 data for %04d-%02d", year, month)
        raw_path = fetch_monthly_data(provider, year, month, data_dir, force=force)

        # 2. Load + land mask
        logger.info("Loading dataset and applying land mask")
        ds = load_era5_data(raw_path)
        ds_masked = apply_germany_land_mask(ds, provider)

        # 3. Anomaly
        logger.info("Calculating temperature anomaly")
        anomaly_ds = calculate_monthly_anomaly(ds_masked, reference_ds, year, month)

        # 4. Export GeoTIFF
        geotiff_path = output_dir / f"anomaly_{year}_{month:02d}.tif"
        logger.info("Exporting GeoTIFF to %s", geotiff_path)
        export_anomaly_geotiff(anomaly_ds, geotiff_path)

        # 5. Full tile regeneration
        tile_dir = output_dir / "tiles" / f"{year}" / f"{month:02d}"
        logger.info("Generating map tiles")
        tile_count = generate_tiles_for_geotiff(geotiff_path, tile_dir, year, month)
        logger.info("Generated %d tiles", tile_count)

        # 6. Upload tiles
        logger.info("Uploading tiles to S3")
        uploaded = upload_tiles_from_env(tile_dir, year, month)
        logger.info("Uploaded %d tiles", uploaded)

        # 7. Validate tile count
        logger.info("Validating tile coverage")
        result = validate_tile_coverage(tile_dir, year, month)
        if not result.is_valid:
            logger.error("Tile validation failed: %s", result)
            return 1

        # Summary log
        logger.info(
            "Monthly pipeline summary",
            extra={
                "year": year,
                "month": month,
                "tiles_generated": tile_count,
                "tiles_uploaded": uploaded,
                "validation": str(result),
            },
        )
        logger.info("ERA5 monthly pipeline finished successfully")
        return 0

    except Exception as exc:
        logger.exception("Unhandled error in monthly pipeline: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
