---
goal: ERA5 Climate Visualization for Germany - Complete Architecture and Implementation Plan
version: 1.0
date_created: 2026-02-16
last_updated: 2026-02-16
owner: Sebastian
status: 'Planned'
tags: [architecture, feature, climate, era5, visualization, infrastructure]
---

# Introduction

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

This plan describes a comprehensive climate visualization platform for Germany using ERA5 reanalysis data, displayed at 1km tile resolution. The system follows the narrative structure and visualization concepts from the original "botox" plans while optimizing for cost (~€5-15/month) through pre-generated static tiles and edge caching.

**Key Design Decisions:**
1. **Pre-generated static WebP tiles** - Eliminates runtime compute costs
2. **Hetzner Object Storage + Cloudflare CDN** - EU-based storage with free egress, existing CDN for caching
3. **Client-side rendering with MapLibre GL (2D map)** - No server required, 3D globe deferred to future release
4. **GitHub Actions for nightly pipelines** - Free compute for public repositories
5. **Flexible architecture** - Supports future country expansion without code changes
6. **Testing-first approach** - Testing infrastructure established in Phase 1 before feature work

**Scope:** Germany only (initial), with architecture supporting arbitrary geographic expansion.

## 1. Requirements & Constraints

### Functional Requirements

- **REQ-001**: Display temperature anomaly maps for Germany using ERA5 data at 1km visual resolution
- **REQ-002**: Support rolling 12-month anomaly visualization (globe/map equivalent)
- **REQ-003**: Display 4-6 static climate metrics (temperature anomaly, warming rate, record days, etc.)
- **REQ-004**: Support city selection with city-specific metrics and visualizations
- **REQ-005**: Implement narrative sections with interactive plots (Recognition, Understanding, Response)
- **REQ-006**: Support land areas only, including coastal islands (exclude ocean)
- **REQ-007**: Support monthly data updates via nightly pipeline
- **REQ-008**: Support arbitrary time range (initial: 10 years, 2016-2026)
- **REQ-009**: Provide responsive design for mobile and desktop

### Non-Functional Requirements

- **NFR-001**: Monthly operational costs ≤ €15/month (target: €5-10/month)
- **NFR-002**: Initial page load < 3 seconds on 4G connection
- **NFR-003**: Map tile loading < 500ms per visible viewport
- **NFR-004**: Support 10,000+ daily visitors without infrastructure changes
- **NFR-005**: Data pipeline completes nightly < 60 minutes

### Technical Constraints

- **CON-001**: ERA5 native resolution is 0.25° (~28km) - interpolation required for 1km display
- **CON-002**: ERA5-Land resolution is 0.1° (~9km) - can be interpolated to 1km
- **CON-003**: HYRAS 1km data available for Germany (1951-2024) as reference/validation
- **CON-004**: Maximum GitHub Actions runtime: 6 hours (free tier)
- **CON-005**: Cloudflare R2 free tier: 10GB storage, 1M reads/month, 10M writes/month

### Security Requirements

- **SEC-001**: No user data collection (privacy-first design)
- **SEC-002**: All data sources must be publicly available (open data)
- **SEC-003**: No API keys exposed in frontend code

### Architecture Guidelines

- **GUD-001**: Follow existing codebase patterns where applicable (Redux, services, createDataSlice)
- **GUD-002**: Use TypeScript for all frontend code with strict mode
- **GUD-003**: Use Python for all data processing pipelines
- **GUD-004**: Comprehensive documentation for all components
- **GUD-005**: Test coverage > 80% for critical paths
- **GUD-006**: All tile generation must be deterministic and reproducible

### Patterns to Follow

- **PAT-001**: Use `createDataSlice` factory for Redux state management (see Code Reference 10.1)
- **PAT-002**: Use service layer pattern for data fetching (see Code Reference 10.2)
- **PAT-003**: Use PlotView component pattern for visualizations (see Code Reference 10.3)
- **PAT-004**: Use StatCard component pattern for metrics display (see Code Reference 10.4)
- **PAT-005**: Follow existing job structure (Dockerfile, entrypoint.sh, src/) for pipelines

## 2. Implementation Steps

### Implementation Phase 1: Testing Infrastructure & Development Setup

**GOAL-001**: Establish testing infrastructure and development environment before any feature work

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-001 | Configure Vitest for React/TypeScript testing (vitest.config.ts, jsdom, @testing-library/react) | | |
| TASK-002 | Configure pytest for Python testing (pyproject.toml, conftest.py, pytest-cov) | | |
| TASK-003 | Add test scripts to package.json (`test`, `test:coverage`, `test:watch`) | | |
| TASK-004 | Create mock data fixtures directory structure (`__mocks__/`, `fixtures/`) | | |
| TASK-005 | Set up GitHub Actions CI workflow for running tests on PR/push | | |
| TASK-006 | Create development environment setup script (`scripts/setup-dev.sh`) | | |
| TASK-007 | Configure environment variables schema (`.env.example`, validation) | | |

**Completion Criteria:**
- `npm test` runs successfully with example test
- `pytest` runs successfully with example test  
- CI workflow runs tests on every PR
- Development environment reproducible from fresh clone

---

### Implementation Phase 2: ERA5 Data Pipeline - Core

**GOAL-002**: Build the core ERA5 data download and processing pipeline

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-007 | Create `analysis/era5/fetch_era5_data.py` - download ERA5/ERA5-Land NetCDF from CDS | | |
| TASK-008 | Create `analysis/era5/config.py` - centralized configuration (bounds, resolution, variables) | | |
| TASK-009 | Create `analysis/era5/interpolate_to_grid.py` - interpolate ERA5 to 1km grid using scipy/xarray | | |
| TASK-010 | Create `analysis/era5/apply_land_mask.py` - filter to land-only using Natural Earth data | | |
| TASK-011 | Create `analysis/era5/calculate_anomalies.py` - compute anomalies vs 1961-1990 reference | | |
| TASK-012 | Create `analysis/era5/types.py` - Python dataclasses for pipeline data structures | | |
| TASK-013 | Write unit tests for all ERA5 processing modules | | |
| TASK-014 | Create integration test with sample ERA5 data subset | | |

**Completion Criteria:**
- Pipeline can download, interpolate, and calculate anomalies for one month
- Land mask correctly excludes ocean, includes German islands (Sylt, Rügen, etc.)
- All tests pass

---

### Implementation Phase 3: Tile Generation Pipeline

