#!/usr/bin/env python3
"""
TypedDict definitions for all climate metrics.

These types define the JSON structure consumed by the frontend.
See schemas/metrics.schema.json for the full schema definition.
"""

from typing import TypedDict, Literal


class FiveYearAnomaly(TypedDict):
    """5-year mean temperature anomaly relative to reference period."""
    value: float           # °C above/below reference
    periodStart: int       # Start year of recent period
    periodEnd: int         # End year of recent period
    referenceStart: int    # Start year of reference period
    referenceEnd: int      # End year of reference period


class WarmingRate(TypedDict):
    """Linear warming trend over analysis period."""
    value: float           # °C per decade
    startYear: int         # Start year of trend period
    endYear: int           # End year of trend period
    confidence: float      # R² of linear regression (0–1)


class RecordDays(TypedDict):
    """Count of temperature record days in a given year."""
    total: int             # Total records (hot + cold)
    hot: int               # New Tmax records
    cold: int              # New Tmin records (coldest)
    year: int              # Year the counts apply to


class WinterWarming(TypedDict):
    """Winter (DJF) temperature anomaly."""
    value: float           # °C above/below reference winter
    periodStart: int
    periodEnd: int
    referenceStart: int
    referenceEnd: int


class SnowDaysLost(TypedDict):
    """Change in snow day count vs reference period."""
    value: int             # Negative = fewer snow days
    currentAverage: float  # Mean snow days in recent period
    referenceAverage: float  # Mean snow days in reference period
    periodStart: int
    periodEnd: int


class ComfortableDays(TypedDict):
    """Days with comfortable temperature (15–25°C)."""
    count: int             # Count in most recent year
    average: float         # Long-term average


class SeasonalWarming(TypedDict):
    """Warming broken down by season."""
    winter: float          # °C anomaly for winter
    spring: float
    summer: float
    fall: float
    fastestSeason: Literal['winter', 'spring', 'summer', 'fall']
    periodStart: int
    periodEnd: int
    referenceStart: int
    referenceEnd: int


class ThresholdDays(TypedDict):
    """Count of days crossing temperature thresholds."""
    hotDays: int           # Tmax >= 30°C
    tropicalNights: int    # Tmin > 20°C
    iceDays: int           # Tmax <= 0°C
    frostDays: int         # Tmin < 0°C
    year: int


class LocationMetrics(TypedDict):
    """Complete metrics bundle for a single location."""
    calculatedAt: str           # ISO 8601 timestamp
    fiveYearAnomaly: FiveYearAnomaly
    warmingRate: WarmingRate
    recordDays: RecordDays
    winterWarming: WinterWarming
    seasonalWarming: SeasonalWarming
    thresholdDays: ThresholdDays
    snowDaysLost: SnowDaysLost
    comfortableDays: ComfortableDays


class CoverageDict(TypedDict):
    """Grid coverage metadata."""
    bounds: dict
    gridResolution: str


class MetricsFile(TypedDict):
    """Root JSON structure written to disk."""
    version: str
    generatedAt: str
    source: str            # provider.dataset_id
    coverage: CoverageDict
    data: LocationMetrics
