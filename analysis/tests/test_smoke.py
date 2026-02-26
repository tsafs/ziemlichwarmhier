"""
Smoke tests for conftest fixtures and fixture files.

Verifies that all pytest fixtures instantiate correctly and that
JSON/CSV fixture files in analysis/tests/fixtures/ are well-formed
and match the ERA5-Land product schemas.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np
import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


# ── Fixture instantiation ───────────────────────────────────────────────

class TestConftest:
    """Verify all conftest fixtures instantiate without error."""

    def test_germany_bounds(self, germany_bounds: dict[str, float]) -> None:
        assert set(germany_bounds.keys()) == {"north", "south", "west", "east"}
        assert germany_bounds["north"] > germany_bounds["south"]
        assert germany_bounds["east"] > germany_bounds["west"]

    def test_sample_era5_grid(self, sample_era5_grid: dict[str, np.ndarray]) -> None:
        assert "lat" in sample_era5_grid and "lon" in sample_era5_grid
        assert sample_era5_grid["lat"].shape == (5, 5)
        assert sample_era5_grid["lon"].shape == (5, 5)
        # Latitude descending (ERA5 convention)
        assert sample_era5_grid["lat_1d"][0] > sample_era5_grid["lat_1d"][-1]

    def test_sample_location_metrics(self, sample_location_metrics: dict[str, Any]) -> None:
        assert sample_location_metrics["version"] == "1.0"
        assert sample_location_metrics["source"] == "era5-land"
        data = sample_location_metrics["data"]
        required_keys = {
            "calculatedAt", "fiveYearAnomaly", "warmingRate", "recordDays",
            "winterWarming", "seasonalWarming", "thresholdDays",
            "snowDaysLost", "comfortableDays",
        }
        assert required_keys <= set(data.keys())

    def test_sample_city_correlation(self, sample_city_correlation: dict[str, Any]) -> None:
        assert sample_city_correlation["meta"]["city_count"] == 3
        cities = sample_city_correlation["cities"]
        assert len(cities) == 3
        slugs = [c["slug"] for c in cities]
        assert "berlin" in slugs
        for city in cities:
            assert "tile_id" in city
            assert "_" in city["tile_id"]

    def test_mock_s3(self, mock_s3) -> None:
        """Verify mock_s3 fixture sets up a callable mock client."""
        assert mock_s3.upload_file is not None
        assert mock_s3.download_file is not None

    def test_mock_era5_env(self, mock_era5_env, monkeypatch) -> None:
        """Verify CDS env vars are set."""
        import os
        assert os.environ.get("CDS_API_KEY") == "12345:fake-api-key"
        assert os.environ.get("CLIMATE_DATA_PROVIDER") == "era5-land"

    def test_tmp_csv(self, tmp_csv) -> None:
        """Verify tmp_csv factory writes valid CSV."""
        rows = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
        path = tmp_csv("test.csv", rows)
        assert path.exists()
        with path.open() as f:
            reader = csv.DictReader(f)
            result = list(reader)
        assert len(result) == 2
        assert result[0]["a"] == "1"


# ── Fixture files ────────────────────────────────────────────────────────

class TestFixtureFiles:
    """Verify on-disk fixture files are well-formed."""

    def test_germany_metrics_json(self) -> None:
        data = json.loads((FIXTURES_DIR / "germany_metrics_sample.json").read_text())
        assert data["source"] == "era5-land"
        assert "data" in data
        assert "fiveYearAnomaly" in data["data"]

    def test_city_correlation_json(self) -> None:
        data = json.loads((FIXTURES_DIR / "city_grid_correlation_sample.json").read_text())
        assert "meta" in data and "cities" in data
        assert data["meta"]["city_count"] == len(data["cities"])

    def test_temperature_evolution_csv(self) -> None:
        path = FIXTURES_DIR / "temperature_evolution_sample.csv"
        with path.open() as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) >= 3
        assert set(reader.fieldnames or []) == {"year", "temperature", "anomaly", "trend"}


# ── Network guard ────────────────────────────────────────────────────────

class TestNetworkGuard:
    """Verify that no_network fixture blocks sockets by default."""

    def test_socket_blocked(self) -> None:
        import socket as _socket
        with pytest.raises(OSError):
            _socket.socket()