**GOAL-003**: Generate WebP map tiles from processed ERA5 data

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-015 | Create `analysis/tiles/generate_tiles.py` - convert GeoTIFF to WebP tile pyramid | | |
| TASK-016 | Create `analysis/tiles/color_ramps.py` - define color scales (diverging blue-red for anomalies) | | |
| TASK-017 | Create `analysis/tiles/tile_config.py` - zoom levels, tile size, coordinate system config | | |
| TASK-018 | Create `analysis/tiles/upload_tiles.py` - upload tiles to R2 with content-type headers | | |
| TASK-019 | Implement tile naming convention: `/{year}/{month}/{z}/{x}/{y}.webp` | | |
| TASK-020 | Add transparency support for land boundaries (alpha channel) | | |
| TASK-021 | Write unit tests for tile generation | | |
| TASK-022 | Create validation script to verify tile coverage and integrity | | |

**Completion Criteria:**
- Tiles generated at zoom levels 6-10 for Germany
- Color ramp matches specification (-2°C to +3°C diverging)
- Tiles have transparent background (land only visible)
- All tiles accessible via R2 URL pattern

---

### Implementation Phase 4: Metrics Calculation Pipeline

**GOAL-004**: Calculate static climate metrics per grid cell and aggregated

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-023 | Create `analysis/metrics/calculate_annual_anomaly.py` - yearly temperature anomaly | | |
| TASK-024 | Create `analysis/metrics/calculate_warming_rate.py` - linear regression trend | | |
| TASK-025 | Create `analysis/metrics/calculate_record_days.py` - count daily records broken | | |
| TASK-026 | Create `analysis/metrics/calculate_seasonal_warming.py` - per-season anomalies | | |
| TASK-027 | Create `analysis/metrics/calculate_threshold_days.py` - hot/ice/frost days counts | | |
| TASK-028 | Create `analysis/metrics/aggregate_metrics.py` - aggregate to city/country level | | |
| TASK-029 | Create `analysis/metrics/export_metrics.py` - export to JSON for frontend | | |
| TASK-030 | Write unit tests for all metric calculations | | |

**Completion Criteria:**
- All 6 metrics calculated per grid cell and aggregated
- JSON output matches schema expected by frontend
- Metrics validated against HYRAS reference data where overlapping

---

### Implementation Phase 5: Nightly Job Orchestration

**GOAL-005**: Create Docker jobs and GitHub Actions for automated nightly processing

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-031 | Create `jobs/job-era5-daily/Dockerfile` - daily update job container | | |
| TASK-032 | Create `jobs/job-era5-daily/entrypoint.sh` - validate env vars, run pipeline | | |
| TASK-033 | Create `jobs/job-era5-daily/src/process_daily.py` - orchestrate daily pipeline | | |
| TASK-034 | Create `jobs/job-era5-monthly/` - monthly tile regeneration job | | |
| TASK-035 | Create `jobs/job-era5-yearly/` - yearly metrics recalculation job | | |
| TASK-036 | Create `.github/workflows/era5-daily-pipeline.yml` - scheduled daily action | | |
| TASK-037 | Create `.github/workflows/era5-monthly-pipeline.yml` - scheduled monthly action | | |
| TASK-038 | Add monitoring/alerting for pipeline failures (GitHub Actions notifications) | | |
| TASK-039 | Write integration tests for complete pipeline execution | | |

**Completion Criteria:**
- Daily job runs successfully < 30 minutes
- Monthly job regenerates tiles < 60 minutes
- Failure notifications sent via GitHub Actions
- All jobs testable locally via Docker

---

### Implementation Phase 6: Frontend - Map Visualization

**GOAL-006**: Implement interactive map with tile overlay using MapLibre GL

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-040 | Install MapLibre GL JS dependency and TypeScript types | | |
| TASK-041 | Create `frontend/src/components/maps/ClimateMap/ClimateMap.tsx` - base map component | | |
| TASK-042 | Create `frontend/src/components/maps/ClimateMap/TileLayer.tsx` - anomaly tile overlay | | |
| TASK-043 | Create `frontend/src/components/maps/ClimateMap/CityMarkers.tsx` - clickable city markers | | |
| TASK-044 | Create `frontend/src/components/maps/ClimateMap/Legend.tsx` - color scale legend | | |
| TASK-045 | Create `frontend/src/components/maps/ClimateMap/DateSelector.tsx` - month/year picker | | |
| TASK-046 | Create `frontend/src/store/slices/mapSlice.ts` - map state (view, selected month) | | |
| TASK-047 | Create `frontend/src/hooks/useMapTiles.ts` - tile URL generation hook | | |
| TASK-048 | Implement responsive behavior (pan, zoom, mobile gestures) | | |
| TASK-049 | Write component tests for all map components | | |

**Completion Criteria:**
- Map displays Germany with anomaly overlay
- Cities clickable, trigger selection
- Month/year selector updates displayed tiles
- Smooth performance on mobile (60fps pan/zoom)

---

### Implementation Phase 7: Frontend - Static Metrics Cards

**GOAL-007**: Implement climate metrics display cards with city-specific updates

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-050 | Create `frontend/src/services/MetricsService.ts` - fetch metrics JSON | | |
| TASK-051 | Create `frontend/src/store/slices/metricsSlice.ts` - metrics state using createDataSlice | | |
| TASK-052 | Create `frontend/src/components/metrics/MetricsRow.tsx` - horizontal metrics layout | | |
| TASK-053 | Create `frontend/src/components/metrics/cards/AnnualAnomalyCard.tsx` | | |
| TASK-054 | Create `frontend/src/components/metrics/cards/WarmingRateCard.tsx` | | |
| TASK-055 | Create `frontend/src/components/metrics/cards/RecordDaysCard.tsx` | | |
| TASK-056 | Create `frontend/src/components/metrics/cards/SeasonalWarmingCard.tsx` | | |
| TASK-057 | Create `frontend/src/components/metrics/cards/ThresholdDaysCard.tsx` | | |
| TASK-058 | Create `frontend/src/components/metrics/cards/ComfortableDaysCard.tsx` | | |
| TASK-059 | Implement city-specific metric loading on city selection | | |
| TASK-060 | Write component tests for all metric cards | | |

**Completion Criteria:**
- 6 metric cards display correctly
- Metrics update when city selected
- Loading/error states handled gracefully
- Mobile responsive (vertical stack)

---

### Implementation Phase 8: Frontend - Narrative Plots

