"""
Shared pytest fixtures for the analysis test suite.

All fixtures target the NEW ERA5-Land product (botox phases), not the
legacy HYRAS/DWD station formats.

Provides:
  - ``no_network``: auto-use fixture that blocks all socket connections
  - ``mock_s3``: patched boto3 client returning local fixture paths
  - ``mock_era5_env``: sets ERA5/CDS-related env vars for tests
  - ``tmp_csv``: helper to write transient CSV files in tmp_path
  - ``sample_era5_grid``: small 5x5 numpy grid mimicking ERA5-Land 0.1° resolution
  - ``sample_location_metrics``: LocationMetrics dict matching Phase 5/8 schema
  - ``germany_bounds``: standard Germany bounding box dict
  - ``sample_city_correlation``: city-grid mapping matching Phase 10 schema
"""

from __future__ import annotations

import csv
import json
import socket
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import numpy as np
import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


# ── Network guard ────────────────────────────────────────────────────────

class _NetworkBlockedError(OSError):
    """Raised when a test accidentally tries to open a socket."""
    pass


@pytest.fixture(autouse=True)
def no_network(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> None:
    """Block all outgoing network connections unless @pytest.mark.network is set."""
    if "network" in (m.name for m in request.node.iter_markers()):
        return
    monkeypatch.setattr(socket, "socket", lambda *a, **kw: (_ for _ in ()).throw(_NetworkBlockedError("Blocked")))


# ── S3 mock ──────────────────────────────────────────────────────────────

@pytest.fixture()
def mock_s3(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Patch ``boto3.client('s3', ...)`` and return the mock client.

    ``download_file`` copies from ``fixtures/`` when key matches; else creates empty file.
    ``upload_file`` is always a no-op.
    """
    client = MagicMock()
    client.upload_file = MagicMock(return_value=None)

    def _download_side_effect(bucket: str, key: str, dest: str) -> None:
        fixture_file = FIXTURES_DIR / Path(key).name
        if fixture_file.exists():
            import shutil
            shutil.copy2(fixture_file, dest)
        else:
            Path(dest).parent.mkdir(parents=True, exist_ok=True)
            Path(dest).touch()

    client.download_file = MagicMock(side_effect=_download_side_effect)

    mock_boto = MagicMock()
    mock_boto.return_value = client

    monkeypatch.setattr("boto3.client", mock_boto)
    # Hetzner S3 env vars (Phase 2 infra)
    monkeypatch.setenv("ACCESS_KEY", "test-key")
    monkeypatch.setenv("SECRET_KEY", "test-secret")
    monkeypatch.setenv("BUCKET_NAME", "climate-tiles")
    monkeypatch.setenv("REGION", "fsn1")
    monkeypatch.setenv("ENDPOINT_URL", "https://climate-tiles.fsn1.your-objectstorage.com")

    return client


# ── ERA5 / CDS env mock ─────────────────────────────────────────────────

@pytest.fixture()
def mock_era5_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set ERA5-related env vars for tests (Phase 2/3)."""
    monkeypatch.setenv("CDS_API_KEY", "12345:fake-api-key")
    monkeypatch.setenv("CLIMATE_DATA_PROVIDER", "era5-land")


# ── CSV helper ───────────────────────────────────────────────────────────

@pytest.fixture()
def tmp_csv(tmp_path: Path):
    """Factory fixture: write a list-of-dicts to a CSV in tmp_path, return path."""

    def _write(filename: str, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> Path:
        fnames = fieldnames or list(rows[0].keys())
        dest = tmp_path / filename
        with dest.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fnames)
            writer.writeheader()
            writer.writerows(rows)
        return dest

    return _write


# ── Germany bounds ───────────────────────────────────────────────────────

@pytest.fixture()
def germany_bounds() -> dict[str, float]:
    """Standard Germany bounding box (Phase 3 config)."""
    return {"north": 55.1, "south": 47.2, "west": 5.8, "east": 15.1}


# ── ERA5-Land grid fixture ──────────────────────────────────────────────

@pytest.fixture()
def sample_era5_grid(germany_bounds: dict[str, float]) -> dict[str, np.ndarray]:
    """Return a small 5x5 numpy lat/lon grid mimicking ERA5-Land 0.1° resolution.

    Grid covers a subset of Germany (5 × 5 cells = 0.5° × 0.5°),
    with latitude descending (north first) as in ERA5-Land convention.
    """
    lat = np.linspace(50.4, 50.0, 5, dtype=np.float64)  # descending
    lon = np.linspace(10.0, 10.4, 5, dtype=np.float64)
    lat_2d, lon_2d = np.meshgrid(lat, lon, indexing="ij")
    return {"lat": lat_2d, "lon": lon_2d, "lat_1d": lat, "lon_1d": lon}


# ── LocationMetrics fixture (Phase 5/8) ─────────────────────────────────

@pytest.fixture()
def sample_location_metrics() -> dict[str, Any]:
    """Return a LocationMetrics dict matching the Phase 5 MetricsFile schema."""
    return {
        "version": "1.0",
        "generatedAt": "2026-02-15T10:00:00Z",
        "source": "era5-land",
        "coverage": {
            "bounds": {"north": 55.1, "south": 47.2, "west": 5.8, "east": 15.1},
            "gridResolution": "0.1deg",
        },
        "data": {
            "calculatedAt": "2026-02-15T10:00:00Z",
            "fiveYearAnomaly": {
                "value": 2.3, "periodStart": 2021, "periodEnd": 2025,
                "referenceStart": 1961, "referenceEnd": 1990,
            },
            "warmingRate": {
                "value": 0.45, "startYear": 1995, "endYear": 2025, "confidence": 0.85,
            },
            "recordDays": {"total": 18, "hot": 16, "cold": 2, "year": 2025},
            "winterWarming": {
                "value": 2.8, "periodStart": 2021, "periodEnd": 2025,
                "referenceStart": 1961, "referenceEnd": 1990,
            },
            "seasonalWarming": {
                "winter": 2.8, "spring": 2.1, "summer": 1.9, "fall": 2.4,
                "fastestSeason": "winter",
                "periodStart": 2021, "periodEnd": 2025,
                "referenceStart": 1961, "referenceEnd": 1990,
            },
            "thresholdDays": {
                "hotDays": 15, "tropicalNights": 8, "iceDays": 4, "frostDays": 52,
                "year": 2025,
            },
            "snowDaysLost": {
                "value": -18, "currentAverage": 12.0, "referenceAverage": 30.0,
                "periodStart": 2021, "periodEnd": 2025,
            },
            "comfortableDays": {"count": 95, "average": 93.0},
        },
    }


# ── City correlation fixture (Phase 10) ─────────────────────────────────

@pytest.fixture()
def sample_city_correlation() -> dict[str, Any]:
    """Return a city-grid correlation dict matching Phase 10 schema."""
    return {
        "meta": {
            "grid_resolution": 0.1,
            "bounds": {"north": 55.1, "south": 47.2, "west": 5.8, "east": 15.1},
            "city_count": 3,
        },
        "cities": [
            {
                "name": "Berlin", "slug": "berlin",
                "lat": 52.52, "lon": 13.405,
                "grid_i": 76, "grid_j": 26,
                "grid_lat": 52.55, "grid_lon": 13.35,
                "tile_id": "76_26",
            },
            {
                "name": "München", "slug": "muenchen",
                "lat": 48.14, "lon": 11.58,
                "grid_i": 57, "grid_j": 69,
                "grid_lat": 48.15, "grid_lon": 11.55,
                "tile_id": "57_69",
            },
            {
                "name": "Freiburg im Breisgau", "slug": "freiburg-im-breisgau",
                "lat": 47.999, "lon": 7.842,
                "grid_i": 20, "grid_j": 71,
                "grid_lat": 47.95, "grid_lon": 7.85,
                "tile_id": "20_71",
            },
        ],
    }
