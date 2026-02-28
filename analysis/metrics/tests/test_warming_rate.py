#!/usr/bin/env python3
"""Tests for warming rate calculation."""

import pytest
import numpy as np

from analysis.metrics.calculate_warming_rate import (
    calculate_annual_means,
    calculate_warming_rate,
)
from analysis.metrics.config import WARMING_RATE_PERIOD, MIN_YEARS_FOR_TREND


class TestCalculateAnnualMeans:
    """Tests for calculate_annual_means."""

    def test_returns_two_arrays(self, linear_trend_dataset):
        """Result should be tuple of (years, means)."""
        years, means = calculate_annual_means(
            linear_trend_dataset, 't2m',
            {'start_year': 1995, 'end_year': 2024}
        )
        assert len(years) > 0
        assert len(years) == len(means)

    def test_correct_year_range(self, linear_trend_dataset):
        """Should return only years in the requested period."""
        period = {'start_year': 2000, 'end_year': 2010}
        years, means = calculate_annual_means(linear_trend_dataset, 't2m', period)
        assert min(years) >= 2000
        assert max(years) <= 2010


class TestCalculateWarmingRate:
    """Tests for calculate_warming_rate."""

    def test_detects_linear_trend(self, linear_trend_dataset):
        """Should detect the 0.4°C/decade trend in the test dataset."""
        result = calculate_warming_rate(
            linear_trend_dataset, 't2m',
            {'start_year': 1991, 'end_year': 2024}
        )
        # Known trend: 0.04°C/year = 0.4°C/decade
        assert abs(result['value'] - 0.4) < 0.05

    def test_high_r_squared_for_linear_data(self, linear_trend_dataset):
        """Perfect linear trend should give R² close to 1."""
        result = calculate_warming_rate(
            linear_trend_dataset, 't2m',
            {'start_year': 1991, 'end_year': 2024}
        )
        assert result['confidence'] > 0.9

    def test_returns_required_keys(self, linear_trend_dataset):
        """Result should have all WarmingRate keys."""
        result = calculate_warming_rate(linear_trend_dataset, 't2m')
        assert 'value' in result
        assert 'startYear' in result
        assert 'endYear' in result
        assert 'confidence' in result

    def test_insufficient_data_returns_zero(self, linear_trend_dataset):
        """Very short period should return zero trend."""
        result = calculate_warming_rate(
            linear_trend_dataset, 't2m',
            {'start_year': 2020, 'end_year': 2022}
        )
        assert result['value'] == 0.0
        assert result['confidence'] == 0.0

    def test_value_rounded(self, linear_trend_dataset):
        """Value should be rounded to 3 decimal places."""
        result = calculate_warming_rate(linear_trend_dataset, 't2m')
        assert result['value'] == round(result['value'], 3)