**GOAL-008**: Implement narrative section with interactive climate plots

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-061 | Create `frontend/src/components/plots/narrative/NarrativeSection.tsx` - tabbed container | | |
| TASK-062 | Create `frontend/src/components/plots/narrative/RecognitionPlots/TemperatureEvolution.tsx` | | |
| TASK-063 | Create `frontend/src/components/plots/narrative/RecognitionPlots/SeasonalWarming.tsx` | | |
| TASK-064 | Create `frontend/src/components/plots/narrative/UnderstandingPlots/MonthlyDistribution.tsx` | | |
| TASK-065 | Create `frontend/src/components/plots/narrative/UnderstandingPlots/ExtremesInverted.tsx` | | |
| TASK-066 | Create `frontend/src/components/plots/narrative/ResponsePlots/FutureProjections.tsx` | | |
| TASK-067 | Create plot data services for each narrative plot type | | |
| TASK-068 | Implement plot animations and transitions | | |
| TASK-069 | Write integration tests for narrative section | | |

**Completion Criteria:**
- All narrative plots render correctly
- Plots update on city selection
- Smooth tab transitions
- Methodology notes displayed via info icons

---

### Implementation Phase 9: City Search and Selection

**GOAL-009**: Implement city search functionality with station correlation

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-070 | Create/update `frontend/src/services/CityService.ts` - extend for ERA5 grid correlation | | |
| TASK-071 | Create `frontend/src/components/search/CitySearch.tsx` - autocomplete search | | |
| TASK-072 | Create `frontend/src/store/slices/citySlice.ts` - city selection state | | |
| TASK-073 | Create `analysis/cities/correlate_cities_to_grid.py` - map cities to nearest grid cell | | |
| TASK-074 | Generate city correlation data (5000+ German cities) | | |
| TASK-075 | Implement URL-based city selection (shareable links) | | |
| TASK-076 | Write tests for search and selection | | |

**Completion Criteria:**
- City search returns results < 100ms
- City selection updates URL
- All components react to city selection
- Works on mobile with touch keyboard

---

### Implementation Phase 10: Documentation and Testing

**GOAL-010**: Comprehensive documentation and test coverage

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-077 | Create `documentation/architecture/era5-pipeline.md` - pipeline architecture docs | | |
| TASK-078 | Create `documentation/architecture/frontend.md` - frontend architecture docs | | |
| TASK-079 | Create `documentation/data-formats/` - schema documentation for all data formats | | |
| TASK-080 | Create `documentation/deployment/` - deployment and operations guide | | |
| TASK-081 | Create `documentation/api/` - internal API documentation | | |
| TASK-082 | Add JSDoc comments to all TypeScript functions | | |
| TASK-083 | Add docstrings to all Python functions | | |
| TASK-084 | Set up coverage reporting in CI | | |
| TASK-085 | Create end-to-end tests for critical user flows | | |

**Completion Criteria:**
- All public functions documented
- Test coverage > 80%
- Documentation readable by new contributors
- E2E tests pass in CI

---

### Implementation Phase 11: Deployment and Operations

**GOAL-011**: Production deployment with monitoring

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-086 | Configure Cloudflare Pages deployment for frontend | | |
| TASK-087 | Set up custom domain and SSL | | |
| TASK-088 | Configure cache invalidation for tile updates | | |
| TASK-089 | Set up uptime monitoring (Cloudflare or external) | | |
| TASK-090 | Create runbook for common operations (tile regeneration, rollback) | | |
| TASK-091 | Set up cost monitoring alerts | | |
| TASK-092 | Performance testing and optimization | | |

**Completion Criteria:**
- Production site accessible and functional
- SSL certificate valid
- Monitoring operational
- Cost tracking in place

## 3. Alternatives

- **ALT-001**: **Server-side rendering with database** - Rejected due to cost (~€50+/month for VPS + database). Pre-generated tiles achieve same visual result at ~€5/month.

- **ALT-002**: **deck.gl instead of MapLibre GL** - Considered for 3D globe support. Rejected for initial implementation due to larger bundle size and complexity. Can be added later for globe view.

- **ALT-003**: **Vector tiles (MVT) instead of raster tiles (WebP)** - Considered for smaller file sizes. Rejected because climate anomaly data benefits from pre-rendered color ramps; vector tiles would require client-side computation.

- **ALT-004**: **PostgreSQL/PostGIS with tile server** - Rejected due to ongoing server costs. Only reconsidered if dynamic queries become essential feature.

- **ALT-005**: **Keep HYRAS as data source** - Considered since HYRAS is already 1km and German-specific. Rejected because project goal is extensibility to other countries; ERA5 provides global coverage for future expansion.

- **ALT-006**: **Hetzner Object Storage instead of Cloudflare R2** - Considered due to lower storage costs (€0.005/GB vs €0.014/GB). Rejected because Cloudflare R2 has free egress vs Hetzner's €1/TB; total cost with bandwidth favors R2.

## 4. Dependencies

### External Data Dependencies

- **DEP-001**: ERA5/ERA5-Land data from Copernicus Climate Data Store (CDS)
- **DEP-002**: Natural Earth land mask data for filtering ocean
- **DEP-003**: German city list (existing: `german_cities_p5000.csv`)

### Python Dependencies (Pipeline)

- **DEP-004**: `xarray` - NetCDF handling and grid operations
- **DEP-005**: `rasterio` - GeoTIFF read/write
- **DEP-006**: `scipy` - Interpolation (bicubic, bilinear)
- **DEP-007**: `rio-tiler` - Tile generation from GeoTIFF
- **DEP-008**: `boto3` - S3/R2 upload
- **DEP-009**: `cdsapi` - Copernicus CDS API client
- **DEP-010**: `numpy` - Numerical operations
- **DEP-011**: `pandas` - Data manipulation
- **DEP-012**: `pytest` - Testing framework

### Frontend Dependencies

- **DEP-013**: `maplibre-gl` - Map rendering
- **DEP-014**: `@maplibre/maplibre-gl-js` - TypeScript types
- **DEP-015**: `react`, `react-dom` - UI framework (existing)
- **DEP-016**: `@reduxjs/toolkit` - State management (existing)
- **DEP-017**: `vitest` - Testing framework
- **DEP-018**: `d3` - Data visualization for plots

### Infrastructure Dependencies

- **DEP-019**: Hetzner Object Storage account (EU-based, free egress)
- **DEP-020**: Cloudflare Pages (existing CDN) or Vercel/Netlify
- **DEP-021**: GitHub Actions (for CI/CD and scheduled jobs)
- **DEP-022**: Copernicus CDS account (free registration required)

## 5. Files

### Pipeline Files (Python)

