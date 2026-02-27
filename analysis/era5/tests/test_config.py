"""Tests for source-agnostic configuration constants."""

from __future__ import annotations

import pytest

from analysis.era5.config import (
    ANOMALY_COLORMAP,
    CDS_DATASETS,
    ERA5_VARIABLES,
    GERMANY_BOUNDS,
    GERMANY_BOUNDS_BUFFERED,
    GERMAN_ISLANDS,
    PRECIPITATION_THRESHOLDS,
    REFERENCE_PERIOD,
    SNOW_DAY_TEMP_THRESHOLD,
    TEMPERATURE_THRESHOLDS,
    validate_bounds,
)


class TestGermanyBounds:
    """Germany bounding box must have all four keys and reasonable values."""

    def test_has_required_keys(self) -> None:
        for key in ("north", "south", "east", "west"):
            assert key in GERMANY_BOUNDS

    def test_north_greater_than_south(self) -> None:
        assert GERMANY_BOUNDS["north"] > GERMANY_BOUNDS["south"]

    def test_east_greater_than_west(self) -> None:
        assert GERMANY_BOUNDS["east"] > GERMANY_BOUNDS["west"]

    def test_values_are_within_germany(self) -> None:
        assert GERMANY_BOUNDS["north"] == pytest.approx(55.1)
        assert GERMANY_BOUNDS["south"] == pytest.approx(47.2)
        assert GERMANY_BOUNDS["west"] == pytest.approx(5.8)
        assert GERMANY_BOUNDS["east"] == pytest.approx(15.1)

    def test_buffered_bounds_are_larger(self) -> None:
        assert GERMANY_BOUNDS_BUFFERED["north"] > GERMANY_BOUNDS["north"]
        assert GERMANY_BOUNDS_BUFFERED["south"] < GERMANY_BOUNDS["south"]
        assert GERMANY_BOUNDS_BUFFERED["west"] < GERMANY_BOUNDS["west"]
        assert GERMANY_BOUNDS_BUFFERED["east"] > GERMANY_BOUNDS["east"]


class TestReferencePeriod:
    """Reference period should be the WMO standard 1961-1990 baseline."""

    def test_is_tuple_of_two(self) -> None:
        assert len(REFERENCE_PERIOD) == 2

    def test_start_year(self) -> None:
        assert REFERENCE_PERIOD[0] == 1961

    def test_end_year(self) -> None:
        assert REFERENCE_PERIOD[1] == 1990

    def test_start_before_end(self) -> None:
        assert REFERENCE_PERIOD[0] < REFERENCE_PERIOD[1]


class TestTemperatureThresholds:
    """DWD temperature threshold values must be correct."""

    def test_hot_day_is_30(self) -> None:
        assert TEMPERATURE_THRESHOLDS["hot_day"] == pytest.approx(30.0)

    def test_extreme_heat_is_35(self) -> None:
        assert TEMPERATURE_THRESHOLDS["extreme_heat"] == pytest.approx(35.0)

    def test_tropical_night_is_20(self) -> None:
        assert TEMPERATURE_THRESHOLDS["tropical_night"] == pytest.approx(20.0)

    def test_ice_day_is_0(self) -> None:
        assert TEMPERATURE_THRESHOLDS["ice_day"] == pytest.approx(0.0)

    def test_frost_day_is_0(self) -> None:
        assert TEMPERATURE_THRESHOLDS["frost_day"] == pytest.approx(0.0)

    def test_comfortable_min_is_15(self) -> None:
        assert TEMPERATURE_THRESHOLDS["comfortable_min"] == pytest.approx(15.0)

    def test_comfortable_max_is_25(self) -> None:
        assert TEMPERATURE_THRESHOLDS["comfortable_max"] == pytest.approx(25.0)


class TestPrecipitationThresholds:
    """Precipitation threshold values."""

    def test_dry_day_threshold(self) -> None:
        assert PRECIPITATION_THRESHOLDS["dry_day"] == pytest.approx(1.0)

    def test_extreme_rain_threshold(self) -> None:
        assert PRECIPITATION_THRESHOLDS["extreme_rain"] == pytest.approx(25.0)

    def test_snow_precip_min(self) -> None:
        assert PRECIPITATION_THRESHOLDS["snow_precip_min"] == pytest.approx(0.1)

    def test_snow_day_temp_threshold(self) -> None:
        assert SNOW_DAY_TEMP_THRESHOLD == pytest.approx(0.0)


class TestAnomalyColormap:
    """Colour-map constants for anomaly rendering."""

    def test_has_vmin_vmax(self) -> None:
        assert "vmin" in ANOMALY_COLORMAP
        assert "vmax" in ANOMALY_COLORMAP

    def test_vmin_negative_vmax_positive(self) -> None:
        assert ANOMALY_COLORMAP["vmin"] < 0
        assert ANOMALY_COLORMAP["vmax"] > 0

    def test_symmetric(self) -> None:
        assert ANOMALY_COLORMAP["vmin"] == pytest.approx(-ANOMALY_COLORMAP["vmax"])


class TestGermanIslands:
    """Island list for land-mask verification."""

    _EXPECTED_ISLANDS = {"Sylt", "Rügen", "Helgoland", "Borkum", "Fehmarn", "Usedom"}

    def test_all_expected_islands_present(self) -> None:
        names = {i["name"] for i in GERMAN_ISLANDS}
        assert names == self._EXPECTED_ISLANDS

    def test_all_islands_have_lat_lon(self) -> None:
        for island in GERMAN_ISLANDS:
            assert "lat" in island
            assert "lon" in island

    def test_all_coordinates_in_germany(self) -> None:
        for island in GERMAN_ISLANDS:
            assert GERMANY_BOUNDS["south"] <= island["lat"] <= GERMANY_BOUNDS["north"]
            assert GERMANY_BOUNDS["west"] <= island["lon"] <= GERMANY_BOUNDS["east"]


class TestValidateBounds:
    """validate_bounds() should catch invalid input."""

    def test_valid_bounds_pass(self) -> None:
        validate_bounds(GERMANY_BOUNDS)  # should not raise

    def test_north_less_than_south_raises(self) -> None:
        invalid = {"north": 47.0, "south": 55.0, "east": 15.1, "west": 5.8}
        with pytest.raises(ValueError, match="north"):
            validate_bounds(invalid)

    def test_east_less_than_west_raises(self) -> None:
        invalid = {"north": 55.1, "south": 47.2, "east": 5.0, "west": 15.1}
        with pytest.raises(ValueError, match="east"):
            validate_bounds(invalid)

    def test_latitude_out_of_range_raises(self) -> None:
        invalid = {"north": 95.0, "south": 47.2, "east": 15.1, "west": 5.8}
        with pytest.raises(ValueError, match="[Ll]atitude"):
            validate_bounds(invalid)
