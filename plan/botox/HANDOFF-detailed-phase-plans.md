# Handoff: Detailed Phase Plan Creation

This document provides context for LLM sessions to create detailed implementation plans for each phase of the ERA5 Germany Climate Visualization project.

## Master Plan Location

**Read first**: [era5-germany-climate-visualization-1.md](era5-germany-climate-visualization-1.md)

This contains the overall architecture, all 11 phases with task lists, requirements, and code references.

---

## Key Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Object Storage** | Hetzner Object Storage | Free egress (outbound bandwidth), EU-based, €0.0052/GB storage |
| **CDN** | Keep existing Cloudflare | Already in use, free tier sufficient |
| **Map Visualization** | MapLibre GL (2D map) | Simpler, better mobile perf; 3D globe deferred |
| **Testing** | Phase 1 restructured for testing-first | Vitest + pytest before any feature work |
| **City Data** | GeoNames (existing) | Already integrated, CC BY 4.0 license, 2,949 cities |
| **Layout Components** | Extend existing PlotView/StatCard | Add tilted labels, MetricsRow, NarrativeTabs |

---

## Existing Codebase Patterns (CRITICAL)

New sessions MUST read these files to understand patterns:

### Frontend (TypeScript/React)

| Pattern | File to Read | Usage |
|---------|--------------|-------|
| **Redux slice factory** | `frontend/src/store/factories/createDataSlice.ts` | All new data slices |
| **Service layer** | `frontend/src/services/LiveDataService.ts` | All data fetching |
| **PlotView layout** | `frontend/src/components/common/PlotView/PlotView.tsx` | Two-column layouts |
| **StatCard** | `frontend/src/components/plots/Stats/StatCard.tsx` | Metric display cards |
| **Store structure** | `frontend/src/store/index.ts` | Redux store organization |
| **Selectors** | `frontend/src/store/selectors/` | Memoized selectors pattern |

### Backend (Python)

| Pattern | File to Read | Usage |
|---------|--------------|-------|
| **NetCDF processing** | `analysis/hyras/extract_hyras_data.py` | xarray patterns |
| **Data fetching** | `analysis/stations/fetch_station_data.py` | HTTP download patterns |
| **S3 upload** | `analysis/utilities/upload_to_s3.py` | boto3 patterns |
| **Threshold calculations** | `analysis/stations/calculate_temperature_days.py` | Metric calculations |

### Jobs

| Pattern | Directory | Usage |
|---------|-----------|-------|
| **Job structure** | `jobs/job-update-10min-station-data/` | Dockerfile, entrypoint, src/ |
| **GitHub Actions** | `.github/workflows/` | CI/CD patterns |

---

## Phase-Specific Instructions

### Phase 1: Testing Infrastructure & Development Setup

**Create**: `plan/botox/phase-01-testing-infrastructure.md`

**Tasks to detail**:
1. Vitest configuration for React (jsdom, @testing-library/react, coverage)
2. Pytest configuration (pyproject.toml, conftest.py, fixtures)
3. Mock data structure (`frontend/src/__mocks__/`, `analysis/fixtures/`)
4. CI workflow for test execution
5. Development setup script

**Include code for**:
- `frontend/vitest.config.ts`
- `frontend/src/setupTests.ts`
- `pyproject.toml` pytest section
- `analysis/conftest.py`
- `.github/workflows/test.yml`

**Testing patterns to establish**:
```typescript
// Frontend: Service mocking pattern
import { vi } from 'vitest';
vi.mock('../utils/fetchUtils', () => ({
  fetchAndParseCSV: vi.fn()
}));

// Frontend: Component testing pattern  
import { render, screen } from '@testing-library/react';
import { Provider } from 'react-redux';
import { store } from '../store';
```

```python
# Python: Fixture pattern
@pytest.fixture
def sample_netcdf_data():
    return xr.Dataset({...})

# Python: Mock external API
@pytest.fixture
def mock_cds_api(monkeypatch):
    monkeypatch.setattr('cdsapi.Client', MockCDSClient)
```

---

### Phase 2: Infrastructure (Storage, CDN)

**Create**: `plan/botox/phase-02-infrastructure.md`