- **FILE-001**: `analysis/era5/config.py` - NEW - Centralized ERA5 configuration
- **FILE-002**: `analysis/era5/fetch_era5_data.py` - NEW - CDS download
- **FILE-003**: `analysis/era5/interpolate_to_grid.py` - NEW - Grid interpolation
- **FILE-004**: `analysis/era5/apply_land_mask.py` - NEW - Land filtering
- **FILE-005**: `analysis/era5/calculate_anomalies.py` - NEW - Anomaly calculation
- **FILE-006**: `analysis/era5/types.py` - NEW - Data structure definitions
- **FILE-007**: `analysis/tiles/generate_tiles.py` - NEW - Tile generation
- **FILE-008**: `analysis/tiles/color_ramps.py` - NEW - Color scale definitions
- **FILE-009**: `analysis/tiles/tile_config.py` - NEW - Tile configuration
- **FILE-010**: `analysis/tiles/upload_tiles.py` - NEW - R2 upload
- **FILE-011**: `analysis/metrics/calculate_annual_anomaly.py` - NEW - Yearly anomaly
- **FILE-012**: `analysis/metrics/calculate_warming_rate.py` - NEW - Trend calculation
- **FILE-013**: `analysis/metrics/calculate_record_days.py` - NEW - Record counting
- **FILE-014**: `analysis/metrics/calculate_seasonal_warming.py` - NEW - Seasonal stats
- **FILE-015**: `analysis/metrics/calculate_threshold_days.py` - NEW - Threshold counting
- **FILE-016**: `analysis/metrics/aggregate_metrics.py` - NEW - Spatial aggregation
- **FILE-017**: `analysis/metrics/export_metrics.py` - NEW - JSON export
- **FILE-018**: `analysis/cities/correlate_cities_to_grid.py` - NEW - City-grid mapping

### Job Files

- **FILE-019**: `jobs/job-era5-daily/Dockerfile` - NEW - Daily job container
- **FILE-020**: `jobs/job-era5-daily/entrypoint.sh` - NEW - Job entry point
- **FILE-021**: `jobs/job-era5-daily/src/process_daily.py` - NEW - Daily orchestrator
- **FILE-022**: `jobs/job-era5-monthly/Dockerfile` - NEW - Monthly job container
- **FILE-023**: `jobs/job-era5-monthly/entrypoint.sh` - NEW - Monthly entry point
- **FILE-024**: `jobs/job-era5-monthly/src/process_monthly.py` - NEW - Monthly orchestrator
- **FILE-025**: `jobs/job-era5-yearly/Dockerfile` - NEW - Yearly job container
- **FILE-026**: `jobs/job-era5-yearly/src/process_yearly.py` - NEW - Yearly orchestrator

### GitHub Actions

- **FILE-027**: `.github/workflows/era5-daily-pipeline.yml` - NEW - Daily schedule
- **FILE-028**: `.github/workflows/era5-monthly-pipeline.yml` - NEW - Monthly schedule
- **FILE-029**: `.github/workflows/era5-yearly-pipeline.yml` - NEW - Yearly schedule

### Frontend Files

- **FILE-030**: `frontend/src/components/maps/ClimateMap/ClimateMap.tsx` - NEW - Map component
- **FILE-031**: `frontend/src/components/maps/ClimateMap/TileLayer.tsx` - NEW - Tile overlay
- **FILE-032**: `frontend/src/components/maps/ClimateMap/CityMarkers.tsx` - NEW - City markers
- **FILE-033**: `frontend/src/components/maps/ClimateMap/Legend.tsx` - NEW - Color legend
- **FILE-034**: `frontend/src/components/maps/ClimateMap/DateSelector.tsx` - NEW - Date picker
- **FILE-035**: `frontend/src/components/metrics/MetricsRow.tsx` - NEW - Metrics container
- **FILE-036**: `frontend/src/components/metrics/cards/AnnualAnomalyCard.tsx` - NEW
- **FILE-037**: `frontend/src/components/metrics/cards/WarmingRateCard.tsx` - NEW
- **FILE-038**: `frontend/src/components/metrics/cards/RecordDaysCard.tsx` - NEW
- **FILE-039**: `frontend/src/components/metrics/cards/SeasonalWarmingCard.tsx` - NEW
- **FILE-040**: `frontend/src/components/metrics/cards/ThresholdDaysCard.tsx` - NEW
- **FILE-041**: `frontend/src/components/metrics/cards/ComfortableDaysCard.tsx` - NEW
- **FILE-042**: `frontend/src/components/plots/narrative/NarrativeSection.tsx` - NEW
- **FILE-043**: `frontend/src/components/plots/narrative/RecognitionPlots/TemperatureEvolution.tsx` - NEW
- **FILE-044**: `frontend/src/components/plots/narrative/RecognitionPlots/SeasonalWarming.tsx` - NEW
- **FILE-045**: `frontend/src/components/plots/narrative/UnderstandingPlots/MonthlyDistribution.tsx` - NEW
- **FILE-046**: `frontend/src/components/plots/narrative/UnderstandingPlots/ExtremesInverted.tsx` - NEW
- **FILE-047**: `frontend/src/components/search/CitySearch.tsx` - NEW - City search
- **FILE-048**: `frontend/src/services/MetricsService.ts` - NEW - Metrics fetching
- **FILE-049**: `frontend/src/services/TileService.ts` - NEW - Tile URL generation
- **FILE-050**: `frontend/src/store/slices/mapSlice.ts` - NEW - Map state
- **FILE-051**: `frontend/src/store/slices/metricsSlice.ts` - NEW - Metrics state
- **FILE-052**: `frontend/src/hooks/useMapTiles.ts` - NEW - Tile hook

### Documentation Files

- **FILE-053**: `documentation/architecture/era5-pipeline.md` - NEW
- **FILE-054**: `documentation/architecture/frontend.md` - NEW
- **FILE-055**: `documentation/data-formats/tiles.md` - NEW
- **FILE-056**: `documentation/data-formats/metrics.md` - NEW
- **FILE-057**: `documentation/deployment/cloudflare.md` - NEW
- **FILE-058**: `documentation/deployment/runbook.md` - NEW

### Test Files

- **FILE-059**: `analysis/era5/tests/test_fetch_era5_data.py` - NEW
- **FILE-060**: `analysis/era5/tests/test_interpolate.py` - NEW
- **FILE-061**: `analysis/era5/tests/test_anomalies.py` - NEW
- **FILE-062**: `analysis/tiles/tests/test_generate_tiles.py` - NEW
- **FILE-063**: `analysis/metrics/tests/test_calculations.py` - NEW
- **FILE-064**: `frontend/src/components/maps/__tests__/ClimateMap.test.tsx` - NEW
- **FILE-065**: `frontend/src/components/metrics/__tests__/MetricsRow.test.tsx` - NEW

## 6. Testing

