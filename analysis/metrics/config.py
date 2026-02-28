#!/usr/bin/env python3
"""
Configuration for climate metrics calculations.

Contains thresholds, reference periods, and helper functions.
"""

from typing import TypedDict


class Period(TypedDict):
    start_year: int
    end_year: int


# Reference climatology period (WMO standard)
REFERENCE_PERIOD: Period = {
    'start_year': 1961,
    'end_year': 1990,
}

# Warming rate analysis period (recent 30 years)
WARMING_RATE_PERIOD: Period = {
    'start_year': 1995,
    'end_year': 2025,
}

# Recent 5-year period for anomaly calculations
FIVE_YEAR_ANOMALY_PERIOD: Period = {
    'start_year': 2021,
    'end_year': 2025,
}

# Temperature thresholds (°C)
THRESHOLDS = {
    'hot_day': 30.0,         # Tmax >= 30°C
    'tropical_night': 20.0,  # Tmin > 20°C
    'extreme_heat_day': 35.0, # Tmax >= 35°C
    'frost_day': 0.0,        # Tmin < 0°C
    'ice_day': 0.0,          # Tmax <= 0°C
}

# Snow day: precipitation > threshold AND mean temp <= 0°C
SNOW_PRECIPITATION_THRESHOLD_MM = 0.1  # mm/day

# Comfortable temperature range (°C)
COMFORTABLE_RANGE = {
    'min': 15.0,
    'max': 25.0,
}

# Season definitions (month numbers)
SEASONS = {
    'winter': [12, 1, 2],
    'spring': [3, 4, 5],
    'summer': [6, 7, 8],
    'fall': [9, 10, 11],
}

# Minimum years required for trend analysis
MIN_YEARS_FOR_TREND = 10

# Minimum R² to report a trend as significant
MIN_R_SQUARED = 0.3

# Decadal bins (inclusive start, exclusive end)
DECADES = [
    (1961, 1970),
    (1971, 1980),
    (1981, 1990),
    (1991, 2000),
    (2001, 2010),
    (2011, 2020),
    (2021, 2025),  # Partial decade
]


def get_years_in_period(period: Period) -> list:
    """Return list of years in a period (inclusive).
    
    Args:
        period: Period dictionary with start_year and end_year
        
    Returns:
        List of years
    """
    return list(range(period['start_year'], period['end_year'] + 1))


def get_season_for_month(month: int) -> str:
    """Return season name for a given month.
    
    Args:
        month: Month number (1-12)
        
    Returns:
        Season name: 'winter', 'spring', 'summer', or 'fall'
    """
    for season, months in SEASONS.items():
        if month in months:
            return season
    raise ValueError(f"Invalid month: {month}")


def get_decade_for_year(year: int) -> tuple:
    """Return the decade bin for a year.
    
    Args:
        year: Year to look up
        
    Returns:
        Tuple of (start_year, end_year) for the decade
    """
    for start, end in DECADES:
        if start <= year <= end:
            return start, end
    return None
