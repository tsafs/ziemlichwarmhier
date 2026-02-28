#!/usr/bin/env python3
"""
Calculate comfortable temperature days (daily mean 15-25°C).

Comfortable days are days with a daily mean temperature between 15°C and 25°C
(inclusive on both ends), representing ideal outdoor conditions.
"""

import logging

import numpy as np
import xarray as xr

from .config import COMFORTABLE_RANGE
from .types import ComfortableDays

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def identify_comfortable_days(
    ds: xr.Dataset,
    tmean_var: str = 'tmean',
    temp_min: float = None,
    temp_max: float = None,
) -> xr.DataArray:
    """Identify comfortable days as boolean mask.
    
    A comfortable day satisfies: temp_min <= Tmean <= temp_max
    
    Args:
        ds: Dataset with daily mean temperature
        tmean_var: Daily mean temperature variable name
        temp_min: Minimum comfortable temperature (default: 15°C)
        temp_max: Maximum comfortable temperature (default: 25°C)
        
    Returns:
        Boolean DataArray where True = comfortable day
    """
    t_min = temp_min if temp_min is not None else COMFORTABLE_RANGE['min']
    t_max = temp_max if temp_max is not None else COMFORTABLE_RANGE['max']
    
    return (ds[tmean_var] >= t_min) & (ds[tmean_var] <= t_max)


def calculate_comfortable_days(
    ds: xr.Dataset,
    tmean_var: str = 'tmean',
    recent_year: int = None,
) -> ComfortableDays:
    """Calculate comfortable days count for most recent year and long-term average.
    
    Args:
        ds: Dataset with daily mean temperature data
        tmean_var: Daily mean temperature variable name
        recent_year: Year to report count for (defaults to last year in dataset)
        
    Returns:
        ComfortableDays dictionary
    """
    comfortable_mask = identify_comfortable_days(ds, tmean_var)
    
    # Spatial mean for country-level
    spatial_dims = [d for d in comfortable_mask.dims if d not in ['time']]
    if spatial_dims:
        comfortable_spatial = comfortable_mask.mean(dim=spatial_dims)
    else:
        comfortable_spatial = comfortable_mask
    
    # Annual count
    annual_comfortable = comfortable_spatial.resample(time='YE').sum()
    years = annual_comfortable['time'].dt.year.values
    
    # Determine target year
    target_year = recent_year or int(years[-1])
    
    # Count for target year
    year_mask = years == target_year
    if not np.any(year_mask):
        raise ValueError(f"No data for year {target_year}")
    
    count = float(annual_comfortable.values[year_mask][0])
    
    # Long-term average (all available years)
    long_term_avg = float(np.nanmean(annual_comfortable.values))
    
    logger.info(
        f"Comfortable days for {target_year}: {count:.0f} "
        f"(long-term average: {long_term_avg:.1f})"
    )
    
    return ComfortableDays(
        count=int(round(count)),
        average=round(long_term_avg, 1),
    )


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Calculate comfortable days')
    parser.add_argument('input_file', help='Input NetCDF with daily mean temperature')
    parser.add_argument('--variable', default='tmean', help='Mean temperature variable')
    parser.add_argument('--year', type=int, help='Year to report (default: last year)')
    args = parser.parse_args()
    
    ds = xr.open_dataset(args.input_file)
    result = calculate_comfortable_days(ds, args.variable, args.year)
    
    print(f"\nComfortable Days (15-25°C):")
    print(f"  Count: {result['count']} days")
    print(f"  Long-term average: {result['average']} days/year")
