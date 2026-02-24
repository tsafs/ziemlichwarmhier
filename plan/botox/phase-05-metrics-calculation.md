---
goal: Phase 5 - Metrics Calculation Pipeline Implementation
version: 1.1
date_created: 2026-02-16
last_updated: 2026-02-17
owner: Sebastian
status: 'Planned'
tags: [phase-5, metrics, climate-stats, statistics, python, json]
---

# Introduction

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

This phase implements the climate metrics calculation pipeline that processes ERA5-Land data to generate statistical indicators for frontend display. The metrics include five-year temperature anomalies, warming rates, record-breaking days, winter warming, snow days lost, and comfortable temperature days.

**Key outputs:**
- Five-year temperature anomaly calculation (2021-2025 vs 1961-1990)
- Warming rate (linear regression trend since 1995)
- Record-breaking days counter
- Winter warming analysis (DJF specifically)
- Snow days lost vs reference period
- Comfortable temperature days (15-25°C mean)
- Aggregation to city and country levels
- JSON export conforming to frontend schema

## 1. Requirements & Constraints

### From Master Plan

- **REQ-003**: Display 6 static climate metrics (Five-Year Temperature Anomaly, Warming Rate, Winter Warming, Record-Breaking Days, Snow Days Lost, Comfortable Days)
- **REQ-004**: Support city selection with tile-based metrics (cities map to grid tiles; multiple cities can share one tile's data)

### Phase-Specific Requirements

- **REQ-P5-001**: Calculate five-year temperature anomaly (2021-2025 mean) versus 1961-1990 baseline
- **REQ-P5-002**: Calculate warming rate using linear regression over 1995-2025 period
- **REQ-P5-003**: Count record-breaking days (new daily temperature records)
- **REQ-P5-004**: Calculate winter warming (DJF anomaly for 2021-2025 vs 1961-1990)
- **REQ-P5-005**: Calculate snow days lost:
  - Snow day: precipitation > 0.1mm AND Tmean ≤ 0°C
  - Compare 2021-2025 average to 1961-1990 average
- **REQ-P5-006**: Count comfortable temperature days (daily mean 15-25°C)
- **REQ-P5-007**: Aggregate metrics from grid cells to city and country level
- **REQ-P5-008**: Export to JSON conforming to frontend LocationMetrics schema
- **REQ-P5-009**: Calculate per-grid-cell metrics for map hover tooltips

### Constraints

- **CON-P5-001**: Use standard WMO reference period (1961-1990)
- **CON-P5-002**: Linear regression must report R² confidence value
- **CON-P5-003**: All calculations must be deterministic
- **CON-P5-004**: Memory-efficient processing for full Germany grid

## 2. Implementation Steps

### Implementation Phase 5.1: Configuration & Types

- GOAL-P5-001: Define metrics configuration and data structures

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P5-001 | Create `analysis/metrics/__init__.py` with module exports | | |
| TASK-P5-002 | Create `analysis/metrics/config.py` with thresholds and reference periods | | |
| TASK-P5-003 | Create `analysis/metrics/types.py` with metric data structures | | |
| TASK-P5-004 | Write unit tests for configuration validation | | |

### Implementation Phase 5.2: Five-Year Anomaly Calculation

- GOAL-P5-002: Calculate five-year temperature anomaly (2021-2025)

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P5-005 | Create `analysis/metrics/calculate_five_year_anomaly.py` | | |
| TASK-P5-006 | Implement per-grid-cell annual mean calculation | | |
| TASK-P5-007 | Implement 5-year mean anomaly vs reference period | | |
| TASK-P5-008 | Write unit tests with known test values | | |

### Implementation Phase 5.3: Warming Rate Calculation

- GOAL-P5-003: Calculate linear warming trend

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P5-009 | Create `analysis/metrics/calculate_warming_rate.py` | | |
| TASK-P5-010 | Implement linear regression with scipy.stats.linregress | | |
| TASK-P5-011 | Include R² value and confidence metrics | | |
| TASK-P5-012 | Support configurable time range for trend calculation | | |
| TASK-P5-013 | Write unit tests with synthetic trend data | | |

### Implementation Phase 5.4: Record Days Calculation

- GOAL-P5-004: Count record-breaking temperature days

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P5-014 | Create `analysis/metrics/calculate_record_days.py` | | |
| TASK-P5-015 | Implement historical daily record tracking | | |
| TASK-P5-016 | Count new hot records (Tmax > historical max) | | |
| TASK-P5-017 | Count new cold records (Tmin < historical min) | | |
| TASK-P5-018 | Write unit tests with edge cases | | |

### Implementation Phase 5.5: Winter Warming

- GOAL-P5-005: Calculate winter (DJF) temperature anomaly

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P5-019 | Create `analysis/metrics/calculate_winter_warming.py` | | |
| TASK-P5-020 | Implement winter (DJF) aggregation | | |
| TASK-P5-021 | Calculate DJF anomaly for 2021-2025 vs 1961-1990 baseline | | |
| TASK-P5-022 | Calculate warming rate for winter specifically | | |
| TASK-P5-023 | Write unit tests for winter calculations | | |

### Implementation Phase 5.6: Snow Days Lost

- GOAL-P5-006: Calculate snow days lost vs reference period

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P5-024 | Create `analysis/metrics/calculate_snow_days_lost.py` | | |
| TASK-P5-025 | Implement snow day detection: precip > 0.1mm AND Tmean ≤ 0°C | | |
| TASK-P5-026 | Calculate reference period (1961-1990) average snow days | | |
| TASK-P5-027 | Calculate current period (2021-2025) average snow days | | |
| TASK-P5-028 | Calculate difference (snow days lost) | | |
| TASK-P5-029 | Write unit tests covering edge cases | | |

### Implementation Phase 5.7: Comfortable Days

- GOAL-P5-007: Count comfortable temperature days

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P5-030 | Create `analysis/metrics/calculate_comfortable_days.py` | | |
| TASK-P5-031 | Implement daily mean temperature calculation | | |
| TASK-P5-032 | Count days with mean in 15-25°C range | | |
| TASK-P5-033 | Write unit tests | | |

### Implementation Phase 5.8: Decadal Aggregation for Narrative Plots

- GOAL-P5-008: Aggregate threshold counts by decade for narrative visualization

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P5-034 | Create `analysis/metrics/calculate_decadal_aggregates.py` | | |
| TASK-P5-035 | Implement decade binning (1950s, 1960s, ..., 2020s) | | |
| TASK-P5-036 | Aggregate threshold days by decade × month for Comfort Calendar | | |
| TASK-P5-037 | Aggregate tropical nights by decade for Sleep Interrupted plot | | |
| TASK-P5-038 | Aggregate hot/dry days by year for Vegetation Stress (requires `tp` precip) | | |
| TASK-P5-039 | Export decadal aggregates to JSON per tile: `{grid_i}_{grid_j}_decadal_metrics.json` | | |
| TASK-P5-040 | Write unit tests for decadal aggregation | | |

### Implementation Phase 5.9: Aggregation & Export

- GOAL-P5-009: Aggregate metrics and export to JSON

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P5-041 | Create `analysis/metrics/aggregate_metrics.py` | | |
| TASK-P5-042 | Implement grid-to-city aggregation (nearest neighbor or avg) | | |
| TASK-P5-043 | Implement country-level aggregation (weighted by area) | | |
| TASK-P5-044 | Create `analysis/metrics/export_metrics.py` | | |
| TASK-P5-045 | Implement JSON export conforming to frontend schema | | |
| TASK-P5-046 | Write integration tests for full pipeline | | |

### Implementation Phase 5.10: Testing & Documentation

- GOAL-P5-010: Complete testing and documentation

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P5-047 | Create `analysis/metrics/tests/` directory structure | | |
| TASK-P5-048 | Create comprehensive test fixtures | | |
| TASK-P5-049 | Write integration test running all metrics | | |
| TASK-P5-050 | Add docstrings and README | | |
| TASK-P5-051 | Validate output against HYRAS where overlapping | | |

## 3. Alternatives

- **ALT-P5-001**: **Use rolling average instead of linear regression for warming rate**
  - More stable but less interpretable
  - Rejected: Linear regression provides °C/decade which is standard metric

- **ALT-P5-002**: **Calculate all metrics at runtime on frontend**
  - More flexible but higher compute on client
  - Rejected: Pre-calculation reduces client load, faster perceived performance

- **ALT-P5-003**: **Store metrics in SQLite instead of JSON**
  - Better query flexibility
  - Rejected: JSON simpler, works with static hosting, small dataset

- **ALT-P5-004**: **Use percentile-based thresholds instead of fixed values**
  - More climatologically appropriate
  - Rejected: Fixed thresholds (30°C hot day) are more intuitive for users

## 4. Dependencies

### Phase Dependencies

- **DEP-P5-001**: Phase 3 (ERA5-Land Pipeline) - provides temperature data
- **DEP-P5-002**: Phase 2 (Infrastructure) - target for JSON upload
- **DEP-P5-003**: City correlation data (Phase 9 overlap) - city-to-grid mapping

### Data Dependencies

- **DEP-P5-004**: Daily Tmax/Tmin from ERA5-Land (not monthly means)
- **DEP-P5-005**: Historical daily records for record-breaking calculation
- **DEP-P5-006**: City list with coordinates (`german_cities_p5000.csv`)

### Python Package Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `xarray` | >=2025.6.1 | Data processing |
| `numpy` | >=2.3.0 | Numerical operations |
| `scipy` | >=1.14.0 | Linear regression |
| `pandas` | >=2.0.0 | Data aggregation |
| `pytest` | >=8.0.0 | Testing |

## 5. Files

### New Files

| File ID | Path | Action | Description |
|---------|------|--------|-------------|
| FILE-P5-001 | `analysis/metrics/__init__.py` | NEW | Module exports |
| FILE-P5-002 | `analysis/metrics/config.py` | NEW | Configuration |
| FILE-P5-003 | `analysis/metrics/types.py` | NEW | Data structures |
| FILE-P5-004 | `analysis/metrics/calculate_five_year_anomaly.py` | NEW | Five-year anomaly |
| FILE-P5-005 | `analysis/metrics/calculate_warming_rate.py` | NEW | Warming trend |
| FILE-P5-006 | `analysis/metrics/calculate_record_days.py` | NEW | Record days |
| FILE-P5-007 | `analysis/metrics/calculate_winter_warming.py` | NEW | Winter warming |
| FILE-P5-008 | `analysis/metrics/calculate_snow_days_lost.py` | NEW | Snow days lost |
| FILE-P5-009 | `analysis/metrics/calculate_comfortable_days.py` | NEW | Comfortable days |
| FILE-P5-010 | `analysis/metrics/calculate_decadal_aggregates.py` | NEW | Decadal aggregation for narrative plots |
| FILE-P5-011 | `analysis/metrics/aggregate_metrics.py` | NEW | Aggregation |
| FILE-P5-012 | `analysis/metrics/export_metrics.py` | NEW | JSON export |
| FILE-P5-013 | `analysis/metrics/tests/__init__.py` | NEW | Test module |
| FILE-P5-014 | `analysis/metrics/tests/conftest.py` | NEW | Fixtures |
| FILE-P5-015 | `analysis/metrics/tests/test_five_year_anomaly.py` | NEW | Anomaly tests |
| FILE-P5-016 | `analysis/metrics/tests/test_warming_rate.py` | NEW | Trend tests |
| FILE-P5-017 | `analysis/metrics/tests/test_snow_days_lost.py` | NEW | Snow days tests |
| FILE-P5-018 | `analysis/metrics/tests/test_decadal_aggregates.py` | NEW | Decadal aggregation tests |
| FILE-P5-019 | `analysis/metrics/tests/test_integration.py` | NEW | Integration tests |

### Output Files

| Path | Description |
|------|-------------|
| `data/metrics/germany.json` | Country-level aggregated metrics |
| `data/metrics/tiles/{grid_i}_{grid_j}.json` | Per-tile metrics (multiple cities can share the same tile) |
| `data/metrics/tiles/{grid_i}_{grid_j}_decadal.json` | Per-tile decadal aggregates for narrative plots (Comfort Calendar, Tropical Nights, Vegetation Stress) |
| `data/metrics/grid/metrics_{year}.nc` | Per-grid-cell metrics (NetCDF) |

**Decadal metrics URL contract:**
- Pattern: `/data/metrics/tiles/{grid_i}_{grid_j}_decadal.json`
- Produced by: `TASK-P5-039` (`calculate_decadal_aggregates.py`)
- Consumed by: Phase 9 plots — Comfort Calendar, Sleep Interrupted (Tropical Nights), Vegetation Stress
- Structure: `{ decade: string, month?: number, value: number }[]` arrays keyed by metric type

> **Future country support note:** `germany.json` is the country-level aggregate for Germany. When expanding to other countries, additional files (e.g. `france.json`) would follow the same pattern. The frontend `MetricsService` and pipeline export logic will need to be extended at that point.

## 6. Testing

### Unit Tests

| Test ID | Description | File |
|---------|-------------|------|
| TEST-P5-001 | Five-year anomaly correct for known values | `test_five_year_anomaly.py` |
| TEST-P5-002 | Anomaly = 0 when current equals baseline | `test_five_year_anomaly.py` |
| TEST-P5-003 | Linear regression slope correct for synthetic data | `test_warming_rate.py` |
| TEST-P5-004 | R² = 1 for perfect linear data | `test_warming_rate.py` |
| TEST-P5-005 | R² < 1 for noisy data | `test_warming_rate.py` |
| TEST-P5-006 | Snow day detection correct at boundary (0°C, 0.1mm) | `test_snow_days_lost.py` |
| TEST-P5-007 | Snow days lost calculation matches manual check | `test_snow_days_lost.py` |
| TEST-P5-008 | Winter grouping assigns DJF correctly | `test_winter_warming.py` |
| TEST-P5-009 | Record days identifies new maximum | `test_record_days.py` |
| TEST-P5-010 | Comfortable days range inclusive (15°C and 25°C count) | `test_comfortable_days.py` |

### Integration Tests

| Test ID | Description | File |
|---------|-------------|------|
| TEST-P5-011 | Full pipeline produces valid JSON | `test_integration.py` |
| TEST-P5-012 | JSON conforms to frontend schema | `test_integration.py` |
| TEST-P5-013 | City aggregation matches manual calculation | `test_integration.py` |

### Mock Data Requirements

```python
# fixtures/sample_daily_temps.nc
# - Daily Tmax and Tmin for 1 year
# - Small grid (10x10)
# - Include values spanning all threshold boundaries
# - Include some record-breaking values
```

## 7. Risks & Assumptions

### Risks

| Risk ID | Description | Probability | Impact | Mitigation |
|---------|-------------|-------------|--------|------------|
| RISK-P5-001 | ERA5-Land daily data not available (only monthly) | High | High | May need ERA5-Land hourly → derive Tmax/Tmin |
| RISK-P5-002 | Historical records incomplete for record-breaking calc | Medium | Medium | Use available data, document limitations |
| RISK-P5-003 | City aggregation misses some cities | Low | Medium | Verify all cities have valid grid assignment |
| RISK-P5-004 | Memory overflow for full historical processing | Medium | Medium | Process year-by-year, chunk operations |

### Assumptions

- **ASSUMPTION-P5-001**: ERA5-Land provides daily Tmax/Tmin (or can be derived)
- **ASSUMPTION-P5-002**: Reference period 1961-1990 has complete ERA5-Land coverage
- **ASSUMPTION-P5-003**: Linear regression over 30 years sufficient for trend
- **ASSUMPTION-P5-004**: Nearest-neighbor adequate for city-to-grid mapping
- **ASSUMPTION-P5-005**: Fixed thresholds (30°C, 0°C) appropriate for Germany

## 8. Multi-Agent Execution Notes

### Execution Order

**Sequential tasks:**
1. TASK-P5-001 → TASK-P5-004 (Configuration)
2. Individual metric modules can be developed in parallel:
   - TASK-P5-005 → TASK-P5-008 (Annual anomaly)
   - TASK-P5-009 → TASK-P5-013 (Warming rate)
   - TASK-P5-014 → TASK-P5-018 (Record days)
   - TASK-P5-019 → TASK-P5-023 (Seasonal)
   - TASK-P5-024 → TASK-P5-029 (Threshold)
   - TASK-P5-030 → TASK-P5-033 (Comfortable)
3. TASK-P5-034 → TASK-P5-039 (Aggregation, requires all above)
4. TASK-P5-040 → TASK-P5-044 (Final testing)

**Parallel opportunities:**
- All individual metric calculation modules (5.2 through 5.7)
- Tests can be written alongside each module

### Agent Context Requirements

Each agent session needs:
- This phase plan document
- Master plan section 10.10 (Metrics JSON Schema)
- ERA5-Land data format from Phase 3

### Validation Checkpoints

- **After Phase 5.1**: Config imports without error
- **After Phase 5.2-5.7**: Each metric module passes unit tests
- **After Phase 5.8**: JSON export validates against schema
- **After Phase 5.9**: `pytest analysis/metrics/tests/ -v` passes

## 9. Related Specifications / Further Reading

- [WMO Climate Normals 1961-1990](https://community.wmo.int/en/activity-areas/climate/wmo-climatological-normals)
- [German Weather Service Threshold Definitions](https://www.dwd.de/DE/leistungen/klimadatendeutschland/vielj_mittelwerte.html)
- [SciPy linregress Documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.linregress.html)
- Master Plan: `plan/botox/era5-germany-climate-visualization-1.md`
- Frontend Schema: Master Plan Section 10.10

## 10. Code Reference

### 10.1 Metrics Configuration

**File**: `analysis/metrics/config.py`

```python
#!/usr/bin/env python3
"""
Metrics calculation configuration.

Defines thresholds, reference periods, and calculation parameters
for all climate metrics.
"""

# Reference period for anomaly calculations (WMO standard)
REFERENCE_PERIOD = {
    'start_year': 1961,
    'end_year': 1990,
}

# Warming rate calculation period
WARMING_RATE_PERIOD = {
    'start_year': 1995,
    'end_year': 2025,
}

# Five-year anomaly calculation period
FIVE_YEAR_ANOMALY_PERIOD = {
    'start_year': 2021,
    'end_year': 2025,
}

# Temperature thresholds (DWD standards)
# Note: 32°C is NOT a DWD standard - excluded per ALT-007
# Note: 25°C (Sommertag) is not used in any current metric or plot - omitted to avoid dead code
THRESHOLDS = {
    'hot_day': 30.0,           # Tmax >= 30°C (Heißer Tag)
    'tropical_night': 20.0,     # Tmin >= 20°C (Tropennacht)
    'extreme_heat_day': 35.0,   # Tmax >= 35°C (vegetation/health damage)
    'frost_day': 0.0,           # Tmin < 0°C (Frosttag)
    'ice_day': 0.0,             # Tmax <= 0°C (Eistag)
}

# Comfortable temperature range (°C)
COMFORTABLE_RANGE = {
    'min': 15.0,
    'max': 25.0,
}

# Season definitions (meteorological seasons)
SEASONS = {
    'winter': [12, 1, 2],    # DJF
    'spring': [3, 4, 5],     # MAM
    'summer': [6, 7, 8],     # JJA
    'fall': [9, 10, 11],     # SON (Herbst)
}

# For display: German season names
SEASON_NAMES_DE = {
    'winter': 'Winter',
    'spring': 'Frühling',
    'summer': 'Sommer',
    'fall': 'Herbst',
}

# Minimum years required for valid trends
MIN_YEARS_FOR_TREND = 10

# Significance threshold for R² value
MIN_R_SQUARED = 0.3


def get_season(month: int) -> str:
    """Get season name for a month.
    
    Args:
        month: Month number (1-12)
        
    Returns:
        Season name ('winter', 'spring', 'summer', 'fall')
    """
    for season, months in SEASONS.items():
        if month in months:
            return season
    raise ValueError(f"Invalid month: {month}")


def validate_year_range(start_year: int, end_year: int) -> bool:
    """Validate a year range for calculations.
    
    Args:
        start_year: Start year
        end_year: End year
        
    Returns:
        True if valid
        
    Raises:
        ValueError: If range is invalid
    """
    if start_year > end_year:
        raise ValueError(f"Start year {start_year} > end year {end_year}")
    if end_year - start_year < MIN_YEARS_FOR_TREND:
        raise ValueError(
            f"Year range too short ({end_year - start_year} years). "
            f"Need at least {MIN_YEARS_FOR_TREND} years."
        )
    return True
```

### 10.2 Data Types

**File**: `analysis/metrics/types.py`

```python
#!/usr/bin/env python3
"""
Type definitions for metrics data structures.

Matches the frontend LocationMetrics schema from master plan Section 10.10.
"""

from typing import TypedDict, Literal


class FiveYearAnomaly(TypedDict):
    """Five-year temperature anomaly metric (2021-2025 vs 1961-1990)."""
    value: float           # °C deviation from reference
    periodStart: int       # Period start (e.g., 2021)
    periodEnd: int         # Period end (e.g., 2025)
    referenceStart: int    # Reference period start (1961)
    referenceEnd: int      # Reference period end (1990)


class WarmingRate(TypedDict):
    """Linear warming trend metric."""
    value: float           # °C per decade
    startYear: int         # Trend calculation start (1995)
    endYear: int           # Trend calculation end (2025)
    confidence: float      # R² value from linear regression (0-1)


class RecordDays(TypedDict):
    """Record-breaking days metric."""
    total: int             # Total records broken
    hot: int               # Hot temperature records
    cold: int              # Cold temperature records
    year: int              # Year of count


class WinterWarming(TypedDict):
    """Winter (DJF) temperature anomaly."""
    value: float           # DJF anomaly (°C)
    periodStart: int       # Period start (2021)
    periodEnd: int         # Period end (2025)
    referenceStart: int    # Reference period start (1961)
    referenceEnd: int      # Reference period end (1990)


class SnowDaysLost(TypedDict):
    """Snow days lost vs reference period."""
    value: int             # Difference (negative = days lost)
    currentAverage: float  # 2021-2025 average snow days
    referenceAverage: float # 1961-1990 average snow days
    periodStart: int       # Current period start
    periodEnd: int         # Current period end


class ComfortableDays(TypedDict):
    """Comfortable temperature days (15-25°C mean)."""
    count: int             # Days with 15-25°C mean
    average: float         # Average per year (2021-2025)


class SeasonalWarming(TypedDict):
    """Seasonal temperature anomalies (DJF, MAM, JJA, SON)."""
    winter: float          # DJF anomaly (°C)
    spring: float          # MAM anomaly (°C)
    summer: float          # JJA anomaly (°C)
    fall: float            # SON anomaly (°C)
    fastestSeason: str     # 'winter' | 'spring' | 'summer' | 'fall'
    periodStart: int
    periodEnd: int
    referenceStart: int
    referenceEnd: int


class ThresholdDays(TypedDict):
    """Thermal threshold day counts for a given year."""
    hotDays: int           # Tmax >= 30°C (Heißer Tag)
    tropicalNights: int    # Tmin >= 20°C (Tropennacht)
    iceDays: int           # Tmax <= 0°C (Eistag)
    frostDays: int         # Tmin < 0°C (Frosttag)
    year: int


class LocationMetrics(TypedDict):
    """Complete metrics for a location (city or country)."""
    calculatedAt: str                   # ISO timestamp
    fiveYearAnomaly: FiveYearAnomaly
    warmingRate: WarmingRate
    recordDays: RecordDays
    winterWarming: WinterWarming
    seasonalWarming: SeasonalWarming
    thresholdDays: ThresholdDays
    snowDaysLost: SnowDaysLost
    comfortableDays: ComfortableDays


class MetricsFile(TypedDict):
    """Root structure for metrics JSON file."""
    version: str           # Schema version
    generatedAt: str       # ISO timestamp
    source: Literal['era5', 'era5-land']
    coverage: dict         # bounds, gridResolution
    data: LocationMetrics
```

### 10.3 Five-Year Anomaly Calculation

**File**: `analysis/metrics/calculate_five_year_anomaly.py`

```python
#!/usr/bin/env python3
"""
Calculate five-year temperature anomaly versus reference period.

Computes the mean difference between 2021-2025 mean temperature
and the 1961-1990 climatological mean.
"""

import logging
from pathlib import Path

import numpy as np
import xarray as xr

from .config import REFERENCE_PERIOD, FIVE_YEAR_ANOMALY_PERIOD
from .types import FiveYearAnomaly

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def calculate_five_year_mean(ds: xr.Dataset, variable: str = 't2m') -> np.ndarray:
    """Calculate five-year (2021-2025) mean temperature.
    
    Args:
        ds: Dataset with temperature data
        variable: Temperature variable name
        
    Returns:
        2D array of five-year mean temperatures
    """
    start_year = FIVE_YEAR_ANOMALY_PERIOD['start_year']
    end_year = FIVE_YEAR_ANOMALY_PERIOD['end_year']
    
    # Select years
    mask = (ds['time'].dt.year >= start_year) & (ds['time'].dt.year <= end_year)
    period_data = ds[variable].where(mask, drop=True)
    
    if len(period_data.time) == 0:
        raise ValueError(f"No data for period {start_year}-{end_year}")
    
    # Calculate mean
    period_mean = period_data.mean(dim='time').values
    
    return period_mean


def calculate_reference_climatology(
    ds: xr.Dataset,
    variable: str = 't2m',
) -> np.ndarray:
    """Calculate reference period (1961-1990) climatological mean.
    
    Args:
        ds: Dataset with historical temperature data
        variable: Temperature variable name
        
    Returns:
        2D array of climatological mean temperatures
    """
    start_year = REFERENCE_PERIOD['start_year']
    end_year = REFERENCE_PERIOD['end_year']
    
    mask = (ds['time'].dt.year >= start_year) & (ds['time'].dt.year <= end_year)
    ref_data = ds[variable].where(mask, drop=True)
    
    if len(ref_data.time) == 0:
        raise ValueError(f"No data for reference period {start_year}-{end_year}")
    
    # Calculate climatological mean
    climatology = ref_data.mean(dim='time').values
    
    logger.info(f"Reference period mean: {np.nanmean(climatology):.2f}°C")
    
    return climatology


def calculate_five_year_anomaly(
    ds: xr.Dataset,
    climatology: np.ndarray = None,
    variable: str = 't2m',
) -> FiveYearAnomaly:
    """Calculate five-year temperature anomaly.
    
    Args:
        ds: Dataset with temperature data
        climatology: Pre-computed reference climatology (optional)
        variable: Temperature variable name
        
    Returns:
        FiveYearAnomaly dictionary
    """
    # Calculate five-year mean
    five_year_mean = calculate_five_year_mean(ds, variable)
    
    # Get or calculate climatology
    if climatology is None:
        climatology = calculate_reference_climatology(ds, variable)
    
    # Calculate anomaly (spatial average)
    anomaly_grid = five_year_mean - climatology
    anomaly_value = float(np.nanmean(anomaly_grid))
    
    logger.info(f"Five-year anomaly ({FIVE_YEAR_ANOMALY_PERIOD['start_year']}-{FIVE_YEAR_ANOMALY_PERIOD['end_year']}): {anomaly_value:+.2f}°C")
    
    return FiveYearAnomaly(
        value=round(anomaly_value, 2),
        periodStart=FIVE_YEAR_ANOMALY_PERIOD['start_year'],
        periodEnd=FIVE_YEAR_ANOMALY_PERIOD['end_year'],
        referenceStart=REFERENCE_PERIOD['start_year'],
        referenceEnd=REFERENCE_PERIOD['end_year'],
    )


def calculate_annual_anomaly_grid(
    ds: xr.Dataset,
    year: int,
    climatology: np.ndarray = None,
    variable: str = 't2m',
) -> xr.DataArray:
    """Calculate annual anomaly at each grid point.
    
    Args:
        ds: Dataset with temperature data
        year: Year to calculate
        climatology: Pre-computed reference climatology
        variable: Temperature variable name
        
    Returns:
        DataArray with per-grid-cell anomalies
    """
    annual_mean = calculate_annual_mean(ds, year, variable)
    
    if climatology is None:
        climatology = calculate_reference_climatology(ds, variable)
    
    anomaly_grid = annual_mean - climatology
    
    # Create DataArray
    result = xr.DataArray(
        anomaly_grid,
        dims=['latitude', 'longitude'],
        coords={
            'latitude': ds['latitude'].values,
            'longitude': ds['longitude'].values,
        },
        attrs={
            'units': '°C',
            'long_name': f'Annual temperature anomaly {year} vs {REFERENCE_PERIOD["start_year"]}-{REFERENCE_PERIOD["end_year"]}',
        }
    )
    
    return result


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Calculate annual temperature anomaly')
    parser.add_argument('input_file', help='Input NetCDF with temperature data')
    parser.add_argument('--year', type=int, required=True, help='Year to calculate')
    args = parser.parse_args()
    
    ds = xr.open_dataset(args.input_file)
    result = calculate_annual_anomaly(ds, args.year)
    
    print(f"Annual Anomaly for {result['year']}: {result['value']:+.2f}°C")
    print(f"Reference period: {result['referenceStart']}-{result['referenceEnd']}")
```

### 10.4 Warming Rate Calculation

**File**: `analysis/metrics/calculate_warming_rate.py`

```python
#!/usr/bin/env python3
"""
Calculate linear warming rate (trend) over time.

Uses linear regression to estimate temperature increase per decade.
"""

import logging
from pathlib import Path
from typing import List, Tuple

import numpy as np
from scipy import stats
import xarray as xr

from .config import WARMING_RATE_PERIOD, MIN_YEARS_FOR_TREND, MIN_R_SQUARED
from .types import WarmingRate

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def calculate_annual_means(
    ds: xr.Dataset,
    start_year: int,
    end_year: int,
    variable: str = 't2m',
) -> Tuple[List[int], List[float]]:
    """Calculate annual mean temperatures for a range of years.
    
    Args:
        ds: Dataset with temperature data
        start_year: Start year (inclusive)
        end_year: End year (inclusive)
        variable: Temperature variable name
        
    Returns:
        Tuple of (years list, mean temperatures list)
    """
    years = []
    means = []
    
    for year in range(start_year, end_year + 1):
        try:
            year_data = ds[variable].sel(time=ds['time'].dt.year == year)
            if len(year_data.time) > 0:
                annual_mean = float(np.nanmean(year_data.mean(dim='time').values))
                years.append(year)
                means.append(annual_mean)
        except Exception as e:
            logger.warning(f"Could not calculate mean for {year}: {e}")
    
    return years, means


def calculate_warming_rate(
    ds: xr.Dataset,
    start_year: int = None,
    end_year: int = None,
    variable: str = 't2m',
) -> WarmingRate:
    """Calculate linear warming rate using linear regression.
    
    Args:
        ds: Dataset with temperature data
        start_year: Start year for trend (default: from config)
        end_year: End year for trend (default: from config)
        variable: Temperature variable name
        
    Returns:
        WarmingRate dictionary
    """
    start_year = start_year or WARMING_RATE_PERIOD['start_year']
    end_year = end_year or WARMING_RATE_PERIOD['end_year']
    
    # Get annual means
    years, means = calculate_annual_means(ds, start_year, end_year, variable)
    
    if len(years) < MIN_YEARS_FOR_TREND:
        raise ValueError(
            f"Insufficient data: only {len(years)} years available, "
            f"need at least {MIN_YEARS_FOR_TREND}"
        )
    
    # Convert to arrays
    x = np.array(years)
    y = np.array(means)
    
    # Perform linear regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    
    # Convert slope from °C/year to °C/decade
    warming_rate = slope * 10
    r_squared = r_value ** 2
    
    logger.info(
        f"Warming rate {start_year}-{end_year}: {warming_rate:+.2f}°C/decade "
        f"(R²={r_squared:.2f})"
    )
    
    if r_squared < MIN_R_SQUARED:
        logger.warning(
            f"Low R² value ({r_squared:.2f}). "
            f"Trend may not be statistically significant."
        )
    
    return WarmingRate(
        value=round(warming_rate, 2),
        startYear=start_year,
        endYear=end_year,
        confidence=round(r_squared, 3),
    )


def calculate_warming_rate_grid(
    ds: xr.Dataset,
    start_year: int = None,
    end_year: int = None,
    variable: str = 't2m',
) -> Tuple[xr.DataArray, xr.DataArray]:
    """Calculate warming rate at each grid point.
    
    Args:
        ds: Dataset with temperature data
        start_year: Start year for trend
        end_year: End year for trend
        variable: Temperature variable name
        
    Returns:
        Tuple of (warming_rate DataArray, r_squared DataArray)
    """
    start_year = start_year or WARMING_RATE_PERIOD['start_year']
    end_year = end_year or WARMING_RATE_PERIOD['end_year']
    
    # Get dimensions
    lats = ds['latitude'].values
    lons = ds['longitude'].values
    
    # Prepare output arrays
    warming_rate = np.full((len(lats), len(lons)), np.nan)
    r_squared = np.full((len(lats), len(lons)), np.nan)
    
    # Get annual means per grid cell
    years = list(range(start_year, end_year + 1))
    annual_means = []
    
    for year in years:
        try:
            year_data = ds[variable].sel(time=ds['time'].dt.year == year)
            if len(year_data.time) > 0:
                annual_mean = year_data.mean(dim='time').values
                annual_means.append(annual_mean)
        except:
            annual_means.append(np.full((len(lats), len(lons)), np.nan))
    
    annual_means = np.array(annual_means)
    x = np.array(years)
    
    # Calculate regression for each grid cell
    for i in range(len(lats)):
        for j in range(len(lons)):
            y = annual_means[:, i, j]
            valid_mask = ~np.isnan(y)
            
            if valid_mask.sum() >= MIN_YEARS_FOR_TREND:
                slope, _, r_value, _, _ = stats.linregress(x[valid_mask], y[valid_mask])
                warming_rate[i, j] = slope * 10  # °C/decade
                r_squared[i, j] = r_value ** 2
    
    # Create DataArrays
    rate_da = xr.DataArray(
        warming_rate,
        dims=['latitude', 'longitude'],
        coords={'latitude': lats, 'longitude': lons},
        attrs={'units': '°C/decade', 'period': f'{start_year}-{end_year}'}
    )
    
    rsq_da = xr.DataArray(
        r_squared,
        dims=['latitude', 'longitude'],
        coords={'latitude': lats, 'longitude': lons},
        attrs={'units': '-', 'long_name': 'R-squared of linear fit'}
    )
    
    return rate_da, rsq_da


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Calculate warming rate')
    parser.add_argument('input_file', help='Input NetCDF')
    parser.add_argument('--start-year', type=int, default=1991)
    parser.add_argument('--end-year', type=int, default=2024)
    args = parser.parse_args()
    
    ds = xr.open_dataset(args.input_file)
    result = calculate_warming_rate(ds, args.start_year, args.end_year)
    
    print(f"Warming Rate: {result['value']:+.2f}°C/decade")
    print(f"Period: {result['startYear']}-{result['endYear']}")
    print(f"R²: {result['confidence']:.3f}")
```

### 10.5 Threshold Days Calculation

**File**: `analysis/metrics/calculate_threshold_days.py`

```python
#!/usr/bin/env python3
"""
Calculate thermal threshold day counts.

Counts days exceeding or falling below temperature thresholds:
- Hot days (Tmax >= 30°C)
- Tropical nights (Tmin ≥ 20°C)
- Ice days (Tmax <= 0°C)
- Frost days (Tmin < 0°C)
"""

import logging
from pathlib import Path

import numpy as np
import xarray as xr

from .config import THRESHOLDS
from .types import ThresholdDays

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def count_hot_days(tmax: np.ndarray, threshold: float = None) -> int:
    """Count days with Tmax >= threshold.
    
    Args:
        tmax: Array of daily maximum temperatures
        threshold: Temperature threshold (default: 30°C)
        
    Returns:
        Number of hot days
    """
    threshold = threshold or THRESHOLDS['hot_day']
    return int(np.sum(tmax >= threshold))


def count_tropical_nights(tmin: np.ndarray, threshold: float = None) -> int:
    """Count nights with Tmin > threshold.
    
    Note: Threshold is > (not >=) for tropical nights.
    
    Args:
        tmin: Array of daily minimum temperatures
        threshold: Temperature threshold (default: 20°C)
        
    Returns:
        Number of tropical nights
    """
    threshold = threshold or THRESHOLDS['tropical_night']
    return int(np.sum(tmin > threshold))


def count_ice_days(tmax: np.ndarray, threshold: float = None) -> int:
    """Count days with Tmax <= threshold.
    
    Args:
        tmax: Array of daily maximum temperatures
        threshold: Temperature threshold (default: 0°C)
        
    Returns:
        Number of ice days
    """
    threshold = threshold or THRESHOLDS['ice_day']
    return int(np.sum(tmax <= threshold))


def count_frost_days(tmin: np.ndarray, threshold: float = None) -> int:
    """Count days with Tmin < threshold.
    
    Note: Threshold is < (not <=) for frost days.
    
    Args:
        tmin: Array of daily minimum temperatures
        threshold: Temperature threshold (default: 0°C)
        
    Returns:
        Number of frost days
    """
    threshold = threshold or THRESHOLDS['frost_day']
    return int(np.sum(tmin < threshold))


def calculate_threshold_days(
    ds: xr.Dataset,
    year: int,
    tmax_var: str = 'tmax',
    tmin_var: str = 'tmin',
) -> ThresholdDays:
    """Calculate all threshold day counts for a year.
    
    Args:
        ds: Dataset with daily temperature data
        year: Year to calculate
        tmax_var: Daily maximum temperature variable name
        tmin_var: Daily minimum temperature variable name
        
    Returns:
        ThresholdDays dictionary
    """
    # Select year
    year_mask = ds['time'].dt.year == year
    
    # Get spatial mean for country-level
    tmax = ds[tmax_var].where(year_mask, drop=True).mean(dim=['latitude', 'longitude']).values
    tmin = ds[tmin_var].where(year_mask, drop=True).mean(dim=['latitude', 'longitude']).values
    
    # Remove NaN
    tmax = tmax[~np.isnan(tmax)]
    tmin = tmin[~np.isnan(tmin)]
    
    hot_days = count_hot_days(tmax)
    tropical_nights = count_tropical_nights(tmin)
    ice_days = count_ice_days(tmax)
    frost_days = count_frost_days(tmin)
    
    logger.info(
        f"Threshold days for {year}: "
        f"hot={hot_days}, tropical_nights={tropical_nights}, "
        f"ice={ice_days}, frost={frost_days}"
    )
    
    return ThresholdDays(
        hotDays=hot_days,
        tropicalNights=tropical_nights,
        iceDays=ice_days,
        frostDays=frost_days,
        year=year,
    )


def calculate_threshold_days_grid(
    ds: xr.Dataset,
    year: int,
    tmax_var: str = 'tmax',
    tmin_var: str = 'tmin',
) -> dict:
    """Calculate threshold days at each grid point.
    
    Args:
        ds: Dataset with daily temperature data
        year: Year to calculate
        tmax_var, tmin_var: Variable names
        
    Returns:
        Dictionary of DataArrays for each threshold type
    """
    year_mask = ds['time'].dt.year == year
    
    tmax = ds[tmax_var].where(year_mask, drop=True)
    tmin = ds[tmin_var].where(year_mask, drop=True)
    
    # Count along time dimension
    hot_days = (tmax >= THRESHOLDS['hot_day']).sum(dim='time')
    tropical_nights = (tmin > THRESHOLDS['tropical_night']).sum(dim='time')
    ice_days = (tmax <= THRESHOLDS['ice_day']).sum(dim='time')
    frost_days = (tmin < THRESHOLDS['frost_day']).sum(dim='time')
    
    return {
        'hot_days': hot_days,
        'tropical_nights': tropical_nights,
        'ice_days': ice_days,
        'frost_days': frost_days,
    }


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Calculate threshold days')
    parser.add_argument('input_file', help='Input NetCDF with daily Tmax/Tmin')
    parser.add_argument('--year', type=int, required=True)
    args = parser.parse_args()
    
    ds = xr.open_dataset(args.input_file)
    result = calculate_threshold_days(ds, args.year)
    
    print(f"Threshold Days for {result['year']}:")
    print(f"  Hot days (>=30°C): {result['hotDays']}")
    print(f"  Tropical nights (>20°C): {result['tropicalNights']}")
    print(f"  Ice days (<=0°C): {result['iceDays']}")
    print(f"  Frost days (<0°C): {result['frostDays']}")
```

### 10.6 Aggregation Module

**File**: `analysis/metrics/aggregate_metrics.py`

```python
#!/usr/bin/env python3
"""
Aggregate grid-level metrics to city and country level.

Provides functions to map city coordinates to nearest grid cells
and aggregate metrics spatially.
"""

import logging
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import xarray as xr

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_city_list(csv_path: Path) -> pd.DataFrame:
    """Load city list from CSV.
    
    Expected columns: name, latitude, longitude, population
    
    Args:
        csv_path: Path to city CSV file
        
    Returns:
        DataFrame with city information
    """
    df = pd.read_csv(csv_path)
    
    # Ensure required columns
    required = ['name', 'latitude', 'longitude']
    for col in required:
        if col not in df.columns:
            # Try common alternatives
            alternatives = {
                'name': ['city', 'city_name', 'NAME'],
                'latitude': ['lat', 'LAT'],
                'longitude': ['lon', 'lng', 'LON'],
            }
            for alt in alternatives.get(col, []):
                if alt in df.columns:
                    df = df.rename(columns={alt: col})
                    break
    
    logger.info(f"Loaded {len(df)} cities from {csv_path}")
    return df


def find_nearest_grid_cell(
    lat: float,
    lon: float,
    grid_lats: np.ndarray,
    grid_lons: np.ndarray,
) -> Tuple[int, int]:
    """Find nearest grid cell for a coordinate.
    
    Args:
        lat, lon: Target coordinates
        grid_lats: Array of grid latitudes
        grid_lons: Array of grid longitudes
        
    Returns:
        Tuple of (lat_index, lon_index)
    """
    lat_idx = np.argmin(np.abs(grid_lats - lat))
    lon_idx = np.argmin(np.abs(grid_lons - lon))
    return int(lat_idx), int(lon_idx)


def aggregate_to_cities(
    grid_data: xr.DataArray,
    cities: pd.DataFrame,
) -> Dict[str, float]:
    """Aggregate grid data to city locations.
    
    Uses nearest-neighbor interpolation.
    
    Args:
        grid_data: DataArray with dims (latitude, longitude)
        cities: DataFrame with city coordinates
        
    Returns:
        Dictionary mapping city name to value
    """
    grid_lats = grid_data['latitude'].values
    grid_lons = grid_data['longitude'].values
    data = grid_data.values
    
    results = {}
    
    for _, city in cities.iterrows():
        lat_idx, lon_idx = find_nearest_grid_cell(
            city['latitude'], city['longitude'],
            grid_lats, grid_lons
        )
        
        value = float(data[lat_idx, lon_idx])
        
        if not np.isnan(value):
            results[city['name']] = round(value, 2)
        else:
            logger.warning(f"No data for city {city['name']}")
    
    return results


def aggregate_to_country(
    grid_data: xr.DataArray,
    weights: xr.DataArray = None,
) -> float:
    """Aggregate grid data to country-level single value.
    
    Args:
        grid_data: DataArray with dims (latitude, longitude)
        weights: Optional area weights for proper averaging
        
    Returns:
        Weighted mean value
    """
    data = grid_data.values
    
    if weights is not None:
        # Weighted average
        weight_data = weights.values
        valid_mask = ~np.isnan(data) & ~np.isnan(weight_data)
        weighted_mean = np.average(data[valid_mask], weights=weight_data[valid_mask])
    else:
        # Simple mean
        weighted_mean = np.nanmean(data)
    
    return float(round(weighted_mean, 2))


def create_area_weights(
    lats: np.ndarray,
    lons: np.ndarray,
) -> xr.DataArray:
    """Create area weights based on latitude (cos weighting).
    
    Grid cells at higher latitudes represent smaller areas.
    
    Args:
        lats: Latitude array
        lons: Longitude array
        
    Returns:
        DataArray with area weights
    """
    # Cosine of latitude for area correction
    weights = np.cos(np.radians(lats))
    
    # Broadcast to 2D
    weights_2d = np.broadcast_to(weights[:, np.newaxis], (len(lats), len(lons)))
    
    return xr.DataArray(
        weights_2d,
        dims=['latitude', 'longitude'],
        coords={'latitude': lats, 'longitude': lons},
    )


def correlate_cities_to_grid(
    cities: pd.DataFrame,
    grid_lats: np.ndarray,
    grid_lons: np.ndarray,
) -> pd.DataFrame:
    """Map all cities to their nearest grid cells.
    
    Adds 'grid_lat_idx', 'grid_lon_idx', 'grid_lat', 'grid_lon' columns.
    
    Args:
        cities: DataFrame with city coordinates
        grid_lats: Array of grid latitudes
        grid_lons: Array of grid longitudes
        
    Returns:
        DataFrame with grid mapping columns added
    """
    cities = cities.copy()
    
    lat_idxs = []
    lon_idxs = []
    grid_lats_mapped = []
    grid_lons_mapped = []
    
    for _, city in cities.iterrows():
        lat_idx, lon_idx = find_nearest_grid_cell(
            city['latitude'], city['longitude'],
            grid_lats, grid_lons
        )
        lat_idxs.append(lat_idx)
        lon_idxs.append(lon_idx)
        grid_lats_mapped.append(grid_lats[lat_idx])
        grid_lons_mapped.append(grid_lons[lon_idx])
    
    cities['grid_lat_idx'] = lat_idxs
    cities['grid_lon_idx'] = lon_idxs
    cities['grid_lat'] = grid_lats_mapped
    cities['grid_lon'] = grid_lons_mapped
    
    return cities


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Aggregate metrics to cities')
    parser.add_argument('grid_file', help='NetCDF with grid data')
    parser.add_argument('--cities', default='frontend/public/german_cities_p5000.csv',
                        help='Path to city CSV')
    parser.add_argument('--variable', default='anomaly', help='Variable to aggregate')
    args = parser.parse_args()
    
    ds = xr.open_dataset(args.grid_file)
    cities = load_city_list(Path(args.cities))
    
    results = aggregate_to_cities(ds[args.variable], cities)
    
    print(f"\nCity values ({args.variable}):")
    for city, value in sorted(results.items())[:10]:
        print(f"  {city}: {value}")
```

### 10.7 JSON Export

**File**: `analysis/metrics/export_metrics.py`

```python
#!/usr/bin/env python3
"""
Export metrics to JSON format for frontend consumption.

Outputs conform to the LocationMetrics schema defined in types.py
and master plan Section 10.10.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict

from .types import LocationMetrics, MetricsFile

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def export_metrics_json(
    metrics: LocationMetrics,
    output_path: Path,
    bounds: dict = None,
    source: str = 'era5-land',
) -> Path:
    """Export metrics to JSON file.
    
    Args:
        metrics: LocationMetrics dictionary
        output_path: Path for output JSON file
        bounds: Geographic bounds dictionary
        source: Data source identifier
        
    Returns:
        Path to created JSON file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Build complete file structure
    metrics_file: MetricsFile = {
        'version': '1.0',
        'generatedAt': datetime.utcnow().isoformat() + 'Z',
        'source': source,
        'coverage': {
            'bounds': bounds or {
                'north': 55.1,
                'south': 47.2,
                'west': 5.8,
                'east': 15.1,
            },
            'gridResolution': '~1km',
        },
        'data': metrics,
    }
    
    # Write JSON with nice formatting
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(metrics_file, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Exported metrics to {output_path}")
    return output_path


def export_all_tile_metrics(
    tile_metrics: Dict[str, LocationMetrics],
    output_dir: Path,
    source: str = 'era5-land',
) -> Dict[str, Path]:
    """Export metrics for all tiles (grid cells).
    
    Args:
        tile_metrics: Dictionary mapping tile_id (grid_i_grid_j) to metrics
        output_dir: Directory for output files
        source: Data source identifier
        
    Returns:
        Dictionary mapping tile_id to output path
    """
    output_dir = Path(output_dir) / 'tiles'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    paths = {}
    
    for tile_id, metrics in tile_metrics.items():
        # tile_id format: "{grid_i}_{grid_j}"
        output_path = output_dir / f"{tile_id}.json"
        
        paths[tile_id] = export_metrics_json(metrics, output_path, source=source)
    
    logger.info(f"Exported metrics for {len(paths)} tiles to {output_dir}")
    return paths


def export_germany_metrics(
    metrics: LocationMetrics,
    output_dir: Path,
    source: str = 'era5-land',
) -> Path:
    """Export country-level metrics for Germany.
    
    Args:
        metrics: Germany-aggregated LocationMetrics
        output_dir: Output directory
        source: Data source identifier
        
    Returns:
        Path to germany.json
    """
    output_path = Path(output_dir) / 'germany.json'
    return export_metrics_json(metrics, output_path, source=source)


def validate_metrics_schema(data: dict) -> bool:
    """Validate that metrics dictionary conforms to schema.
    
    Args:
        data: Metrics dictionary to validate
        
    Returns:
        True if valid
        
    Raises:
        ValueError: If schema validation fails
    """
    required_keys = [
        'fiveYearAnomaly',
        'warmingRate',
        'recordDays',
        'winterWarming',
        'seasonalWarming',
        'thresholdDays',
        'snowDaysLost',
        'comfortableDays',
    ]
    
    for key in required_keys:
        if key not in data:
            raise ValueError(f"Missing required key: {key}")
    
    # Validate nested structures
    if 'value' not in data['fiveYearAnomaly']:
        raise ValueError("fiveYearAnomaly missing 'value'")
    if 'confidence' not in data['warmingRate']:
        raise ValueError("warmingRate missing 'confidence'"))
    
    return True


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Export metrics to JSON')
    parser.add_argument('--output-dir', default='./data/metrics', help='Output directory')
    args = parser.parse_args()
    
    # Example: Create sample metrics
    sample_metrics: LocationMetrics = {
        'calculatedAt': datetime.utcnow().isoformat() + 'Z',
        'fiveYearAnomaly': {
            'value': 2.3,
            'periodStart': 2021,
            'periodEnd': 2025,
            'referenceStart': 1961,
            'referenceEnd': 1990,
        },
        'warmingRate': {
            'value': 0.45,
            'startYear': 1995,
            'endYear': 2025,
            'confidence': 0.85,
        },
        'recordDays': {
            'total': 18,
            'hot': 16,
            'cold': 2,
            'year': 2025,
        },
        'winterWarming': {
            'value': 2.8,
            'periodStart': 2021,
            'periodEnd': 2025,
            'referenceStart': 1961,
            'referenceEnd': 1990,
        },
        'seasonalWarming': {
            'winter': 2.8,
            'spring': 2.1,
            'summer': 1.9,
            'fall': 2.4,
            'fastestSeason': 'winter',
            'periodStart': 2021,
            'periodEnd': 2025,
            'referenceStart': 1961,
            'referenceEnd': 1990,
        },
        'thresholdDays': {
            'hotDays': 15,
            'tropicalNights': 8,
            'iceDays': 4,
            'frostDays': 52,
            'year': 2025,
        },
        'snowDaysLost': {
            'value': -18,
            'currentAverage': 12.0,
            'referenceAverage': 30.0,
            'periodStart': 2021,
            'periodEnd': 2025,
        },
        'comfortableDays': {
            'count': 95,
            'average': 93.0,
        },
    }
    
    path = export_germany_metrics(sample_metrics, Path(args.output_dir))
    print(f"Exported sample metrics to {path}")
```

### 10.8 Test Examples

**File**: `analysis/metrics/tests/test_threshold_days.py`

```python
#!/usr/bin/env python3
"""Tests for threshold day calculations."""

import pytest
import numpy as np
from analysis.metrics.calculate_threshold_days import (
    count_hot_days,
    count_tropical_nights,
    count_ice_days,
    count_frost_days,
)


class TestHotDays:
    """Tests for hot day counting."""
    
    def test_exact_threshold_counts(self):
        """Temperature exactly at threshold counts as hot day."""
        tmax = np.array([29.9, 30.0, 30.1])
        assert count_hot_days(tmax, threshold=30.0) == 2  # 30.0 and 30.1
    
    def test_all_above(self):
        """All days above threshold."""
        tmax = np.array([31, 32, 33, 34, 35])
        assert count_hot_days(tmax) == 5
    
    def test_none_above(self):
        """No days above threshold."""
        tmax = np.array([20, 22, 25, 28, 29])
        assert count_hot_days(tmax) == 0
    
    def test_handles_nan(self):
        """NaN values are handled correctly."""
        tmax = np.array([31, np.nan, 32, np.nan, 29])
        # NaN comparisons return False
        assert count_hot_days(tmax) == 2


class TestTropicalNights:
    """Tests for tropical night counting."""
    
    def test_exact_threshold_excluded(self):
        """Temperature exactly at 20°C does NOT count (>20, not >=20)."""
        tmin = np.array([19.9, 20.0, 20.1])
        assert count_tropical_nights(tmin, threshold=20.0) == 1  # Only 20.1
    
    def test_typical_summer_nights(self):
        """Count tropical nights in summer data."""
        tmin = np.array([18, 19, 21, 22, 23, 19, 17])
        assert count_tropical_nights(tmin) == 3


class TestIceDays:
    """Tests for ice day counting."""
    
    def test_exact_threshold_counts(self):
        """Temperature exactly at 0°C counts as ice day."""
        tmax = np.array([-1, 0, 1])
        assert count_ice_days(tmax, threshold=0.0) == 2  # -1 and 0
    
    def test_freezing_period(self):
        """Count ice days in winter data."""
        tmax = np.array([-5, -3, -1, 0, 2, 1, -2])
        assert count_ice_days(tmax) == 5


class TestFrostDays:
    """Tests for frost day counting."""
    
    def test_exact_threshold_excluded(self):
        """Temperature exactly at 0°C does NOT count (<0, not <=0)."""
        tmin = np.array([-1, 0, 1])
        assert count_frost_days(tmin, threshold=0.0) == 1  # Only -1
    
    def test_winter_period(self):
        """Count frost days in winter data."""
        tmin = np.array([-10, -5, 0, 2, -1, 3, 1])
        assert count_frost_days(tmin) == 3
```

**File**: `analysis/metrics/tests/conftest.py`

```python
#!/usr/bin/env python3
"""Pytest fixtures for metrics tests."""

import pytest
import numpy as np
import xarray as xr
from datetime import datetime, timedelta


@pytest.fixture
def sample_temperature_dataset():
    """Create sample temperature dataset for testing.
    
    Contains daily data for 3 years with known patterns.
    """
    # Create time coordinate for 3 years
    start = datetime(2022, 1, 1)
    times = [start + timedelta(days=i) for i in range(365 * 3)]
    
    # Small grid
    lats = np.linspace(48, 52, 5)
    lons = np.linspace(8, 12, 5)
    
    # Generate synthetic temperature data
    # Base: 10°C with seasonal pattern (+/- 15°C)
    base_temp = 10
    seasonal = 15 * np.sin(np.linspace(0, 2*np.pi*3, len(times)))
    
    # Create 3D temperature array
    temps = np.zeros((len(times), len(lats), len(lons)))
    for i, t in enumerate(times):
        temps[i] = base_temp + seasonal[i] + np.random.uniform(-2, 2, (len(lats), len(lons)))
    
    ds = xr.Dataset(
        {
            't2m': (['time', 'latitude', 'longitude'], temps.astype(np.float32))
        },
        coords={
            'time': times,
            'latitude': lats,
            'longitude': lons,
        }
    )
    
    return ds


@pytest.fixture
def sample_daily_extremes_dataset():
    """Create dataset with daily Tmax/Tmin for threshold tests."""
    times = [datetime(2024, 1, 1) + timedelta(days=i) for i in range(365)]
    lats = np.linspace(48, 52, 5)
    lons = np.linspace(8, 12, 5)
    
    # Tmax: 0-35°C range with summer peak
    tmax_base = 17.5 + 17.5 * np.sin(np.linspace(-np.pi/2, 3*np.pi/2, 365))
    tmax = np.broadcast_to(tmax_base[:, np.newaxis, np.newaxis], (365, 5, 5))
    tmax = tmax + np.random.uniform(-3, 3, (365, 5, 5))
    
    # Tmin: typically 8-10°C below Tmax
    tmin = tmax - 8 + np.random.uniform(-2, 2, (365, 5, 5))
    
    ds = xr.Dataset(
        {
            'tmax': (['time', 'latitude', 'longitude'], tmax.astype(np.float32)),
            'tmin': (['time', 'latitude', 'longitude'], tmin.astype(np.float32)),
        },
        coords={
            'time': times,
            'latitude': lats,
            'longitude': lons,
        }
    )
    
    return ds


@pytest.fixture
def linear_trend_dataset():
    """Create dataset with known linear warming trend.
    
    Trend: 0.4°C/decade = 0.04°C/year
    """
    years = range(1991, 2025)
    temps = [10 + 0.04 * (y - 1991) for y in years]  # Perfect linear trend
    
    times = [datetime(y, 6, 15) for y in years]  # Mid-year
    lats = np.array([50.0])
    lons = np.array([10.0])
    
    ds = xr.Dataset(
        {
            't2m': (['time', 'latitude', 'longitude'], np.array(temps)[:, np.newaxis, np.newaxis])
        },
        coords={
            'time': times,
            'latitude': lats,
            'longitude': lons,
        }
    )
    
    return ds
```
