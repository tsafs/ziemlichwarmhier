#!/usr/bin/env python3
"""
Calculate temperature threshold day counts.

Counts days exceeding various temperature thresholds per year:
- Hot days: Tmax >= 30°C
- Tropical nights: Tmin > 20°C
- Ice days: Tmax <= 0°C
- Frost days: Tmin < 0°C
"""

import logging

import numpy as np
import xarray as xr

from .config import THRESHOLDS
from .types import ThresholdDays

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def count_hot_days(tmax: np.ndarray, threshold: float = None) -> int:
    """Count days with Tmax >= threshold.
    
    Args:
        tmax: Array of daily maximum temperatures
        threshold: Temperature threshold (default: 30°C)
        
    Returns:
        Number of hot days
    """
    threshold = threshold if threshold is not None else THRESHOLDS['hot_day']
    return int(np.sum(tmax >= threshold))


def count_tropical_nights(tmin: np.ndarray, threshold: float = None) -> int:
    """Count nights with Tmin > threshold.
    
    Note: Threshold is > (not >=) for tropical nights.
    
    Args:
        tmin: Array of daily minimum temperatures
        threshold: Temperature threshold (default: 20°C)
        
    Returns:
        Number of tropical nights
    """
    threshold = threshold if threshold is not None else THRESHOLDS['tropical_night']
    return int(np.sum(tmin > threshold))


def count_ice_days(tmax: np.ndarray, threshold: float = None) -> int:
    """Count days with Tmax <= threshold.
    
    Args:
        tmax: Array of daily maximum temperatures
        threshold: Temperature threshold (default: 0°C)
        
    Returns:
        Number of ice days
    """
    threshold = threshold if threshold is not None else THRESHOLDS['ice_day']
    return int(np.sum(tmax <= threshold))


def count_frost_days(tmin: np.ndarray, threshold: float = None) -> int:
    """Count days with Tmin < threshold.
    
    Note: Threshold is < (not <=) for frost days.
    
    Args:
        tmin: Array of daily minimum temperatures
        threshold: Temperature threshold (default: 0°C)
        
    Returns:
        Number of frost days
    """
    threshold = threshold if threshold is not None else THRESHOLDS['frost_day']
    return int(np.sum(tmin < threshold))


def calculate_threshold_days(
    ds: xr.Dataset,
    year: int,
    tmax_var: str = 'tmax',
    tmin_var: str = 'tmin',
) -> ThresholdDays:
    """Calculate all threshold day counts for a year.
    
    Args:
        ds: Dataset with daily temperature data
        year: Year to calculate
        tmax_var: Daily maximum temperature variable name
        tmin_var: Daily minimum temperature variable name
        
    Returns:
        ThresholdDays dictionary
    """
    # Select year
    year_mask = ds['time'].dt.year == year
    
    # Get spatial mean for country-level
    tmax = ds[tmax_var].where(year_mask, drop=True).mean(dim=['latitude', 'longitude']).values
    tmin = ds[tmin_var].where(year_mask, drop=True).mean(dim=['latitude', 'longitude']).values
    
    # Remove NaN
    tmax = tmax[~np.isnan(tmax)]
    tmin = tmin[~np.isnan(tmin)]
    
    hot_days = count_hot_days(tmax)
    tropical_nights = count_tropical_nights(tmin)
    ice_days = count_ice_days(tmax)
    frost_days = count_frost_days(tmin)
    
    logger.info(
        f"Threshold days for {year}: "
        f"hot={hot_days}, tropical_nights={tropical_nights}, "
        f"ice={ice_days}, frost={frost_days}"
    )
    
    return ThresholdDays(
        hotDays=hot_days,
        tropicalNights=tropical_nights,
        iceDays=ice_days,
        frostDays=frost_days,
        year=year,
    )


def calculate_threshold_days_grid(
    ds: xr.Dataset,
    year: int,
    tmax_var: str = 'tmax',
    tmin_var: str = 'tmin',
) -> dict:
    """Calculate threshold days at each grid point.
    
    Args:
        ds: Dataset with daily temperature data
        year: Year to calculate
        tmax_var, tmin_var: Variable names
        
    Returns:
        Dictionary of DataArrays for each threshold type
    """
    year_mask = ds['time'].dt.year == year
    
    tmax = ds[tmax_var].where(year_mask, drop=True)
    tmin = ds[tmin_var].where(year_mask, drop=True)
    
    # Count along time dimension
    hot_days = (tmax >= THRESHOLDS['hot_day']).sum(dim='time')
    tropical_nights = (tmin > THRESHOLDS['tropical_night']).sum(dim='time')
    ice_days = (tmax <= THRESHOLDS['ice_day']).sum(dim='time')
    frost_days = (tmin < THRESHOLDS['frost_day']).sum(dim='time')
    
    return {
        'hot_days': hot_days,
        'tropical_nights': tropical_nights,
        'ice_days': ice_days,
        'frost_days': frost_days,
    }


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Calculate threshold days')
    parser.add_argument('input_file', help='Input NetCDF with daily Tmax/Tmin')
    parser.add_argument('--year', type=int, required=True)
    args = parser.parse_args()
    
    ds = xr.open_dataset(args.input_file)
    result = calculate_threshold_days(ds, args.year)
    
    print(f"Threshold Days for {result['year']}:")
    print(f"  Hot days (>=30°C): {result['hotDays']}")
    print(f"  Tropical nights (>20°C): {result['tropicalNights']}")
    print(f"  Ice days (<=0°C): {result['iceDays']}")
    print(f"  Frost days (<0°C): {result['frostDays']}")
