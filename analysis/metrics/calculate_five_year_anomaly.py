#!/usr/bin/env python3
"""
Calculate 5-year mean temperature anomaly relative to a reference climatology.

The anomaly represents how much warmer/cooler the recent 5-year period is
compared to pre-industrial baseline (1961-1990 reference period).
"""

import logging

import numpy as np
import xarray as xr

from .config import FIVE_YEAR_ANOMALY_PERIOD, REFERENCE_PERIOD
from .types import FiveYearAnomaly

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def calculate_five_year_mean(
    ds: xr.Dataset,
    variable: str,
    period: dict,
) -> xr.DataArray:
    """Calculate mean over a 5-year period.
    
    Args:
        ds: Dataset with time coordinate
        variable: Variable name to average
        period: Dict with 'start_year' and 'end_year'
        
    Returns:
        Spatial DataArray of mean values over the period
    """
    start = period['start_year']
    end = period['end_year']
    
    # Select years in period
    time_mask = (ds['time'].dt.year >= start) & (ds['time'].dt.year <= end)
    period_data = ds[variable].where(time_mask, drop=True)
    
    if len(period_data['time']) == 0:
        raise ValueError(f"No data found for period {start}-{end}")
    
    # Mean over time dimension to get spatial field
    return period_data.mean(dim='time')


def calculate_reference_climatology(
    ds: xr.Dataset,
    variable: str,
    reference_period: dict = None,
) -> xr.DataArray:
    """Calculate long-term mean over reference period.
    
    Args:
        ds: Dataset with time coordinate
        variable: Variable name to average
        reference_period: Period dict (defaults to REFERENCE_PERIOD)
        
    Returns:
        Spatial DataArray of reference climatology
    """
    ref_period = reference_period or REFERENCE_PERIOD
    return calculate_five_year_mean(ds, variable, ref_period)


def calculate_five_year_anomaly(
    ds: xr.Dataset,
    variable: str,
    recent_period: dict = None,
    reference_period: dict = None,
) -> FiveYearAnomaly:
    """Calculate 5-year mean temperature anomaly.
    
    Computes anomaly as: recent_mean - reference_mean
    
    Args:
        ds: Dataset with daily/monthly temperature data
        variable: Temperature variable name
        recent_period: Period to compare (defaults to FIVE_YEAR_ANOMALY_PERIOD)
        reference_period: Baseline period (defaults to REFERENCE_PERIOD)
        
    Returns:
        FiveYearAnomaly dictionary
    """
    recent = recent_period or FIVE_YEAR_ANOMALY_PERIOD
    ref = reference_period or REFERENCE_PERIOD
    
    logger.info(
        f"Calculating 5-year anomaly: {recent['start_year']}-{recent['end_year']} "
        f"vs {ref['start_year']}-{ref['end_year']}"
    )
    
    # Calculate means
    recent_mean = calculate_five_year_mean(ds, variable, recent)
    reference_mean = calculate_reference_climatology(ds, variable, ref)
    
    # Anomaly = recent - reference
    anomaly_grid = recent_mean - reference_mean
    
    # Country-level value (spatial mean)
    anomaly_value = float(anomaly_grid.mean().values)
    
    logger.info(f"5-year anomaly: {anomaly_value:.2f}°C")
    
    return FiveYearAnomaly(
        value=round(anomaly_value, 2),
        periodStart=recent['start_year'],
        periodEnd=recent['end_year'],
        referenceStart=ref['start_year'],
        referenceEnd=ref['end_year'],
    )


def calculate_annual_anomaly_grid(
    ds: xr.Dataset,
    variable: str,
    reference_period: dict = None,
) -> xr.DataArray:
    """Calculate annual anomaly relative to reference for each year.
    
    Args:
        ds: Dataset with daily/monthly temperature data
        variable: Temperature variable name
        reference_period: Baseline period (defaults to REFERENCE_PERIOD)
        
    Returns:
        DataArray with dims (year, latitude, longitude)
    """
    ref = reference_period or REFERENCE_PERIOD
    reference_mean = calculate_reference_climatology(ds, variable, ref)
    
    # Group by year and compute annual means
    annual_means = ds[variable].groupby('time.year').mean()
    
    # Subtract reference climatology
    anomalies = annual_means - reference_mean
    
    return anomalies


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Calculate 5-year temperature anomaly')
    parser.add_argument('input_file', help='Input NetCDF file')
    parser.add_argument('--variable', default='t2m', help='Temperature variable name')
    args = parser.parse_args()
    
    ds = xr.open_dataset(args.input_file)
    result = calculate_five_year_anomaly(ds, args.variable)
    
    print(f"\n5-Year Temperature Anomaly:")
    print(f"  Period: {result['periodStart']}-{result['periodEnd']}")
    print(f"  Reference: {result['referenceStart']}-{result['referenceEnd']}")
    print(f"  Anomaly: {result['value']:+.2f}°C")
