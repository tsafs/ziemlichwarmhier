"""Tests for the Germany land mask module.

Network-requiring tests (Natural Earth download) are marked ``@pytest.mark.network``
and excluded from the default test run.  All other tests use synthetic data.
"""

from __future__ import annotations

import numpy as np
import pytest
import xarray as xr

from analysis.era5.config import GERMANY_BOUNDS, GERMAN_ISLANDS
from analysis.era5.tests.conftest import StubProvider


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_grid_dataset(
    north: float,
    south: float,
    west: float,
    east: float,
    n_lat: int = 20,
    n_lon: int = 20,
) -> xr.Dataset:
    """Create a synthetic xr.Dataset with t2m on a regular grid."""
    lats = np.linspace(north, south, n_lat)  # descending
    lons = np.linspace(west, east, n_lon)
    vals = np.ones((n_lat, n_lon), dtype=np.float32) * 285.0
    return xr.Dataset(
        {"t2m": (["latitude", "longitude"], vals)},
        coords={"latitude": lats, "longitude": lons},
    )


# ---------------------------------------------------------------------------
# Tests using synthetic mask data (no network needed)
# ---------------------------------------------------------------------------


class TestApplyGermanyLandMask:
    """apply_germany_land_mask() must set ocean cells to NaN."""

    def test_ocean_area_becomes_nan(self, tmp_path) -> None:
        """Cells explicitly marked as ocean are NaN after masking."""
        from analysis.era5.apply_land_mask import apply_germany_land_mask
        import rasterio
        from rasterio.transform import from_bounds as rasterio_from_bounds
        import numpy as np

        provider = StubProvider()
        ds = _make_grid_dataset(
            provider.bounds["north"],
            provider.bounds["south"],
            provider.bounds["west"],
            provider.bounds["east"],
        )
        n_lat = ds.latitude.size
        n_lon = ds.longitude.size

        # Write a synthetic mask with a clear land/ocean split: top half land
        mask_data = np.zeros((n_lat, n_lon), dtype=np.uint8)
        mask_data[: n_lat // 2, :] = 1  # top half = land

        bnd = provider.bounds
        transform = rasterio_from_bounds(
            bnd["west"], bnd["south"], bnd["east"], bnd["north"], n_lon, n_lat
        )
        mask_path = tmp_path / "test_mask.tif"
        with rasterio.open(
            mask_path, "w", driver="GTiff",
            height=n_lat, width=n_lon, count=1,
            dtype=np.uint8, crs="EPSG:4326", transform=transform,
        ) as dst:
            dst.write(mask_data, 1)

        masked_ds = apply_germany_land_mask(ds, provider, mask_path=mask_path)

        # Bottom half should be NaN
        vals = masked_ds["t2m"].values
        assert np.all(np.isnan(vals[n_lat // 2 :, :]))

    def test_land_area_preserved(self, tmp_path) -> None:
        """Cells marked as land retain their original values."""
        from analysis.era5.apply_land_mask import apply_germany_land_mask
        import rasterio
        from rasterio.transform import from_bounds as rasterio_from_bounds

        provider = StubProvider()
        original_value = 285.0
        ds = _make_grid_dataset(
            provider.bounds["north"],
            provider.bounds["south"],
            provider.bounds["west"],
            provider.bounds["east"],
        )
        n_lat = ds.latitude.size
        n_lon = ds.longitude.size

        mask_data = np.ones((n_lat, n_lon), dtype=np.uint8)  # all land
        bnd = provider.bounds
        transform = rasterio_from_bounds(
            bnd["west"], bnd["south"], bnd["east"], bnd["north"], n_lon, n_lat
        )
        mask_path = tmp_path / "all_land_mask.tif"
        with rasterio.open(
            mask_path, "w", driver="GTiff",
            height=n_lat, width=n_lon, count=1,
            dtype=np.uint8, crs="EPSG:4326", transform=transform,
        ) as dst:
            dst.write(mask_data, 1)

        masked_ds = apply_germany_land_mask(ds, provider, mask_path=mask_path)

        vals = masked_ds["t2m"].values
        assert not np.any(np.isnan(vals))
        np.testing.assert_allclose(vals, original_value)

    def test_output_has_land_mask_attribute(self, tmp_path) -> None:
        """Masked dataset carries the ``land_mask_applied`` attribute."""
        from analysis.era5.apply_land_mask import apply_germany_land_mask
        import rasterio
        from rasterio.transform import from_bounds as rasterio_from_bounds

        provider = StubProvider()
        ds = _make_grid_dataset(
            provider.bounds["north"],
            provider.bounds["south"],
            provider.bounds["west"],
            provider.bounds["east"],
        )
        n_lat = ds.latitude.size
        n_lon = ds.longitude.size
        mask_data = np.ones((n_lat, n_lon), dtype=np.uint8)
        bnd = provider.bounds
        transform = rasterio_from_bounds(
            bnd["west"], bnd["south"], bnd["east"], bnd["north"], n_lon, n_lat
        )
        mask_path = tmp_path / "attr_mask.tif"
        with rasterio.open(
            mask_path, "w", driver="GTiff",
            height=n_lat, width=n_lon, count=1,
            dtype=np.uint8, crs="EPSG:4326", transform=transform,
        ) as dst:
            dst.write(mask_data, 1)

        masked_ds = apply_germany_land_mask(ds, provider, mask_path=mask_path)
        assert masked_ds.attrs.get("land_mask_applied") is True


# ---------------------------------------------------------------------------
# Island coordinate parametrize (using synthetic mask with all land = True)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "island",
    [
        {"name": "Sylt",      "lat": 54.9,  "lon": 8.3},
        {"name": "Rügen",     "lat": 54.4,  "lon": 13.4},
        {"name": "Helgoland", "lat": 54.18, "lon": 7.89},
    ],
    ids=["Sylt", "Ruegen", "Helgoland"],
)
def test_island_coordinates_within_germany_bounds(island: dict) -> None:
    """Island coordinates lie within GERMANY_BOUNDS (prerequisite for masking)."""
    assert GERMANY_BOUNDS["south"] <= island["lat"] <= GERMANY_BOUNDS["north"], (
        f"{island['name']} lat={island['lat']} outside Germany N-S bounds"
    )
    assert GERMANY_BOUNDS["west"] <= island["lon"] <= GERMANY_BOUNDS["east"], (
        f"{island['name']} lon={island['lon']} outside Germany E-W bounds"
    )


@pytest.mark.parametrize(
    "island",
    [
        {"name": "Sylt",      "lat": 54.9,  "lon": 8.3},
        {"name": "Rügen",     "lat": 54.4,  "lon": 13.4},
        {"name": "Helgoland", "lat": 54.18, "lon": 7.89},
    ],
    ids=["Sylt", "Ruegen", "Helgoland"],
)
def test_island_included_in_all_land_mask(island: dict, tmp_path) -> None:
    """Islands show as land in a mask that marks every Germany cell as land."""
    import rasterio
    from rasterio.transform import from_bounds as rasterio_from_bounds
    from analysis.era5.apply_land_mask import load_land_mask

    n_lat, n_lon = 82, 94  # approximate ERA5-Land grid for Germany
    bnd = GERMANY_BOUNDS
    mask_data = np.ones((n_lat, n_lon), dtype=np.uint8)
    transform = rasterio_from_bounds(
        bnd["west"], bnd["south"], bnd["east"], bnd["north"], n_lon, n_lat
    )
    mask_path = tmp_path / f"mask_{island['name']}.tif"
    with rasterio.open(
        mask_path, "w", driver="GTiff",
        height=n_lat, width=n_lon, count=1,
        dtype=np.uint8, crs="EPSG:4326", transform=transform,
    ) as dst:
        dst.write(mask_data, 1)

    mask = load_land_mask(mask_path)

    with rasterio.open(mask_path) as src:
        row, col = src.index(island["lon"], island["lat"])

    row, col = int(row), int(col)
    assert 0 <= row < n_lat, f"Row {row} out of bounds for {island['name']}"
    assert 0 <= col < n_lon, f"Col {col} out of bounds for {island['name']}"
    assert mask[row, col], f"Island {island['name']} should be land"
