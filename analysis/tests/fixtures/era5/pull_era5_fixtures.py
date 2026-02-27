#!/usr/bin/env python3
"""
pull_era5_fixtures.py — One-time download of ERA5-Land fixture data for tests.

Downloads small Germany-subset NetCDF files from the Copernicus Climate Data
Store (CDS) for use as pytest fixtures. These fixtures enable offline testing
of the ERA5-Land pipeline without requiring network access during test runs.

Data downloaded:
  1. 2m temperature (t2m) — hourly, one month (Jan 2024), Germany bbox
  2. 2m temperature (t2m) — daily min/max (from derived-era5-land-daily-statistics)
  3. Total precipitation (tp) — hourly, one month (Jan 2024), Germany bbox

Germany bounding box: N=55.1, W=5.8, S=47.2, E=15.1

Usage:
    # Requires CDS_API_KEY in .env or environment
    python analysis/tests/fixtures/era5/pull_era5_fixtures.py

    # Or pass key directly
    CDS_API_KEY=<key> python analysis/tests/fixtures/era5/pull_era5_fixtures.py

Attribution:
    Muñoz Sabater, J., (2019): ERA5-Land hourly data from 1950 to present.
    Copernicus Climate Change Service (C3S) Climate Data Store (CDS).
    DOI: 10.24381/cds.e2161bac
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Resolve project root (4 levels up from this script)
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[3]
FIXTURES_DIR = SCRIPT_DIR

# Germany bounding box (same as phase-03 config)
GERMANY_BBOX = {
    "north": 55.1,
    "south": 47.2,
    "west": 5.8,
    "east": 15.1,
}

# Fixture year/month — use a recent complete month
FIXTURE_YEAR = "2024"
FIXTURE_MONTH = "01"


def load_api_key() -> str:
    """Load CDS API key from environment or .env file."""
    key = os.environ.get("CDS_API_KEY")
    if key:
        return key

    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line.startswith("CDS_API_KEY="):
                return line.split("=", 1)[1].strip().strip("'\"")

    print("ERROR: CDS_API_KEY not found in environment or .env file.")
    print("  Set it via: export CDS_API_KEY=<your-key>")
    print("  Or add to .env: CDS_API_KEY=<your-key>")
    sys.exit(1)


def pull_hourly_temperature(client, output_path: Path) -> None:
    """Download hourly 2m temperature for Germany, one month."""
    if output_path.exists():
        print(f"  [SKIP] {output_path.name} already exists")
        return

    print(f"  [PULL] Hourly 2m temperature → {output_path.name}")
    client.retrieve(
        "reanalysis-era5-land",
        {
            "variable": ["2m_temperature"],
            "year": FIXTURE_YEAR,
            "month": FIXTURE_MONTH,
            "day": [f"{d:02d}" for d in range(1, 32)],
            "time": ["06:00", "12:00", "18:00"],  # 3 times/day to keep size small
            "data_format": "netcdf",
            "download_format": "unarchived",
            "area": [
                GERMANY_BBOX["north"],
                GERMANY_BBOX["west"],
                GERMANY_BBOX["south"],
                GERMANY_BBOX["east"],
            ],
        },
        str(output_path),
    )
    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"  [OK]   {output_path.name} ({size_mb:.1f} MB)")


def pull_daily_statistics(client, output_path: Path) -> None:
    """Download daily min/max 2m temperature for Germany, one month.

    The derived-era5-land-daily-statistics dataset accepts only one
    daily_statistic per request, so we pull daily_minimum and daily_maximum
    separately and merge them into a single NetCDF file.
    """
    if output_path.exists():
        print(f"  [SKIP] {output_path.name} already exists")
        return

    import xarray as xr

    base_request = {
        "variable": ["2m_temperature"],
        "year": FIXTURE_YEAR,
        "month": FIXTURE_MONTH,
        "day": [f"{d:02d}" for d in range(1, 32)],
        "time_zone": "utc+00:00",
        "frequency": "1_hourly",
        "area": [
            GERMANY_BBOX["north"],
            GERMANY_BBOX["west"],
            GERMANY_BBOX["south"],
            GERMANY_BBOX["east"],
        ],
    }

    tmp_min = output_path.with_suffix(".tmp_min.nc")
    tmp_max = output_path.with_suffix(".tmp_max.nc")

    try:
        # Pull daily minimum
        print(f"  [PULL] Daily Tmin → {output_path.name} (1/2)")
        client.retrieve(
            "derived-era5-land-daily-statistics",
            {**base_request, "daily_statistic": ["daily_minimum"]},
            str(tmp_min),
        )

        # Pull daily maximum
        print(f"  [PULL] Daily Tmax → {output_path.name} (2/2)")
        client.retrieve(
            "derived-era5-land-daily-statistics",
            {**base_request, "daily_statistic": ["daily_maximum"]},
            str(tmp_max),
        )

        # Merge into a single file with t2m_min and t2m_max variables
        ds_min = xr.open_dataset(tmp_min)
        ds_max = xr.open_dataset(tmp_max)

        merged = xr.Dataset(
            {
                "t2m_min": ds_min["t2m"].rename("t2m_min"),
                "t2m_max": ds_max["t2m"].rename("t2m_max"),
            },
            attrs={
                "source": "derived-era5-land-daily-statistics (CDS)",
                "description": "Daily min/max 2m temperature for Germany, Jan 2024",
            },
        )
        merged.to_netcdf(output_path)
        ds_min.close()
        ds_max.close()

    finally:
        # Clean up temp files
        tmp_min.unlink(missing_ok=True)
        tmp_max.unlink(missing_ok=True)

    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"  [OK]   {output_path.name} ({size_mb:.1f} MB)")


def pull_precipitation(client, output_path: Path) -> None:
    """Download hourly total precipitation for Germany, one month."""
    if output_path.exists():
        print(f"  [SKIP] {output_path.name} already exists")
        return

    print(f"  [PULL] Hourly total precipitation → {output_path.name}")
    client.retrieve(
        "reanalysis-era5-land",
        {
            "variable": ["total_precipitation"],
            "year": FIXTURE_YEAR,
            "month": FIXTURE_MONTH,
            "day": [f"{d:02d}" for d in range(1, 32)],
            "time": ["06:00", "12:00", "18:00"],
            "data_format": "netcdf",
            "download_format": "unarchived",
            "area": [
                GERMANY_BBOX["north"],
                GERMANY_BBOX["west"],
                GERMANY_BBOX["south"],
                GERMANY_BBOX["east"],
            ],
        },
        str(output_path),
    )
    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"  [OK]   {output_path.name} ({size_mb:.1f} MB)")


def main() -> None:
    import cdsapi

    print("=" * 60)
    print("  ERA5-Land Fixture Pull")
    print(f"  Period: {FIXTURE_YEAR}-{FIXTURE_MONTH}")
    print(f"  Area: Germany ({GERMANY_BBOX})")
    print(f"  Output: {FIXTURES_DIR}")
    print("=" * 60)

    api_key = load_api_key()
    print(f"  API key: {api_key[:8]}...{api_key[-4:]}")

    # CDS API endpoint (new CDS, post-migration from CDS-Beta)
    client = cdsapi.Client(
        url="https://cds.climate.copernicus.eu/api",
        key=api_key,
    )

    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Hourly 2m temperature
    pull_hourly_temperature(
        client,
        FIXTURES_DIR / f"era5land_t2m_hourly_{FIXTURE_YEAR}{FIXTURE_MONTH}_germany.nc",
    )

    # 2. Daily min/max temperature (two CDS calls, merged)
    pull_daily_statistics(
        client,
        FIXTURES_DIR / f"era5land_t2m_daily_minmax_{FIXTURE_YEAR}{FIXTURE_MONTH}_germany.nc",
    )

    # 3. Hourly precipitation
    pull_precipitation(
        client,
        FIXTURES_DIR / f"era5land_tp_hourly_{FIXTURE_YEAR}{FIXTURE_MONTH}_germany.nc",
    )

    # Print summary
    print("\n" + "=" * 60)
    total_mb = sum(
        f.stat().st_size / (1024 * 1024)
        for f in FIXTURES_DIR.glob("*.nc")
    )
    nc_files = list(FIXTURES_DIR.glob("*.nc"))
    print(f"  Done! {len(nc_files)} files, {total_mb:.1f} MB total")
    for f in sorted(nc_files):
        print(f"    {f.name} ({f.stat().st_size / (1024*1024):.1f} MB)")
    print("=" * 60)


if __name__ == "__main__":
    main()