### Unit Tests

- **TEST-001**: ERA5 data fetching correctly downloads and validates NetCDF files
- **TEST-002**: Grid interpolation produces correct 1km resolution output
- **TEST-003**: Land mask correctly includes German islands (Sylt, Rügen, Helgoland, etc.)
- **TEST-004**: Anomaly calculation matches reference values from HYRAS overlap
- **TEST-005**: Tile generation produces valid WebP files at expected zoom levels
- **TEST-006**: Color ramp mapping correctly handles edge cases (-3°C, +4°C, null values)
- **TEST-007**: Metric calculations produce correct values for known test data
- **TEST-008**: R2 upload correctly sets content-type and cache headers
- **TEST-009**: Frontend components render without errors with mock data
- **TEST-010**: Redux slices handle loading, success, and error states correctly

### Integration Tests

- **TEST-011**: Complete pipeline execution produces valid tiles for test month
- **TEST-012**: Frontend loads and displays tiles from R2 bucket
- **TEST-013**: City selection updates all components (map, metrics, plots)
- **TEST-014**: Date selection correctly switches tile layer source
- **TEST-015**: Mobile responsive layout renders correctly at 375px width

### End-to-End Tests

- **TEST-016**: User can load page, select city, and view city-specific data
- **TEST-017**: User can navigate date selector and see different month data
- **TEST-018**: User can search for city and select from results
- **TEST-019**: Shared URL with city parameter loads correct city
- **TEST-020**: Page load performance meets NFR-002 (< 3s on 4G)

### Validation Tests

- **TEST-021**: Generated tiles match visual reference (screenshot comparison)
- **TEST-022**: Metric values within expected ranges for test cities
- **TEST-023**: No console errors during normal operation
- **TEST-024**: Accessibility audit passes WCAG 2.1 AA

## 7. Risks & Assumptions

### Risks

- **RISK-001**: ERA5/ERA5-Land API rate limiting or downtime delays pipeline
  - **Mitigation**: Implement retry logic with exponential backoff; maintain local cache of last successful download
  
- **RISK-002**: Interpolation from 28km to 1km introduces visual artifacts
  - **Mitigation**: Use bicubic interpolation with edge handling; compare against HYRAS reference; adjust smoothing if needed
  
- **RISK-003**: GitHub Actions runtime exceeds 6-hour limit for full regeneration
  - **Mitigation**: Split into smaller jobs; use job matrix for parallel processing; consider Hetzner runner for large jobs (~€5/month)
  
- **RISK-004**: Hetzner Object Storage limitations (1TB/bucket, no versioning)
  - **Mitigation**: Climate tiles <1GB total; versioning not needed for immutable tiles; can migrate to Scaleway if limits hit
  
- **RISK-005**: MapLibre GL rendering issues on older mobile browsers
  - **Mitigation**: Feature detection with fallback to static image; test on BrowserStack
  
- **RISK-006**: Land mask excludes small but important islands
  - **Mitigation**: Use high-resolution Natural Earth data (1:10m); manually verify German islands in test

### Assumptions

- **ASSUMPTION-001**: ERA5 data remains freely available via Copernicus CDS
- **ASSUMPTION-002**: Cloudflare R2 free tier (10GB, 1M reads) sufficient for initial deployment
- **ASSUMPTION-003**: GitHub Actions free tier sufficient for daily/monthly pipelines
- **ASSUMPTION-004**: User has modern browser with WebGL support (90%+ of traffic)
- **ASSUMPTION-005**: 1km visual resolution sufficient for climate data (actual ERA5 is 28km)
- **ASSUMPTION-006**: German city list (5000+) covers all user needs initially
- **ASSUMPTION-007**: Monthly update frequency sufficient (vs. daily updates)

## 8. Multi-Agent Execution Notes

### Execution Order

**Parallel tasks (can run simultaneously):**
- TASK-001 to TASK-006 (Infrastructure) - independent setup tasks
- TASK-007 to TASK-014 (ERA5 Pipeline) - can start after TASK-004 (dev environment)
- TASK-040 to TASK-049 (Frontend Map) - independent of pipeline
- TASK-050 to TASK-060 (Frontend Metrics) - independent of map

**Sequential dependencies:**
- Phase 2 (ERA5 Pipeline) → Phase 3 (Tile Generation) → Phase 5 (Nightly Jobs)
- Phase 4 (Metrics) depends on Phase 2 completion
- Phase 6-9 (Frontend) can proceed in parallel with Phase 2-5 using mock data
- Phase 10 (Documentation) should follow each phase completion
- Phase 11 (Deployment) requires all previous phases

### Agent Context Requirements

Each phase can be executed by a separate agent session. Provide these context files:

**Phase 1 (Infrastructure):**
- This plan document
- `.env.example` template (to be created)
- Existing GitHub Actions workflows as reference

**Phase 2-4 (Pipeline):**
- This plan document, sections 2.1-2.4
- Code Reference 10.5, 10.6 (existing pipeline patterns)
- ERA5 API documentation link

**Phase 6-9 (Frontend):**
- This plan document, sections 2.6-2.9
- Code Reference 10.1-10.4 (existing frontend patterns)
- MapLibre GL documentation link

### Validation Checkpoints

- **After Phase 1**: `scripts/setup-dev.sh` runs successfully; R2 bucket accessible
- **After Phase 2**: `python -m pytest analysis/era5/tests/` passes; sample data processed
- **After Phase 3**: Tiles visible at R2 URL; tile validation script passes
- **After Phase 4**: Metrics JSON generated; values within expected ranges
- **After Phase 5**: Docker jobs build and run locally; GitHub Actions workflows valid YAML
- **After Phase 6**: Map renders with test tile data; zoom/pan functional
- **After Phase 7**: All metric cards render with mock data; loading states work
- **After Phase 9**: City search returns results; selection updates state
- **After Phase 10**: Coverage report shows >80%; docs build without errors
- **After Phase 11**: Production URL returns 200; Lighthouse score >90

## 9. Related Specifications / Further Reading

### Original Planning Documents
- [project-overview.md](plan/botox/project-overview.md) - Original global project overview
- [narrative.md](plan/botox/narrative.md) - Narrative structure and plot specifications
- [globe-plot.md](plan/botox/globe-plot.md) - Globe visualization specification
- [static-metrics.md](plan/botox/static-metrics.md) - Metrics specification

