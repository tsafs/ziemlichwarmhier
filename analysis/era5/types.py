"""Type definitions for ERA5-Land data processing.

Defines data structures used throughout the ERA5-Land pipeline.
Source-agnostic types shared by all climate data providers.

Note: Variable name mappings between ERA5 and standard names are properties
of the provider (see providers/era5_land.py), not global constants.
"""

from __future__ import annotations

from typing import TypedDict


class BoundsDict(TypedDict):
    """Geographic bounds dictionary (EPSG:4326)."""

    north: float
    south: float
    east: float
    west: float


class ProcessingResult(TypedDict):
    """Result of a single processing step in the pipeline."""

    success: bool
    output_path: str
    message: str
    metadata: dict


class AnomalyMetadata(TypedDict):
    """Metadata attached to an anomaly GeoTIFF/NetCDF output."""

    year: int
    month: int
    reference_start: int
    reference_end: int
    bounds: BoundsDict
    resolution: str
    crs: str
    units: str


# ---------------------------------------------------------------------------
# Legacy variable name mappings (informational; authoritative copies live in
# ERA5LandProvider.variable_name_mapping).
# ---------------------------------------------------------------------------

#: Map ERA5-Land short names → dataset-agnostic standard names.
ERA5_TO_STANDARD: dict[str, str] = {
    "t2m": "temperature_2m",
    "tp": "total_precipitation",
    "ssrd": "surface_solar_radiation",
}

#: Reverse mapping: standard names → ERA5-Land short names.
STANDARD_TO_ERA5: dict[str, str] = {v: k for k, v in ERA5_TO_STANDARD.items()}
