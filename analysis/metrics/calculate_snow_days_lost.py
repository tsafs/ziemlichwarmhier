#!/usr/bin/env python3
"""
Calculate change in snow days vs reference period.

A snow day is defined as a day where:
- Daily mean temperature <= 0°C AND
- Precipitation > 0.1 mm/day

This definition follows DWD standard for snow-capable days.
"""

import logging

import numpy as np
import xarray as xr

from .config import (
    FIVE_YEAR_ANOMALY_PERIOD,
    REFERENCE_PERIOD,
    SNOW_PRECIPITATION_THRESHOLD_MM,
)
from .types import SnowDaysLost

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def identify_snow_days(
    ds: xr.Dataset,
    tmean_var: str = 'tmean',
    precip_var: str = 'precipitation',
    precip_threshold_mm: float = None,
) -> xr.DataArray:
    """Identify snow days as boolean mask.
    
    A snow day satisfies:
    - Tmean <= 0°C (freezing)
    - Precipitation > threshold (precipitation present)
    
    Args:
        ds: Dataset with temperature and precipitation data
        tmean_var: Daily mean temperature variable name
        precip_var: Precipitation variable name (mm/day)
        precip_threshold_mm: Minimum precipitation to count (default: 0.1mm)
        
    Returns:
        Boolean DataArray where True = snow day
    """
    threshold = precip_threshold_mm if precip_threshold_mm is not None else SNOW_PRECIPITATION_THRESHOLD_MM
    
    freezing = ds[tmean_var] <= 0.0
    has_precip = ds[precip_var] > threshold
    
    return freezing & has_precip


def count_annual_snow_days(
    ds: xr.Dataset,
    tmean_var: str = 'tmean',
    precip_var: str = 'precipitation',
) -> xr.DataArray:
    """Count snow days per year at each grid point.
    
    Args:
        ds: Dataset with temperature and precipitation data
        tmean_var: Daily mean temperature variable
        precip_var: Precipitation variable (mm/day)
        
    Returns:
        DataArray with dims (year, ...) counting snow days per year
    """
    snow_mask = identify_snow_days(ds, tmean_var, precip_var)
    
    # Count True values per year
    annual_snow_days = snow_mask.resample(time='YE').sum()
    
    return annual_snow_days


def calculate_snow_days_lost(
    ds: xr.Dataset,
    tmean_var: str = 'tmean',
    precip_var: str = 'precipitation',
    recent_period: dict = None,
    reference_period: dict = None,
) -> SnowDaysLost:
    """Calculate change in snow days between recent and reference periods.
    
    Args:
        ds: Dataset with daily mean temperature and precipitation
        tmean_var: Daily mean temperature variable name
        precip_var: Precipitation variable name
        recent_period: Recent period dict (defaults to FIVE_YEAR_ANOMALY_PERIOD)
        reference_period: Reference period dict (defaults to REFERENCE_PERIOD)
        
    Returns:
        SnowDaysLost dictionary
    """
    recent = recent_period or FIVE_YEAR_ANOMALY_PERIOD
    ref = reference_period or REFERENCE_PERIOD
    
    logger.info(
        f"Calculating snow days lost: {recent['start_year']}-{recent['end_year']} "
        f"vs {ref['start_year']}-{ref['end_year']}"
    )
    
    snow_mask = identify_snow_days(ds, tmean_var, precip_var)
    
    # Spatial mean first (country-level), then count per year
    spatial_dims = [d for d in snow_mask.dims if d not in ['time']]
    if spatial_dims:
        snow_spatial_mean = snow_mask.mean(dim=spatial_dims)
    else:
        snow_spatial_mean = snow_mask
    
    # Annual counts
    annual_snow = snow_spatial_mean.resample(time='YE').sum()
    years = annual_snow['time'].dt.year.values
    
    # Recent period average
    recent_mask = (years >= recent['start_year']) & (years <= recent['end_year'])
    reference_mask = (years >= ref['start_year']) & (years <= ref['end_year'])
    
    recent_values = annual_snow.values[recent_mask]
    reference_values = annual_snow.values[reference_mask]
    
    if len(recent_values) == 0:
        raise ValueError(f"No data for recent period {recent['start_year']}-{recent['end_year']}")
    if len(reference_values) == 0:
        raise ValueError(f"No data for reference period {ref['start_year']}-{ref['end_year']}")
    
    recent_avg = float(np.nanmean(recent_values))
    reference_avg = float(np.nanmean(reference_values))
    
    # Negative value means fewer snow days (warming)
    change = recent_avg - reference_avg
    
    logger.info(
        f"Snow days: recent={recent_avg:.1f}/year, "
        f"reference={reference_avg:.1f}/year, "
        f"change={change:+.1f}"
    )
    
    return SnowDaysLost(
        value=int(round(change)),
        currentAverage=round(recent_avg, 1),
        referenceAverage=round(reference_avg, 1),
        periodStart=recent['start_year'],
        periodEnd=recent['end_year'],
    )


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Calculate snow days lost')
    parser.add_argument('input_file', help='Input NetCDF with Tmean and precipitation')
    args = parser.parse_args()
    
    ds = xr.open_dataset(args.input_file)
    result = calculate_snow_days_lost(ds)
    
    print(f"\nSnow Days Lost:")
    print(f"  Recent average: {result['currentAverage']} days/year")
    print(f"  Reference average: {result['referenceAverage']} days/year")
    print(f"  Change: {result['value']:+d} days/year")
