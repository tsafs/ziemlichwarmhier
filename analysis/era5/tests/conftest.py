"""Pytest fixtures for the ERA5-Land pipeline test suite.

All fixtures that would normally require CDS API access use
deterministic in-memory datasets built from numpy arrays.

Available fixtures:
  - ``sample_era5_ds``         — 5x5 Germany-area Dataset with ``t2m`` in K
  - ``sample_anomaly_ds``      — Anomaly Dataset with ``anomaly`` variable
  - ``stub_provider``          — StubProvider implementing ClimateDataProvider
  - ``reference_climatology_ds`` — 12-month climatology Dataset
  - ``stub_hourly_ds``         — Hourly-like Dataset for daily extraction tests
  - ``stub_precip_ds``         — Hourly-like Dataset with ``tp`` variable
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import numpy as np
import pytest
import xarray as xr

from analysis.era5.types import BoundsDict

# ---------------------------------------------------------------------------
# Coordinate arrays for the 5x5 Germany test grid
# ---------------------------------------------------------------------------

_LATS = np.array([54.0, 53.9, 53.8, 53.7, 53.6], dtype=np.float32)  # descending
_LONS = np.array([9.5, 9.7, 9.9, 10.1, 10.3], dtype=np.float32)

# Kelvin baseline that puts values in the ~15–20 °C range
_KELVIN_BASE = 288.15


# ---------------------------------------------------------------------------
# ERA5-style dataset helpers
# ---------------------------------------------------------------------------


def _make_t2m_ds(
    lats: np.ndarray = _LATS,
    lons: np.ndarray = _LONS,
    values_k: np.ndarray | None = None,
    time_str: str = "2024-01-01",
) -> xr.Dataset:
    """Return a minimal ERA5-style ``xr.Dataset`` with a ``t2m`` variable."""
    import pandas as pd

    if values_k is None:
        rng = np.random.default_rng(42)
        values_k = (_KELVIN_BASE + rng.uniform(-5, 5, (1, len(lats), len(lons)))).astype(
            np.float32
        )

    ds = xr.Dataset(
        {"t2m": (["time", "latitude", "longitude"], values_k)},
        coords={
            "time": pd.to_datetime([time_str]),
            "latitude": lats,
            "longitude": lons,
        },
        attrs={"source": "stub_test_data"},
    )
    ds["t2m"].attrs = {"units": "K", "long_name": "2 metre temperature"}
    return ds


# ---------------------------------------------------------------------------
# StubProvider
# ---------------------------------------------------------------------------


class StubProvider:
    """Minimal climate data provider that returns deterministic data.

    Satisfies the :class:`~analysis.era5.providers.protocol.ClimateDataProvider`
    protocol without making any network calls.  Useful for offline
    pipeline integration tests.
    """

    dataset_id: str = "stub"
    display_name: str = "StubProvider"
    native_resolution_deg: float = 0.1

    bounds: BoundsDict = {"north": 54.0, "south": 53.6, "west": 9.5, "east": 10.3}  # type: ignore[assignment]

    coordinate_names: dict[str, str] = {
        "latitude": "latitude",
        "longitude": "longitude",
        "time": "time",
    }

    latitude_descending: bool = True

    variables: dict[str, dict] = {
        "t2m": {"cds_name": "2m_temperature", "unit": "K", "description": "stub temp"},
        "tp": {"cds_name": "total_precipitation", "unit": "m", "description": "stub precip"},
    }

    unit_conversions: dict[str, dict] = {
        "temperature": {"from": "K", "offset": -273.15},
        "precipitation": {"from": "m", "factor": 1000},
    }

    def fetch_monthly(
        self,
        year: int,
        month: int,
        output_dir: Path,
        variable: str = "t2m",
        force: bool = False,
    ) -> Path:
        """Write a deterministic tiny NetCDF and return its path."""
        import pandas as pd

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / f"stub_{variable}_{year}{month:02d}.nc"
        if path.exists() and not force:
            return path

        rng = np.random.default_rng(seed=year * 100 + month)
        vals = (_KELVIN_BASE + rng.uniform(-5, 5, (1, 5, 5))).astype(np.float32)
        ds = _make_t2m_ds(values_k=vals, time_str=f"{year}-{month:02d}-01")
        ds.to_netcdf(path)
        return path

    def fetch_daily(
        self,
        year: int,
        month: int,
        output_dir: Path,
        force: bool = False,
    ) -> Path:
        """Write a deterministic 24-step hourly NetCDF for one day."""
        import pandas as pd

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / f"stub_hourly_{year}{month:02d}.nc"
        if path.exists() and not force:
            return path

        rng = np.random.default_rng(seed=year * 100 + month + 500)
        n_hours = 24
        vals = (_KELVIN_BASE + rng.uniform(-5, 5, (n_hours, 5, 5))).astype(np.float32)
        times = pd.date_range(f"{year}-{month:02d}-01", periods=n_hours, freq="h")
        ds = xr.Dataset(
            {"t2m": (["time", "latitude", "longitude"], vals)},
            coords={
                "time": times,
                "latitude": _LATS,
                "longitude": _LONS,
            },
        )
        ds["t2m"].attrs = {"units": "K", "long_name": "2 metre temperature"}
        ds.to_netcdf(path)
        return path

    def load_dataset(self, file_path: Path) -> xr.Dataset:
        """Load the file as-is (no spatial subsetting needed for stub data)."""
        return xr.open_dataset(file_path)


# ---------------------------------------------------------------------------
# Pytest fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def sample_era5_ds() -> xr.Dataset:
    """5x5 ERA5-style Dataset with ``t2m`` in Kelvin over Hamburg area."""
    return _make_t2m_ds()


@pytest.fixture()
def sample_anomaly_ds() -> xr.Dataset:
    """Anomaly Dataset with a ``anomaly`` variable (°C) over the stub grid."""
    rng = np.random.default_rng(0)
    anomaly_vals = rng.uniform(-2.0, 2.0, (5, 5)).astype(np.float32)
    ds = xr.Dataset(
        {"anomaly": (["latitude", "longitude"], anomaly_vals)},
        coords={"latitude": _LATS, "longitude": _LONS},
        attrs={"year": 2024, "month": 1, "reference_start": 1961, "reference_end": 1990},
    )
    ds["anomaly"].attrs = {"units": "°C", "long_name": "Temperature anomaly"}
    return ds


@pytest.fixture()
def reference_climatology_ds() -> xr.Dataset:
    """12-month climatology Dataset (t2m in Kelvin, month dim 1–12)."""
    rng = np.random.default_rng(7)
    month_vals = np.stack(
        [
            (_KELVIN_BASE + 10 * np.sin((m - 1) / 12 * 2 * np.pi - np.pi / 2)
             + rng.uniform(-1, 1, (5, 5))).astype(np.float32)
            for m in range(1, 13)
        ]
    )  # shape (12, 5, 5)

    ds = xr.Dataset(
        {"t2m": (["month", "latitude", "longitude"], month_vals)},
        coords={
            "month": np.arange(1, 13),
            "latitude": _LATS,
            "longitude": _LONS,
        },
    )
    ds["t2m"].attrs = {"units": "K", "long_name": "Climatological 2m temperature"}
    return ds


@pytest.fixture()
def stub_provider() -> StubProvider:
    """StubProvider instance satisfying the ClimateDataProvider protocol."""
    return StubProvider()


@pytest.fixture()
def stub_hourly_ds() -> xr.Dataset:
    """24-step hourly Dataset with ``t2m`` in Kelvin (one day)."""
    import pandas as pd

    rng = np.random.default_rng(99)
    n_hours = 24
    vals = (_KELVIN_BASE + rng.uniform(-5, 5, (n_hours, 5, 5))).astype(np.float32)
    times = pd.date_range("2024-01-01", periods=n_hours, freq="h")
    ds = xr.Dataset(
        {"t2m": (["time", "latitude", "longitude"], vals)},
        coords={"time": times, "latitude": _LATS, "longitude": _LONS},
    )
    ds["t2m"].attrs = {"units": "K", "long_name": "2 metre temperature"}
    return ds


@pytest.fixture()
def stub_precip_ds() -> xr.Dataset:
    """24-step hourly Dataset with ``tp`` in metres (one day)."""
    import pandas as pd

    rng = np.random.default_rng(12)
    n_hours = 24
    # Small positive precip values in metres (0–2 mm/h)
    vals = rng.uniform(0.0, 0.002, (n_hours, 5, 5)).astype(np.float32)
    times = pd.date_range("2024-01-01", periods=n_hours, freq="h")
    ds = xr.Dataset(
        {"tp": (["time", "latitude", "longitude"], vals)},
        coords={"time": times, "latitude": _LATS, "longitude": _LONS},
    )
    ds["tp"].attrs = {"units": "m", "long_name": "Total precipitation"}
    return ds
