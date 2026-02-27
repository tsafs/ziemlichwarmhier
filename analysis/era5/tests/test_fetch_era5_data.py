"""Tests for ERA5-Land data fetching (all CDS calls mocked)."""

from __future__ import annotations

import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
import xarray as xr

from analysis.era5.fetch_era5_data import (
    fetch_monthly_data,
    fetch_reference_climatology,
    get_cds_client,
    load_era5_data,
)
from analysis.era5.tests.conftest import StubProvider


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_minimal_nc(path: Path, year: int = 2024, month: int = 1) -> None:
    """Write a tiny valid NetCDF to *path* (simulates a CDS download)."""
    import pandas as pd

    lats = np.linspace(55.0, 47.0, 5, dtype=np.float32)
    lons = np.linspace(6.0, 15.0, 5, dtype=np.float32)
    t_data = np.full((1, 5, 5), 283.15, dtype=np.float32)

    ds = xr.Dataset(
        {"t2m": (["time", "latitude", "longitude"], t_data)},
        coords={
            "time": pd.to_datetime([f"{year}-{month:02d}-01"]),
            "latitude": lats,
            "longitude": lons,
        },
    )
    ds["t2m"].attrs = {"units": "K", "long_name": "2 metre temperature"}
    ds.to_netcdf(path)


# ---------------------------------------------------------------------------
# get_cds_client
# ---------------------------------------------------------------------------


