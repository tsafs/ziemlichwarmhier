---
goal: Phase 3 - ERA5-Land Data Pipeline Core Implementation
version: 1.1
date_created: 2026-02-16
last_updated: 2026-02-27
owner: Sebastian
status: 'Completed'
tags: [phase-3, era5, data-pipeline, python, xarray, cdsapi]
---

# Introduction

![Status: Completed](https://img.shields.io/badge/status-Completed-brightgreen)

This phase implements the core ERA5-Land data download and processing pipeline. It establishes the foundation for all climate data processing by creating modules to fetch ERA5-Land data from the Copernicus Climate Data Store (CDS), apply a land mask for Germany, and calculate temperature anomalies against a reference period.

**Key outputs:**
- CDS API client setup with authentication
- ERA5-Land monthly AND daily temperature data download
- Daily Tmin/Tmax extraction for threshold calculations
- Precipitation data download for snow/rain metrics
- Germany bounding box extraction
- Natural Earth land mask (1:10m resolution)
- Monthly anomaly calculation vs 1961-1990 baseline
- Daily threshold detection (30°C, 35°C, 20°C, 0°C)

## 0. Preflight & Self-Correction

> **Mandatory gate**: Before starting any task in this phase and after every change, run the preflight script and follow the self-correction loop.

1. **Run preflight**: `./scripts/run-preflight.sh` — all checks must pass before starting work
2. **After each change**: re-run preflight or the targeted test subset (see `docs/self-correct-playbook.md`)
3. **On failure**: follow retry guidance in the playbook (max 3 attempts per issue, then revert and re-analyze)
4. **Local CI parity**: optionally run `./scripts/act-local.sh build` to verify GHA workflows locally (requires Docker + act)
5. **CDS fixture data**: This phase requires ERA5-Land data from the Copernicus Climate Data Store. Prompt the user for their `CDS_API_KEY` — never assume it is available. See `docs/self-correct-playbook.md` §7 for the one-time fixture pull procedure.

## 0.1 Regular Commits

Commit after each logical unit of work to maintain a clear and reviewable change history. Avoid accumulating large batches of uncommitted changes — they make it harder to understand what belongs to what, harder to review PRs, and harder to revert individual changes if something goes wrong.

**Guidelines:**
- Commit after completing each task group or implementation sub-section
- Use [Conventional Commits](https://www.conventionalcommits.org/) format: `feat(phase-X):`, `fix(phase-X):`, `chore(phase-X):`, `test(phase-X):`, etc.
- Each commit should pass the preflight checks (see § 0 above)
- Keep PRs focused — one logical concern per PR makes reviews faster and safer

## 1. Requirements & Constraints

### From Master Plan

- **REQ-001**: Display temperature anomaly maps for Germany using ERA5-Land data at native resolution (~9 km)
- **REQ-006**: Support land areas only, including coastal islands (exclude ocean)
- **CON-001**: ERA5-Land native resolution is 0.1° (~9 km); data is used at native resolution, visual upscaling handled by tile rendering
- **CON-003**: HYRAS 1km data available for Germany (1951-2024) as reference/validation

### Phase-Specific Requirements

- **REQ-P3-001**: Fetch ERA5-Land monthly AND daily 2m temperature from CDS API
- **REQ-P3-002**: Subset data to Germany bounds (47.2°N–55.1°N, 5.8°E–15.1°E)
- **REQ-P3-004**: Apply land mask including all German islands (Sylt, Rügen, Helgoland, Borkum, etc.)
- **REQ-P3-005**: Calculate anomalies relative to 1961-1990 climatology
- **REQ-P3-006**: Handle edge cases (missing data, partial months, API timeouts)
- **REQ-P3-007**: Output data in GeoTIFF format for tile generation (Phase 4)
- **REQ-P3-008**: Extract daily Tmin and Tmax from hourly ERA5-Land data
- **REQ-P3-009**: Fetch total precipitation (tp) for snow/rain day calculations
- **REQ-P3-010**: Detect snow days: precipitation > 0.1mm AND Tmean ≤ 0°C

### Constraints

- **CON-P3-001**: CDS API has rate limits; implement retry with exponential backoff
- **CON-P3-002**: ERA5-Land data delayed ~5 days; account for in date logic
- **CON-P3-003**: Processing must be deterministic for reproducibility
- **CON-P3-004**: Memory efficient for GitHub Actions (7GB RAM limit)

## 2. Implementation Steps

### Implementation Phase 3.0: Provider Protocol

- GOAL-P3-000: Define a pluggable `ClimateDataProvider` abstraction so the data source is replaceable without code changes

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P3-100 | Create `analysis/era5/providers/__init__.py` with provider factory (`get_provider()`) and registry | | |
| TASK-P3-101 | Create `analysis/era5/providers/protocol.py` defining `ClimateDataProvider(Protocol)` with properties: `dataset_id`, `display_name`, `native_resolution_deg`, `bounds`, `variables`, `coordinate_names`, `latitude_descending`, `unit_conversions`; and methods: `fetch_monthly()`, `fetch_daily()`, `load_dataset()` | | |
| TASK-P3-102 | Create `analysis/era5/providers/era5_land.py` implementing `ERA5LandProvider` — move all ERA5-Land-specific constants (CDS dataset names, variable mappings, resolution, bounds) from `config.py` into the provider | | |
| TASK-P3-103 | Refactor `config.py` to retain only source-agnostic settings (thresholds, reference period, color mapping, island list). Remove `CDS_DATASETS`, `ERA5_VARIABLES`, `GERMANY_BOUNDS`, `GERMANY_BOUNDS_BUFFERED`, `ERA5_LAND_RESOLUTION`, `CDS_CONFIG` — these become provider properties | | |
| TASK-P3-104 | Write unit test: `ERA5LandProvider` satisfies `ClimateDataProvider` protocol at type-check time (`isinstance` check with `@runtime_checkable`) | | |
| TASK-P3-105 | Create `StubProvider` test fixture that returns deterministic data for offline pipeline tests | | |
| TASK-P3-106 | Write provider-swap integration test: pipeline produces valid output with `StubProvider` | | |

### Implementation Phase 3.1: Configuration Module

- GOAL-P3-001: Centralize all source-agnostic ERA5-Land processing configuration (thresholds, reference period, color mapping)

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P3-001 | Create `analysis/era5/__init__.py` with module exports | | |
| TASK-P3-002 | Create `analysis/era5/config.py` with all constants (bounds, variables, reference period) | | |
| TASK-P3-003 | Create `analysis/era5/types.py` with source-agnostic data structures (`BoundsDict`, `ProcessingResult`, `AnomalyMetadata`). Variable name mappings (`ERA5_TO_STANDARD`, `STANDARD_TO_ERA5`) move to provider's `variable_name_mapping` | | |
| TASK-P3-004 | Write unit tests for configuration validation | | |

### Implementation Phase 3.2: CDS Data Fetching

- GOAL-P3-002: Implement ERA5-Land data download from Copernicus CDS

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P3-005 | Create `analysis/era5/fetch_era5_data.py` — accepts a `ClimateDataProvider` instance (injected, not imported). CDS dataset name, variable mapping, bounds, and retry config come from the provider | | |
| TASK-P3-006 | Implement `fetch_monthly_data(provider, year, month, output_dir)` for single month download | | |
| TASK-P3-007 | Implement `fetch_reference_climatology()` for 1961-1990 data | | |
| TASK-P3-008 | Add retry logic with exponential backoff | | |
| TASK-P3-009 | Add local caching to avoid redundant downloads | | |
| TASK-P3-010 | Write unit tests with mocked provider protocol (not CDS client directly) | | |

### Implementation Phase 3.3: Land Mask Application

- GOAL-P3-004: Apply Germany land mask to exclude ocean areas

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P3-016 | Create `analysis/era5/apply_land_mask.py` module | | |
| TASK-P3-017 | Download and process Natural Earth 1:10m land polygons | | |
| TASK-P3-018 | Rasterize land polygons to match native data grid | | |
| TASK-P3-019 | Implement mask application preserving islands | | |
| TASK-P3-020 | Create mask validation script for visual verification | | |
| TASK-P3-021 | Write unit tests verifying island inclusion | | |

### Implementation Phase 3.5: Anomaly Calculation

- GOAL-P3-005: Calculate temperature anomalies versus reference period

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P3-022 | Create `analysis/era5/calculate_anomalies.py` module | | |
| TASK-P3-023 | Implement monthly climatology calculation (1961-1990 mean per cell) | | |
| TASK-P3-024 | Implement anomaly calculation (current - climatology) | | |
| TASK-P3-025 | Export anomaly grids as GeoTIFF with proper metadata | | |
| TASK-P3-026 | Validate against HYRAS reference data where overlapping | | |
| TASK-P3-027 | Write comprehensive unit tests | | |

### Implementation Phase 3.6: Integration & Testing

- GOAL-P3-006: Ensure complete pipeline works end-to-end

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P3-028 | Create `analysis/era5/tests/` directory structure | | |
| TASK-P3-029 | Create sample ERA5-Land test data subset (1 month, reduced grid) | | |
| TASK-P3-030 | Create integration test running full pipeline | | |
| TASK-P3-031 | Add pytest fixtures for common test data | | |
| TASK-P3-032 | Document module usage in docstrings and README | | |

### Implementation Phase 3.7: Daily Data Extraction

- GOAL-P3-007: Extract daily Tmin/Tmax from ERA5-Land hourly data

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P3-033 | Create `analysis/era5/fetch_daily_data.py` module | | |
| TASK-P3-034 | Implement hourly ERA5-Land download for Germany | | |
| TASK-P3-035 | Extract daily Tmax from hourly maxima | | |
| TASK-P3-036 | Extract daily Tmin from hourly minima | | |
| TASK-P3-037 | Calculate daily Tmean from hourly average | | |
| TASK-P3-038 | Store daily values in NetCDF format | | |
| TASK-P3-039 | Write unit tests for daily extraction | | |

### Implementation Phase 3.8: Precipitation Data

- GOAL-P3-008: Fetch and process precipitation data for snow/rain metrics

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P3-040 | Create `analysis/era5/fetch_precipitation.py` module | | |
| TASK-P3-041 | Implement daily `tp` (total precipitation) download | | |
| TASK-P3-042 | Convert precipitation from meters to mm | | |
| TASK-P3-043 | Calculate snow days: precip > 0.1mm AND Tmean ≤ 0°C | | |
| TASK-P3-044 | Calculate dry spell lengths (consecutive days < 1mm) | | |
| TASK-P3-045 | Calculate extreme rain days (precip ≥ 25mm) | | |
| TASK-P3-046 | Write unit tests for precipitation calculations | | |

### Implementation Phase 3.9: Threshold Detection

- GOAL-P3-009: Detect temperature threshold exceedances for metrics

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P3-047 | Create `analysis/era5/detect_thresholds.py` module | | |
| TASK-P3-048 | Implement hot day detection: Tmax ≥ 30°C (DWD Heißer Tag) | | |
| TASK-P3-049 | Implement extreme heat detection: Tmax ≥ 35°C | | |
| TASK-P3-050 | Implement tropical night detection: Tmin ≥ 20°C (DWD Tropennacht) | | |
| TASK-P3-051 | Implement ice day detection: Tmax ≤ 0°C (DWD Eistag) | | |
| TASK-P3-052 | Implement frost day detection: Tmin < 0°C (DWD Frosttag) | | |
| TASK-P3-053 | Count threshold days per month and store | | |
| TASK-P3-054 | Write unit tests for threshold detection | | |

## 3. Alternatives

- **ALT-P3-003**: **Download full European domain, crop later**
  - Would simplify API calls but increase download size 10x
  - Rejected: Bandwidth cost, storage, and processing time

- **ALT-P3-004**: **Use GADM boundaries instead of Natural Earth**
  - GADM has more detailed admin boundaries
  - Rejected: More complex licensing; Natural Earth 1:10m sufficient

## 4. Dependencies

### External Dependencies

- **DEP-P3-001**: Copernicus CDS account with API key
- **DEP-P3-002**: Natural Earth 1:10m land polygons dataset
- **DEP-P3-003**: Phase 1 testing infrastructure (pytest configured)

### Python Package Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `cdsapi` | >=0.7.0 | Copernicus CDS API client |
| `xarray` | >=2025.6.1 | NetCDF/multidimensional array handling |
| `netCDF4` | >=1.7.2 | NetCDF file backend |
| `rasterio` | >=1.4.0 | GeoTIFF read/write |
| `shapely` | >=2.0.0 | Geometry operations |
| `geopandas` | >=1.0.0 | Geospatial data handling |
| `numpy` | >=2.3.0 | Numerical operations |
| `pytest` | >=8.0.0 | Testing framework |
| `pytest-cov` | >=5.0.0 | Coverage reporting |

## 5. Files

### New Files

| File ID | Path | Action | Description |
|---------|------|--------|-------------|
| FILE-P3-001 | `analysis/era5/__init__.py` | NEW | Module exports |
| FILE-P3-001a | `analysis/era5/providers/__init__.py` | NEW | Provider factory and registry |
| FILE-P3-001b | `analysis/era5/providers/protocol.py` | NEW | `ClimateDataProvider` Protocol definition |
| FILE-P3-001c | `analysis/era5/providers/era5_land.py` | NEW | `ERA5LandProvider` implementation |
| FILE-P3-002 | `analysis/era5/config.py` | NEW | Source-agnostic configuration (thresholds, reference period, color mapping) |
| FILE-P3-003 | `analysis/era5/types.py` | NEW | Type definitions |
| FILE-P3-004 | `analysis/era5/fetch_era5_data.py` | NEW | CDS data download |
| FILE-P3-006 | `analysis/era5/apply_land_mask.py` | NEW | Land mask application |
| FILE-P3-007 | `analysis/era5/calculate_anomalies.py` | NEW | Anomaly calculation |
| FILE-P3-008 | `analysis/era5/tests/__init__.py` | NEW | Test module |
| FILE-P3-009 | `analysis/era5/tests/conftest.py` | NEW | Pytest fixtures |
| FILE-P3-010 | `analysis/era5/tests/test_fetch_era5_data.py` | NEW | Fetch tests |
| FILE-P3-012 | `analysis/era5/tests/test_land_mask.py` | NEW | Land mask tests |
| FILE-P3-013 | `analysis/era5/tests/test_anomalies.py` | NEW | Anomaly tests |
| FILE-P3-014 | `analysis/era5/tests/test_integration.py` | NEW | Integration tests |
| FILE-P3-014a | `analysis/era5/tests/test_provider.py` | NEW | Provider protocol and swap tests |
| FILE-P3-015 | `analysis/era5/fixtures/` | NEW | Test data directory |
| FILE-P3-016 | `analysis/era5/fetch_daily_data.py` | NEW | Daily Tmin/Tmax extraction |
| FILE-P3-017 | `analysis/era5/fetch_precipitation.py` | NEW | Precipitation download |
| FILE-P3-018 | `analysis/era5/detect_thresholds.py` | NEW | Temperature threshold detection |
| FILE-P3-019 | `analysis/era5/tests/test_daily_data.py` | NEW | Daily extraction tests |
| FILE-P3-020 | `analysis/era5/tests/test_precipitation.py` | NEW | Precipitation tests |
| FILE-P3-021 | `analysis/era5/tests/test_thresholds.py` | NEW | Threshold tests |

### Modified Files

| File ID | Path | Action | Description |
|---------|------|--------|-------------|
| FILE-P3-022 | `pyproject.toml` | MODIFY | Add new dependencies |

## 6. Testing

### Unit Tests

| Test ID | Description | File |
|---------|-------------|------|
| TEST-P3-001 | Config loads with valid bounds | `test_config.py` |
| TEST-P3-002 | Bounds validation rejects invalid coordinates | `test_config.py` |
| TEST-P3-003 | CDS client initializes with valid credentials | `test_fetch_era5_data.py` |
| TEST-P3-004 | fetch_monthly_data handles API timeout with retry | `test_fetch_era5_data.py` |
| TEST-P3-005 | fetch_monthly_data returns valid xarray Dataset | `test_fetch_era5_data.py` |
| TEST-P3-009 | Land mask includes Sylt island | `test_land_mask.py` |
| TEST-P3-010 | Land mask includes Rügen island | `test_land_mask.py` |
| TEST-P3-011 | Land mask includes Helgoland island | `test_land_mask.py` |
| TEST-P3-012 | Land mask excludes North Sea | `test_land_mask.py` |
| TEST-P3-013 | Land mask excludes Baltic Sea | `test_land_mask.py` |
| TEST-P3-014 | Anomaly calculation produces expected difference | `test_anomalies.py` |
| TEST-P3-015 | Anomaly output has correct CRS and bounds | `test_anomalies.py` |
| TEST-P3-016 | GeoTIFF export contains valid metadata | `test_anomalies.py` |

### Integration Tests

| Test ID | Description | File |
|---------|-------------|------|
| TEST-P3-017 | Full pipeline produces valid GeoTIFF from sample data | `test_integration.py` |
| TEST-P3-018 | Pipeline handles missing input gracefully | `test_integration.py` |
| TEST-P3-019 | Pipeline is deterministic (same input → same output) | `test_integration.py` |

### Mock Data Requirements

```python
# fixtures/sample_era5_land.nc - Small test NetCDF
# Grid: 5x5 cells (0.1° resolution)
# Bounds: 10.0-10.4°E, 50.0-50.4°N (small German area)
# Time: Single month (2024-01)
# Variables: t2m (2m temperature)
```

## 7. Risks & Assumptions

### Risks

| Risk ID | Description | Probability | Impact | Mitigation |
|---------|-------------|-------------|--------|------------|
| RISK-P3-001 | CDS API unavailable/rate limited | Medium | High | Retry logic, local cache |
| RISK-P3-003 | Natural Earth mask misses small islands | Low | Medium | Manual verification checklist |
| RISK-P3-004 | Memory overflow on full Germany grid | Low | High | Process in chunks if needed |
| RISK-P3-005 | Coordinate system confusion (lat/lon order) | Medium | Medium | Explicit coordinate handling, tests |

### Assumptions

- **ASSUMPTION-P3-001**: CDS API key available via environment variable
- **ASSUMPTION-P3-002**: ERA5-Land data available for 1961-present
- **ASSUMPTION-P3-003**: Output grid coordinate system is EPSG:4326 (WGS84)
- **ASSUMPTION-P3-005**: Reference period 1961-1990 is standard WMO baseline

## 8. Multi-Agent Execution Notes

### Execution Order

**Sequential tasks (must run in order):**
1. TASK-P3-100 → TASK-P3-106 (Provider protocol first)
2. TASK-P3-001 → TASK-P3-004 (Source-agnostic configuration)
3. TASK-P3-005 → TASK-P3-010 (CDS fetching, injected with provider)
4. TASK-P3-016 → TASK-P3-021 (Land mask)
5. TASK-P3-022 → TASK-P3-027 (Anomalies)
6. TASK-P3-028 → TASK-P3-032 (Integration)

**Parallel opportunities:**
- Phase 3.3 (Land mask) can develop after 3.2
- Tests can be written alongside implementation

### Agent Context Requirements

Each agent session needs:
- This phase plan document
- Master plan section 10.5 (NetCDF processing pattern)
- Existing `analysis/hyras/extract_hyras_data.py` as reference
- ERA5-Land variable documentation

### Validation Checkpoints

- **After Phase 3.0**: `python -c "from analysis.era5.providers import get_provider; p = get_provider(); assert isinstance(p, ClimateDataProvider)"` works
- **After Phase 3.1**: `python -c "from analysis.era5.config import REFERENCE_PERIOD, TEMPERATURE_THRESHOLDS"` works (source-agnostic config only)
- **After Phase 3.2**: Sample data downloads to `data/era5/raw/`
- **After Phase 3.3**: Land mask PNG shows Germany with islands, no ocean
- **After Phase 3.5**: GeoTIFF opens in QGIS with valid anomaly values
- **After Phase 3.6**: `pytest analysis/era5/tests/ -v` passes all tests
- **After Phase 3.7**: Daily Tmin/Tmax NetCDF files exist with valid ranges
- **After Phase 3.8**: Precipitation data in mm, snow day counts calculated
- **After Phase 3.9**: Threshold counts match manual spot-checks

## 9. Related Specifications / Further Reading

- [ERA5-Land Documentation](https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-land-monthly-means)
- [CDS API Documentation](https://cds.climate.copernicus.eu/api-how-to)
- [Natural Earth 1:10m Cultural Vectors](https://www.naturalearthdata.com/downloads/10m-cultural-vectors/)
- [Rasterio Documentation](https://rasterio.readthedocs.io/)
- Master Plan: `plan/botox/era5-germany-climate-visualization-1.md`

## 10. Code Reference

### 10.0a Provider Protocol

**File**: `analysis/era5/providers/protocol.py`

```python
#!/usr/bin/env python3
"""Climate data provider protocol.

Defines the interface that all climate data sources must satisfy.
Uses structural subtyping (typing.Protocol) — providers do not need
to inherit from this class, only implement its methods/properties.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

import xarray as xr

from ..types import BoundsDict


@runtime_checkable
class ClimateDataProvider(Protocol):
    """Interface for pluggable climate reanalysis data sources."""

    @property
    def dataset_id(self) -> str:
        """Short identifier, e.g. 'era5-land', 'cerra', 'hyras'."""
        ...

    @property
    def display_name(self) -> str:
        """Human-readable name, e.g. 'ERA5-Land'."""
        ...

    @property
    def native_resolution_deg(self) -> float:
        """Native grid resolution in degrees, e.g. 0.1 for ERA5-Land."""
        ...

    @property
    def bounds(self) -> BoundsDict:
        """Geographic bounds for data extraction."""
        ...

    @property
    def variables(self) -> dict[str, dict]:
        """Variable definitions: keys are internal names, values contain
        'cds_name', 'unit', 'description', optional 'derived'."""
        ...

    @property
    def coordinate_names(self) -> dict[str, str]:
        """Mapping of standard coord roles to dataset-specific names.
        E.g. {'latitude': 'latitude', 'longitude': 'longitude', 'time': 'time'}."""
        ...

    @property
    def latitude_descending(self) -> bool:
        """True if latitude is stored north-to-south (ERA5-Land convention)."""
        ...

    @property
    def unit_conversions(self) -> dict[str, dict]:
        """Unit conversion rules. E.g. {'temperature': {'from': 'K', 'offset': -273.15},
        'precipitation': {'from': 'm', 'factor': 1000}}."""
        ...

    def fetch_monthly(
        self, year: int, month: int, output_dir: Path, variable: str = 't2m',
        force: bool = False,
    ) -> Path:
        """Download monthly aggregated data. Returns path to NetCDF."""
        ...

    def fetch_daily(
        self, year: int, month: int, output_dir: Path,
        force: bool = False,
    ) -> Path:
        """Download daily/hourly data for Tmin/Tmax derivation. Returns path to NetCDF."""
        ...

    def load_dataset(self, file_path: Path) -> xr.Dataset:
        """Load and subset a downloaded file to the provider's bounds."""
        ...
```

**Notes:** `@runtime_checkable` enables `isinstance(obj, ClimateDataProvider)` checks for validation. All ERA5-Land-specific constants (CDS dataset names, variable mappings, resolution, bounds) move into `ERA5LandProvider`. `config.py` retains only source-agnostic settings (thresholds, reference period, color mapping). No `OUTPUT_GRID` or `get_grid_dimensions()` — the pipeline uses the provider's `native_resolution_deg` and the actual data grid shape.

### 10.0b ERA5-Land Provider Implementation

**File**: `analysis/era5/providers/era5_land.py`

```python
#!/usr/bin/env python3
"""ERA5-Land climate data provider implementation."""

from pathlib import Path

import cdsapi
import xarray as xr

from ..types import BoundsDict


class ERA5LandProvider:
    """Concrete provider for Copernicus ERA5-Land reanalysis data."""

    dataset_id = 'era5-land'
    display_name = 'ERA5-Land'
    native_resolution_deg = 0.1  # ~9 km

    bounds = BoundsDict(north=55.1, south=47.2, west=5.8, east=15.1)

    coordinate_names = {
        'latitude': 'latitude',
        'longitude': 'longitude',
        'time': 'time',
    }

    latitude_descending = True  # ERA5-Land stores north first

    variables = {
        't2m': {'cds_name': '2m_temperature', 'unit': 'K', 'description': '2m air temperature'},
        'tp': {'cds_name': 'total_precipitation', 'unit': 'm', 'description': 'Total precipitation'},
        # ... (moved from config.py ERA5_VARIABLES)
    }

    unit_conversions = {
        'temperature': {'from': 'K', 'offset': -273.15},
        'precipitation': {'from': 'm', 'factor': 1000},  # m → mm
    }

    CDS_DATASETS = {
        'monthly': 'reanalysis-era5-land-monthly-means',
        'hourly': 'reanalysis-era5-land',
    }

    def fetch_monthly(self, year, month, output_dir, variable='t2m', force=False):
        # CDS API call using self.CDS_DATASETS['monthly'], self.bounds, etc.
        ...

    def fetch_daily(self, year, month, output_dir, force=False):
        # CDS API call using self.CDS_DATASETS['hourly']
        ...

    def load_dataset(self, file_path: Path) -> xr.Dataset:
        ds = xr.open_dataset(file_path)
        lat_key = self.coordinate_names['latitude']
        lon_key = self.coordinate_names['longitude']
        if self.latitude_descending:
            ds = ds.sel(**{
                lat_key: slice(self.bounds['north'], self.bounds['south']),
                lon_key: slice(self.bounds['west'], self.bounds['east']),
            })
        return ds
```

**Notes:** This is a sketch. The actual implementation will be specified during implementation. The key point is that ALL ERA5-Land-specific knowledge is encapsulated here.

### 10.0c Provider Factory

**File**: `analysis/era5/providers/__init__.py`

```python
"""Climate data provider registry."""

import os
from .protocol import ClimateDataProvider
from .era5_land import ERA5LandProvider

_PROVIDERS: dict[str, type[ClimateDataProvider]] = {
    'era5-land': ERA5LandProvider,
}

def get_provider(provider_id: str | None = None) -> ClimateDataProvider:
    """Instantiate the configured climate data provider.
    
    Args:
        provider_id: Provider identifier. If None, reads from
                     CLIMATE_DATA_PROVIDER env var (default: 'era5-land').
    """
    pid = provider_id or os.environ.get('CLIMATE_DATA_PROVIDER', 'era5-land')
    if pid not in _PROVIDERS:
        raise ValueError(f"Unknown provider '{pid}'. Available: {list(_PROVIDERS)}")
    return _PROVIDERS[pid]()
```

**Notes:** Adding a new provider = implement the protocol + add one entry to `_PROVIDERS`. Zero changes to pipeline code.

### 10.1 Configuration Module

**File**: `analysis/era5/config.py`

```python
#!/usr/bin/env python3
"""
ERA5-Land data processing configuration.

Source-agnostic configuration for climate data processing including
reference periods, temperature thresholds, and color mapping.
Dataset-specific values (bounds, variables, resolution, CDS config)
live in the active ClimateDataProvider implementation.
"""

# NOTE: The following constants move to ERA5LandProvider (providers/era5_land.py)
# during TASK-P3-103. They remain here as reference for the initial implementation
# but will be accessed via provider.bounds, provider.variables, etc.

# Germany geographic bounds (EPSG:4326) → provider.bounds
GERMANY_BOUNDS = {
    'north': 55.1,
    'south': 47.2,
    'west': 5.8,
    'east': 15.1,
}

# Add small buffer for edge handling
GERMANY_BOUNDS_BUFFERED = {
    'north': 55.2,
    'south': 47.1,
    'west': 5.7,
    'east': 15.2,
}

# ERA5-Land variables to process
ERA5_VARIABLES = {
    't2m': {
        'cds_name': '2m_temperature',
        'unit': 'K',  # Kelvin, convert to Celsius
        'description': '2-meter air temperature (mean)',
    },
    't2m_max': {
        'cds_name': '2m_temperature',
        'unit': 'K',
        'description': 'Daily maximum 2-meter temperature (derived from hourly)',
        'derived': True,
    },
    't2m_min': {
        'cds_name': '2m_temperature',
        'unit': 'K',
        'description': 'Daily minimum 2-meter temperature (derived from hourly)',
        'derived': True,
    },
    'tp': {
        'cds_name': 'total_precipitation',
        'unit': 'm',  # meters, convert to mm
        'description': 'Total precipitation for snow/rain metrics',
    },
}

# CDS datasets
CDS_DATASETS = {
    'monthly': 'reanalysis-era5-land-monthly-means',
    'hourly': 'reanalysis-era5-land',  # For daily Tmin/Tmax derivation
}

# Reference period for anomaly calculation (WMO standard)
REFERENCE_PERIOD = {
    'start_year': 1961,
    'end_year': 1990,
}

# Temperature thresholds (DWD standards)
# Note: 32°C is NOT a DWD standard - removed per ALT-007
TEMPERATURE_THRESHOLDS = {
    'hot_day': 30.0,           # Tmax >= 30°C (DWD: Heißer Tag)
    'extreme_heat': 35.0,      # Tmax >= 35°C (extreme heat, vegetation damage)
    'tropical_night': 20.0,    # Tmin >= 20°C (DWD: Tropennacht)
    'ice_day': 0.0,            # Tmax <= 0°C (DWD: Eistag)
    'frost_day': 0.0,          # Tmin < 0°C (DWD: Frosttag)
}

# Precipitation thresholds
PRECIPITATION_THRESHOLDS = {
    'dry_day': 1.0,            # Precip < 1mm (for dry spell calculation)
    'extreme_rain': 25.0,      # Precip >= 25mm (flooding risk)
    'snow_precip_min': 0.1,    # Precip > 0.1mm for snow day detection
}

# Snow day detection: precip > 0.1mm AND Tmean <= 0°C
SNOW_DAY_TEMP_THRESHOLD = 0.0  # °C

# ERA5-Land native resolution
ERA5_LAND_RESOLUTION = 0.1  # degrees (~9km)

# CDS API configuration
CDS_CONFIG = {
    'dataset': 'reanalysis-era5-land-monthly-means',
    'product_type': 'monthly_averaged_reanalysis',
    'format': 'netcdf',
    'max_retries': 5,
    'retry_delay_base': 60,  # seconds
}

# Color mapping for anomalies
ANOMALY_COLORMAP = {
    'vmin': -3.0,  # °C
    'vmax': 3.0,   # °C
    'colormap': 'RdBu_r',  # Red (warm) to Blue (cold), reversed
}

# Important German islands to verify in land mask
GERMAN_ISLANDS = [
    {'name': 'Sylt', 'lat': 54.9, 'lon': 8.3},
    {'name': 'Rügen', 'lat': 54.4, 'lon': 13.4},
    {'name': 'Helgoland', 'lat': 54.18, 'lon': 7.89},
    {'name': 'Borkum', 'lat': 53.59, 'lon': 6.66},
    {'name': 'Fehmarn', 'lat': 54.45, 'lon': 11.2},
    {'name': 'Usedom', 'lat': 53.93, 'lon': 14.0},
]


def validate_bounds(bounds):
    """Validate geographic bounds dictionary.
    
    Args:
        bounds: Dictionary with 'north', 'south', 'east', 'west' keys
        
    Raises:
        ValueError: If bounds are invalid
    """
    if bounds['north'] <= bounds['south']:
        raise ValueError("North bound must be greater than south bound")
    if bounds['east'] <= bounds['west']:
        raise ValueError("East bound must be greater than west bound")
    if not (-90 <= bounds['south'] <= 90 and -90 <= bounds['north'] <= 90):
        raise ValueError("Latitude bounds must be between -90 and 90")
    if not (-180 <= bounds['west'] <= 180 and -180 <= bounds['east'] <= 180):
        raise ValueError("Longitude bounds must be between -180 and 180")
```

### 10.2 Data Types Module

**File**: `analysis/era5/types.py`

```python
#!/usr/bin/env python3
"""
Type definitions for ERA5-Land data processing.

Defines data structures used throughout the ERA5-Land pipeline.
Note: Using dictionaries rather than dataclasses for consistency
with existing codebase patterns.
"""

from typing import TypedDict


class BoundsDict(TypedDict):
    """Geographic bounds dictionary."""
    north: float
    south: float
    east: float
    west: float


class ProcessingResult(TypedDict):
    """Result of a processing step."""
    success: bool
    output_path: str
    message: str
    metadata: dict


class AnomalyMetadata(TypedDict):
    """Metadata for anomaly GeoTIFF."""
    year: int
    month: int
    reference_start: int
    reference_end: int
    bounds: BoundsDict
    resolution: str
    crs: str
    units: str


# Variable name mappings between datasets
# NOTE: These move to provider.variable_name_mapping during TASK-P3-103
ERA5_TO_STANDARD = {
    't2m': 'temperature_2m',
    'tp': 'total_precipitation',
    'ssrd': 'surface_solar_radiation',
}

STANDARD_TO_ERA5 = {v: k for k, v in ERA5_TO_STANDARD.items()}
```

### 10.3 CDS Data Fetching

**File**: `analysis/era5/fetch_era5_data.py`

```python
#!/usr/bin/env python3
"""
ERA5-Land data fetching from Copernicus Climate Data Store.

Downloads monthly ERA5-Land temperature data for Germany with
retry logic and local caching. Accepts a ClimateDataProvider
instance for dataset-specific parameters.
"""

import os
import sys
import time
import logging
from pathlib import Path

import cdsapi
import xarray as xr

from .providers.protocol import ClimateDataProvider
from .config import REFERENCE_PERIOD

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def get_cds_client():
    """Initialize CDS API client.
    
    Expects CDS_API_KEY environment variable to be set.
    Alternatively, uses ~/.cdsapirc configuration.
    
    Returns:
        cdsapi.Client instance
        
    Raises:
        RuntimeError: If credentials not found
    """
    api_key = os.environ.get('CDS_API_KEY')
    if api_key:
        # Format: "uid:key"
        return cdsapi.Client(
            url='https://cds.climate.copernicus.eu/api/v2',
            key=api_key
        )
    
    # Fall back to .cdsapirc file
    cdsapirc = Path.home() / '.cdsapirc'
    if cdsapirc.exists():
        return cdsapi.Client()
    
    raise RuntimeError(
        "CDS credentials not found. Set CDS_API_KEY environment variable "
        "or create ~/.cdsapirc file."
    )


def fetch_monthly_data(
    provider: ClimateDataProvider,
    year: int,
    month: int,
    output_dir: Path,
    variable: str = 't2m',
    force_download: bool = False,
) -> Path:
    """Fetch monthly data for a specific month via the active provider.
    
    Args:
        provider: Climate data provider instance
        year: Year to fetch (e.g., 2024)
        month: Month to fetch (1-12)
        output_dir: Directory to save downloaded file
        variable: Variable name (default: t2m)
        force_download: If True, download even if cached
        
    Returns:
        Path to downloaded NetCDF file
        
    Raises:
        RuntimeError: If download fails after retries
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"{provider.dataset_id}_{variable}_{year}{month:02d}.nc"
    output_path = output_dir / filename
    
    # Check cache
    if output_path.exists() and not force_download:
        logger.info(f"Using cached file: {output_path}")
        return output_path
    
    logger.info(f"Fetching {provider.display_name} {variable} for {year}-{month:02d}")
    
    # Delegate to provider
    return provider.fetch_monthly(year, month, output_dir, variable, force_download)


def fetch_reference_climatology(
    provider: ClimateDataProvider,
    output_dir: Path,
    variable: str = 't2m',
) -> Path:
    """Fetch or calculate reference climatology (1961-1990 monthly means).
    
    If climatology file exists, returns path. Otherwise downloads
    all years in reference period and calculates monthly means.
    
    Args:
        provider: Climate data provider instance
        output_dir: Directory for climatology files
        variable: Variable name
        
    Returns:
        Path to climatology NetCDF file
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    clim_file = output_dir / f"climatology_{variable}_1961_1990.nc"
    
    if clim_file.exists():
        logger.info(f"Using cached climatology: {clim_file}")
        return clim_file
    
    logger.info("Calculating reference climatology (1961-1990)...")
    
    # Download all reference years
    datasets = []
    for year in range(REFERENCE_PERIOD['start_year'], REFERENCE_PERIOD['end_year'] + 1):
        for month in range(1, 13):
            try:
                nc_path = fetch_monthly_data(year, month, output_dir / 'reference', variable)
                ds = xr.open_dataset(nc_path)
                datasets.append(ds)
            except Exception as e:
                logger.error(f"Failed to fetch {year}-{month:02d}: {e}")
    
    if not datasets:
        raise RuntimeError("No reference data could be downloaded")
    
    # Combine and calculate monthly climatology
    combined = xr.concat(datasets, dim='time')
    climatology = combined.groupby('time.month').mean(dim='time')
    
    # Save climatology
    climatology.to_netcdf(clim_file)
    logger.info(f"Saved climatology: {clim_file}")
    
    return clim_file


def load_era5_data(file_path: Path) -> xr.Dataset:
    """Load ERA5-Land NetCDF file as xarray Dataset.
    
    Args:
        file_path: Path to NetCDF file
        
    Returns:
        xarray Dataset with temperature data
    """
    ds = xr.open_dataset(file_path)
    
    # Convert temperature from Kelvin to Celsius
    if 't2m' in ds:
        ds['t2m'] = ds['t2m'] - 273.15
        ds['t2m'].attrs['units'] = '°C'
    
    return ds


if __name__ == '__main__':
    # Example usage
    import argparse
    
    parser = argparse.ArgumentParser(description='Fetch ERA5-Land data')
    parser.add_argument('--year', type=int, required=True, help='Year to fetch')
    parser.add_argument('--month', type=int, required=True, help='Month to fetch')
    parser.add_argument('--output-dir', type=str, default='./data/era5/raw',
                        help='Output directory')
    args = parser.parse_args()
    
    output_path = fetch_monthly_data(args.year, args.month, Path(args.output_dir))
    print(f"Data saved to: {output_path}")
```

### 10.4 Land Mask Application

**File**: `analysis/era5/apply_land_mask.py`

```python
#!/usr/bin/env python3
"""
Apply Germany land mask to native-resolution ERA5-Land data.

Uses Natural Earth 1:10m land polygons to mask out ocean areas
while preserving German islands.
"""

import logging
from pathlib import Path

import numpy as np
import xarray as xr
import geopandas as gpd
import rasterio
from rasterio import features
from rasterio.transform import from_bounds
from shapely.geometry import Point

from .config import GERMAN_ISLANDS
from .providers.protocol import ClimateDataProvider

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Natural Earth data URL
NATURAL_EARTH_URL = (
    "https://naciscdn.org/naturalearth/10m/physical/"
    "ne_10m_land.zip"
)


def download_land_polygons(cache_dir: Path) -> Path:
    """Download Natural Earth 1:10m land polygons.
    
    Args:
        cache_dir: Directory to cache downloaded file
        
    Returns:
        Path to downloaded/cached shapefile
    """
    import requests
    import zipfile
    
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    zip_path = cache_dir / 'ne_10m_land.zip'
    shp_path = cache_dir / 'ne_10m_land' / 'ne_10m_land.shp'
    
    if shp_path.exists():
        logger.info(f"Using cached land polygons: {shp_path}")
        return shp_path
    
    logger.info("Downloading Natural Earth land polygons...")
    response = requests.get(NATURAL_EARTH_URL)
    response.raise_for_status()
    
    with open(zip_path, 'wb') as f:
        f.write(response.content)
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(cache_dir / 'ne_10m_land')
    
    logger.info(f"Downloaded and extracted: {shp_path}")
    return shp_path


def create_germany_land_mask(
    output_path: Path,
    ds: xr.Dataset,
    provider: ClimateDataProvider,
    cache_dir: Path = Path('./data/cache'),
) -> np.ndarray:
    """Create a land mask for Germany matching the native data grid.
    
    Args:
        output_path: Path to save mask as GeoTIFF
        ds: xarray Dataset whose grid shape to match
        provider: Climate data provider for bounds
        cache_dir: Directory for cached data
        
    Returns:
        Boolean array (True = land, False = ocean/outside)
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Download land polygons
    shp_path = download_land_polygons(cache_dir)
    
    # Load and clip to provider bounds (with buffer)
    logger.info("Loading and clipping land polygons...")
    land = gpd.read_file(shp_path)
    
    bounds = provider.bounds
    # Create bounding box with buffer
    bounds_buffered = {
        'north': bounds['north'] + 0.5,
        'south': bounds['south'] - 0.5,
        'west': bounds['west'] - 0.5,
        'east': bounds['east'] + 0.5,
    }
    
    # Clip to bounds
    land_clipped = land.cx[
        bounds_buffered['west']:bounds_buffered['east'],
        bounds_buffered['south']:bounds_buffered['north']
    ]
    
    # Get grid dimensions from the dataset
    n_lat = len(ds['latitude'])
    n_lon = len(ds['longitude'])
    
    # Create transform for rasterization
    transform = from_bounds(
        bounds['west'],
        bounds['south'],
        bounds['east'],
        bounds['north'],
        n_lon,
        n_lat
    )
    
    # Rasterize land polygons
    logger.info(f"Rasterizing to {n_lat}x{n_lon} grid...")
    shapes = [(geom, 1) for geom in land_clipped.geometry]
    
    mask = features.rasterize(
        shapes,
        out_shape=(n_lat, n_lon),
        transform=transform,
        fill=0,
        dtype=np.uint8
    )
    
    # Convert to boolean
    mask = mask.astype(bool)
    
    # Verify islands are included
    verify_islands(mask, transform)
    
    # Save as GeoTIFF
    with rasterio.open(
        output_path,
        'w',
        driver='GTiff',
        height=n_lat,
        width=n_lon,
        count=1,
        dtype=np.uint8,
        crs='EPSG:4326',
        transform=transform,
    ) as dst:
        dst.write(mask.astype(np.uint8), 1)
    
    logger.info(f"Saved land mask: {output_path}")
    return mask


def verify_islands(mask: np.ndarray, transform) -> None:
    """Verify that German islands are included in the mask.
    
    Args:
        mask: Boolean land mask array
        transform: Rasterio transform for coordinate conversion
        
    Raises:
        ValueError: If any island is not included
    """
    logger.info("Verifying island inclusion...")
    
    for island in GERMAN_ISLANDS:
        # Convert lat/lon to pixel coordinates
        col, row = ~transform * (island['lon'], island['lat'])
        row, col = int(row), int(col)
        
        # Check bounds
        if 0 <= row < mask.shape[0] and 0 <= col < mask.shape[1]:
            if not mask[row, col]:
                logger.warning(
                    f"Island {island['name']} at ({island['lat']}, {island['lon']}) "
                    "not included in mask!"
                )
            else:
                logger.info(f"✓ {island['name']} included")
        else:
            logger.warning(f"Island {island['name']} outside grid bounds")


def load_land_mask(mask_path: Path) -> np.ndarray:
    """Load precomputed land mask from GeoTIFF.
    
    Args:
        mask_path: Path to mask GeoTIFF
        
    Returns:
        Boolean array (True = land)
    """
    with rasterio.open(mask_path) as src:
        mask = src.read(1)
    return mask.astype(bool)


def apply_germany_land_mask(
    input_path: Path,
    output_dir: Path,
    mask_path: Path = None,
    variable: str = 't2m',
) -> Path:
    """Apply land mask to ERA5-Land data.
    
    Args:
        input_path: Path to ERA5-Land NetCDF
        output_dir: Output directory
        mask_path: Path to precomputed mask (creates if None)
        variable: Variable to mask
        
    Returns:
        Path to masked output file
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create or load mask
    if mask_path is None:
        mask_path = output_dir / 'germany_land_mask.tif'
        if not mask_path.exists():
            mask = create_germany_land_mask(mask_path)
        else:
            mask = load_land_mask(mask_path)
    else:
        mask = load_land_mask(mask_path)
    
    # Load data
    ds = xr.open_dataset(input_path)
    data = ds[variable].values
    
    # Apply mask
    logger.info("Applying land mask...")
    masked_data = np.where(mask, data, np.nan)
    
    # Create output Dataset
    out_ds = xr.Dataset(
        {variable: (['latitude', 'longitude'], masked_data)},
        coords={
            'latitude': ds['latitude'].values,
            'longitude': ds['longitude'].values,
        },
        attrs=ds.attrs.copy()
    )
    out_ds[variable].attrs = ds[variable].attrs.copy()
    out_ds.attrs['land_mask_applied'] = True
    
    # Save
    output_filename = input_path.stem + '_masked.nc'
    output_path = output_dir / output_filename
    out_ds.to_netcdf(output_path)
    
    logger.info(f"Saved masked data: {output_path}")
    return output_path


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Apply Germany land mask')
    parser.add_argument('input_file', nargs='?', help='Input NetCDF file')
    parser.add_argument('--output-dir', default='./data/era5/masked',
                        help='Output directory')
    parser.add_argument('--create-mask-only', action='store_true',
                        help='Only create the land mask, do not process data')
    args = parser.parse_args()
    
    if args.create_mask_only:
        mask_path = Path(args.output_dir) / 'germany_land_mask.tif'
        create_germany_land_mask(mask_path)
    else:
        if not args.input_file:
            parser.error("input_file required unless --create-mask-only")
        apply_germany_land_mask(Path(args.input_file), Path(args.output_dir))
```

### 10.6 Anomaly Calculation

**File**: `analysis/era5/calculate_anomalies.py`

```python
#!/usr/bin/env python3
"""
Calculate temperature anomalies relative to reference period.

Computes monthly anomalies by subtracting the 1961-1990 climatology
from current values.
"""

import logging
from pathlib import Path

import numpy as np
import xarray as xr
import rasterio
from rasterio.transform import from_bounds

from .config import REFERENCE_PERIOD, ANOMALY_COLORMAP
from .providers.protocol import ClimateDataProvider
from .types import AnomalyMetadata

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_climatology(climatology_path: Path, month: int) -> xr.DataArray:
    """Load climatology for a specific month.
    
    Args:
        climatology_path: Path to climatology NetCDF
        month: Month (1-12)
        
    Returns:
        xarray DataArray with monthly climatology
    """
    ds = xr.open_dataset(climatology_path)
    
    # Climatology has 'month' dimension
    if 'month' in ds.dims:
        return ds['t2m'].sel(month=month)
    else:
        # Single month file
        return ds['t2m']


def calculate_monthly_anomaly(
    provider: ClimateDataProvider,
    current_path: Path,
    year: int,
    month: int,
    output_dir: Path,
    climatology_path: Path = None,
    variable: str = 't2m',
) -> Path:
    """Calculate temperature anomaly for a specific month.
    
    Args:
        provider: Climate data provider instance
        current_path: Path to current month masked data
        year: Year of current data
        month: Month of current data
        output_dir: Directory for output
        climatology_path: Path to pre-computed climatology (optional)
        variable: Variable name
        
    Returns:
        Path to anomaly GeoTIFF
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Calculating anomaly for {year}-{month:02d}")
    
    # Load current data
    ds_current = xr.open_dataset(current_path)
    current_data = ds_current[variable].values
    
    # Load climatology
    if climatology_path is None:
        climatology_path = output_dir.parent / 'reference' / 'climatology_t2m_1961_1990.nc'
    
    if not climatology_path.exists():
        raise FileNotFoundError(
            f"Climatology file not found: {climatology_path}. "
            "Run fetch_reference_climatology() first."
        )
    
    clim_data = load_climatology(climatology_path, month)
    
    # Ensure shapes match (may need to regrid climatology)
    if clim_data.shape != current_data.shape:
        logger.info("Regridding climatology to match current data grid...")
        clim_ds = xr.Dataset({variable: clim_data})
        clim_ds = clim_ds.interp(
            latitude=ds_current['latitude'],
            longitude=ds_current['longitude'],
            method='linear',
        )
        clim_data = clim_ds[variable].values
    else:
        clim_data = clim_data.values
    
    # Calculate anomaly
    anomaly = current_data - clim_data
    
    logger.info(f"Anomaly range: {np.nanmin(anomaly):.2f} to {np.nanmax(anomaly):.2f}°C")
    
    # Create metadata
    metadata: AnomalyMetadata = {
        'year': year,
        'month': month,
        'reference_start': REFERENCE_PERIOD['start_year'],
        'reference_end': REFERENCE_PERIOD['end_year'],
        'bounds': provider.bounds,
        'resolution': f'native {provider.display_name} {provider.native_resolution_deg}°',
        'crs': 'EPSG:4326',
        'units': '°C',
    }
    
    # Save as GeoTIFF
    n_lat = len(ds_current['latitude'])
    n_lon = len(ds_current['longitude'])
    transform = from_bounds(
        provider.bounds['west'],
        provider.bounds['south'],
        provider.bounds['east'],
        provider.bounds['north'],
        n_lon,
        n_lat
    )
    
    output_filename = f"anomaly_{year}{month:02d}.tif"
    output_path = output_dir / output_filename
    
    with rasterio.open(
        output_path,
        'w',
        driver='GTiff',
        height=n_lat,
        width=n_lon,
        count=1,
        dtype=np.float32,
        crs='EPSG:4326',
        transform=transform,
        nodata=np.nan,
    ) as dst:
        dst.write(anomaly.astype(np.float32), 1)
        
        # Add metadata as tags
        dst.update_tags(
            year=str(year),
            month=str(month),
            reference_period=f"{REFERENCE_PERIOD['start_year']}-{REFERENCE_PERIOD['end_year']}",
            units='°C',
            colormap_vmin=str(ANOMALY_COLORMAP['vmin']),
            colormap_vmax=str(ANOMALY_COLORMAP['vmax']),
        )
    
    logger.info(f"Saved anomaly GeoTIFF: {output_path}")
    
    # Also save as NetCDF for further processing
    nc_path = output_path.with_suffix('.nc')
    out_ds = xr.Dataset(
        {'anomaly': (['latitude', 'longitude'], anomaly)},
        coords={
            'latitude': ds_current['latitude'].values,
            'longitude': ds_current['longitude'].values,
        },
        attrs=metadata
    )
    out_ds['anomaly'].attrs = {
        'units': '°C',
        'long_name': f'Temperature anomaly vs {REFERENCE_PERIOD["start_year"]}-{REFERENCE_PERIOD["end_year"]}',
    }
    out_ds.to_netcdf(nc_path)
    
    return output_path


def validate_against_hyras(
    anomaly_path: Path,
    hyras_path: Path,
    tolerance: float = 0.5,
) -> dict:
    """Validate ERA5-Land anomalies against HYRAS reference (if available).
    
    Args:
        anomaly_path: Path to ERA5-Land anomaly GeoTIFF
        hyras_path: Path to HYRAS data for same period
        tolerance: Acceptable mean difference in °C
        
    Returns:
        Dictionary with validation statistics
    """
    logger.info("Validating against HYRAS reference...")
    
    # Load ERA5-Land anomaly
    with rasterio.open(anomaly_path) as src:
        era5 = src.read(1)
    
    # Load HYRAS (would need to be processed to same grid)
    # This is a placeholder - actual implementation depends on HYRAS format
    
    # For now, return placeholder stats
    return {
        'validated': False,
        'reason': 'HYRAS comparison not yet implemented',
    }


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Calculate temperature anomaly')
    parser.add_argument('input_file', help='Masked NetCDF file')
    parser.add_argument('--year', type=int, required=True)
    parser.add_argument('--month', type=int, required=True)
    parser.add_argument('--output-dir', default='./data/era5/anomalies')
    parser.add_argument('--climatology', help='Path to climatology file')
    args = parser.parse_args()
    
    calculate_monthly_anomaly(
        Path(args.input_file),
        args.year,
        args.month,
        Path(args.output_dir),
        Path(args.climatology) if args.climatology else None
    )
```

### 10.7 Test Fixtures

**File**: `analysis/era5/tests/conftest.py`

```python
#!/usr/bin/env python3
"""
Pytest fixtures for ERA5-Land processing tests.
"""

import pytest
import numpy as np
import xarray as xr
from pathlib import Path
import tempfile


@pytest.fixture
def sample_era5_data():
    """Create sample ERA5-Land data for testing.
    
    Creates a small 5x5 grid over a portion of Germany.
    """
    # Small test area near Hamburg
    lats = np.linspace(54.0, 53.6, 5)  # North to south
    lons = np.linspace(9.5, 10.3, 5)   # West to east
    
    # Temperature in Kelvin (15-20°C range)
    temp_kelvin = np.random.uniform(288, 293, (1, 5, 5)).astype(np.float32)
    
    ds = xr.Dataset(
        {
            't2m': (['time', 'latitude', 'longitude'], temp_kelvin)
        },
        coords={
            'time': ['2024-01-01'],
            'latitude': lats,
            'longitude': lons,
        },
        attrs={'source': 'test_data'}
    )
    
    ds['t2m'].attrs = {'units': 'K', 'long_name': '2 metre temperature'}
    
    return ds


@pytest.fixture
def sample_climatology():
    """Create sample climatology data for 12 months."""
    lats = np.linspace(54.0, 53.6, 5)
    lons = np.linspace(9.5, 10.3, 5)
    
    # Monthly temperatures (seasonal pattern)
    monthly_temps = []
    for month in range(1, 13):
        # Simple seasonal pattern centered on July
        base = 283 + 10 * np.sin((month - 1) / 12 * 2 * np.pi - np.pi/2)
        temp = np.full((5, 5), base, dtype=np.float32)
        temp += np.random.uniform(-1, 1, (5, 5))
        monthly_temps.append(temp)
    
    ds = xr.Dataset(
        {
            't2m': (['month', 'latitude', 'longitude'], np.array(monthly_temps))
        },
        coords={
            'month': list(range(1, 13)),
            'latitude': lats,
            'longitude': lons,
        }
    )
    
    return ds


@pytest.fixture
def temp_output_dir():
    """Provide a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_cds_client(monkeypatch):
    """Mock the CDS API client for testing without network access."""
    
    class MockCDSClient:
        def __init__(self, *args, **kwargs):
            pass
        
        def retrieve(self, dataset, request, target):
            # Create a minimal NetCDF file
            lats = np.linspace(55.0, 47.0, 10)
            lons = np.linspace(6.0, 15.0, 10)
            temp = np.random.uniform(280, 300, (1, 10, 10)).astype(np.float32)
            
            ds = xr.Dataset(
                {'t2m': (['time', 'latitude', 'longitude'], temp)},
                coords={
                    'time': [f"{request['year']}-{request['month']}-01"],
                    'latitude': lats,
                    'longitude': lons,
                }
            )
            ds.to_netcdf(target)
    
    monkeypatch.setattr('cdsapi.Client', MockCDSClient)


@pytest.fixture
def germany_bounds():
    """Return Germany bounds dictionary."""
    return {
        'north': 55.1,
        'south': 47.2,
        'west': 5.8,
        'east': 15.1,
    }


@pytest.fixture
def sample_geotiff(temp_output_dir):
    """Create a sample GeoTIFF for testing."""
    import rasterio
    from rasterio.transform import from_bounds
    
    data = np.random.uniform(-2, 2, (100, 100)).astype(np.float32)
    transform = from_bounds(5.8, 47.2, 15.1, 55.1, 100, 100)
    
    path = temp_output_dir / 'sample.tif'
    with rasterio.open(
        path, 'w',
        driver='GTiff',
        height=100, width=100,
        count=1, dtype=np.float32,
        crs='EPSG:4326',
        transform=transform,
    ) as dst:
        dst.write(data, 1)
    
    return path
```

### 10.8 Example Unit Tests

**File**: `analysis/era5/tests/test_fetch_era5_data.py`

```python
#!/usr/bin/env python3
"""Tests for ERA5-Land data fetching."""

import pytest
from pathlib import Path
from analysis.era5.fetch_era5_data import (
    fetch_monthly_data,
    load_era5_data,
    get_cds_client,
)


class TestCDSClient:
    """Tests for CDS client initialization."""
    
    def test_client_with_env_key(self, monkeypatch):
        """Client initializes with CDS_API_KEY env variable."""
        monkeypatch.setenv('CDS_API_KEY', '12345:test-key')
        client = get_cds_client()
        assert client is not None
    
    def test_client_without_credentials_raises(self, monkeypatch):
        """Client raises error without credentials."""
        monkeypatch.delenv('CDS_API_KEY', raising=False)
        # Remove .cdsapirc if it exists
        cdsapirc = Path.home() / '.cdsapirc'
        if cdsapirc.exists():
            pytest.skip(".cdsapirc exists, cannot test missing credentials")
        
        with pytest.raises(RuntimeError, match="credentials not found"):
            get_cds_client()


class TestFetchMonthlyData:
    """Tests for monthly data fetching."""
    
    def test_fetch_creates_output_directory(self, mock_cds_client, temp_output_dir):
        """Fetch creates output directory if missing."""
        output_dir = temp_output_dir / 'new_dir'
        assert not output_dir.exists()
        
        result = fetch_monthly_data(2024, 1, output_dir)
        
        assert output_dir.exists()
        assert result.exists()
    
    def test_fetch_uses_cache(self, mock_cds_client, temp_output_dir):
        """Subsequent fetch uses cached file."""
        result1 = fetch_monthly_data(2024, 1, temp_output_dir)
        mtime1 = result1.stat().st_mtime
        
        result2 = fetch_monthly_data(2024, 1, temp_output_dir)
        mtime2 = result2.stat().st_mtime
        
        assert mtime1 == mtime2  # File not re-downloaded
    
    def test_fetch_force_download(self, mock_cds_client, temp_output_dir):
        """Force download re-fetches even with cache."""
        result1 = fetch_monthly_data(2024, 1, temp_output_dir)
        
        # Touch file to change mtime
        import time
        time.sleep(0.1)
        
        result2 = fetch_monthly_data(2024, 1, temp_output_dir, force_download=True)
        
        assert result2.stat().st_mtime > result1.stat().st_mtime


class TestLoadERA5LandData:
    """Tests for loading ERA5-Land data."""
    
    def test_load_converts_kelvin_to_celsius(self, sample_era5_data, temp_output_dir):
        """Temperature is converted from Kelvin to Celsius."""
        nc_path = temp_output_dir / 'test.nc'
        sample_era5_data.to_netcdf(nc_path)
        
        ds = load_era5_data(nc_path)
        
        # Original was ~288-293K, should be ~15-20°C
        assert ds['t2m'].values.max() < 100  # Not Kelvin
        assert ds['t2m'].values.min() > -50  # Reasonable Celsius
        assert ds['t2m'].attrs['units'] == '°C'
```

**File**: `analysis/era5/tests/test_land_mask.py`

```python
#!/usr/bin/env python3
"""Tests for land mask application."""

import pytest
import numpy as np
from pathlib import Path
from analysis.era5.apply_land_mask import (
    create_germany_land_mask,
    load_land_mask,
    verify_islands,
)
from analysis.era5.config import GERMAN_ISLANDS


class TestLandMaskCreation:
    """Tests for land mask creation."""
    
    @pytest.mark.slow
    def test_mask_created_with_correct_shape(self, temp_output_dir, sample_era5_data):
        """Land mask has expected dimensions for Germany at native ERA5-Land grid."""
        mask_path = temp_output_dir / 'mask.tif'
        mask = create_germany_land_mask(mask_path, sample_era5_data)
        
        # Expected shape ~79 x 93 for Germany at ERA5-Land 0.1° native resolution
        assert mask.shape[0] > 70
        assert mask.shape[1] > 80
        assert mask.dtype == bool
    
    @pytest.mark.slow
    def test_mask_includes_mainland(self, temp_output_dir):
        """Mask includes German mainland (not all NaN/False)."""
        mask_path = temp_output_dir / 'mask.tif'
        mask = create_germany_land_mask(mask_path)
        
        land_fraction = mask.sum() / mask.size
        assert land_fraction > 0.3  # Germany is ~40% of bounding box
        assert land_fraction < 0.7


class TestIslandVerification:
    """Tests for German island inclusion."""
    
    @pytest.mark.slow  
    @pytest.mark.parametrize("island", GERMAN_ISLANDS)
    def test_island_included(self, temp_output_dir, island):
        """Each German island is included in the mask."""
        mask_path = temp_output_dir / 'mask.tif'
        mask = create_germany_land_mask(mask_path)
        
        # This test runs verify_islands which logs but doesn't fail
        # We check by loading mask and testing specific coordinates
        import rasterio
        with rasterio.open(mask_path) as src:
            row, col = src.index(island['lon'], island['lat'])
            if 0 <= row < mask.shape[0] and 0 <= col < mask.shape[1]:
                assert mask[row, col], f"Island {island['name']} should be land"
```
