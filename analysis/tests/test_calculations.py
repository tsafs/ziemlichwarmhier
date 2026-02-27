"""Smoke tests for pure calculation functions in the analysis modules.

These tests verify deterministic functions with no I/O or network access.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


# ── calculate_temperature_days ───────────────────────────────────────────

from calculate_temperature_days import calculate_threshold_days, generate_output_filename


class TestCalculateThresholdDays:
    """Test calculate_threshold_days with synthetic DataFrames."""

    @pytest.fixture()
    def daily_temps(self) -> pd.DataFrame:
        """DataFrame with 3 years × 3 days of tasmax values."""
        return pd.DataFrame({
            "date": pd.to_datetime([
                "1951-07-01", "1951-07-15", "1951-08-01",
                "1952-06-20", "1952-07-10", "1952-08-05",
                "1953-07-01", "1953-07-02", "1953-07-03",
            ]),
            "tasmax": [28.0, 31.0, 26.0,   # 1951: 2 above 25, 1 above 30
                       24.0, 30.5, 32.0,    # 1952: 2 above 25 (30.5, 32), 2 above 30
                       29.0, 25.1, 24.9],   # 1953: 2 above 25, 0 above 30
        })

    def test_days_above_25(self, daily_temps: pd.DataFrame) -> None:
        result = calculate_threshold_days(daily_temps, 25, "above", "tasmax")
        assert result["x"] == [1951, 1952, 1953]
        assert result["y"] == [3, 2, 2]

    def test_days_above_30(self, daily_temps: pd.DataFrame) -> None:
        result = calculate_threshold_days(daily_temps, 30, "above", "tasmax")
        assert result["x"] == [1951, 1952, 1953]
        assert result["y"] == [1, 2, 0]

    def test_days_below_0(self) -> None:
        df = pd.DataFrame({
            "date": pd.to_datetime(["1951-01-01", "1951-01-02", "1952-01-01"]),
            "tasmin": [-5.0, 2.0, -1.0],
        })
        result = calculate_threshold_days(df, 0, "below", "tasmin")
        assert result["x"] == [1951, 1952]
        assert result["y"] == [1, 1]

    def test_empty_dataframe(self) -> None:
        df = pd.DataFrame({"date": pd.Series(dtype="datetime64[ns]"), "tasmax": pd.Series(dtype=float)})
        result = calculate_threshold_days(df, 25, "above", "tasmax")
        assert result["x"] == []
        assert result["y"] == []


class TestGenerateOutputFilename:
    def test_above_30_tasmax(self) -> None:
        result = generate_output_filename("01234", 30, "above", "tasmax")
        assert result == "01234_daysAbove30TmaxHistorical.json"

    def test_below_0_tmin(self) -> None:
        result = generate_output_filename("01234", 0, "below", "tasmin")
        assert result == "01234_daysBelow0TminHistorical.json"

    def test_below_minus10_tmin(self) -> None:
        result = generate_output_filename("01234", -10, "below", "tasmin")
        assert result == "01234_daysBelowMinus10TminHistorical.json"


# ── merge_temperature_days string functions ──────────────────────────────

from merge_temperature_days import extract_station_id_from_filename, create_key_from_filename


class TestExtractStationId:
    def test_standard(self) -> None:
        assert extract_station_id_from_filename("01234_daysAbove30TmaxHistorical.json") == "01234"

    def test_no_days_returns_none(self) -> None:
        assert extract_station_id_from_filename("some_random_file.json") is None


class TestCreateKeyFromFilename:
    def test_above_30(self) -> None:
        result = create_key_from_filename("01234_daysAbove30TmaxHistorical.json")
        assert result == "daysAbove30Tmax"

    def test_below_minus10(self) -> None:
        result = create_key_from_filename("01234_daysBelowMinus10TminHistorical.json")
        assert result == "daysBelowMinus10Tmin"
