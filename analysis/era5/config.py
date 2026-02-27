"""Source-agnostic configuration for ERA5-Land climate data processing.

This module holds only settings that are independent of the data provider:
  - Reference period for anomaly baselines
  - Temperature and precipitation thresholds
  - Germany bounding box (also kept here for convenience; authoritative copy
    lives in ERA5LandProvider.bounds)
  - Color-mapping constants for visualisation
  - German island list for land-mask validation

Provider-specific values (CDS dataset names, ERA5 variable mappings,
native resolution, API retry config) live in the corresponding provider
implementation (``analysis/era5/providers/era5_land.py``).
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Germany geographic bounds (EPSG:4326)
# ---------------------------------------------------------------------------
# These are also exposed via ERA5LandProvider.bounds; kept here for modules
# that import directly from config without going through the provider.

GERMANY_BOUNDS: dict[str, float] = {
    "north": 55.1,
    "south": 47.2,
    "west": 5.8,
    "east": 15.1,
}

# Slightly enlarged bounds used when downloading/clipping to avoid edge gaps.
GERMANY_BOUNDS_BUFFERED: dict[str, float] = {
    "north": 55.2,
    "south": 47.1,
    "west": 5.7,
    "east": 15.2,
}

# ---------------------------------------------------------------------------
# ERA5-Land variables (informational; authoritative copy in ERA5LandProvider)
# ---------------------------------------------------------------------------

ERA5_VARIABLES: dict[str, dict] = {
    "t2m": {
        "cds_name": "2m_temperature",
        "unit": "K",
        "description": "2-meter air temperature (mean)",
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
        "description": "Total precipitation for snow/rain metrics",
    },
}

CDS_DATASETS: dict[str, str] = {
    "monthly": "reanalysis-era5-land-monthly-means",
    "hourly": "reanalysis-era5-land",
}

# ---------------------------------------------------------------------------
# Reference period (WMO standard baseline)
# ---------------------------------------------------------------------------

REFERENCE_PERIOD: tuple[int, int] = (1961, 1990)

# ---------------------------------------------------------------------------
# Temperature thresholds (DWD standards)
# ---------------------------------------------------------------------------

TEMPERATURE_THRESHOLDS: dict[str, float] = {
    "hot_day": 30.0,         # Tmax >= 30 °C  (DWD: Heißer Tag)
    "extreme_heat": 35.0,    # Tmax >= 35 °C  (extreme heat / vegetation damage)
    "tropical_night": 20.0,  # Tmin >= 20 °C  (DWD: Tropennacht)
    "ice_day": 0.0,          # Tmax <=  0 °C  (DWD: Eistag)
    "frost_day": 0.0,        # Tmin <   0 °C  (DWD: Frosttag)
    "comfortable_min": 15.0, # Lower bound for a "comfortable" day
    "comfortable_max": 25.0, # Upper bound for a "comfortable" day
}

# ---------------------------------------------------------------------------
# Precipitation thresholds
# ---------------------------------------------------------------------------

PRECIPITATION_THRESHOLDS: dict[str, float] = {
    "dry_day": 1.0,           # Precip < 1 mm  → dry spell count
    "extreme_rain": 25.0,     # Precip >= 25 mm → flooding risk
    "snow_precip_min": 0.1,   # Precip > 0.1 mm required for snow-day flag
}

# Temperature threshold for snow-day detection (Tmean <= 0 °C AND precip > 0.1 mm)
SNOW_DAY_TEMP_THRESHOLD: float = 0.0  # °C

# ---------------------------------------------------------------------------
# ERA5-Land native resolution (informational; authoritative in provider)
# ---------------------------------------------------------------------------

ERA5_LAND_RESOLUTION: float = 0.1  # degrees (~9 km)

# ---------------------------------------------------------------------------
# CDS API configuration (informational; authoritative in provider)
# ---------------------------------------------------------------------------

CDS_CONFIG: dict[str, object] = {
    "dataset": "reanalysis-era5-land-monthly-means",
    "product_type": "monthly_averaged_reanalysis",
    "format": "netcdf",
    "max_retries": 5,
    "retry_delay_base": 60,  # seconds
}

# ---------------------------------------------------------------------------
# Colour mapping for anomaly visualisation
# ---------------------------------------------------------------------------

ANOMALY_COLORMAP: dict[str, object] = {
    "vmin": -3.0,        # °C
    "vmax": 3.0,         # °C
    "colormap": "RdBu_r",  # Red (warm anomaly) to Blue (cold anomaly)
}

# ---------------------------------------------------------------------------
# German islands for land-mask validation
# ---------------------------------------------------------------------------

GERMAN_ISLANDS: list[dict[str, object]] = [
    {"name": "Sylt",     "lat": 54.9,  "lon": 8.3},
    {"name": "Rügen",    "lat": 54.4,  "lon": 13.4},
    {"name": "Helgoland","lat": 54.18, "lon": 7.89},
    {"name": "Borkum",   "lat": 53.59, "lon": 6.66},
    {"name": "Fehmarn",  "lat": 54.45, "lon": 11.2},
    {"name": "Usedom",   "lat": 53.93, "lon": 14.0},
]


# ---------------------------------------------------------------------------
# Validation helper
# ---------------------------------------------------------------------------

def validate_bounds(bounds: dict[str, float]) -> None:
    """Validate a geographic bounds dictionary.

    Args:
        bounds: Mapping with keys ``north``, ``south``, ``east``, ``west``
                containing float degree values (EPSG:4326).

    Raises:
        ValueError: If any bound value is out of range or logically inconsistent.
    """
    if bounds["north"] <= bounds["south"]:
        raise ValueError(
            f"north ({bounds['north']}) must be greater than south ({bounds['south']})"
        )
    if bounds["east"] <= bounds["west"]:
        raise ValueError(
            f"east ({bounds['east']}) must be greater than west ({bounds['west']})"
        )
    if not (-90.0 <= bounds["south"] <= 90.0 and -90.0 <= bounds["north"] <= 90.0):
        raise ValueError("Latitude bounds must be in the range [-90, 90]")
    if not (-180.0 <= bounds["west"] <= 180.0 and -180.0 <= bounds["east"] <= 180.0):
        raise ValueError("Longitude bounds must be in the range [-180, 180]")
