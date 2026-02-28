#!/usr/bin/env python3
"""Pytest fixtures for metrics tests."""

import pytest
import numpy as np
import xarray as xr
from datetime import datetime, timedelta


@pytest.fixture
def sample_temperature_dataset():
    """Create sample temperature dataset for testing.
    
    Contains daily data for 3 years with known patterns.
    """
    # Create time coordinate for 3 years
    start = datetime(2022, 1, 1)
    times = [start + timedelta(days=i) for i in range(365 * 3)]
    
    # Small grid
    lats = np.linspace(48, 52, 5)
    lons = np.linspace(8, 12, 5)
    
    # Generate synthetic temperature data
    # Base: 10°C with seasonal pattern (+/- 15°C)
    base_temp = 10
    seasonal = 15 * np.sin(np.linspace(0, 2*np.pi*3, len(times)))
    
    rng = np.random.default_rng(42)
    # Create 3D temperature array
    temps = np.zeros((len(times), len(lats), len(lons)))
    for i, _ in enumerate(times):
        temps[i] = base_temp + seasonal[i] + rng.uniform(-2, 2, (len(lats), len(lons)))
    
    ds = xr.Dataset(
        {
            't2m': (['time', 'latitude', 'longitude'], temps.astype(np.float32))
        },
        coords={
            'time': times,
            'latitude': lats,
            'longitude': lons,
        }
    )
    
    return ds


@pytest.fixture
def sample_daily_extremes_dataset():
    """Create dataset with daily Tmax/Tmin for threshold tests."""
    times = [datetime(2024, 1, 1) + timedelta(days=i) for i in range(365)]
    lats = np.linspace(48, 52, 5)
    lons = np.linspace(8, 12, 5)
    
    rng = np.random.default_rng(42)
    # Tmax: 0-35°C range with summer peak
    tmax_base = 17.5 + 17.5 * np.sin(np.linspace(-np.pi/2, 3*np.pi/2, 365))
    tmax = np.broadcast_to(tmax_base[:, np.newaxis, np.newaxis], (365, 5, 5)).copy()
    tmax = tmax + rng.uniform(-3, 3, (365, 5, 5))
    
    # Tmin: typically 8-10°C below Tmax
    tmin = tmax - 8 + rng.uniform(-2, 2, (365, 5, 5))
    
    ds = xr.Dataset(
        {
            'tmax': (['time', 'latitude', 'longitude'], tmax.astype(np.float32)),
            'tmin': (['time', 'latitude', 'longitude'], tmin.astype(np.float32)),
        },
        coords={
            'time': times,
            'latitude': lats,
            'longitude': lons,
        }
    )
    
    return ds


@pytest.fixture
def linear_trend_dataset():
    """Create dataset with known linear warming trend.
    
    Trend: 0.4°C/decade = 0.04°C/year
    """
    years = range(1991, 2025)
    temps = [10 + 0.04 * (y - 1991) for y in years]  # Perfect linear trend
    
    times = [datetime(y, 6, 15) for y in years]  # Mid-year
    lats = np.array([50.0])
    lons = np.array([10.0])
    
    ds = xr.Dataset(
        {
            't2m': (['time', 'latitude', 'longitude'], np.array(temps)[:, np.newaxis, np.newaxis])
        },
        coords={
            'time': times,
            'latitude': lats,
            'longitude': lons,
        }
    )
    
    return ds


@pytest.fixture
def long_temperature_dataset():
    """Create a long dataset spanning 1961-2025 with a warming trend.
    
    Used for anomaly and warming rate tests that need reference period data.
    """
    rng = np.random.default_rng(42)
    years = range(1961, 2026)
    times = [datetime(y, 6, 15) for y in years]
    lats = np.array([50.0, 51.0])
    lons = np.array([10.0, 11.0])
    
    # Linear trend: 0.03°C/year from base 9°C in 1961
    base = 9.0
    trend_temps = [base + 0.03 * (y - 1961) + rng.uniform(-0.5, 0.5) for y in years]
    
    temps = np.array(trend_temps)[:, np.newaxis, np.newaxis] * np.ones((len(years), 2, 2))
    
    ds = xr.Dataset(
        {
            't2m': (['time', 'latitude', 'longitude'], temps.astype(np.float32)),
        },
        coords={
            'time': times,
            'latitude': lats,
            'longitude': lons,
        }
    )
    
    return ds
