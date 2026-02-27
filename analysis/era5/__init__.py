"""ERA5-Land climate data pipeline.

Public API for the ERA5-Land data processing pipeline.
"""

from __future__ import annotations

from .config import (
    ANOMALY_COLORMAP,
    GERMANY_BOUNDS,
    GERMANY_BOUNDS_BUFFERED,
    GERMAN_ISLANDS,
    PRECIPITATION_THRESHOLDS,
    REFERENCE_PERIOD,
    SNOW_DAY_TEMP_THRESHOLD,
    TEMPERATURE_THRESHOLDS,
)
from .providers import get_provider
from .types import AnomalyMetadata, BoundsDict, ProcessingResult

__all__ = [
    # Config
    "ANOMALY_COLORMAP",
    "GERMANY_BOUNDS",
    "GERMANY_BOUNDS_BUFFERED",
    "GERMAN_ISLANDS",
    "PRECIPITATION_THRESHOLDS",
    "REFERENCE_PERIOD",
    "SNOW_DAY_TEMP_THRESHOLD",
    "TEMPERATURE_THRESHOLDS",
    # Provider factory
    "get_provider",
    # Types
    "AnomalyMetadata",
    "BoundsDict",
    "ProcessingResult",
]