**Tasks to detail**:
1. Hetzner Object Storage bucket creation
2. Bucket policy for public read (tiles only)
3. CDN cache configuration (Cloudflare existing)
4. Environment variable setup for credentials

**Include code for**:
- `analysis/utilities/upload_to_hetzner.py`
- `.env.example` with all required vars
- `scripts/setup-hetzner-bucket.sh`

**Hetzner specifics**:
- Endpoint: `https://fsn1.your-objectstorage.com` (Falkenstein) or `https://hel1.your-objectstorage.com` (Helsinki)
- Uses standard S3 API (boto3 compatible)
- Set `endpoint_url` in boto3 client

---

### Phase 3: ERA5 Data Pipeline - Core

**Create**: `plan/botox/phase-03-era5-pipeline.md`

**Tasks to detail**:
1. CDS API client setup and authentication
2. ERA5-Land monthly data download (higher res than ERA5)
3. Germany bounding box extraction
4. Interpolation from 0.1° to ~1km visual resolution
5. Land mask application (Natural Earth 1:10m)

**Include code for**:
- `analysis/era5/config.py` - all configuration constants
- `analysis/era5/fetch_era5_data.py` - CDS download
- `analysis/era5/interpolate_to_grid.py` - scipy interpolation
- `analysis/era5/apply_land_mask.py` - Natural Earth mask

**Key configuration values**:
```python
# Germany bounds
BOUNDS = {
    'north': 55.1,
    'south': 47.2,
    'west': 5.8,
    'east': 15.1
}

# ERA5-Land variables
VARIABLES = ['t2m']  # 2m temperature

# Reference period
REFERENCE_START = 1961
REFERENCE_END = 1990

# Output resolution (visual)
OUTPUT_RESOLUTION_KM = 1
```

**Testing requirements**:
- Unit test for interpolation with known input/output
- Unit test for land mask including islands (Sylt, Rügen, Helgoland)
- Integration test with sample ERA5 subset

---

### Phase 4: Tile Generation Pipeline

**Create**: `plan/botox/phase-04-tile-generation.md`

**Tasks to detail**:
1. GeoTIFF creation from interpolated data
2. Color ramp application (diverging blue-red)
3. WebP tile pyramid generation (z6-z10)
4. Tile naming convention and directory structure
5. Upload to Hetzner with correct content-type

**Include code for**:
- `analysis/tiles/generate_tiles.py`
- `analysis/tiles/color_ramps.py`
- `analysis/tiles/upload_tiles.py`

**Tile specifications**:
```python
ZOOM_LEVELS = range(6, 11)  # z6 to z10
TILE_SIZE = 256
FORMAT = 'webp'
QUALITY = 80
COLOR_RAMP = 'RdBu_r'  # Red (hot) to Blue (cold), reversed
VMIN = -3.0  # °C anomaly
VMAX = 3.0   # °C anomaly
```

**URL pattern**: `/{year}/{month:02d}/{z}/{x}/{y}.webp`

---

### Phase 5: Metrics Calculation Pipeline

**Create**: `plan/botox/phase-05-metrics-calculation.md`

**Tasks to detail**:
1. Annual temperature anomaly calculation
2. Warming rate (linear regression)
3. Record-breaking days count
4. Seasonal warming per season
5. Threshold days (hot, ice, frost, tropical nights)
6. Aggregation to city and country level
7. JSON export for frontend

**Include code for**:
- Each `analysis/metrics/calculate_*.py` module
- `analysis/metrics/aggregate_metrics.py`
- `analysis/metrics/export_metrics.py`

**Output schema** (from master plan section 10.10):
```typescript
interface LocationMetrics {
    annualAnomaly: { value: number; year: number; ... };
    warmingRate: { value: number; startYear: number; ... };
    recordDays: { total: number; hot: number; cold: number; ... };
    seasonalWarming: { winter: number; spring: number; ... };
    thresholdDays: { hotDays: number; iceDays: number; ... };
    comfortableDays: { count: number; year: number; };
}
```

---

### Phase 6: Nightly Job Orchestration

**Create**: `plan/botox/phase-06-nightly-jobs.md`