class TestGetCdsClient:
    def test_raises_without_credentials(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """RuntimeError when no CDS_API_KEY and no ~/.cdsapirc."""
        monkeypatch.delenv("CDS_API_KEY", raising=False)

        # Redirect home so no real .cdsapirc is found
        fake_home = tmp_path / "fakehome"
        fake_home.mkdir()
        monkeypatch.setenv("HOME", str(fake_home))

        # Patch Path.home() to return our fake home
        import pathlib
        monkeypatch.setattr(pathlib.Path, "home", lambda: fake_home)

        with pytest.raises(RuntimeError, match="CDS credentials not found"):
            get_cds_client()

    def test_with_api_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """No error when CDS_API_KEY env var is set (client may not connect)."""
        monkeypatch.setenv("CDS_API_KEY", "12345:fake-key")

        mock_client = MagicMock()
        with patch("cdsapi.Client", return_value=mock_client) as mock_cls:
            client = get_cds_client()
            mock_cls.assert_called_once()
            assert client is mock_client


# ---------------------------------------------------------------------------
# fetch_monthly_data – using StubProvider (no network)
# ---------------------------------------------------------------------------


class TestFetchMonthlyDataWithStubProvider:
    def test_creates_output_file(
        self, stub_provider: StubProvider, tmp_path: Path
    ) -> None:
        path = fetch_monthly_data(stub_provider, 2024, 1, tmp_path)
        assert path.exists()

    def test_returns_path_object(
        self, stub_provider: StubProvider, tmp_path: Path
    ) -> None:
        result = fetch_monthly_data(stub_provider, 2024, 3, tmp_path)
        assert isinstance(result, Path)

    def test_skips_download_if_file_exists_and_not_forced(
        self, stub_provider: StubProvider, tmp_path: Path
    ) -> None:
        """Second call returns the same file without re-downloading (mtime stable)."""
        path1 = fetch_monthly_data(stub_provider, 2024, 1, tmp_path)
        mtime1 = path1.stat().st_mtime

        path2 = fetch_monthly_data(stub_provider, 2024, 1, tmp_path, force=False)
        mtime2 = path2.stat().st_mtime

        assert path1 == path2
        assert mtime1 == mtime2

    def test_force_flag_re_downloads(
        self, stub_provider: StubProvider, tmp_path: Path
    ) -> None:
        """force=True overwrites existing file (mtime changes)."""
        path1 = fetch_monthly_data(stub_provider, 2024, 1, tmp_path)
        mtime1 = path1.stat().st_mtime

        time.sleep(0.05)  # ensure filesystem mtime resolution

        path2 = fetch_monthly_data(stub_provider, 2024, 1, tmp_path, force=True)
        mtime2 = path2.stat().st_mtime

        assert mtime2 > mtime1

    def test_creates_output_directory(
        self, stub_provider: StubProvider, tmp_path: Path
    ) -> None:
        new_dir = tmp_path / "nested" / "output"
        assert not new_dir.exists()
        fetch_monthly_data(stub_provider, 2024, 2, new_dir)
        assert new_dir.exists()


# ---------------------------------------------------------------------------
# fetch_monthly_data – mocked cdsapi.Client (ERA5LandProvider path)
# ---------------------------------------------------------------------------


class TestFetchMonthlyDataWithMockedCDS:
    """Use ERA5LandProvider with a patched cdsapi to avoid real network calls."""

    def _build_mock_retrieve(self, tmp_path: Path):
        """Return a side_effect function that writes a minimal NetCDF."""

        def _retrieve(dataset: str, request: dict, target: str) -> None:
            _write_minimal_nc(Path(target), year=int(request["year"]))

        return _retrieve

    def test_fetch_creates_output_file(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        from analysis.era5.providers.era5_land import ERA5LandProvider

        mock_client = MagicMock()
        mock_client.retrieve.side_effect = self._build_mock_retrieve(tmp_path)

        monkeypatch.setenv("CDS_API_KEY", "0:fake")
        with patch("cdsapi.Client", return_value=mock_client):
            provider = ERA5LandProvider()
            path = fetch_monthly_data(provider, 2020, 6, tmp_path)

        assert path.exists()

    def test_retries_on_error(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Provider retries after a transient error."""
        from analysis.era5.providers.era5_land import ERA5LandProvider

        call_count = {"n": 0}

        def _flaky_retrieve(dataset, request, target):
            call_count["n"] += 1
            if call_count["n"] < 2:
                raise ConnectionError("Transient CDS error")
            _write_minimal_nc(Path(target))

        mock_client = MagicMock()
        mock_client.retrieve.side_effect = _flaky_retrieve

        monkeypatch.setenv("CDS_API_KEY", "0:fake")
        # Patch sleep so tests don't actually wait
        with patch("cdsapi.Client", return_value=mock_client), patch(
            "time.sleep"
        ):
            provider = ERA5LandProvider()
            path = fetch_monthly_data(provider, 2020, 6, tmp_path)

        assert path.exists()
        assert call_count["n"] == 2


# ---------------------------------------------------------------------------
# load_era5_data
# ---------------------------------------------------------------------------


class TestLoadEra5Data:
    def test_converts_kelvin_to_celsius(self, tmp_path: Path) -> None:
        nc_path = tmp_path / "test_k.nc"
        _write_minimal_nc(nc_path)

        ds = load_era5_data(nc_path)

        assert ds["t2m"].attrs["units"] == "°C"
        assert float(ds["t2m"].values.max()) < 100  # not Kelvin
        assert float(ds["t2m"].values.min()) > -50

    def test_skip_conversion(self, tmp_path: Path) -> None:
        nc_path = tmp_path / "test_no_conv.nc"
        _write_minimal_nc(nc_path)

        ds = load_era5_data(nc_path, convert_temperature=False)
        # Still in Kelvin: 283 K is about 10 °C, so should be ~283
        assert float(ds["t2m"].values.mean()) > 200

    def test_returns_xr_dataset(self, tmp_path: Path) -> None:
        nc_path = tmp_path / "test_ds.nc"
        _write_minimal_nc(nc_path)
        result = load_era5_data(nc_path)
        assert isinstance(result, xr.Dataset)


# ---------------------------------------------------------------------------
# fetch_reference_climatology – using StubProvider (no network)
# ---------------------------------------------------------------------------


class TestFetchReferenceClimatology:
    def test_creates_climatology_file(
        self, stub_provider: StubProvider, tmp_path: Path
    ) -> None:
        """Climatology NetCDF should be created for a short test period."""
        clim_path = fetch_reference_climatology(
            stub_provider,
            tmp_path / "clim",
            years_start=1961,
            years_end=1962,  # two years only — fast
        )
        assert clim_path.exists()

    def test_returns_cached_file_on_second_call(
        self, stub_provider: StubProvider, tmp_path: Path
    ) -> None:
        """Second call returns the same file (mtime unchanged)."""
        out_dir = tmp_path / "clim2"
        path1 = fetch_reference_climatology(stub_provider, out_dir, years_start=1961, years_end=1961)
        mtime1 = path1.stat().st_mtime

        path2 = fetch_reference_climatology(stub_provider, out_dir, years_start=1961, years_end=1961)
        mtime2 = path2.stat().st_mtime

        assert path1 == path2
        assert mtime1 == mtime2
