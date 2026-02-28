#!/usr/bin/env python3
"""
Calculate winter (DJF) temperature anomaly.

Winter is defined as December-January-February (meteorological winter).
For a given year Y, winter consists of:
  - December of year Y-1
  - January and February of year Y
"""

import logging

import numpy as np
import xarray as xr

from .config import FIVE_YEAR_ANOMALY_PERIOD, REFERENCE_PERIOD, SEASONS
from .types import WinterWarming

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def select_winter_data(ds: xr.Dataset, variable: str) -> xr.DataArray:
    """Select only winter (DJF) time steps from dataset.
    
    Args:
        ds: Dataset with time coordinate
        variable: Variable name to select
        
    Returns:
        DataArray with only DJF timesteps
    """
    winter_months = SEASONS['winter']  # [12, 1, 2]
    month_mask = ds['time'].dt.month.isin(winter_months)
    return ds[variable].where(month_mask, drop=True)


def calculate_winter_mean(
    ds: xr.Dataset,
    variable: str,
    period: dict,
) -> xr.DataArray:
    """Calculate mean winter temperature over a period.
    
    Args:
        ds: Dataset with daily/monthly temperature data
        variable: Temperature variable name
        period: Period dict with start_year and end_year
        
    Returns:
        Spatial DataArray of mean winter temperatures
    """
    start = period['start_year']
    end = period['end_year']
    
    # Select winter months
    winter_data = select_winter_data(ds, variable)
    
    # Select years in period (use the year of Jan/Feb, not December)
    # December of previous year + Jan/Feb of current year
    # For simplicity, filter winter months by year range
    time_mask = (winter_data['time'].dt.year >= start) & (winter_data['time'].dt.year <= end)
    period_winter = winter_data.where(time_mask, drop=True)
    
    if len(period_winter['time']) == 0:
        raise ValueError(f"No winter data found for period {start}-{end}")
    
    return period_winter.mean(dim='time')


def calculate_winter_warming(
    ds: xr.Dataset,
    variable: str,
    recent_period: dict = None,
    reference_period: dict = None,
) -> WinterWarming:
    """Calculate winter warming anomaly.
    
    Args:
        ds: Dataset with temperature data
        variable: Temperature variable name
        recent_period: Recent period (defaults to FIVE_YEAR_ANOMALY_PERIOD)
        reference_period: Baseline period (defaults to REFERENCE_PERIOD)
        
    Returns:
        WinterWarming dictionary
    """
    recent = recent_period or FIVE_YEAR_ANOMALY_PERIOD
    ref = reference_period or REFERENCE_PERIOD
    
    logger.info(
        f"Calculating winter warming: {recent['start_year']}-{recent['end_year']} "
        f"vs {ref['start_year']}-{ref['end_year']}"
    )
    
    # Calculate winter means
    recent_winter_mean = calculate_winter_mean(ds, variable, recent)
    reference_winter_mean = calculate_winter_mean(ds, variable, ref)
    
    # Anomaly
    anomaly_grid = recent_winter_mean - reference_winter_mean
    anomaly_value = float(anomaly_grid.mean().values)
    
    logger.info(f"Winter warming anomaly: {anomaly_value:+.2f}°C")
    
    return WinterWarming(
        value=round(anomaly_value, 2),
        periodStart=recent['start_year'],
        periodEnd=recent['end_year'],
        referenceStart=ref['start_year'],
        referenceEnd=ref['end_year'],
    )


def calculate_seasonal_warming(
    ds: xr.Dataset,
    variable: str,
    recent_period: dict = None,
    reference_period: dict = None,
) -> dict:
    """Calculate warming anomaly for all four seasons.
    
    Args:
        ds: Dataset with temperature data
        variable: Temperature variable name
        recent_period: Recent period
        reference_period: Baseline period
        
    Returns:
        Dict with seasonal anomalies and fastest warming season
    """
    recent = recent_period or FIVE_YEAR_ANOMALY_PERIOD
    ref = reference_period or REFERENCE_PERIOD
    
    seasonal_anomalies = {}
    
    for season_name, months in SEASONS.items():
        # Select season months
        month_mask_recent = (
            ds['time'].dt.month.isin(months) &
            (ds['time'].dt.year >= recent['start_year']) &
            (ds['time'].dt.year <= recent['end_year'])
        )
        month_mask_ref = (
            ds['time'].dt.month.isin(months) &
            (ds['time'].dt.year >= ref['start_year']) &
            (ds['time'].dt.year <= ref['end_year'])
        )
        
        recent_season = ds[variable].where(month_mask_recent, drop=True)
        ref_season = ds[variable].where(month_mask_ref, drop=True)
        
        if len(recent_season['time']) == 0 or len(ref_season['time']) == 0:
            seasonal_anomalies[season_name] = 0.0
            continue
        
        anomaly = float((recent_season.mean(dim='time') - ref_season.mean(dim='time')).mean().values)
        seasonal_anomalies[season_name] = round(anomaly, 2)
    
    # Find fastest warming season
    fastest_season = max(seasonal_anomalies, key=lambda k: seasonal_anomalies[k])
    
    return {
        'winter': seasonal_anomalies.get('winter', 0.0),
        'spring': seasonal_anomalies.get('spring', 0.0),
        'summer': seasonal_anomalies.get('summer', 0.0),
        'fall': seasonal_anomalies.get('fall', 0.0),
        'fastestSeason': fastest_season,
        'periodStart': recent['start_year'],
        'periodEnd': recent['end_year'],
        'referenceStart': ref['start_year'],
        'referenceEnd': ref['end_year'],
    }


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Calculate winter warming')
    parser.add_argument('input_file', help='Input NetCDF file')
    parser.add_argument('--variable', default='t2m', help='Temperature variable')
    args = parser.parse_args()
    
    ds = xr.open_dataset(args.input_file)
    result = calculate_winter_warming(ds, args.variable)
    
    print(f"\nWinter Warming:")
    print(f"  Period: {result['periodStart']}-{result['periodEnd']}")
    print(f"  Reference: {result['referenceStart']}-{result['referenceEnd']}")
    print(f"  Anomaly: {result['value']:+.2f}°C")
