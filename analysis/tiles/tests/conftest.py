"""
Pytest fixtures for the analysis.tiles test suite.

Fixtures
--------
no_network (autouse)
    Blocks all outgoing socket connections so no test accidentally makes a
    network call.

sample_geotiff_path
    Creates a synthetic 200×200 float32 GeoTIFF covering Germany bounds in
    EPSG:4326.  Values are random anomalies in °C; the western 20 % of
    columns are set to NaN to simulate ocean / NoData.

mock_s3_client
    Patches ``boto3.client`` so every ``upload_file`` call is a no-op.
    Returns the :class:`unittest.mock.MagicMock` instance for assertion.

tmp_tile_dir
    A fresh :class:`pathlib.Path` backed by pytest's ``tmp_path`` fixture.
"""

from __future__ import annotations

import socket
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_bounds

GERMANY_BOUNDS = {
    "north": 55.1,
    "south": 47.2,
    "west": 5.8,
    "east": 15.1,
}

# ---------------------------------------------------------------------------
# Network guard
# ---------------------------------------------------------------------------


class _NetworkBlockedError(OSError):
    """Raised when a test accidentally tries to open a socket."""


@pytest.fixture(autouse=True)
def no_network(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> None:
    """Block all outgoing network connections unless ``@pytest.mark.network``."""
    if "network" in {m.name for m in request.node.iter_markers()}:
        return
    monkeypatch.setattr(
        socket,
        "socket",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            _NetworkBlockedError("Network blocked in tests")
        ),
    )


# ---------------------------------------------------------------------------
# synthetic GeoTIFF
# ---------------------------------------------------------------------------


@pytest.fixture()
def sample_geotiff_path(tmp_path: Path) -> Path:
    """Create a synthetic anomaly GeoTIFF covering Germany bounds.

    Properties
    ----------
    * EPSG:4326, single band, float32
    * 200 × 200 pixels at ≈ 0.047° / 0.046° resolution (≈ 5 km)
    * Values: random anomalies in ``[-2.5, 2.5]`` °C
    * Pixels with column index < 40 set to NaN (simulates ocean / NoData)
    * NoData value set to -9999.0 in the rasterio profile

    Returns
    -------
    pathlib.Path
        Path to the written GeoTIFF file inside ``tmp_path``.
    """
    width, height = 200, 200
    rng = np.random.default_rng(seed=42)
    data = rng.uniform(-2.5, 2.5, (height, width)).astype(np.float32)

    # Simulate ocean on the western edge
    data[:, :40] = np.nan

    transform = from_bounds(
        GERMANY_BOUNDS["west"],
        GERMANY_BOUNDS["south"],
        GERMANY_BOUNDS["east"],
        GERMANY_BOUNDS["north"],
        width,
        height,
    )

    tif_path = tmp_path / "sample_anomaly.tif"

    with rasterio.open(
        tif_path,
        "w",
        driver="GTiff",
        height=height,
        width=width,
        count=1,
        dtype=np.float32,
        crs="EPSG:4326",
        transform=transform,
        nodata=-9999.0,
    ) as dst:
        # Write data (rasterio will replace NaN with nodata on read,
        # but we write the array as-is; rio-tiler masks via nodata metadata)
        dst.write(np.where(np.isnan(data), -9999.0, data), 1)

    return tif_path


# ---------------------------------------------------------------------------
# S3 mock
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_s3_client(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Patch ``boto3.client`` to return a MagicMock with a no-op upload_file.

    The mock records every :py:meth:`upload_file` call so tests can assert
    on call count, arguments, and ``ExtraArgs``.

    Returns
    -------
    MagicMock
        The mock S3 client instance.
    """
    client = MagicMock()
    client.upload_file = MagicMock(return_value=None)

    mock_boto = MagicMock(return_value=client)
    monkeypatch.setattr("boto3.client", mock_boto)

    # Provide env vars used by upload_tiles helpers
    monkeypatch.setenv("ACCESS_KEY", "test-access-key")
    monkeypatch.setenv("SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("BUCKET_NAME", "climate-tiles-test")
    monkeypatch.setenv("ENDPOINT_URL", "https://fsn1.your-objectstorage.com")

    return client


# ---------------------------------------------------------------------------
# tmp_tile_dir
# ---------------------------------------------------------------------------


@pytest.fixture()
def tmp_tile_dir(tmp_path: Path) -> Path:
    """Return a fresh temporary directory for tile output.

    The directory is automatically cleaned up by pytest after the test.

    Returns
    -------
    pathlib.Path
        Empty directory inside pytest's ``tmp_path``.
    """
    tile_dir = tmp_path / "tiles"
    tile_dir.mkdir(parents=True, exist_ok=True)
    return tile_dir
