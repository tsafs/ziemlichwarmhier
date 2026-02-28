#!/usr/bin/env python3
"""
Calculate linear warming trend (°C/decade) using linear regression.

Uses scipy.stats.linregress for robust trend analysis.
"""

import logging

import numpy as np
import xarray as xr
from scipy.stats import linregress

from .config import MIN_R_SQUARED, MIN_YEARS_FOR_TREND, WARMING_RATE_PERIOD
from .types import WarmingRate

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def calculate_annual_means(
    ds: xr.Dataset,
    variable: str,
    period: dict,
) -> tuple:
    """Calculate annual means for a period.
    
    Args:
        ds: Dataset with time coordinate
        variable: Variable to average
        period: Period dict with start_year and end_year
        
    Returns:
        Tuple of (years array, means array)
    """
    start = period['start_year']
    end = period['end_year']
    
    # Filter to period
    time_mask = (ds['time'].dt.year >= start) & (ds['time'].dt.year <= end)
    period_data = ds[variable].where(time_mask, drop=True)
    
    if len(period_data['time']) == 0:
        raise ValueError(f"No data for period {start}-{end}")
    
    # Annual means (spatial mean → time series)
    # If spatial dims exist, average over space first
    spatial_dims = [d for d in ['latitude', 'longitude'] if d in period_data.dims]
    if spatial_dims:
        spatial_mean = period_data.mean(dim=spatial_dims)
    else:
        spatial_mean = period_data
    
    # Group by year
    annual = spatial_mean.groupby('time.year').mean()
    
    years = annual['year'].values.astype(float)
    means = annual.values
    
    return years, means


def calculate_warming_rate(
    ds: xr.Dataset,
    variable: str,
    period: dict = None,
) -> WarmingRate:
    """Calculate linear warming trend.
    
    Args:
        ds: Dataset with temperature data
        variable: Temperature variable name
        period: Analysis period (defaults to WARMING_RATE_PERIOD)
        
    Returns:
        WarmingRate dictionary with °C/decade and R²
    """
    analysis_period = period or WARMING_RATE_PERIOD
    start = analysis_period['start_year']
    end = analysis_period['end_year']
    
    logger.info(f"Calculating warming rate for {start}-{end}")
    
    years, means = calculate_annual_means(ds, variable, analysis_period)
    
    # Remove NaN
    valid_mask = ~np.isnan(means)
    years_valid = years[valid_mask]
    means_valid = means[valid_mask]
    
    if len(years_valid) < MIN_YEARS_FOR_TREND:
        logger.warning(
            f"Only {len(years_valid)} valid years, need {MIN_YEARS_FOR_TREND}. "
            "Returning zero trend."
        )
        return WarmingRate(
            value=0.0,
            startYear=start,
            endYear=end,
            confidence=0.0,
        )
    
    # Linear regression: slope in °C/year → convert to °C/decade
    slope, intercept, r_value, p_value, std_err = linregress(years_valid, means_valid)
    
    # °C/decade
    warming_per_decade = slope * 10
    r_squared = r_value ** 2
    
    if r_squared < MIN_R_SQUARED:
        logger.warning(
            f"Low R² ({r_squared:.2f} < {MIN_R_SQUARED}) for warming rate — trend may not be significant"
        )
    
    logger.info(
        f"Warming rate: {warming_per_decade:.3f}°C/decade, "
        f"R²={r_squared:.2f}, p={p_value:.4f}"
    )
    
    return WarmingRate(
        value=round(warming_per_decade, 3),
        startYear=int(start),
        endYear=int(end),
        confidence=round(r_squared, 3),
    )


def calculate_warming_rate_grid(
    ds: xr.Dataset,
    variable: str,
    period: dict = None,
) -> xr.DataArray:
    """Calculate warming rate at each grid point.
    
    Args:
        ds: Dataset with temperature data
        variable: Temperature variable name
        period: Analysis period
        
    Returns:
        DataArray of warming rates (°C/decade) per grid cell
    """
    analysis_period = period or WARMING_RATE_PERIOD
    start = analysis_period['start_year']
    end = analysis_period['end_year']
    
    # Filter to period
    time_mask = (ds['time'].dt.year >= start) & (ds['time'].dt.year <= end)
    period_data = ds[variable].where(time_mask, drop=True)
    
    # Annual means keeping spatial dimensions
    annual = period_data.groupby('time.year').mean()
    
    years = annual['year'].values.astype(float)
    
    # Vectorized regression using polyfit
    # xarray.polyfit fits over a dimension
    poly_result = annual.polyfit(dim='year', deg=1)
    
    # Coefficient[0] is the slope (°C/year) → convert to °C/decade
    slope = poly_result.polyfit_coefficients.sel(degree=1)
    warming_per_decade = slope * 10
    
    # Rename for clarity
    warming_per_decade.name = 'warming_rate_per_decade'
    
    return warming_per_decade


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Calculate warming rate')
    parser.add_argument('input_file', help='Input NetCDF file')
    parser.add_argument('--variable', default='t2m', help='Temperature variable')
    args = parser.parse_args()
    
    ds = xr.open_dataset(args.input_file)
    result = calculate_warming_rate(ds, args.variable)
    
    print(f"\nWarming Rate:")
    print(f"  Period: {result['startYear']}-{result['endYear']}")
    print(f"  Rate: {result['value']:+.3f}°C/decade")
    print(f"  Confidence (R²): {result['confidence']:.2f}")
