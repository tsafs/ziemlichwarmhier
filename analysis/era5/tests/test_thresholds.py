"""Tests for temperature threshold detection functions."""

from __future__ import annotations

import numpy as np
import pytest

from analysis.era5.detect_thresholds import (
    comfortable_days,
    count_threshold_days,
    extreme_heat_days,
    frost_days,
    hot_days,
    ice_days,
    tropical_nights,
)


# ---------------------------------------------------------------------------
# hot_days
# ---------------------------------------------------------------------------


class TestHotDays:
    def test_above_threshold_is_true(self) -> None:
        arr = np.array([31.0])
        assert hot_days(arr)[0] is np.bool_(True)

    def test_exactly_at_threshold_is_true(self) -> None:
        arr = np.array([30.0])
        assert hot_days(arr)[0] is np.bool_(True)

    def test_below_threshold_is_false(self) -> None:
        arr = np.array([29.9])
        assert not hot_days(arr)[0]

    def test_no_hot_day_at_29(self) -> None:
        arr = np.array([29.0, 25.0, 22.0])
        assert not np.any(hot_days(arr))

    def test_mixed_array(self) -> None:
        arr = np.array([29.0, 30.0, 31.0, 34.9, 35.0])
        result = hot_days(arr)
        expected = np.array([False, True, True, True, True])
        np.testing.assert_array_equal(result, expected)

    def test_custom_threshold(self) -> None:
        arr = np.array([28.0, 32.0])
        result = hot_days(arr, threshold=32.0)
        np.testing.assert_array_equal(result, [False, True])

    def test_returns_numpy_bool_array(self) -> None:
        result = hot_days(np.array([31.0, 29.0]))
        assert result.dtype == bool


# ---------------------------------------------------------------------------
# extreme_heat_days
# ---------------------------------------------------------------------------


class TestExtremeHeatDays:
    def test_above_35_is_true(self) -> None:
        assert extreme_heat_days(np.array([36.0]))[0]

    def test_exactly_35_is_true(self) -> None:
        assert extreme_heat_days(np.array([35.0]))[0]

    def test_below_35_is_false(self) -> None:
        assert not extreme_heat_days(np.array([34.9]))[0]


# ---------------------------------------------------------------------------
# tropical_nights
# ---------------------------------------------------------------------------


class TestTropicalNights:
    def test_above_20_is_true(self) -> None:
        assert tropical_nights(np.array([21.0]))[0]

    def test_exactly_20_is_true(self) -> None:
        assert tropical_nights(np.array([20.0]))[0]

    def test_below_20_is_false(self) -> None:
        assert not tropical_nights(np.array([19.9]))[0]

    def test_tropical_night_count(self) -> None:
        arr = np.array([18.0, 20.0, 21.0, 19.0, 22.0])
        assert count_threshold_days(tropical_nights(arr)) == 3


# ---------------------------------------------------------------------------
# ice_days
# ---------------------------------------------------------------------------


class TestIceDays:
    def test_negative_tmax_is_ice_day(self) -> None:
        assert ice_days(np.array([-1.0]))[0]

    def test_zero_tmax_is_ice_day(self) -> None:
        assert ice_days(np.array([0.0]))[0]

    def test_positive_tmax_is_not_ice_day(self) -> None:
        assert not ice_days(np.array([0.1]))[0]

    def test_mixed_array(self) -> None:
        arr = np.array([-5.0, 0.0, 0.1, 5.0])
        expected = np.array([True, True, False, False])
        np.testing.assert_array_equal(ice_days(arr), expected)


# ---------------------------------------------------------------------------
# frost_days
# ---------------------------------------------------------------------------


class TestFrostDays:
    def test_negative_tmin_is_frost_day(self) -> None:
        assert frost_days(np.array([-0.1]))[0]

    def test_zero_tmin_is_not_frost_day(self) -> None:
        """frost_days uses strict < 0, so zero is NOT a frost day."""
        assert not frost_days(np.array([0.0]))[0]

    def test_positive_tmin_is_not_frost_day(self) -> None:
        assert not frost_days(np.array([1.0]))[0]


# ---------------------------------------------------------------------------
# comfortable_days
# ---------------------------------------------------------------------------


class TestComfortableDays:
    def test_within_range_is_comfortable(self) -> None:
        assert comfortable_days(np.array([20.0]))[0]

    def test_exactly_min_is_comfortable(self) -> None:
        assert comfortable_days(np.array([15.0]))[0]

    def test_exactly_max_is_comfortable(self) -> None:
        assert comfortable_days(np.array([25.0]))[0]

    def test_below_min_is_not_comfortable(self) -> None:
        assert not comfortable_days(np.array([14.9]))[0]

    def test_above_max_is_not_comfortable(self) -> None:
        assert not comfortable_days(np.array([25.1]))[0]

    def test_custom_range(self) -> None:
        arr = np.array([18.0, 22.0, 26.0])
        result = comfortable_days(arr, min_t=18.0, max_t=22.0)
        np.testing.assert_array_equal(result, [True, True, False])


# ---------------------------------------------------------------------------
# count_threshold_days
# ---------------------------------------------------------------------------


class TestCountThresholdDays:
    def test_count_matches_sum(self) -> None:
        arr = np.array([True, False, True, True, False])
        assert count_threshold_days(arr) == 3

    def test_all_false_returns_zero(self) -> None:
        assert count_threshold_days(np.array([False, False])) == 0

    def test_all_true_returns_length(self) -> None:
        arr = np.array([True] * 7)
        assert count_threshold_days(arr) == 7

    def test_returns_int(self) -> None:
        result = count_threshold_days(np.array([True, False]))
        assert isinstance(result, int)


# ---------------------------------------------------------------------------
# Multi-dimensional arrays
# ---------------------------------------------------------------------------


class TestMultiDimensionalArrays:
    """All threshold functions must work on N-D arrays (e.g. lat×lon grids)."""

    def test_2d_hot_days(self) -> None:
        grid = np.array([[29.0, 30.0], [31.0, 25.0]])
        expected = np.array([[False, True], [True, False]])
        np.testing.assert_array_equal(hot_days(grid), expected)

    def test_3d_tropical_nights(self) -> None:
        cube = np.full((3, 4, 5), 21.0)
        result = tropical_nights(cube)
        assert result.shape == (3, 4, 5)
        assert np.all(result)
