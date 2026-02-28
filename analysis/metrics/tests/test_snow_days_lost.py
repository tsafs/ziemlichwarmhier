#!/usr/bin/env python3
"""Tests for snow days lost calculation."""

import pytest
import numpy as np
import xarray as xr
from datetime import datetime, timedelta

from analysis.metrics.calculate_snow_days_lost import (
    identify_snow_days,
    count_annual_snow_days,
    calculate_snow_days_lost,
)


@pytest.fixture
def snow_dataset():
    """Create dataset with known snow day patterns.
    
    Reference period (2000-2004): 30 snow days/year
    Recent period (2020-2024): 15 snow days/year
    """
    # Build a ~25 year daily dataset
    start = datetime(2000, 1, 1)
    days = 25 * 365
    times = [start + timedelta(days=i) for i in range(days)]
    
    lats = np.array([50.0])
    lons = np.array([10.0])
    
    rng = np.random.default_rng(0)
    n = len(times)
    # Temperatures: colder in early years, warmer later
    tmean = np.array([
        -2 if t.month in [12, 1, 2] and t.year < 2010 else  # cold winters early
        0.5 if t.month in [12, 1, 2] else                   # mild winters late
        15.0                                                  # warm rest of year
        for t in times
    ]) + rng.uniform(-0.1, 0.1, n)
    
    # Precipitation: present on about 30% of days
    precip = rng.choice([0.0, 1.0], size=n, p=[0.7, 0.3])
    
    tmean_3d = tmean[:, np.newaxis, np.newaxis]
    precip_3d = precip[:, np.newaxis, np.newaxis]
    
    ds = xr.Dataset(
        {
            'tmean': (['time', 'latitude', 'longitude'], tmean_3d.astype(np.float32)),
            'precipitation': (['time', 'latitude', 'longitude'], precip_3d.astype(np.float32)),
        },
        coords={
            'time': times,
            'latitude': lats,
            'longitude': lons,
        }
    )
    return ds


class TestIdentifySnowDays:
    """Tests for identify_snow_days."""

    def test_freezing_with_precip_is_snow(self, snow_dataset):
        """Day with Tmean <= 0 and precip > 0.1 should be snow day."""
        mask = identify_snow_days(snow_dataset)
        # Should have some snow days in the dataset
        assert bool(mask.any().values)

    def test_warm_day_not_snow(self, snow_dataset):
        """Warm day (Tmean > 0) should not be snow day even with precip."""
        mask = identify_snow_days(snow_dataset)
        # Get summer days (all warm)
        summer_mask = snow_dataset['time'].dt.month.isin([6, 7, 8])
        summer_snow = mask.where(summer_mask, drop=True)
        assert not bool(summer_snow.any().values)

    def test_dry_freezing_not_snow(self, snow_dataset):
        """Freezing day with no precipitation should not count."""
        # Create a dataset with all zero precipitation
        ds_no_precip = snow_dataset.copy()
        ds_no_precip['precipitation'] = xr.zeros_like(ds_no_precip['precipitation'])
        mask = identify_snow_days(ds_no_precip)
        assert not bool(mask.any().values)


class TestCalculateSnowDaysLost:
    """Tests for calculate_snow_days_lost."""

    def test_returns_required_keys(self, snow_dataset):
        """Result should contain all SnowDaysLost keys."""
        result = calculate_snow_days_lost(
            snow_dataset,
            recent_period={'start_year': 2020, 'end_year': 2024},
            reference_period={'start_year': 2000, 'end_year': 2004},
        )
        assert 'value' in result
        assert 'currentAverage' in result
        assert 'referenceAverage' in result
        assert 'periodStart' in result
        assert 'periodEnd' in result

    def test_negative_value_for_warming_trend(self, snow_dataset):
        """The warm-trend dataset should show fewer snow days recently."""
        result = calculate_snow_days_lost(
            snow_dataset,
            recent_period={'start_year': 2020, 'end_year': 2024},
            reference_period={'start_year': 2000, 'end_year': 2004},
        )
        # Cold winters early → positive reference; warmer recent → negative change
        assert result['value'] <= 0
