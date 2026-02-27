"""Tests for the ClimateDataProvider protocol and provider factory."""

from __future__ import annotations

import os

import pytest

from analysis.era5.providers import get_provider
from analysis.era5.providers.era5_land import ERA5LandProvider
from analysis.era5.providers.protocol import ClimateDataProvider
from analysis.era5.tests.conftest import StubProvider


class TestERA5LandProviderProtocol:
    """ERA5LandProvider must satisfy ClimateDataProvider at runtime."""

    def test_isinstance_check(self) -> None:
        """ERA5LandProvider instance is a ClimateDataProvider."""
        provider = ERA5LandProvider()
        assert isinstance(provider, ClimateDataProvider)

    def test_has_dataset_id(self) -> None:
        provider = ERA5LandProvider()
        assert provider.dataset_id == "era5-land"

    def test_has_display_name(self) -> None:
        provider = ERA5LandProvider()
        assert isinstance(provider.display_name, str)
        assert len(provider.display_name) > 0

    def test_has_native_resolution(self) -> None:
        provider = ERA5LandProvider()
        assert provider.native_resolution_deg == pytest.approx(0.1)

    def test_has_bounds(self) -> None:
        provider = ERA5LandProvider()
        bnd = provider.bounds
        for key in ("north", "south", "east", "west"):
            assert key in bnd

    def test_has_variables(self) -> None:
        provider = ERA5LandProvider()
        assert "t2m" in provider.variables
        assert "tp" in provider.variables

    def test_has_coordinate_names(self) -> None:
        provider = ERA5LandProvider()
        for key in ("latitude", "longitude", "time"):
            assert key in provider.coordinate_names

    def test_latitude_descending_is_bool(self) -> None:
        provider = ERA5LandProvider()
        assert isinstance(provider.latitude_descending, bool)

    def test_has_unit_conversions(self) -> None:
        provider = ERA5LandProvider()
        assert "temperature" in provider.unit_conversions
        assert "precipitation" in provider.unit_conversions


class TestGetProvider:
    """get_provider() factory behaviour."""

    def test_returns_era5_by_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Default provider is ERA5LandProvider."""
        monkeypatch.delenv("CLIMATE_DATA_PROVIDER", raising=False)
        provider = get_provider()
        assert isinstance(provider, ERA5LandProvider)

    def test_returns_era5_explicit(self) -> None:
        provider = get_provider("era5-land")
        assert isinstance(provider, ERA5LandProvider)

    def test_env_var_selects_provider(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("CLIMATE_DATA_PROVIDER", "era5-land")
        provider = get_provider()
        assert isinstance(provider, ERA5LandProvider)

    def test_unknown_provider_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown provider"):
            get_provider("unknown-source-xyz")

    def test_error_lists_available_providers(self) -> None:
        with pytest.raises(ValueError, match="era5-land"):
            get_provider("does-not-exist")


class TestStubProvider:
    """StubProvider must also satisfy the ClimateDataProvider protocol."""

    def test_isinstance_check(self) -> None:
        stub = StubProvider()
        assert isinstance(stub, ClimateDataProvider)

    def test_dataset_id(self) -> None:
        stub = StubProvider()
        assert stub.dataset_id == "stub"

    def test_has_required_properties(self) -> None:
        stub = StubProvider()
        assert stub.native_resolution_deg > 0
        assert isinstance(stub.bounds, dict)
        assert stub.variables
        assert stub.coordinate_names
        assert isinstance(stub.latitude_descending, bool)
        assert stub.unit_conversions

    def test_fetch_monthly_creates_file(
        self, stub_provider: StubProvider, tmp_path
    ) -> None:
        path = stub_provider.fetch_monthly(2024, 1, tmp_path)
        assert path.exists()

    def test_fetch_daily_creates_file(
        self, stub_provider: StubProvider, tmp_path
    ) -> None:
        path = stub_provider.fetch_daily(2024, 1, tmp_path)
        assert path.exists()

    def test_load_dataset_returns_xr_dataset(
        self, stub_provider: StubProvider, tmp_path
    ) -> None:
        import xarray as xr

        path = stub_provider.fetch_monthly(2024, 1, tmp_path)
        ds = stub_provider.load_dataset(path)
        assert isinstance(ds, xr.Dataset)
