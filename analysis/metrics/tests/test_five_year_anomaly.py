#!/usr/bin/env python3
"""Tests for 5-year anomaly calculation."""

import pytest
import numpy as np
import xarray as xr
from datetime import datetime

from analysis.metrics.calculate_five_year_anomaly import (
    calculate_five_year_mean,
    calculate_reference_climatology,
    calculate_five_year_anomaly,
    calculate_annual_anomaly_grid,
)
from analysis.metrics.config import FIVE_YEAR_ANOMALY_PERIOD, REFERENCE_PERIOD


class TestFiveYearMean:
    """Tests for calculate_five_year_mean."""

    def test_returns_dataarray(self, long_temperature_dataset):
        """Result should be a DataArray."""
        result = calculate_five_year_mean(
            long_temperature_dataset, 't2m',
            {'start_year': 2021, 'end_year': 2025}
        )
        assert isinstance(result, xr.DataArray)

    def test_period_not_found_raises(self, long_temperature_dataset):
        """Should raise ValueError when period has no data."""
        with pytest.raises(ValueError):
            calculate_five_year_mean(
                long_temperature_dataset, 't2m',
                {'start_year': 2090, 'end_year': 2095}
            )

    def test_mean_within_reasonable_range(self, long_temperature_dataset):
        """Mean should be within data range."""
        result = calculate_five_year_mean(
            long_temperature_dataset, 't2m',
            {'start_year': 1961, 'end_year': 1990}
        )
        # Temperatures in our test data are around 9-12°C
        assert float(result.mean().values) > 5.0
        assert float(result.mean().values) < 20.0


class TestFiveYearAnomaly:
    """Tests for calculate_five_year_anomaly."""

    def test_returns_typed_dict(self, long_temperature_dataset):
        """Result should have required FiveYearAnomaly keys."""
        result = calculate_five_year_anomaly(long_temperature_dataset, 't2m')
        assert 'value' in result
        assert 'periodStart' in result
        assert 'periodEnd' in result
        assert 'referenceStart' in result
        assert 'referenceEnd' in result

    def test_positive_anomaly_for_warming_trend(self, long_temperature_dataset):
        """Dataset with warming trend should show positive anomaly."""
        result = calculate_five_year_anomaly(long_temperature_dataset, 't2m')
        # 2021-2025 should be warmer than 1961-1990 due to trend
        assert result['value'] > 0

    def test_period_info_correct(self, long_temperature_dataset):
        """Period info should match config defaults."""
        result = calculate_five_year_anomaly(long_temperature_dataset, 't2m')
        assert result['periodStart'] == FIVE_YEAR_ANOMALY_PERIOD['start_year']
        assert result['periodEnd'] == FIVE_YEAR_ANOMALY_PERIOD['end_year']
        assert result['referenceStart'] == REFERENCE_PERIOD['start_year']
        assert result['referenceEnd'] == REFERENCE_PERIOD['end_year']

    def test_value_rounded_to_2dp(self, long_temperature_dataset):
        """Value should be rounded to 2 decimal places."""
        result = calculate_five_year_anomaly(long_temperature_dataset, 't2m')
        assert result['value'] == round(result['value'], 2)
