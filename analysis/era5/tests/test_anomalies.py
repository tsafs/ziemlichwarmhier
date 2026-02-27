"""Tests for the anomaly calculation module."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import xarray as xr

from analysis.era5.calculate_anomalies import (
    calculate_monthly_anomaly,
    export_anomaly_geotiff,
    load_climatology,
)
from analysis.era5.tests.conftest import StubProvider


# ---------------------------------------------------------------------------
# calculate_monthly_anomaly
# ---------------------------------------------------------------------------


class TestCalculateMonthlyAnomaly:
    """Anomaly = current - reference for every spatial cell."""

    def test_anomaly_is_difference(
        self,
        sample_era5_ds: xr.Dataset,
        reference_climatology_ds: xr.Dataset,
    ) -> None:
        """anomaly[i,j] == current[i,j] - reference[i,j] (month 1)."""
        month = 1
        anomaly_ds = calculate_monthly_anomaly(
            sample_era5_ds, reference_climatology_ds, 2024, month
        )

        current = sample_era5_ds["t2m"].isel(time=0).values
        ref = reference_climatology_ds.sel(month=month)["t2m"].values

        expected = current - ref
        np.testing.assert_allclose(
            anomaly_ds["anomaly"].values, expected, rtol=1e-5
        )

    def test_output_variable_is_named_anomaly(
        self,
        sample_era5_ds: xr.Dataset,
        reference_climatology_ds: xr.Dataset,
    ) -> None:
        anomaly_ds = calculate_monthly_anomaly(
            sample_era5_ds, reference_climatology_ds, 2024, 1
        )
        assert "anomaly" in anomaly_ds.data_vars

    def test_output_preserves_coordinates(
        self,
        sample_era5_ds: xr.Dataset,
        reference_climatology_ds: xr.Dataset,
    ) -> None:
        anomaly_ds = calculate_monthly_anomaly(
            sample_era5_ds, reference_climatology_ds, 2024, 1
        )
        np.testing.assert_array_equal(
            anomaly_ds["latitude"].values,
            sample_era5_ds["latitude"].values,
        )
        np.testing.assert_array_equal(
            anomaly_ds["longitude"].values,
            sample_era5_ds["longitude"].values,
        )

    def test_output_has_global_attributes(
        self,
        sample_era5_ds: xr.Dataset,
        reference_climatology_ds: xr.Dataset,
    ) -> None:
        anomaly_ds = calculate_monthly_anomaly(
            sample_era5_ds, reference_climatology_ds, 2024, 3
        )
        assert anomaly_ds.attrs["year"] == 2024
        assert anomaly_ds.attrs["month"] == 3

    def test_units_attribute_is_celsius(
        self,
        sample_era5_ds: xr.Dataset,
        reference_climatology_ds: xr.Dataset,
    ) -> None:
        anomaly_ds = calculate_monthly_anomaly(
            sample_era5_ds, reference_climatology_ds, 2024, 6
        )
        assert anomaly_ds["anomaly"].attrs.get("units") == "°C"

    def test_zero_anomaly_for_identical_datasets(
        self,
        sample_era5_ds: xr.Dataset,
    ) -> None:
        """If current == reference, anomaly should be all zeros."""
        # Build a single-month climatology that matches sample_era5_ds month 1
        current_vals = sample_era5_ds["t2m"].isel(time=0).values
        clim_vals = np.stack([current_vals] * 12)  # same value for all months
        ref_ds = xr.Dataset(
            {"t2m": (["month", "latitude", "longitude"], clim_vals)},
            coords={
                "month": np.arange(1, 13),
                "latitude": sample_era5_ds["latitude"].values,
                "longitude": sample_era5_ds["longitude"].values,
            },
        )

        anomaly_ds = calculate_monthly_anomaly(sample_era5_ds, ref_ds, 2024, 1)
        np.testing.assert_allclose(
            anomaly_ds["anomaly"].values, 0.0, atol=1e-5
        )


# ---------------------------------------------------------------------------
# export_anomaly_geotiff
# ---------------------------------------------------------------------------


class TestExportAnomalyGeoTIFF:
    """GeoTIFF export / roundtrip tests."""

    def test_file_is_created(
        self, sample_anomaly_ds: xr.Dataset, tmp_path: Path
    ) -> None:
        provider = StubProvider()
        out = export_anomaly_geotiff(
            sample_anomaly_ds, tmp_path / "anomaly.tif", provider=provider
        )
        assert out.exists()

    def test_roundtrip_values(
        self, sample_anomaly_ds: xr.Dataset, tmp_path: Path
    ) -> None:
        """Values written to GeoTIFF are recovered on read."""
        import rasterio

        provider = StubProvider()
        out = export_anomaly_geotiff(
            sample_anomaly_ds, tmp_path / "roundtrip.tif", provider=provider
        )

        with rasterio.open(out) as src:
            data_read = src.read(1)

        np.testing.assert_allclose(
            data_read,
            sample_anomaly_ds["anomaly"].values.astype(np.float32),
            rtol=1e-4,
        )

    def test_geotiff_has_epsg4326(
        self, sample_anomaly_ds: xr.Dataset, tmp_path: Path
    ) -> None:
        import rasterio

        provider = StubProvider()
        out = export_anomaly_geotiff(
            sample_anomaly_ds, tmp_path / "crs_check.tif", provider=provider
        )
        with rasterio.open(out) as src:
            assert src.crs.to_epsg() == 4326

    def test_geotiff_tags_contain_year_month(
        self, sample_anomaly_ds: xr.Dataset, tmp_path: Path
    ) -> None:
        import rasterio

        provider = StubProvider()
        out = export_anomaly_geotiff(
            sample_anomaly_ds, tmp_path / "tags.tif", provider=provider
        )
        with rasterio.open(out) as src:
            tags = src.tags()
        assert tags.get("year") == "2024"
        assert tags.get("month") == "1"

    def test_geotiff_shape_matches_dataset(
        self, sample_anomaly_ds: xr.Dataset, tmp_path: Path
    ) -> None:
        import rasterio

        provider = StubProvider()
        out = export_anomaly_geotiff(
            sample_anomaly_ds, tmp_path / "shape.tif", provider=provider
        )
        n_lat = sample_anomaly_ds.latitude.size
        n_lon = sample_anomaly_ds.longitude.size
        with rasterio.open(out) as src:
            assert src.height == n_lat
            assert src.width == n_lon

    def test_export_without_provider_uses_coordinates(
        self, sample_anomaly_ds: xr.Dataset, tmp_path: Path
    ) -> None:
        """bounds can be inferred from coordinates if provider not supplied."""
        out = export_anomaly_geotiff(
            sample_anomaly_ds, tmp_path / "no_provider.tif"
        )
        assert out.exists()


# ---------------------------------------------------------------------------
# load_climatology helper
# ---------------------------------------------------------------------------


class TestLoadClimatology:
    """load_climatology() must return a DataArray for the requested month."""

    def test_returns_correct_month(
        self, reference_climatology_ds: xr.Dataset, tmp_path: Path
    ) -> None:
        clim_path = tmp_path / "clim.nc"
        reference_climatology_ds.to_netcdf(clim_path)

        da = load_climatology(clim_path, month=6)
        assert da.shape == (5, 5)  # 5x5 stub grid

    def test_all_months_accessible(
        self, reference_climatology_ds: xr.Dataset, tmp_path: Path
    ) -> None:
        clim_path = tmp_path / "clim_all.nc"
        reference_climatology_ds.to_netcdf(clim_path)

        for m in range(1, 13):
            da = load_climatology(clim_path, month=m)
            assert da is not None
            assert not np.all(np.isnan(da.values))
