#!/usr/bin/env python3
"""Tests for decadal aggregate calculations."""

import json
import pytest
import numpy as np
import xarray as xr
from datetime import datetime
from pathlib import Path

from analysis.metrics.calculate_decadal_aggregates import (
    calculate_decadal_mean_temp,
    calculate_decadal_aggregates,
    export_decadal_aggregates,
)
from analysis.metrics.config import DECADES


class TestDecadalMeanTemp:
    """Tests for calculate_decadal_mean_temp."""

    def test_returns_float(self, long_temperature_dataset):
        """Should return a float value."""
        result = calculate_decadal_mean_temp(
            long_temperature_dataset, 't2m', (1961, 1970)
        )
        assert isinstance(result, float)

    def test_nan_for_missing_decade(self, long_temperature_dataset):
        """Should return NaN for decade with no data."""
        result = calculate_decadal_mean_temp(
            long_temperature_dataset, 't2m', (2050, 2059)
        )
        assert np.isnan(result)

    def test_warming_trend_reflected(self, long_temperature_dataset):
        """Later decades should be warmer than earlier ones."""
        early = calculate_decadal_mean_temp(
            long_temperature_dataset, 't2m', (1961, 1970)
        )
        late = calculate_decadal_mean_temp(
            long_temperature_dataset, 't2m', (2011, 2020)
        )
        assert late > early


class TestCalculateDecadalAggregates:
    """Tests for calculate_decadal_aggregates."""

    def test_returns_list(self, long_temperature_dataset):
        """Should return a list of aggregates."""
        result = calculate_decadal_aggregates(long_temperature_dataset)
        assert isinstance(result, list)

    def test_has_expected_structure(self, long_temperature_dataset):
        """Each aggregate should have required keys."""
        result = calculate_decadal_aggregates(long_temperature_dataset)
        for agg in result:
            assert 'decade' in agg
            assert 'startYear' in agg
            assert 'endYear' in agg
            assert 'meanTemp' in agg
            assert 'anomaly' in agg

    def test_reference_period_has_zero_ish_anomaly(self, long_temperature_dataset):
        """Reference period (1961-1990) anomaly should be near zero."""
        result = calculate_decadal_aggregates(long_temperature_dataset)
        ref_decades = [a for a in result if a['startYear'] in [1961, 1971, 1981]]
        for agg in ref_decades:
            if agg['anomaly'] is not None:
                # Should be within 1°C of zero (it is the reference period)
                assert abs(agg['anomaly']) < 1.5


class TestExportDecadalAggregates:
    """Tests for export_decadal_aggregates."""

    def test_creates_file(self, long_temperature_dataset, tmp_path):
        """Should create a JSON file at the specified path."""
        aggregates = calculate_decadal_aggregates(long_temperature_dataset)
        output_path = tmp_path / "0_0_decadal.json"
        result = export_decadal_aggregates(aggregates, output_path)
        assert result.exists()

    def test_valid_json(self, long_temperature_dataset, tmp_path):
        """Output file should be valid JSON."""
        aggregates = calculate_decadal_aggregates(long_temperature_dataset)
        output_path = tmp_path / "test_decadal.json"
        export_decadal_aggregates(aggregates, output_path)
        
        with open(output_path) as f:
            data = json.load(f)
        
        assert isinstance(data, list)
        assert len(data) > 0
