#!/usr/bin/env python3
"""
Calculate temperature record days for a given year.

A record day is when the temperature exceeds the historical max (hot record)
or falls below the historical min (cold record) for that calendar day.
"""

import logging
from datetime import datetime

import numpy as np
import xarray as xr

from .types import RecordDays

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def calculate_historical_extremes(
    ds: xr.Dataset,
    tmax_var: str,
    tmin_var: str,
    reference_end_year: int,
) -> tuple:
    """Calculate day-of-year historical max and min over reference period.
    
    Args:
        ds: Dataset with daily temperature data
        tmax_var: Daily maximum temperature variable
        tmin_var: Daily minimum temperature variable
        reference_end_year: Last year of historical baseline (exclusive — records are
                            'new' only *after* this period)
        
    Returns:
        Tuple of (historical_tmax_by_doy, historical_tmin_by_doy) DataArrays
    """
    # Use all years up to reference_end_year as historical baseline
    historical_mask = ds['time'].dt.year <= reference_end_year
    historical_ds = ds.where(historical_mask, drop=True)
    
    # Group by day-of-year and take max/min
    historical_tmax = historical_ds[tmax_var].groupby('time.dayofyear').max()
    historical_tmin = historical_ds[tmin_var].groupby('time.dayofyear').min()
    
    return historical_tmax, historical_tmin


def count_record_days(
    ds: xr.Dataset,
    year: int,
    tmax_var: str = 'tmax',
    tmin_var: str = 'tmin',
    reference_end_year: int = 2020,
) -> RecordDays:
    """Count temperature record days in a year.
    
    Hot records: new Tmax > historical max for that day of year.
    Cold records: new Tmin < historical min for that day of year.
    
    Args:
        ds: Dataset with full time series
        year: Year to check for records
        tmax_var: Daily maximum temperature variable
        tmin_var: Daily minimum temperature variable
        reference_end_year: Historical baseline ends at this year (inclusive)
        
    Returns:
        RecordDays dictionary
    """
    # Build historical extremes from pre-record period
    hist_tmax, hist_tmin = calculate_historical_extremes(
        ds, tmax_var, tmin_var, reference_end_year
    )
    
    # Select target year data
    year_mask = ds['time'].dt.year == year
    year_ds = ds.where(year_mask, drop=True)
    
    if len(year_ds['time']) == 0:
        raise ValueError(f"No data for year {year}")
    
    # Spatial mean for country-level counts
    spatial_dims = [d for d in year_ds[tmax_var].dims if d != 'time']
    if spatial_dims:
        year_tmax = year_ds[tmax_var].mean(dim=spatial_dims)
        year_tmin = year_ds[tmin_var].mean(dim=spatial_dims)
        hist_tmax_mean = hist_tmax.mean(dim=spatial_dims)
        hist_tmin_mean = hist_tmin.mean(dim=spatial_dims)
    else:
        year_tmax = year_ds[tmax_var]
        year_tmin = year_ds[tmin_var]
        hist_tmax_mean = hist_tmax
        hist_tmin_mean = hist_tmin
    
    # Compare each day to historical max/min for that day-of-year
    doys = year_ds['time'].dt.dayofyear.values
    
    hot_records = 0
    cold_records = 0
    
    for i, doy in enumerate(doys):
        if doy not in hist_tmax_mean['dayofyear'].values:
            continue
        
        t_max = float(year_tmax.isel(time=i).values)
        t_min = float(year_tmin.isel(time=i).values)
        hist_max = float(hist_tmax_mean.sel(dayofyear=doy).values)
        hist_min = float(hist_tmin_mean.sel(dayofyear=doy).values)
        
        if not np.isnan(t_max) and not np.isnan(hist_max):
            if t_max > hist_max:
                hot_records += 1
        
        if not np.isnan(t_min) and not np.isnan(hist_min):
            if t_min < hist_min:
                cold_records += 1
    
    total = hot_records + cold_records
    
    logger.info(
        f"Record days for {year}: total={total}, hot={hot_records}, cold={cold_records}"
    )
    
    return RecordDays(
        total=total,
        hot=hot_records,
        cold=cold_records,
        year=year,
    )


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Calculate record days')
    parser.add_argument('input_file', help='Input NetCDF with daily Tmax/Tmin')
    parser.add_argument('--year', type=int, required=True)
    parser.add_argument('--reference-end', type=int, default=2020)
    args = parser.parse_args()
    
    ds = xr.open_dataset(args.input_file)
    result = count_record_days(ds, args.year, reference_end_year=args.reference_end)
    
    print(f"Record Days for {result['year']}:")
    print(f"  Hot records: {result['hot']}")
    print(f"  Cold records: {result['cold']}")
    print(f"  Total: {result['total']}")