**Tasks to detail**:
1. Daily job (check for new ERA5 data, process if available)
2. Monthly job (regenerate tiles for completed month)
3. Yearly job (recalculate all metrics)
4. GitHub Actions scheduled workflows
5. Failure notification setup

**Include code for**:
- `jobs/job-era5-daily/` - complete directory
- `jobs/job-era5-monthly/` - complete directory
- `.github/workflows/era5-*.yml` - all workflows

**Schedule**:
- Daily: 06:00 UTC (ERA5 has ~5 day delay)
- Monthly: 1st of month, 08:00 UTC
- Yearly: January 15, 10:00 UTC

---

### Phase 7: Frontend - Map Visualization

**Create**: `plan/botox/phase-07-frontend-map.md`

**Tasks to detail**:
1. MapLibre GL setup and configuration
2. ClimateMap component with tile overlay
3. City markers with click handlers
4. Color legend component
5. Date selector (month/year picker)
6. Redux slice for map state
7. Responsive behavior (mobile gestures)

**Include code for**:
- `frontend/src/components/maps/ClimateMap/` - all files
- `frontend/src/store/slices/mapSlice.ts`
- `frontend/src/hooks/useMapTiles.ts`

**Map features required**:
- Base map (OpenStreetMap or similar)
- Anomaly tile overlay with transparency
- Germany bounds constraint
- Zoom levels 6-10
- City markers from GeoNames data
- Legend showing color scale

---

### Phase 8: Frontend - Static Metrics Cards

**Create**: `plan/botox/phase-08-frontend-metrics.md`

**Tasks to detail**:
1. Extend StatCard with `labelTilt` prop
2. Create MetricsRow container (6 cards, responsive)
3. Create individual metric card components
4. MetricsService for fetching JSON
5. metricsSlice using createDataSlice factory
6. City selection integration

**Include code for**:
- Updated `StatCard.tsx` with tilt support
- `frontend/src/components/metrics/MetricsRow.tsx`
- All 6 card components in `frontend/src/components/metrics/cards/`
- `frontend/src/services/MetricsService.ts`
- `frontend/src/store/slices/metricsSlice.ts`

**StatCard enhancement**:
```tsx
interface StatCardProps {
  // ... existing props
  labelTilt?: number; // degrees, default 0, typically 5-10
}

// CSS addition
.title {
  transform: rotate(${props.labelTilt || 0}deg);
}
```

**MetricsRow responsive**:
- Desktop: 6 cards in row
- Tablet: 3x2 grid
- Mobile: single column stack

---

### Phase 9: Frontend - Narrative Plots

**Create**: `plan/botox/phase-09-frontend-narrative.md`

**Tasks to detail**:
1. NarrativeSection container with tab navigation
2. Recognition plots (2): Temperature Evolution, Seasonal Warming
3. Understanding plots (2): Monthly Distribution, Extremes Inverted
4. Plot data services
5. ExpandableText component for "Read more"

**Include code for**:
- `frontend/src/components/plots/narrative/NarrativeSection.tsx`
- `frontend/src/components/plots/narrative/TabNavigation.tsx`
- `frontend/src/components/common/ExpandableText.tsx`
- All plot components

**Plot types needed** (use D3 or existing charting library):
- Scatter with trend line (LOWESS or rolling average)
- Multi-line chart (seasonal comparison)
- Box plots (monthly distributions)
- Diverging bar chart (extremes)

---

### Phase 10: City Search and Selection

**Create**: `plan/botox/phase-10-city-selection.md`

**Tasks to detail**:
1. City search autocomplete component
2. City-to-grid correlation (Python script)
3. URL-based city selection (shareable links)
4. Redux integration for city selection
5. Update all components on city change

**Include code for**:
- `frontend/src/components/search/CitySearch.tsx`
- `frontend/src/store/slices/citySlice.ts`
- `analysis/cities/correlate_cities_to_grid.py`

**City data source**: Existing `frontend/public/german_cities_p5000.csv` from GeoNames

---

### Phase 11: Documentation and Deployment

**Create**: `plan/botox/phase-11-documentation-deployment.md`

