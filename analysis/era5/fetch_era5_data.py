"""ERA5-Land data fetching from the Copernicus Climate Data Store.

High-level wrappers around the provider protocol for downloading monthly
and reference-climatology data.  All CDS-specific logic (retry, API
payload construction) lives in the provider; this module handles
orchestration, caching checks, and multi-year climatology aggregation.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

import xarray as xr

from .config import REFERENCE_PERIOD
from .providers.protocol import ClimateDataProvider

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# CDS client helper (provider-independent)
# ---------------------------------------------------------------------------


def get_cds_client():
    """Initialise a standalone CDS API client.

    This is a convenience helper for scripts that want a raw
    ``cdsapi.Client`` without going through the provider abstraction.

    Reads credentials from the ``CDS_API_KEY`` environment variable
    (format ``"uid:key"``) or falls back to ``~/.cdsapirc``.

    Returns:
        ``cdsapi.Client`` instance ready for use.

    Raises:
        RuntimeError: If no credentials can be found.
    """
    import cdsapi  # deferred import so monkeypatch works in tests

    api_key = os.environ.get("CDS_API_KEY")
    if api_key:
        return cdsapi.Client(
            url="https://cds.climate.copernicus.eu/api/v2",
            key=api_key,
            quiet=True,
        )

    cdsapirc = Path.home() / ".cdsapirc"
    if cdsapirc.exists():
        return cdsapi.Client(quiet=True)

    raise RuntimeError(
        "CDS credentials not found.  Set the CDS_API_KEY environment variable "
        "(format 'uid:key') or create ~/.cdsapirc."
    )


# ---------------------------------------------------------------------------
# Monthly download
# ---------------------------------------------------------------------------


def fetch_monthly_data(
    provider: ClimateDataProvider,
    year: int,
    month: int,
    output_dir: Path,
    variable: str = "t2m",
    force: bool = False,
) -> Path:
    """Fetch a single month of data via the active provider.

    Delegates entirely to ``provider.fetch_monthly()``; the cache check
    is also performed inside the provider.  This wrapper exists so
    pipeline scripts can call a stable function signature without
    importing the provider class directly.

    Args:
        provider: Instantiated climate data provider.
        year: Four-digit year (e.g. 2024).
        month: Month index 1–12.
        output_dir: Directory for downloaded NetCDF files.
        variable: Variable short name (default ``'t2m'``).
        force: Re-download even if a cached copy exists.

    Returns:
        Path to the downloaded (or cached) NetCDF file.

    Raises:
        RuntimeError: If the download fails after all retries.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(
        "Requesting %s %s for %d-%02d …",
        provider.display_name,
        variable,
        year,
        month,
    )
    return provider.fetch_monthly(year, month, output_dir, variable, force)


# ---------------------------------------------------------------------------
# Reference climatology
# ---------------------------------------------------------------------------


def fetch_reference_climatology(
    provider: ClimateDataProvider,
    output_dir: Path,
    variable: str = "t2m",
    years_start: int | None = None,
    years_end: int | None = None,
) -> Path:
    """Fetch (or load) the 1961-1990 monthly-mean climatology.

    If a pre-computed climatology file exists in ``output_dir``, it is
    returned immediately.  Otherwise, all monthly files for the reference
    period are downloaded (or loaded from cache) and a 12-month-mean
    climatology is computed and saved.

    Args:
        provider: Instantiated climate data provider.
        output_dir: Directory for climatology output and raw monthly files.
        variable: Variable short name (default ``'t2m'``).
        years_start: First year of reference period (default: from
            :data:`~analysis.era5.config.REFERENCE_PERIOD`).
        years_end: Last year of reference period (inclusive).

    Returns:
        Path to the climatology NetCDF file
        (``climatology_{variable}_{start}_{end}.nc``).

    Raises:
        RuntimeError: If no reference data could be obtained.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    ref_start = years_start if years_start is not None else REFERENCE_PERIOD[0]
    ref_end = years_end if years_end is not None else REFERENCE_PERIOD[1]

    clim_file = output_dir / f"climatology_{variable}_{ref_start}_{ref_end}.nc"

    if clim_file.exists():
        logger.info("Using cached climatology: %s", clim_file)
        return clim_file

    logger.info(
        "Building reference climatology %d–%d for '%s' …",
        ref_start,
        ref_end,
        variable,
    )

    raw_dir = output_dir / "reference_raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    datasets: list[xr.Dataset] = []
    for year in range(ref_start, ref_end + 1):
        for month in range(1, 13):
            try:
                nc_path = fetch_monthly_data(provider, year, month, raw_dir, variable)
                datasets.append(xr.open_dataset(nc_path))
            except Exception:
                logger.exception(
                    "Failed to fetch reference data for %d-%02d", year, month
                )

    if not datasets:
        raise RuntimeError(
            "No reference data could be downloaded.  "
            "Check CDS credentials and network access."
        )

    combined = xr.concat(datasets, dim="time")
    climatology = combined.groupby("time.month").mean(dim="time")
    climatology.to_netcdf(clim_file)
    logger.info("Saved climatology: %s", clim_file)
    return clim_file


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


def load_era5_data(file_path: Path, convert_temperature: bool = True) -> xr.Dataset:
    """Load an ERA5-Land NetCDF file and optionally convert units.

    Args:
        file_path: Path to a NetCDF file produced by this pipeline.
        convert_temperature: If ``True`` (default), convert ``t2m``
            from Kelvin to Celsius (subtract 273.15).

    Returns:
        ``xr.Dataset`` with any requested unit conversions applied.
    """
    ds = xr.open_dataset(file_path)

    if convert_temperature and "t2m" in ds:
        ds["t2m"] = ds["t2m"] - 273.15
        ds["t2m"].attrs["units"] = "°C"
        ds["t2m"].attrs.setdefault(
            "long_name", "2 metre temperature (converted from K)"
        )

    return ds