### External Documentation
- [ERA5 Documentation](https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels-monthly-means)
- [ERA5-Land Documentation](https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-land-monthly-means)
- [MapLibre GL JS](https://maplibre.org/maplibre-gl-js/docs/)
- [Cloudflare R2 Documentation](https://developers.cloudflare.com/r2/)
- [Natural Earth Data](https://www.naturalearthdata.com/)

### Existing Codebase References
- [HYRAS Processing](analysis/hyras/) - Reference for NetCDF processing patterns
- [Job Structure](jobs/) - Reference for Docker job patterns
- [Frontend Store](frontend/src/store/) - Reference for Redux patterns

## 10. Code Reference (REQUIRED)

This section provides code context for implementing each phase.

### 10.1 createDataSlice Factory Pattern

**File**: `frontend/src/store/factories/createDataSlice.ts`

```typescript
// Existing factory pattern for Redux slices - USE THIS for new slices
export const createDataSlice = <TData, TArgs, TShape extends StateShape>({
    name,
    fetchFn,
    stateShape,
    cache,
}: CreateDataSliceOptions<TData, TArgs, TShape>) => {
    // Returns { slice, actions, selectors }
    // Handles loading, success, error states automatically
    // Supports caching strategies: 'all', 'by-key', 'by-context'
};

// Usage example for metrics slice (TASK-051):
export const { slice: metricsSlice, actions: metricsActions, selectors: metricsSelectors } = 
    createDataSlice<MetricsData, { cityId?: string }, 'keyed'>({
        name: 'metrics',
        fetchFn: async ({ cityId }) => fetchMetrics(cityId),
        stateShape: 'keyed',
        cache: { strategy: 'by-key', keyExtractor: ({ cityId }) => cityId || 'global', ttl: 3600000 }
    });
```

**Notes**: All new data slices should use this factory. See `frontend/src/store/slices/` for examples.

### 10.2 Service Layer Pattern

**File**: `frontend/src/services/LiveDataService.ts`

```typescript
// Existing service pattern - USE THIS for new services
import { fetchAndParseCSV, buildUrl } from '../utils/fetchUtils';

export const fetchLiveData = async (): Promise<LiveDataResponse> => {
    return fetchAndParseCSV<LiveDataResponse>(
        buildUrl('/station_data/10min_station_data.csv', true, 'yyyyLLddHH'),
        (rows) => {
            // Parse rows into typed response
            const stations: Record<string, Station> = {};
            const stationData: Record<string, StationData> = {};
            // ... parsing logic
            return { stations, stationData };
        },
        { 
            validateHeaders: ['station_id', 'station_name', 'lat', 'lon', 'temperature'],
            errorContext: 'live station data' 
        }
    );
};

// For MetricsService.ts (TASK-050), adapt pattern for JSON:
export const fetchMetrics = async (cityId?: string): Promise<MetricsData> => {
    const url = cityId 
        ? `/data/metrics/cities/${cityId}.json`
        : `/data/metrics/germany.json`;
    const response = await fetch(buildUrl(url, true));
    if (!response.ok) throw new Error(`Failed to fetch metrics: ${response.status}`);
    return response.json();
};
```

### 10.3 PlotView Component Pattern

**File**: `frontend/src/components/common/PlotView/PlotView.tsx`

```typescript
// Existing two-column layout pattern
interface PlotViewProps {
    leftContent: React.ComponentType;
    rightContent: React.ComponentType;
    config?: { leftWidth?: number; darkMode?: boolean };
}

// Factory function for creating plot views
export const createPlotView = ({ leftContent, rightContent, config }: PlotViewProps) => {
    return function PlotViewComponent() {
        return (
            <div className={styles.plotView}>
                <div className={styles.left} style={{ width: `${config?.leftWidth || 50}%` }}>
                    {React.createElement(leftContent)}
                </div>
                <div className={styles.right}>
                    {React.createElement(rightContent)}
                </div>
            </div>
        );
    };
};

// Usage for ClimateMap (TASK-040):
const ClimateMapView = createPlotView({
    leftContent: ClimateMapLeftSide,  // Map component
    rightContent: ClimateMapRightSide, // Legend + controls
    config: { leftWidth: 60, darkMode: true }
});
```

### 10.4 StatCard Component Pattern

**File**: `frontend/src/components/plots/Stats/StatCard.tsx`

```typescript
// Existing StatCard pattern - REUSE for metric cards
interface StatCardProps {
    title: string;
    value: string | number;
    subtitle?: string;
    footnote?: string;
    infoText?: string;  // For info tooltip
    isLoading?: boolean;
    error?: string;
    width?: number | string;
    colorScheme?: 'default' | 'warm' | 'cool';
}

export const StatCard: React.FC<StatCardProps> = ({
    title, value, subtitle, footnote, infoText, isLoading, error, width, colorScheme
}) => {
    if (isLoading) return <StatCardSkeleton width={width} />;
    if (error) return <StatCardError error={error} width={width} />;
    
    return (
        <div className={cn(styles.card, styles[colorScheme || 'default'])} style={{ width }}>
            <div className={styles.title}>
                {title}
                {infoText && <InfoTooltip text={infoText} />}
            </div>
            <div className={styles.value}>{value}</div>
            {subtitle && <div className={styles.subtitle}>{subtitle}</div>}
            {footnote && <div className={styles.footnote}>{footnote}</div>}
        </div>
    );
};

// Usage for AnnualAnomalyCard (TASK-053):
export const AnnualAnomalyCard: React.FC = () => {
    const { data, isLoading, error } = useMetrics();
    return (
        <StatCard
            title="Temperaturanomalie"
            value={data ? `+${data.annualAnomaly.toFixed(1)}°C` : '-'}
            subtitle={`${data?.year} vs. 1961-1990`}
            infoText="Differenz der Jahresmitteltemperatur zum langjährigen Durchschnitt"
            isLoading={isLoading}
            error={error}
            colorScheme="warm"
        />
    );
};
```

### 10.5 ERA5/HYRAS NetCDF Processing Pattern

**File**: `analysis/hyras/extract_hyras_data.py`

```python
# Existing NetCDF processing pattern - ADAPT for ERA5
import xarray as xr
import numpy as np
from pathlib import Path

def find_nearest_grid_point(centers_lat: np.ndarray, centers_lon: np.ndarray, lat: float, lon: float) -> tuple[int, int]:
    """Find indices of nearest grid point to given coordinates."""
    lat_diff = centers_lat - lat
    lon_diff = centers_lon - lon
    dist_squared = lat_diff**2 + lon_diff**2
    y, x = np.unravel_index(np.argmin(dist_squared), dist_squared.shape)
    return int(y), int(x)

def extract_timeseries_at_point(ds: xr.Dataset, y: int, x: int, variable: str) -> np.ndarray:
    """Extract time series for a specific grid point."""
    return ds[variable].isel(y=y, x=x).values

# For ERA5 (TASK-007), adapt coordinate names:
# ERA5 uses 'latitude', 'longitude' instead of 'y', 'x'
# ERA5 uses 't2m' (2m temperature) instead of 'tas'
def load_era5_data(file_path: Path, bounds: dict) -> xr.Dataset:
    """Load ERA5 NetCDF with geographic subsetting."""
    ds = xr.open_dataset(file_path)
    # Subset to Germany bounds
    ds = ds.sel(
        latitude=slice(bounds['north'], bounds['south']),  # ERA5: north first
        longitude=slice(bounds['west'], bounds['east'])
    )
    return ds
```

### 10.6 Tile Generation Pattern (NEW - Reference Implementation)

**File**: `analysis/tiles/generate_tiles.py` (to be created)

```python
# Reference pattern for tile generation using rio-tiler
from rio_tiler.io import Reader
from rio_tiler.colormap import cmap
from rio_tiler.models import ImageData
import numpy as np
from pathlib import Path

def generate_tiles_for_geotiff(
    geotiff_path: Path,
    output_dir: Path,
    min_zoom: int = 6,
    max_zoom: int = 10,
    colormap_name: str = 'rdbu_r',  # Diverging: red (hot) to blue (cold)
    vmin: float = -3.0,
    vmax: float = 3.0,
) -> int:
    """Generate WebP map tiles from a GeoTIFF file.
    
    Args:
        geotiff_path: Path to input GeoTIFF with anomaly data
        output_dir: Base directory for tiles (will create z/x/y structure)
        min_zoom: Minimum zoom level
        max_zoom: Maximum zoom level
        colormap_name: Rio-tiler colormap name
        vmin, vmax: Value range for color mapping
        
    Returns:
        Number of tiles generated
    """
    tile_count = 0
    with Reader(str(geotiff_path)) as src:
        # Get tile indices for the bounds
        for z in range(min_zoom, max_zoom + 1):
            tiles = src.tile_list(z)
            for tile_x, tile_y in tiles:
                # Read tile data
                img = src.tile(tile_x, tile_y, z)
                
                # Apply colormap
                img_colored = apply_diverging_colormap(img.data, vmin, vmax, colormap_name)
                
                # Save as WebP with transparency
                tile_path = output_dir / f"{z}/{tile_x}/{tile_y}.webp"
                tile_path.parent.mkdir(parents=True, exist_ok=True)
                save_webp(img_colored, tile_path, quality=80)
                tile_count += 1
    
    return tile_count

def apply_diverging_colormap(data: np.ndarray, vmin: float, vmax: float, cmap_name: str) -> np.ndarray:
    """Apply diverging colormap to data array.
    
    Returns RGBA array with NoData as transparent.
    """
    # Normalize to 0-1 range
    normalized = (data - vmin) / (vmax - vmin)
    normalized = np.clip(normalized, 0, 1)
    
    # Get colormap
    colormap = cmap.get(cmap_name)
    
    # Apply colormap (returns RGBA)
    rgba = colormap(normalized)
    
    # Set NoData to transparent
    rgba[..., 3] = np.where(np.isnan(data), 0, 255)
    
    return rgba.astype(np.uint8)
```

### 10.7 Job Structure Pattern

**File**: `jobs/job-update-10min-station-data/`

```dockerfile
# Dockerfile pattern - REUSE for ERA5 jobs
FROM python:3.13-slim

WORKDIR /app

# Copy job-specific source
COPY jobs/job-era5-daily/src ./src/

# Copy shared analysis modules
COPY analysis/era5/*.py ./src/era5/
COPY analysis/tiles/*.py ./src/tiles/
COPY analysis/utilities/upload_to_s3.py ./src/

# Install dependencies
RUN pip install --no-cache-dir \
    xarray \
    rasterio \
    rio-tiler \
    scipy \
    boto3 \
    cdsapi \
    numpy \
    netCDF4

COPY jobs/job-era5-daily/entrypoint.sh ./
RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
```

```bash
# entrypoint.sh pattern
#!/bin/bash
set -e

# Validate required environment variables
required_vars=("ACCESS_KEY" "SECRET_KEY" "BUCKET_NAME" "CDS_API_KEY")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Error: $var is not set"
        exit 1
    fi
done

# Run the pipeline
python src/process_daily.py

echo "ERA5 daily pipeline completed successfully"
```

```python
# process_daily.py pattern (TASK-033)
"""ERA5 daily processing pipeline orchestrator."""
import logging
from datetime import datetime, timedelta
from pathlib import Path

from era5.fetch_era5_data import fetch_latest_month
from era5.interpolate_to_grid import interpolate_to_1km
from era5.apply_land_mask import apply_germany_land_mask
from era5.calculate_anomalies import calculate_monthly_anomaly
from tiles.generate_tiles import generate_tiles_for_geotiff
from upload_to_s3 import upload_directory_to_s3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Run daily ERA5 processing pipeline."""
    # Calculate target month (previous complete month)
    today = datetime.now()
    target_date = today.replace(day=1) - timedelta(days=1)
    year, month = target_date.year, target_date.month
    
    logger.info(f"Processing ERA5 data for {year}-{month:02d}")
    
    # Step 1: Fetch ERA5 data
    raw_path = fetch_latest_month(year, month, output_dir=Path("./data/raw"))
    
    # Step 2: Interpolate to 1km grid
    interpolated_path = interpolate_to_1km(raw_path, output_dir=Path("./data/interpolated"))
    
    # Step 3: Apply land mask
    masked_path = apply_germany_land_mask(interpolated_path, output_dir=Path("./data/masked"))
    
    # Step 4: Calculate anomalies
    anomaly_path = calculate_monthly_anomaly(masked_path, year, month, output_dir=Path("./data/anomalies"))
    
    # Step 5: Generate tiles
    tiles_dir = Path(f"./data/tiles/{year}/{month:02d}")
    generate_tiles_for_geotiff(anomaly_path, tiles_dir)
    
    # Step 6: Upload to R2
    upload_directory_to_s3(tiles_dir, f"tiles/{year}/{month:02d}/")
    
    logger.info(f"Pipeline completed for {year}-{month:02d}")

if __name__ == "__main__":
    main()
```

### 10.8 MapLibre GL Integration Pattern (NEW)

**File**: `frontend/src/components/maps/ClimateMap/ClimateMap.tsx` (to be created)

```typescript
// Reference pattern for MapLibre GL integration
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { useEffect, useRef, useState } from 'react';
import { useAppSelector } from '../../../hooks/redux';
import { selectSelectedDate } from '../../../store/selectors/dateSelectors';

const GERMANY_BOUNDS: [[number, number], [number, number]] = [
    [5.87, 47.27],  // Southwest
    [15.04, 55.06]  // Northeast
];

const TILE_BASE_URL = import.meta.env.VITE_TILE_BASE_URL || 'https://era5-tiles.example.com';

export const ClimateMap: React.FC = () => {
    const mapContainer = useRef<HTMLDivElement>(null);
    const map = useRef<maplibregl.Map | null>(null);
    const [loaded, setLoaded] = useState(false);
    
    const selectedDate = useAppSelector(selectSelectedDate);
    const { year, month } = selectedDate;
    
    // Initialize map
    useEffect(() => {
        if (!mapContainer.current || map.current) return;
        
        map.current = new maplibregl.Map({
            container: mapContainer.current,
            style: {
                version: 8,
                sources: {
                    'osm': {
                        type: 'raster',
                        tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
                        tileSize: 256,
                        attribution: '© OpenStreetMap'
                    }
                },
                layers: [
                    { id: 'osm', type: 'raster', source: 'osm' }
                ]
            },
            center: [10.45, 51.16],  // Germany center
            zoom: 5,
            maxBounds: GERMANY_BOUNDS
        });
        
        map.current.on('load', () => setLoaded(true));
        
        return () => {
            map.current?.remove();
            map.current = null;
        };
    }, []);
    
    // Update anomaly tile layer when date changes
    useEffect(() => {
        if (!map.current || !loaded) return;
        
        const sourceId = 'anomaly-tiles';
        const layerId = 'anomaly-layer';
        
        // Remove existing layer/source
        if (map.current.getLayer(layerId)) map.current.removeLayer(layerId);
        if (map.current.getSource(sourceId)) map.current.removeSource(sourceId);
        
        // Add new source with updated URL
        map.current.addSource(sourceId, {
            type: 'raster',
            tiles: [`${TILE_BASE_URL}/${year}/${String(month).padStart(2, '0')}/{z}/{x}/{y}.webp`],
            tileSize: 256,
            bounds: [5.87, 47.27, 15.04, 55.06]
        });
        
        // Add layer with transparency
        map.current.addLayer({
            id: layerId,
            type: 'raster',
            source: sourceId,
            paint: {
                'raster-opacity': 0.8,
                'raster-fade-duration': 300
            }
        }, 'osm');  // Insert below labels if any
        
    }, [year, month, loaded]);
    
    return (
        <div ref={mapContainer} className={styles.mapContainer} />
    );
};
```

### 10.9 GitHub Actions Workflow Pattern

**File**: `.github/workflows/era5-daily-pipeline.yml` (to be created)

```yaml
# Reference pattern for scheduled ERA5 pipeline
name: ERA5 Daily Pipeline

on:
  schedule:
    # Run at 06:00 UTC daily (ERA5 data typically available ~5 days delayed)
    - cron: '0 6 * * *'
  workflow_dispatch:  # Allow manual trigger

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}/era5-daily

jobs:
  run-pipeline:
    runs-on: ubuntu-latest
    timeout-minutes: 120  # 2 hours max
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'
          cache: 'pip'
          
      - name: Install dependencies
        run: |
          pip install -r analysis/era5/requirements.txt
          
      - name: Run ERA5 pipeline
        env:
          CDS_API_KEY: ${{ secrets.CDS_API_KEY }}
          ACCESS_KEY: ${{ secrets.R2_ACCESS_KEY }}
          SECRET_KEY: ${{ secrets.R2_SECRET_KEY }}
          BUCKET_NAME: era5-climate-tiles
          ENDPOINT_URL: ${{ secrets.R2_ENDPOINT_URL }}
        run: |
          python jobs/job-era5-daily/src/process_daily.py
          
      - name: Notify on failure
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: `ERA5 Pipeline Failed - ${new Date().toISOString().split('T')[0]}`,
              body: `The daily ERA5 pipeline failed. Check [workflow run](${context.serverUrl}/${context.repo.owner}/${context.repo.repo}/actions/runs/${context.runId}) for details.`,
              labels: ['pipeline-failure', 'automated']
            });
```

### 10.10 Metrics JSON Schema

**File**: `documentation/data-formats/metrics.md` (to be created)

```typescript
// TypeScript interface for metrics data (FILE-056 reference)

/** Metrics for a single location (city or country aggregate) */
interface LocationMetrics {
    /** ISO date of last calculation */
    calculatedAt: string;
    
    /** Annual temperature anomaly vs 1961-1990 */
    annualAnomaly: {
        value: number;      // e.g., 2.3 (°C)
        year: number;       // e.g., 2025
        referenceStart: number;  // e.g., 1961
        referenceEnd: number;    // e.g., 1990
    };
    
    /** Linear warming trend */
    warmingRate: {
        value: number;      // e.g., 0.4 (°C/decade)
        startYear: number;  // e.g., 1995
        endYear: number;    // e.g., 2025
        confidence: number; // R² value
    };
    
    /** Record-breaking days in most recent year */
    recordDays: {
        total: number;      // e.g., 18
        hot: number;        // e.g., 17
        cold: number;       // e.g., 1
        year: number;       // e.g., 2025
    };
    
    /** Seasonal warming rates */
    seasonalWarming: {
        winter: number;     // DJF anomaly
        spring: number;     // MAM anomaly
        summer: number;     // JJA anomaly
        fall: number;       // SON anomaly
        fastestSeason: 'winter' | 'spring' | 'summer' | 'fall';
    };
    
    /** Threshold day counts */
    thresholdDays: {
        hotDays: number;         // Tmax ≥ 30°C
        tropicalNights: number;  // Tmin > 20°C
        iceDays: number;         // Tmax ≤ 0°C
        frostDays: number;       // Tmin < 0°C
        year: number;
    };
    
    /** Comfortable temperature days */
    comfortableDays: {
        count: number;      // Days with 15-25°C mean
        year: number;
    };
}

/** Root metrics file structure */
interface MetricsFile {
    version: string;        // Schema version, e.g., "1.0"
    generatedAt: string;    // ISO timestamp
    source: 'era5' | 'era5-land';
    coverage: {
        bounds: { north: number; south: number; east: number; west: number };
        gridResolution: string;  // e.g., "1km"
    };
    data: LocationMetrics;
}

// Example: /data/metrics/germany.json
// Example: /data/metrics/cities/berlin.json
```

**Notes**: All metric calculation modules (TASK-023 to TASK-029) should output data conforming to this schema. The frontend MetricsService (TASK-050) will parse this format.
