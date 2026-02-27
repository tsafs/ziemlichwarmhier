#!/usr/bin/env python3
"""
check_new_data.py - Check CDS API for ERA5-Land data availability for a given year/month.
"""

import logging
import os
import sys
from datetime import date

import requests

logger = logging.getLogger(__name__)


def check_era5_data_available(year: int, month: int) -> bool:
    """
    Check whether ERA5-Land monthly data is available in the CDS catalogue
    for the given year and month.

    Uses the CDS API endpoint to probe whether a dataset record exists.
    ERA5-Land typically has a ~5-day publication delay after month end.

    Returns True if data appears to be available, False otherwise.
    """
    api_key = os.environ.get("CDS_API_KEY", "")
    if not api_key:
        logger.warning("CDS_API_KEY not set; assuming data is unavailable")
        return False

    # CDS API v2 catalogue check endpoint
    url = "https://cds.climate.copernicus.eu/api/catalogue/v1/collections/reanalysis-era5-land-monthly-means"
    try:
        response = requests.get(url, timeout=30, auth=(api_key, api_key))
        if response.status_code != 200:
            logger.warning(
                "CDS catalogue returned HTTP %s; cannot confirm availability",
                response.status_code,
            )
            return False

        # The catalogue entry exists; check if target period is within the advertised
        # temporal extent.  The response JSON contains an "extent" → "temporal" block.
        data = response.json()
        temporal = (
            data.get("extent", {})
            .get("temporal", {})
            .get("interval", [[None, None]])[0]
        )
        end_str = temporal[1] if temporal else None

        if end_str is None:
            # Cannot determine end date; fall back to date-arithmetic heuristic
            return _heuristic_available(year, month)

        # end_str is ISO-8601, e.g. "2026-01-31T00:00:00Z"
        end_date = date.fromisoformat(end_str[:10])
        target_last_day = date(year, month, 28)  # conservative: last day of month
        if end_date >= target_last_day:
            logger.info(
                "CDS catalogue confirms data available through %s", end_str[:10]
            )
            return True
        else:
            logger.info(
                "CDS catalogue end date %s is before target %04d-%02d",
                end_str[:10],
                year,
                month,
            )
            return False

    except Exception as exc:
        logger.warning("Error querying CDS catalogue: %s; using heuristic", exc)
        return _heuristic_available(year, month)


def _heuristic_available(year: int, month: int) -> bool:
    """
    Fallback heuristic: ERA5-Land data for a given month is typically published
    ~5 days after the end of that month.  Assume available if today is at least
    the 6th day of the following month.
    """
    today = date.today()
    next_month_year = year if month < 12 else year + 1
    next_month = month + 1 if month < 12 else 1
    publication_date = date(next_month_year, next_month, 6)
    available = today >= publication_date
    logger.debug(
        "Heuristic check for %04d-%02d: publication_date=%s, today=%s → %s",
        year,
        month,
        publication_date,
        today,
        available,
    )
    return available


if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Check CDS data availability")
    parser.add_argument("year", type=int)
    parser.add_argument("month", type=int)
    args = parser.parse_args()
    available = check_era5_data_available(args.year, args.month)
    print(f"{args.year}-{args.month:02d}: {'AVAILABLE' if available else 'NOT AVAILABLE'}")
    sys.exit(0 if available else 1)
