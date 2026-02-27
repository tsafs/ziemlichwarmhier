"""Fetch ERA5-Land hourly data and derive daily Tmin / Tmax / Tmean.

ERA5-Land data is available at hourly resolution.  This module downloads
the full hourly 2m-temperature dataset for a given month and then derives
daily statistics by resampling.
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import xarray as xr

from .providers.protocol import ClimateDataProvider

logger = logging.getLogger(__name__)

# Kelvin → Celsius offset
_K_TO_C: float = 273.15


# ---------------------------------------------------------------------------
# Download wrapper
# ---------------------------------------------------------------------------


def fetch_daily_data(
    provider: ClimateDataProvider,
    year: int,
    month: int,
    output_dir: Path,
    force: bool = False,
) -> Path:
    """Download ERA5-Land hourly 2 m temperature data for a calendar month.

    Delegates the actual CDS API call to ``provider.fetch_daily()``.

    Args:
        provider: Active climate data provider.
        year: Four-digit year (e.g. 2024).
        month: Calendar month 1–12.
        output_dir: Directory where the NetCDF file is saved.
        force: Re-download even if a cached copy already exists.

    Returns:
        Path to the downloaded (or cached) hourly NetCDF file.

    Raises:
        RuntimeError: If the download fails after all provider retries.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(
        "Fetching hourly %s data for %d-%02d …",
        provider.display_name,
        year,
        month,
    )
    return provider.fetch_daily(year, month, output_dir, force)


# ---------------------------------------------------------------------------
# Daily statistic extraction
# ---------------------------------------------------------------------------


def extract_daily_tmin_tmax(
    hourly_ds: xr.Dataset,
    t_variable: str = "t2m",
    convert_kelvin: bool = True,
) -> xr.Dataset:
    """Derive daily Tmin, Tmax, and Tmean from an hourly xr.Dataset.

    Resampling is performed on the time dimension at daily frequency.
    Latitude and longitude dimensions are preserved.

    Args:
        hourly_ds: ``xr.Dataset`` containing at least one variable with a
            ``time`` coordinate at sub-daily frequency (typically 1-hourly).
        t_variable: Name of the temperature variable in *hourly_ds*
            (default ``'t2m'``).
        convert_kelvin: If ``True`` (default), subtract 273.15 from all
            output fields so that units are °C.  Set to ``False`` if the
            input is already in Celsius.

    Returns:
        ``xr.Dataset`` with three variables:
          - ``tmax``  Daily maximum temperature
          - ``tmin``  Daily minimum temperature
          - ``tmean`` Daily mean temperature

        All share the same ``latitude`` / ``longitude`` coordinates as the
        input.  The ``time`` coordinate contains one value per calendar day.
    """
    temp = hourly_ds[t_variable]

    tmax = temp.resample(time="1D").max(dim="time")
    tmin = temp.resample(time="1D").min(dim="time")
    tmean = temp.resample(time="1D").mean(dim="time")

    if convert_kelvin and temp.attrs.get("units", "K") == "K":
        tmax = tmax - _K_TO_C
        tmin = tmin - _K_TO_C
        tmean = tmean - _K_TO_C
        unit_str = "°C"
    else:
        unit_str = temp.attrs.get("units", "unknown")

    tmax.attrs = {"units": unit_str, "long_name": "Daily maximum 2m temperature"}
    tmin.attrs = {"units": unit_str, "long_name": "Daily minimum 2m temperature"}
    tmean.attrs = {"units": unit_str, "long_name": "Daily mean 2m temperature"}

    daily_ds = xr.Dataset(
        {"tmax": tmax, "tmin": tmin, "tmean": tmean},
        attrs={
            "source": hourly_ds.attrs.get("source", "ERA5-Land hourly"),
            "derived_from": "Hourly 2m temperature resampled to daily",
        },
    )
    return daily_ds


# ---------------------------------------------------------------------------
# Convenience: download → extract in one call
# ---------------------------------------------------------------------------


def fetch_and_extract_daily(
    provider: ClimateDataProvider,
    year: int,
    month: int,
    output_dir: Path,
    force: bool = False,
) -> xr.Dataset:
    """Download hourly data and immediately extract daily Tmin/Tmax/Tmean.

    Combines :func:`fetch_daily_data` and :func:`extract_daily_tmin_tmax`.

    Args:
        provider: Active climate data provider.
        year: Four-digit year.
        month: Calendar month 1–12.
        output_dir: Directory where the hourly NetCDF is cached.
        force: Re-download even if a cached copy exists.

    Returns:
        ``xr.Dataset`` with ``tmax``, ``tmin``, ``tmean`` variables at
        daily resolution.
    """
    hourly_path = fetch_daily_data(provider, year, month, output_dir, force)
    hourly_ds = provider.load_dataset(hourly_path)
    return extract_daily_tmin_tmax(hourly_ds)
