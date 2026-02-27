"""ERA5-Land climate data provider implementation.

All ERA5-Land-specific knowledge is encapsulated here:
  - CDS dataset names
  - Variable mappings and units
  - Native resolution and Germany bounds
  - API retry configuration
  - CDS download logic with exponential back-off
"""

from __future__ import annotations

import logging
import os
import time
from pathlib import Path

import xarray as xr

from ..types import BoundsDict

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Retry constants
# ---------------------------------------------------------------------------

_MAX_RETRIES: int = 5
_RETRY_DELAY_BASE: float = 30.0  # seconds; doubled on each retry


class ERA5LandProvider:
    """Concrete provider for Copernicus ERA5-Land reanalysis data.

    Implements the :class:`~analysis.era5.providers.protocol.ClimateDataProvider`
    protocol using structural subtyping — no explicit inheritance required.

    All CDS API calls use :mod:`cdsapi` and apply exponential back-off on
    transient errors.  A local cache keyed on (year, month, variable) avoids
    redundant downloads.
    """

    # ------------------------------------------------------------------
    # Protocol properties
    # ------------------------------------------------------------------

    dataset_id: str = "era5-land"
    display_name: str = "ERA5-Land"
    native_resolution_deg: float = 0.1  # ~9 km

    bounds: BoundsDict = BoundsDict(
        north=55.1,
        south=47.2,
        west=5.8,
        east=15.1,
    )

    coordinate_names: dict[str, str] = {
        "latitude": "latitude",
        "longitude": "longitude",
        "time": "time",
    }

    latitude_descending: bool = True  # ERA5-Land stores north-first

    variables: dict[str, dict] = {
        "t2m": {
            "cds_name": "2m_temperature",
            "unit": "K",
            "description": "2-meter air temperature",
        },
        "t2m_max": {
            "cds_name": "2m_temperature",
            "unit": "K",
            "description": "Daily maximum 2-meter temperature (derived from hourly)",
            "derived": True,
        },
        "t2m_min": {
            "cds_name": "2m_temperature",
            "unit": "K",
            "description": "Daily minimum 2-meter temperature (derived from hourly)",
            "derived": True,
        },
        "tp": {
            "cds_name": "total_precipitation",
            "unit": "m",
            "description": "Total precipitation",
        },
    }

    unit_conversions: dict[str, dict] = {
        "temperature": {"from": "K", "offset": -273.15},
        "precipitation": {"from": "m", "factor": 1000},  # metres → mm
    }

    #: ERA5-Land-specific CDS dataset identifiers.
    CDS_DATASETS: dict[str, str] = {
        "monthly": "reanalysis-era5-land-monthly-means",
        "hourly": "reanalysis-era5-land",
    }

    #: Variable name mapping from internal short name to standard name.
    variable_name_mapping: dict[str, str] = {
        "t2m": "temperature_2m",
        "tp": "total_precipitation",
        "ssrd": "surface_solar_radiation",
    }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_cds_client(self):
        """Initialise and return a :class:`cdsapi.Client`.

        Reads authentication from the ``CDS_API_KEY`` environment variable
        (format ``"uid:key"``) or falls back to ``~/.cdsapirc``.

        Raises:
            RuntimeError: If no credentials are found.
        """
        import cdsapi  # deferred so tests can monkeypatch before import

        api_key = os.environ.get("CDS_API_KEY")
        if api_key:
            return cdsapi.Client(
                url="https://cds.climate.copernicus.eu/api/v2",
                key=api_key,
                quiet=True,
            )

        cdsapirc = Path.home() / ".cdsapirc"
        if cdsapirc.exists():
            return cdsapi.Client(quiet=True)

        raise RuntimeError(
            "CDS credentials not found.  Set the CDS_API_KEY environment "
            "variable (format 'uid:key') or create ~/.cdsapirc."
        )

    def _area_list(self) -> list[float]:
        """Return [north, west, south, east] area list for CDS request."""
        return [
            self.bounds["north"],
            self.bounds["west"],
            self.bounds["south"],
            self.bounds["east"],
        ]

    def _download_with_retry(
        self,
        client,
        dataset: str,
        request: dict,
        output_path: Path,
    ) -> None:
        """Submit a CDS retrieve request with exponential back-off retries.

        Args:
            client: Initialised ``cdsapi.Client`` instance.
            dataset: CDS dataset identifier string.
            request: CDS API request payload dict.
            output_path: Destination file path.

        Raises:
            RuntimeError: If all retries are exhausted.
        """
        delay = _RETRY_DELAY_BASE
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                logger.info(
                    "CDS download attempt %d/%d → %s",
                    attempt,
                    _MAX_RETRIES,
                    output_path.name,
                )
                client.retrieve(dataset, request, str(output_path))
                return
            except Exception as exc:  # noqa: BLE001
                if attempt == _MAX_RETRIES:
                    raise RuntimeError(
                        f"CDS download failed after {_MAX_RETRIES} attempts: {exc}"
                    ) from exc
                logger.warning(
                    "CDS download attempt %d failed (%s); retrying in %.0f s …",
                    attempt,
                    exc,
                    delay,
                )
                time.sleep(delay)
                delay *= 2

    # ------------------------------------------------------------------
    # Protocol methods
    # ------------------------------------------------------------------

    def fetch_monthly(
        self,
        year: int,
        month: int,
        output_dir: Path,
        variable: str = "t2m",
        force: bool = False,
    ) -> Path:
        """Download monthly-averaged ERA5-Land data for one month.

        Args:
            year: Four-digit year (e.g. 2024).
            month: Month index 1–12.
            output_dir: Directory to write the NetCDF file.
            variable: Internal variable short name (default ``'t2m'``).
            force: Re-download even if a cached file already exists.

        Returns:
            Path to the downloaded (or cached) NetCDF file.

        Raises:
            KeyError: If ``variable`` is not in :attr:`variables`.
            RuntimeError: If the CDS download fails after all retries.
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{self.dataset_id}_{variable}_{year}{month:02d}.nc"
        output_path = output_dir / filename

        if output_path.exists() and not force:
            logger.info("Cache hit: %s", output_path)
            return output_path

        var_meta = self.variables[variable]
        cds_var_name = var_meta["cds_name"]

        request = {
            "product_type": "monthly_averaged_reanalysis",
            "variable": cds_var_name,
            "year": str(year),
            "month": f"{month:02d}",
            "time": "00:00",
            "area": self._area_list(),
            "format": "netcdf",
        }

        client = self._get_cds_client()
        self._download_with_retry(
            client,
            self.CDS_DATASETS["monthly"],
            request,
            output_path,
        )
        return output_path

    def fetch_daily(
        self,
        year: int,
        month: int,
        output_dir: Path,
        force: bool = False,
    ) -> Path:
        """Download all hourly 2 m temperature values for one month.

        Hourly data is required to derive daily Tmin / Tmax.

        Args:
            year: Four-digit year.
            month: Month index 1–12.
            output_dir: Directory to write the NetCDF file.
            force: Re-download even if a cached file already exists.

        Returns:
            Path to the downloaded (or cached) NetCDF file.

        Raises:
            RuntimeError: If the CDS download fails after all retries.
        """
        import calendar

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{self.dataset_id}_hourly_{year}{month:02d}.nc"
        output_path = output_dir / filename

        if output_path.exists() and not force:
            logger.info("Cache hit: %s", output_path)
            return output_path

        _, n_days = calendar.monthrange(year, month)
        days = [f"{d:02d}" for d in range(1, n_days + 1)]
        hours = [f"{h:02d}:00" for h in range(24)]

        request = {
            "product_type": "reanalysis",
            "variable": "2m_temperature",
            "year": str(year),
            "month": f"{month:02d}",
            "day": days,
            "time": hours,
            "area": self._area_list(),
            "format": "netcdf",
        }

        client = self._get_cds_client()
        self._download_with_retry(
            client,
            self.CDS_DATASETS["hourly"],
            request,
            output_path,
        )
        return output_path

    def load_dataset(self, file_path: Path) -> xr.Dataset:
        """Load a NetCDF file and subset it to the provider's bounds.

        For ERA5-Land data, latitude is stored in descending order
        (north first), so we use a ``slice(north, south)`` selection.

        Args:
            file_path: Path to a NetCDF file produced by this provider.

        Returns:
            ``xr.Dataset`` spatially subset to :attr:`bounds`.
        """
        ds = xr.open_dataset(file_path)
        lat_key = self.coordinate_names["latitude"]
        lon_key = self.coordinate_names["longitude"]

        if self.latitude_descending:
            ds = ds.sel(
                **{
                    lat_key: slice(self.bounds["north"], self.bounds["south"]),
                    lon_key: slice(self.bounds["west"], self.bounds["east"]),
                }
            )
        else:
            ds = ds.sel(
                **{
                    lat_key: slice(self.bounds["south"], self.bounds["north"]),
                    lon_key: slice(self.bounds["west"], self.bounds["east"]),
                }
            )
        return ds
