"""Climate data provider protocol definition.

Defines the interface that all climate data sources must satisfy.
Uses structural subtyping (typing.Protocol) — providers do not need
to inherit from this class, only implement its methods / properties.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

import xarray as xr

from ..types import BoundsDict


@runtime_checkable
class ClimateDataProvider(Protocol):
    """Interface for pluggable climate reanalysis data sources.

    Any object that implements all properties and methods below
    satisfies the protocol and can be used with ``isinstance``
    checks at runtime (due to ``@runtime_checkable``).

    All ERA5-Land-specific knowledge (CDS dataset names, variable
    mappings, API retry config) lives in ``ERA5LandProvider``.
    This protocol defines only the stable contract that pipeline
    modules depend on.
    """

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    @property
    def dataset_id(self) -> str:
        """Short identifier used in file names, e.g. ``'era5-land'``."""
        ...

    @property
    def display_name(self) -> str:
        """Human-readable name for logging, e.g. ``'ERA5-Land'``."""
        ...

    # ------------------------------------------------------------------
    # Grid metadata
    # ------------------------------------------------------------------

    @property
    def native_resolution_deg(self) -> float:
        """Native grid spacing in degrees (e.g. ``0.1`` for ERA5-Land ~9 km)."""
        ...

    @property
    def bounds(self) -> BoundsDict:
        """Geographic extraction bounds (EPSG:4326)."""
        ...

    # ------------------------------------------------------------------
    # Variable catalogue
    # ------------------------------------------------------------------

    @property
    def variables(self) -> dict[str, dict]:
        """Variable definitions keyed by internal short name.

        Each value is a dict with at least:
          - ``cds_name``: the name used when querying the remote API
          - ``unit``: native unit (e.g. ``'K'``, ``'m'``)
          - ``description``: human-readable description
          - ``derived`` (optional bool): ``True`` if computed from other vars
        """
        ...

    @property
    def coordinate_names(self) -> dict[str, str]:
        """Map standard coordinate roles to dataset-specific dimension names.

        Required keys: ``'latitude'``, ``'longitude'``, ``'time'``.
        Example: ``{'latitude': 'latitude', 'longitude': 'longitude', 'time': 'time'}``.
        """
        ...

    @property
    def latitude_descending(self) -> bool:
        """``True`` if latitude is stored north-to-south (ERA5-Land convention)."""
        ...

    @property
    def unit_conversions(self) -> dict[str, dict]:
        """Unit conversion rules applied when loading data.

        Example::

            {
                'temperature': {'from': 'K', 'offset': -273.15},
                'precipitation': {'from': 'm', 'factor': 1000},
            }
        """
        ...

    # ------------------------------------------------------------------
    # Data access
    # ------------------------------------------------------------------

    def fetch_monthly(
        self,
        year: int,
        month: int,
        output_dir: Path,
        variable: str = "t2m",
        force: bool = False,
    ) -> Path:
        """Download monthly aggregated data.

        Args:
            year: Four-digit year.
            month: Month (1–12).
            output_dir: Directory where the NetCDF file is written.
            variable: Internal variable short name (e.g. ``'t2m'``).
            force: Re-download even if a local cache file exists.

        Returns:
            Absolute path to the downloaded (or cached) NetCDF file.
        """
        ...

    def fetch_daily(
        self,
        year: int,
        month: int,
        output_dir: Path,
        force: bool = False,
    ) -> Path:
        """Download hourly/daily-resolution data for Tmin/Tmax derivation.

        Args:
            year: Four-digit year.
            month: Month (1–12).
            output_dir: Directory where the NetCDF file is written.
            force: Re-download even if a local cache file exists.

        Returns:
            Absolute path to the downloaded (or cached) NetCDF file.
        """
        ...

    def load_dataset(self, file_path: Path) -> xr.Dataset:
        """Load and subset a downloaded file to the provider's bounds.

        Args:
            file_path: Path to a NetCDF file previously downloaded by this
                       provider.

        Returns:
            ``xr.Dataset`` subset to ``self.bounds``.
        """
        ...
