#!/usr/bin/env python3
"""
process_yearly.py - Yearly ERA5 aggregation pipeline.

Fetches all 12 monthly ERA5-Land files for the target year, then:
  - Calculates per-pixel annual threshold-day counts (hot days, extreme heat
    days, tropical nights, ice days, frost days, comfortable days)
  - Computes the mean annual temperature anomaly (mean of 12 monthly anomalies
    vs 1961-1990 reference climatology)
  - Exports summary metrics JSON to /app/output/metrics_{year}.json
  - Uploads metrics JSON to S3 at metrics/metrics_{year}.json

Environment variables:
  CDS_API_KEY       - Copernicus CDS API key (required)
  ACCESS_KEY        - S3 access key (required)
  SECRET_KEY        - S3 secret key (required)
  ENDPOINT_URL      - S3 endpoint URL (required)
  BUCKET_NAME       - S3 bucket name (required)
  TARGET_YEAR       - Year to process (optional, defaults to previous year)
  CLIMATE_DATA_PROVIDER - Override provider id (optional, defaults to "era5-land")
"""

import json
import logging
import os
import sys
from datetime import date
from pathlib import Path

import boto3
import numpy as np

from analysis.era5.providers import get_provider
from analysis.era5.fetch_era5_data import (
    fetch_monthly_data,
    fetch_reference_climatology,
    load_era5_data,
)
from analysis.era5.apply_land_mask import apply_germany_land_mask
from analysis.era5.calculate_anomalies import calculate_monthly_anomaly
from analysis.era5.detect_thresholds import (
    hot_days,
    extreme_heat_days,
    tropical_nights,
    ice_days,
    frost_days,
    comfortable_days,
    count_threshold_days,
)

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
# Helpers
# ---------------------------------------------------------------------------

def resolve_target_year() -> int:
    env_year = os.environ.get("TARGET_YEAR")
    if env_year:
        return int(env_year)
    return date.today().year - 1


def upload_metrics_to_s3(local_path: Path, year: int) -> None:
    bucket = os.environ["BUCKET_NAME"]
    s3_key = f"metrics/metrics_{year}.json"
    client = boto3.client(
        "s3",
        endpoint_url=os.environ["ENDPOINT_URL"],
        aws_access_key_id=os.environ["ACCESS_KEY"],
        aws_secret_access_key=os.environ["SECRET_KEY"],
    )
    client.upload_file(str(local_path), bucket, s3_key)
    logger.info("Uploaded metrics to s3://%s/%s", bucket, s3_key)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    setup_logging()
    logger.info("ERA5 yearly pipeline starting")

    year = resolve_target_year()
    logger.info("Target year: %d", year)

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

    try:
        # Fetch reference climatology
        logger.info("Fetching reference climatology")
        ref_path = fetch_reference_climatology(provider, data_dir)
        reference_ds = load_era5_data(ref_path, convert_temperature=False)

        # Accumulators for annual aggregation
        # We collect per-pixel daily tmax/tmin arrays across all 12 months,
        # then compute threshold counts over the full year.
        tmax_list: list[np.ndarray] = []  # (time, lat, lon) arrays, °C
        tmin_list: list[np.ndarray] = []
        anomaly_values: list[float] = []  # mean anomaly per month (Germany mean)

        months_processed = []

        for month in range(1, 13):
            logger.info("Processing month %02d", month)
            try:
                raw_path = fetch_monthly_data(provider, year, month, data_dir)
                ds = load_era5_data(raw_path)
                ds_masked = apply_germany_land_mask(ds, provider)

                # Extract tmax and tmin arrays (°C)
                # ERA5-Land monthly-means dataset contains 't2m' (mean),
                # 'mx2t' (daily max), 'mn2t' (daily min) depending on request.
                # We use 't2m' as mean proxy where hourly isn't available.
                if "mx2t" in ds_masked:
                    tmax_arr = ds_masked["mx2t"].values  # already converted to °C
                    tmax_list.append(tmax_arr)
                if "mn2t" in ds_masked:
                    tmin_arr = ds_masked["mn2t"].values
                    tmin_list.append(tmin_arr)

                # Monthly anomaly (Germany-wide mean)
                anomaly_ds = calculate_monthly_anomaly(ds_masked, reference_ds, year, month)
                if "t2m_anomaly" in anomaly_ds:
                    mean_val = float(anomaly_ds["t2m_anomaly"].mean().values)
                else:
                    mean_val = float(anomaly_ds[list(anomaly_ds.data_vars)[0]].mean().values)
                anomaly_values.append(mean_val)
                months_processed.append(month)

            except Exception as exc:
                logger.warning("Skipping month %02d due to error: %s", month, exc)
                continue

        logger.info("Processed %d / 12 months", len(months_processed))

        # Compute annual threshold-day counts (per pixel, then Germany mean)
        metrics: dict = {
            "year": year,
            "months_processed": months_processed,
        }

        if tmax_list:
            tmax_all = np.concatenate(tmax_list, axis=0)  # (total_days, lat, lon)
            if tmin_list:
                tmin_all = np.concatenate(tmin_list, axis=0)

            def _mean_count(arr):
                return float(np.nanmean(arr))

            metrics["hot_days_mean"] = _mean_count(hot_days(tmax_all))
            metrics["extreme_heat_days_mean"] = _mean_count(extreme_heat_days(tmax_all))
            metrics["ice_days_mean"] = _mean_count(ice_days(tmax_all))

            if tmin_list:
                metrics["tropical_nights_mean"] = _mean_count(tropical_nights(tmin_all))
                metrics["frost_days_mean"] = _mean_count(frost_days(tmin_all))
                metrics["comfortable_days_mean"] = _mean_count(
                    comfortable_days(tmin_all, tmax_all)
                )

        if anomaly_values:
            metrics["mean_annual_anomaly_celsius"] = float(np.mean(anomaly_values))
            metrics["monthly_anomalies_celsius"] = {
                str(m): round(v, 4)
                for m, v in zip(months_processed, anomaly_values)
            }

        # Export metrics JSON
        metrics_path = output_dir / f"metrics_{year}.json"
        with open(metrics_path, "w") as f:
            json.dump(metrics, f, indent=2)
        logger.info("Metrics written to %s", metrics_path)

        # Upload to S3
        upload_metrics_to_s3(metrics_path, year)

        logger.info("ERA5 yearly pipeline finished successfully")
        logger.info("Annual summary: %s", json.dumps({k: v for k, v in metrics.items() if k != "monthly_anomalies_celsius"}))
        return 0

    except Exception as exc:
        logger.exception("Unhandled error in yearly pipeline: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
