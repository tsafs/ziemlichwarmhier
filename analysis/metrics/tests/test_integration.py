#!/usr/bin/env python3
"""Integration tests for the metrics pipeline."""

import pytest
import numpy as np
import xarray as xr
from datetime import datetime, timedelta

from analysis.metrics.calculate_five_year_anomaly import calculate_five_year_anomaly
from analysis.metrics.calculate_warming_rate import calculate_warming_rate
from analysis.metrics.calculate_threshold_days import calculate_threshold_days
from analysis.metrics.calculate_winter_warming import calculate_winter_warming, calculate_seasonal_warming
from analysis.metrics.calculate_comfortable_days import calculate_comfortable_days
from analysis.metrics.export_metrics import validate_metrics_schema


@pytest.fixture
def full_pipeline_dataset():
    """Create a comprehensive dataset for pipeline integration tests."""
    rng = np.random.default_rng(42)
    start = datetime(1961, 1, 1)
    days = (2025 - 1961) * 365 + 365
    times = [start + timedelta(days=i) for i in range(days)]
    
    lats = np.linspace(48, 52, 3)
    lons = np.linspace(8, 12, 3)
    
    n = len(times)
    seasonal = 12 * np.sin(np.linspace(0, 2*np.pi*(days/365), n))
    base = np.array([9.0 + 0.03 * (t.year - 1961) for t in times])
    noise = rng.uniform(-2, 2, n)
    tmean = base + seasonal + noise
    
    tmax = tmean + 6 + rng.uniform(0, 3, n)
    tmin = tmean - 6 - rng.uniform(0, 3, n)
    precip = np.abs(rng.normal(1.5, 2.0, n))
    
    shape = (n, len(lats), len(lons))
    
    ds = xr.Dataset(
        {
            't2m': (['time', 'latitude', 'longitude'],
                    np.broadcast_to(tmean[:, None, None], shape).copy().astype(np.float32)),
            'tmax': (['time', 'latitude', 'longitude'],
                     np.broadcast_to(tmax[:, None, None], shape).copy().astype(np.float32)),
            'tmin': (['time', 'latitude', 'longitude'],
                     np.broadcast_to(tmin[:, None, None], shape).copy().astype(np.float32)),
            'tmean': (['time', 'latitude', 'longitude'],
                      np.broadcast_to(tmean[:, None, None], shape).copy().astype(np.float32)),
            'precipitation': (['time', 'latitude', 'longitude'],
                              np.broadcast_to(precip[:, None, None], shape).copy().astype(np.float32)),
        },
        coords={
            'time': times,
            'latitude': lats,
            'longitude': lons,
        }
    )
    return ds


class TestMetricsPipeline:
    """End-to-end tests of the metrics pipeline."""

    def test_five_year_anomaly_runs(self, full_pipeline_dataset):
        """five_year_anomaly should complete without error."""
        result = calculate_five_year_anomaly(full_pipeline_dataset, 't2m')
        assert result['value'] != 0  # Should detect warming trend

    def test_warming_rate_runs(self, full_pipeline_dataset):
        """warming_rate should detect a positive trend."""
        result = calculate_warming_rate(full_pipeline_dataset, 't2m')
        assert result['confidence'] > 0.5  # Should be well-correlated

    def test_threshold_days_runs(self, full_pipeline_dataset):
        """threshold_days should complete without error."""
        result = calculate_threshold_days(full_pipeline_dataset, 2024)
        assert result['year'] == 2024
        assert result['hotDays'] >= 0
        assert result['frostDays'] >= 0

    def test_winter_warming_runs(self, full_pipeline_dataset):
        """winter_warming should complete without error."""
        result = calculate_winter_warming(full_pipeline_dataset, 't2m')
        assert 'value' in result

    def test_seasonal_warming_runs(self, full_pipeline_dataset):
        """seasonal_warming should provide all four seasons."""
        result = calculate_seasonal_warming(full_pipeline_dataset, 't2m')
        assert 'winter' in result
        assert 'spring' in result
        assert 'summer' in result
        assert 'fall' in result
        assert result['fastestSeason'] in ['winter', 'spring', 'summer', 'fall']

    def test_comfortable_days_runs(self, full_pipeline_dataset):
        """comfortable_days should complete without error."""
        result = calculate_comfortable_days(full_pipeline_dataset, 'tmean', recent_year=2024)
        assert result['count'] >= 0
        assert result['average'] >= 0

    def test_validate_schema_catches_missing_key(self):
        """validate_metrics_schema should raise on missing required key."""
        incomplete = {
            'fiveYearAnomaly': {'value': 1.0},
            # Missing 'warmingRate' and others
        }
        with pytest.raises(ValueError):
            validate_metrics_schema(incomplete)