**Tasks to detail**:
1. Architecture documentation
2. Data format documentation
3. Deployment guide (Cloudflare Pages)
4. Operations runbook
5. E2E tests for critical flows
6. Performance optimization

**Include templates for**:
- `documentation/architecture/` structure
- `documentation/deployment/` guides
- E2E test examples

---

## Template for Each Phase Plan

Use the template from [implementation-plan.agent.md](../../.github/agents/implementation-plan.agent.md):

```markdown
---
goal: [Phase X: Brief Description]
version: 1.0
date_created: 2026-02-16
last_updated: 2026-02-16
owner: Sebastian
status: 'Planned'
tags: [phase-X, specific-tags]
---

# Introduction
[Brief description of this phase]

## 1. Requirements & Constraints
[Phase-specific requirements, referencing master plan]

## 2. Implementation Steps
[Detailed tasks with file paths, function signatures, test requirements]

## 3. Alternatives
[Considered alternatives for this phase]

## 4. Dependencies
[Phase dependencies - other phases, external]

## 5. Files
[Complete file list for this phase]

## 6. Testing
[Specific tests for this phase - unit, integration, mocks needed]

## 7. Risks & Assumptions
[Phase-specific risks]

## 8. Multi-Agent Execution Notes
[Parallelization, execution order within phase]

## 9. Related Specifications
[Links to relevant docs]

## 10. Code Reference
[Complete code snippets for implementation]
```

---

## Testing Requirements Per Phase

**CRITICAL**: Every phase must include:

1. **Unit tests** for all new functions
2. **Mock data fixtures** for external dependencies
3. **Integration tests** for combined functionality
4. **Test file locations** following pattern:
   - Frontend: `__tests__/` directories or `.test.tsx` files
   - Python: `tests/` directories or `test_*.py` files

---

## Priority Order for Phase Plan Creation

Recommended order (dependencies):

1. **Phase 1**: Testing Infrastructure (no dependencies)
2. **Phase 2**: Infrastructure/Storage (no dependencies)
3. **Phase 3**: ERA5 Pipeline (depends on Phase 1)
4. **Phase 4**: Tile Generation (depends on Phase 3)
5. **Phase 5**: Metrics Calculation (depends on Phase 3)
6. **Phase 6**: Nightly Jobs (depends on Phase 4, 5)
7. **Phase 7**: Frontend Map (depends on Phase 1, can use mock tiles)
8. **Phase 8**: Frontend Metrics (depends on Phase 1, can use mock data)
9. **Phase 9**: Frontend Narrative (depends on Phase 8)
10. **Phase 10**: City Selection (depends on Phase 7, 8)
11. **Phase 11**: Documentation/Deployment (depends on all)

**Parallelizable**:
- Phases 3-6 (backend) can be developed parallel to Phases 7-10 (frontend) using mock data
- Phase 1 and 2 can run in parallel

---

## Quick Reference: File Paths

```
/home/sebastian/Projects/itishotnow/
├── .github/
│   ├── agents/implementation-plan.agent.md  # Template reference
│   └── workflows/                           # CI/CD workflows
├── analysis/
│   ├── era5/                                # NEW: ERA5 processing
│   ├── tiles/                               # NEW: Tile generation
│   ├── metrics/                             # NEW: Metrics calculation
│   ├── cities/                              # NEW: City correlation
│   └── hyras/                               # REFERENCE: Existing patterns
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── maps/ClimateMap/             # NEW
│   │   │   ├── metrics/                     # NEW
│   │   │   ├── plots/narrative/             # NEW
│   │   │   └── search/                      # NEW
│   │   ├── services/                        # Extend with new services
│   │   ├── store/slices/                    # New slices
│   │   └── __mocks__/                       # NEW: Mock data
│   └── vitest.config.ts                     # NEW
├── jobs/
│   ├── job-era5-daily/                      # NEW
│   ├── job-era5-monthly/                    # NEW
│   └── job-era5-yearly/                     # NEW
├── plan/botox/
│   ├── era5-germany-climate-visualization-1.md  # Master plan
│   └── phase-XX-*.md                        # Detailed phase plans
└── documentation/                           # NEW
```
