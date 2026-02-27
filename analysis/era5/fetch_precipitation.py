"""Fetch ERA5-Land precipitation data and compute derived metrics.

ERA5-Land total precipitation (``tp``) is expressed in metres per hour.
This module downloads hourly ``tp``, aggregates to daily totals, converts
to mm, and provides helpers for snow-day and dry-spell detection.
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import xarray as xr

from .config import PRECIPITATION_THRESHOLDS, SNOW_DAY_TEMP_THRESHOLD
from .providers.protocol import ClimateDataProvider

logger = logging.getLogger(__name__)

# ERA5-Land stores tp in metres; multiply by 1000 to get mm.
_M_TO_MM: float = 1000.0


# ---------------------------------------------------------------------------
# Download
# ---------------------------------------------------------------------------


def fetch_precipitation(
    provider: ClimateDataProvider,
    year: int,
    month: int,
    output_dir: Path,
    force: bool = False,
) -> Path:
    """Download ERA5-Land hourly total precipitation for a calendar month.

    Delegates the CDS API call to ``provider.fetch_daily()``.  The same
    hourly file used for Tmin/Tmax extraction also contains ``tp``, so
    this function is a thin wrapper that ensures the file exists locally.

    Args:
        provider: Active climate data provider.
        year: Four-digit year.
        month: Calendar month 1–12.
        output_dir: Directory where the NetCDF file is saved.
        force: Re-download even if a cached copy exists.

    Returns:
        Path to the downloaded (or cached) hourly NetCDF file.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(
        "Fetching precipitation data for %d-%02d via %s …",
        year,
        month,
        provider.display_name,
    )
    return provider.fetch_daily(year, month, output_dir, force)


# ---------------------------------------------------------------------------
# Unit conversion and daily aggregation
# ---------------------------------------------------------------------------


def aggregate_daily_precipitation(
    hourly_ds: xr.Dataset,
    tp_variable: str = "tp",
    to_mm: bool = True,
) -> xr.DataArray:
    """Sum hourly precipitation to daily totals.

    Args:
        hourly_ds: ``xr.Dataset`` with hourly ``tp`` in metres.
        tp_variable: Name of the precipitation variable (default ``'tp'``).
        to_mm: Convert output from metres to mm (default ``True``).

    Returns:
        ``xr.DataArray`` of daily precipitation totals with units ``'mm'``
        (or ``'m'`` if *to_mm* is ``False``).
    """
    tp_hourly = hourly_ds[tp_variable]
    tp_daily = tp_hourly.resample(time="1D").sum(dim="time")

    if to_mm:
        tp_daily = tp_daily * _M_TO_MM
        tp_daily.attrs["units"] = "mm"
    else:
        tp_daily.attrs["units"] = "m"

    tp_daily.attrs["long_name"] = "Daily total precipitation"
    return tp_daily


# ---------------------------------------------------------------------------
# Derived metrics
# ---------------------------------------------------------------------------


def calculate_snow_days(
    precip_mm: np.ndarray,
    tmean_c: np.ndarray,
    precip_threshold: float = PRECIPITATION_THRESHOLDS["snow_precip_min"],
    temp_threshold: float = SNOW_DAY_TEMP_THRESHOLD,
) -> np.ndarray:
    """Detect snow days: precipitation > threshold AND Tmean <= 0 °C.

    Args:
        precip_mm: Daily precipitation totals in mm.  Any shape.
        tmean_c: Daily mean temperatures in °C.  Same shape as *precip_mm*.
        precip_threshold: Minimum precipitation for a snow-day flag
            (default 0.1 mm from :data:`~analysis.era5.config.PRECIPITATION_THRESHOLDS`).
        temp_threshold: Maximum Tmean for a snow-day flag (default 0.0 °C).

    Returns:
        Boolean array — ``True`` where both criteria are satisfied.
    """
    p = np.asarray(precip_mm, dtype=float)
    t = np.asarray(tmean_c, dtype=float)
    return (p > precip_threshold) & (t <= temp_threshold)


def calculate_dry_spells(
    precip_mm: np.ndarray,
    threshold: float = PRECIPITATION_THRESHOLDS["dry_day"],
) -> np.ndarray:
    """Count consecutive dry days ending at each position.

    A *dry day* is defined as daily precipitation < *threshold* mm.

    Args:
        precip_mm: 1-D array of daily precipitation totals in mm.
        threshold: Precipitation threshold below which a day is considered
            dry (default 1.0 mm from
            :data:`~analysis.era5.config.PRECIPITATION_THRESHOLDS`).

    Returns:
        Integer array of the same length as *precip_mm* where each element
        contains the number of consecutive dry days ending on that day
        (inclusive).  Wet days have value 0.

    Examples:
        >>> import numpy as np
        >>> calculate_dry_spells(np.array([0.0, 0.1, 5.0, 0.5, 0.0]))
        array([1, 2, 0, 1, 2])
    """
    p = np.asarray(precip_mm, dtype=float)
    is_dry = p < threshold
    result = np.zeros(len(p), dtype=int)
    streak = 0
    for i, dry in enumerate(is_dry):
        if dry:
            streak += 1
        else:
            streak = 0
        result[i] = streak
    return result


def calculate_extreme_rain_days(
    precip_mm: np.ndarray,
    threshold: float = PRECIPITATION_THRESHOLDS["extreme_rain"],
) -> np.ndarray:
    """Detect extreme rain days: daily precipitation >= threshold.

    Args:
        precip_mm: Daily precipitation totals in mm.
        threshold: Threshold in mm (default 25.0 mm).

    Returns:
        Boolean array — ``True`` where extreme rain is detected.
    """
    return np.asarray(precip_mm, dtype=float) >= threshold
