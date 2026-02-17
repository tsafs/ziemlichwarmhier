---
goal: ERA5 Climate Visualization for Germany - Complete Architecture and Implementation Plan
version: 1.1
date_created: 2026-02-16
last_updated: 2026-02-17
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
- **REQ-003**: Display 6 static climate metrics: Five-Year Temperature Anomaly, Warming Rate, Winter Warming, Record-Breaking Days, Snow Days Lost, Comfortable Days
- **REQ-004**: Support city selection with city-specific metrics and visualizations
- **REQ-005**: Implement narrative sections with 9 interactive plots across 3 tabs:
  - Recognition (2 plots): Temperature Evolution, Seasonal Warming
  - Understanding (4 plots): Monthly Distribution, Extremes Inverted, Record-Breaking Reality, Winter Snow Loss
  - Response (3 plots): Comfort Calendar, Tropical Nights, Vegetation Stress
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

**GOAL-004**: Calculate static climate metrics and plot data per grid cell

**Temperature Thresholds (DWD Standards + Scientific):**
- Ice day: Tmax ≤ 0°C (DWD: Eistag)
- Frost day: Tmin < 0°C (DWD: Frosttag)
- Hot day: Tmax ≥ 30°C (DWD: Heißer Tag)
- Extreme heat day: Tmax ≥ 35°C (vegetation/health damage threshold)
- Tropical night: Tmin ≥ 20°C (DWD: Tropennacht)
- Comfortable day: Tmean 15-25°C
- Snow day: precip > 0.1mm AND Tmean ≤ 0°C
- Late frost: Tmin ≤ -2°C after April 15

**Static Metrics (6 cards):**

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-023 | Create `analysis/metrics/calculate_five_year_anomaly.py` - mean annual anomalies 2021-2025 vs 1961-1990 | | |
| TASK-024 | Create `analysis/metrics/calculate_warming_rate.py` - linear regression trend 1995-2025 (°C/decade) | | |
| TASK-025 | Create `analysis/metrics/calculate_winter_warming.py` - DJF anomaly 2021-2025 vs 1961-1990 | | |
| TASK-026 | Create `analysis/metrics/calculate_record_days.py` - count daily Tmax/Tmin records broken per year | | |
| TASK-027 | Create `analysis/metrics/calculate_snow_days_lost.py` - snow days difference (recent vs reference) | | |
| TASK-028 | Create `analysis/metrics/calculate_comfortable_days.py` - days with Tmean 15-25°C | | |

**Plot Data Generation:**

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-029 | Create `analysis/plots/generate_temperature_evolution.py` - monthly anomalies with trend | | |
| TASK-030 | Create `analysis/plots/generate_seasonal_warming.py` - seasonal anomalies (DJF, MAM, JJA, SON) | | |
| TASK-031 | Create `analysis/plots/generate_monthly_distribution.py` - percentiles (p10, p25, p50, p75, p90) per month | | |
| TASK-032 | Create `analysis/plots/generate_extremes.py` - ice days, hot days, dry spells, extreme rain days | | |
| TASK-033 | Create `analysis/plots/generate_record_breaking.py` - hot vs cold daily records per year | | |
| TASK-034 | Create `analysis/plots/generate_winter_snow.py` - snow days and transition rain days | | |
| TASK-035 | Create `analysis/plots/generate_comfort_calendar.py` - comfortable days by decade × month | | |
| TASK-036 | Create `analysis/plots/generate_tropical_nights.py` - tropical nights + hot days per year | | |
| TASK-037 | Create `analysis/plots/generate_vegetation_stress.py` - hot & dry days, extreme heat, late frost | | |

**Aggregation & Export:**

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-038 | Create `analysis/metrics/aggregate_metrics.py` - aggregate to city/country level | | |
| TASK-039 | Create `analysis/metrics/export_metrics.py` - export metrics to JSON for frontend | | |
| TASK-040 | Create `analysis/plots/export_plot_data.py` - export plot CSVs per location | | |
| TASK-041 | Write unit tests for all metric and plot calculations | | |

**Completion Criteria:**
- All 6 static metrics calculated per grid cell and aggregated
- All 9 plot datasets generated as CSV per location
- JSON/CSV output matches schemas expected by frontend
- Metrics validated against HYRAS reference data where overlapping

---

### Implementation Phase 5: Nightly Job Orchestration

**GOAL-005**: Create Docker jobs and GitHub Actions for automated nightly processing

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-042 | Create `jobs/job-era5-daily/Dockerfile` - daily update job container | | |
| TASK-043 | Create `jobs/job-era5-daily/entrypoint.sh` - validate env vars, run pipeline | | |
| TASK-044 | Create `jobs/job-era5-daily/src/process_daily.py` - orchestrate daily pipeline | | |
| TASK-045 | Create `jobs/job-era5-monthly/` - monthly tile regeneration job | | |
| TASK-046 | Create `jobs/job-era5-yearly/` - yearly metrics recalculation job | | |
| TASK-047 | Create `.github/workflows/era5-daily-pipeline.yml` - scheduled daily action | | |
| TASK-048 | Create `.github/workflows/era5-monthly-pipeline.yml` - scheduled monthly action | | |
| TASK-049 | Add monitoring/alerting for pipeline failures (GitHub Actions notifications) | | |
| TASK-050 | Write integration tests for complete pipeline execution | | |

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
| TASK-051 | Install MapLibre GL JS dependency and TypeScript types | | |
| TASK-052 | Create `frontend/src/components/maps/ClimateMap/ClimateMap.tsx` - base map component | | |
| TASK-053 | Create `frontend/src/components/maps/ClimateMap/TileLayer.tsx` - anomaly tile overlay | | |
| TASK-054 | Create `frontend/src/components/maps/ClimateMap/CityMarkers.tsx` - clickable city markers | | |
| TASK-055 | Create `frontend/src/components/maps/ClimateMap/Legend.tsx` - color scale legend | | |
| TASK-056 | Create `frontend/src/components/maps/ClimateMap/DateSelector.tsx` - month/year picker | | |
| TASK-057 | Create `frontend/src/store/slices/mapSlice.ts` - map state (view, selected month) | | |
| TASK-058 | Create `frontend/src/hooks/useMapTiles.ts` - tile URL generation hook | | |
| TASK-059 | Implement responsive behavior (pan, zoom, mobile gestures) | | |
| TASK-060 | Write component tests for all map components | | |

**Completion Criteria:**
- Map displays Germany with anomaly overlay
- Cities clickable, trigger selection
- Month/year selector updates displayed tiles
- Smooth performance on mobile (60fps pan/zoom)

---

### Implementation Phase 7: Frontend - Static Metrics Cards

**GOAL-007**: Implement 6 climate metrics display cards with city-specific updates

**The 6 Static Metrics:**
1. **Five-Year Temperature Anomaly**: "+2.4°C warmer" (2021-2025 vs 1961-1990)
2. **Warming Rate**: "+0.4°C per decade" (trend since 1995)
3. **Winter Warming**: "+2.9°C winter warming" (DJF 2021-2025 vs 1961-1990, fastest-changing season)
4. **Record-Breaking Days**: "18 record-breaking days" (daily Tmax/Tmin records in latest year)
5. **Snow Days Lost**: "18 fewer snow days" (2021-2025 vs 1961-1990)
6. **Comfortable Days**: "145 comfortable days" (Tmean 15-25°C, 2021-2025 average)

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-061 | Create `frontend/src/services/MetricsService.ts` - fetch metrics JSON | | |
| TASK-062 | Create `frontend/src/store/slices/metricsSlice.ts` - metrics state using createDataSlice | | |
| TASK-063 | Create `frontend/src/components/metrics/MetricsRow.tsx` - horizontal metrics layout | | |
| TASK-064 | Create `frontend/src/components/metrics/cards/FiveYearAnomalyCard.tsx` | | |
| TASK-065 | Create `frontend/src/components/metrics/cards/WarmingRateCard.tsx` | | |
| TASK-066 | Create `frontend/src/components/metrics/cards/WinterWarmingCard.tsx` | | |
| TASK-067 | Create `frontend/src/components/metrics/cards/RecordDaysCard.tsx` | | |
| TASK-068 | Create `frontend/src/components/metrics/cards/SnowDaysLostCard.tsx` | | |
| TASK-069 | Create `frontend/src/components/metrics/cards/ComfortableDaysCard.tsx` | | |
| TASK-070 | Implement city-specific metric loading on city selection | | |
| TASK-071 | Write component tests for all metric cards | | |

**Completion Criteria:**
- 6 metric cards display correctly with values and subtitles
- Metrics update when city selected (smooth transition animation)
- Loading/error states handled gracefully
- Mobile responsive (vertical stack)

---

### Implementation Phase 8: Frontend - Narrative Plots

**GOAL-008**: Implement narrative section with 9 interactive climate plots across 3 tabs

**Narrative Arc: Recognition → Understanding → Response**

**Tab 1: Recognition - "The Warming Is Real" (2 plots)**

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-072 | Create `NarrativeSection.tsx` - tabbed container with German labels (Erkennen, Verstehen, Handeln) | | |
| TASK-073 | Create `TemperatureEvolution.tsx` - scatter plot with LOWESS trend, color-coded anomalies | | |
| TASK-074 | Create `SeasonalWarming.tsx` - 4-line chart (DJF, MAM, JJA, SON), highlight fastest-warming season | | |

**Narrative text (inline):**
- Plot 1.1 intro: *"Every point represents one month. Blue = cooler than 1961-1990 average. Red = warmer."*
- Plot 1.1 key insight: *"The scatter hasn't disappeared—weather is still chaotic—but the entire distribution has shifted upward."*
- Plot 1.2 intro: *"Winter is disappearing faster than summer is arriving."*
- Plot 1.2 key insight: *"The seasons aren't just warmer—they're being redistributed."*

**Tab 2: Understanding - "How Climate Is Reshaping" (4 plots)**

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-075 | Create `MonthlyDistribution.tsx` - 12-panel box plots (1961-1990 vs 2015-2025) | | |
| TASK-076 | Create `ExtremesInverted.tsx` - diverging bars: ice days, hot days, dry spells, extreme rain | | |
| TASK-077 | Create `RecordBreakingReality.tsx` - stacked area (hot vs cold records per year) | | |
| TASK-078 | Create `WinterForgotToCome.tsx` - dual-axis: snow days + transition rain days | | |

**Narrative text (inline):**
- Plot 2.1 intro: *"The calendar still says 'January' and 'July,' but what those months feel like has fundamentally changed."*
- Plot 2.2 key insight: *"In a stable climate, extremes balance. Not anymore."*
- Plot 2.3 key insight: *"For every one cold record broken, ten hot records fall. The record books are being rewritten in real-time."*
- Plot 2.4 intro: *"Snow days are becoming rain days."*

**Tab 3: Response - "Planning for Heat" (3 plots)**

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-079 | Create `ComfortCalendar.tsx` - heatmap (decades × months) of comfortable days | | |
| TASK-080 | Create `TropicalNights.tsx` - bars (tropical nights) + line (hot days ≥30°C) per year | | |
| TASK-081 | Create `VegetationStress.tsx` - stacked area (hot & dry, extreme heat ≥35°C, late frost) | | |

**Narrative text (inline):**
- Plot 3.1 intro: *"When is it comfortable to be outside?"*
- Plot 3.2 key insight: *"Sleepless summer nights are no longer rare events."*
- Plot 3.3 intro: *"Plants face a triple threat: drought, heat waves, and late frost."*

**Supporting Infrastructure:**

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-082 | Create `frontend/src/services/NarrativePlotService.ts` - fetch plot CSVs | | |
| TASK-083 | Create `frontend/src/store/slices/narrativePlotSlice.ts` - plot data state | | |
| TASK-084 | Create `frontend/src/components/common/ExpandableText.tsx` - methodology info toggle | | |
| TASK-085 | Implement plot animations and tab transitions | | |
| TASK-086 | Write integration tests for all 9 narrative plots | | |

**Completion Criteria:**
- All 9 narrative plots render correctly with Observable Plot
- Each plot includes brief intro text and key insight
- Methodology available via ExpandableText (collapsed by default)
- Plots update on city selection
- Smooth tab transitions
- Mobile: tabs become accordion

---

### Implementation Phase 9: City Search and Selection

**GOAL-009**: Implement city search functionality with station correlation

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-087 | Create/update `frontend/src/services/CityService.ts` - extend for ERA5 grid correlation | | |
| TASK-088 | Create `frontend/src/components/search/CitySearch.tsx` - autocomplete search | | |
| TASK-089 | Create `frontend/src/store/slices/citySlice.ts` - city selection state | | |
| TASK-090 | Create `analysis/cities/correlate_cities_to_grid.py` - map cities to nearest grid cell | | |
| TASK-091 | Generate city correlation data (5000+ German cities) | | |
| TASK-092 | Implement URL-based city selection (shareable links) | | |
| TASK-093 | Write tests for search and selection | | |

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
| TASK-094 | Create `documentation/architecture/era5-pipeline.md` - pipeline architecture docs | | |
| TASK-095 | Create `documentation/architecture/frontend.md` - frontend architecture docs | | |
| TASK-096 | Create `documentation/data-formats/` - schema documentation for all data formats | | |
| TASK-097 | Create `documentation/deployment/` - deployment and operations guide | | |
| TASK-098 | Create `documentation/api/` - internal API documentation | | |
| TASK-099 | Add JSDoc comments to all TypeScript functions | | |
| TASK-100 | Add docstrings to all Python functions | | |
| TASK-101 | Set up coverage reporting in CI | | |
| TASK-102 | Create end-to-end tests for critical user flows | | |

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
| TASK-103 | Configure Cloudflare Pages deployment for frontend | | |
| TASK-104 | Set up custom domain and SSL | | |
| TASK-105 | Configure cache invalidation for tile updates | | |
| TASK-106 | Set up uptime monitoring (Cloudflare or external) | | |
| TASK-107 | Create runbook for common operations (tile regeneration, rollback) | | |
| TASK-108 | Set up cost monitoring alerts | | |
| TASK-109 | Performance testing and optimization | | |

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

- **ALT-007**: **32°C "heat stress" threshold** - Considered adding 32°C threshold between hot days (30°C) and extreme heat (35°C). Rejected because: (1) 32°C is not a DWD-recognized threshold, (2) too similar to 30°C to be meaningful distinction, (3) adds complexity without clear user benefit. Use DWD standards: 30°C (Heißer Tag) and 35°C for extreme heat narratives.

- **ALT-008**: **Climate Analog Map (Plot 3.4)** - Would show "City X now feels like City Y did in 1980". Rejected for Germany-only scope because: (1) requires climate signatures for hundreds of European cities, (2) complex matching algorithms and preprocessing, (3) most analog cities would be outside Germany, making comparison less meaningful. Reconsider when expanding to pan-European scope.

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
- **FILE-002**: `analysis/era5/fetch_era5_data.py` - NEW - CDS download (temp + precipitation)
- **FILE-003**: `analysis/era5/interpolate_to_grid.py` - NEW - Grid interpolation
- **FILE-004**: `analysis/era5/apply_land_mask.py` - NEW - Land filtering
- **FILE-005**: `analysis/era5/calculate_anomalies.py` - NEW - Anomaly calculation
- **FILE-006**: `analysis/era5/types.py` - NEW - Data structure definitions
- **FILE-007**: `analysis/tiles/generate_tiles.py` - NEW - Tile generation
- **FILE-008**: `analysis/tiles/color_ramps.py` - NEW - Color scale definitions
- **FILE-009**: `analysis/tiles/tile_config.py` - NEW - Tile configuration
- **FILE-010**: `analysis/tiles/upload_tiles.py` - NEW - R2 upload

**Metric Calculators:**
- **FILE-011**: `analysis/metrics/calculate_five_year_anomaly.py` - NEW - 5-year mean anomaly
- **FILE-012**: `analysis/metrics/calculate_warming_rate.py` - NEW - Trend calculation (°C/decade)
- **FILE-013**: `analysis/metrics/calculate_winter_warming.py` - NEW - DJF anomaly
- **FILE-014**: `analysis/metrics/calculate_record_days.py` - NEW - Record counting
- **FILE-015**: `analysis/metrics/calculate_snow_days_lost.py` - NEW - Snow days difference
- **FILE-016**: `analysis/metrics/calculate_comfortable_days.py` - NEW - Days 15-25°C

**Plot Data Generators:**
- **FILE-017**: `analysis/plots/generate_temperature_evolution.py` - NEW - Monthly anomalies + trend
- **FILE-018**: `analysis/plots/generate_seasonal_warming.py` - NEW - Seasonal anomalies
- **FILE-019**: `analysis/plots/generate_monthly_distribution.py` - NEW - Percentiles per month
- **FILE-020**: `analysis/plots/generate_extremes.py` - NEW - Ice, hot, dry spells, extreme rain
- **FILE-021**: `analysis/plots/generate_record_breaking.py` - NEW - Hot vs cold records
- **FILE-022**: `analysis/plots/generate_winter_snow.py` - NEW - Snow + transition rain
- **FILE-023**: `analysis/plots/generate_comfort_calendar.py` - NEW - Decade x month heatmap
- **FILE-024**: `analysis/plots/generate_tropical_nights.py` - NEW - Tropical nights + hot days
- **FILE-025**: `analysis/plots/generate_vegetation_stress.py` - NEW - Hot & dry, extreme heat, late frost

**Aggregation & Export:**
- **FILE-026**: `analysis/metrics/aggregate_metrics.py` - NEW - Spatial aggregation
- **FILE-027**: `analysis/metrics/export_metrics.py` - NEW - JSON export
- **FILE-028**: `analysis/plots/export_plot_data.py` - NEW - CSV export per location
- **FILE-029**: `analysis/cities/correlate_cities_to_grid.py` - NEW - City-grid mapping

### Job Files

- **FILE-030**: `jobs/job-era5-daily/Dockerfile` - NEW - Daily job container
- **FILE-031**: `jobs/job-era5-daily/entrypoint.sh` - NEW - Job entry point
- **FILE-032**: `jobs/job-era5-daily/src/process_daily.py` - NEW - Daily orchestrator
- **FILE-033**: `jobs/job-era5-monthly/Dockerfile` - NEW - Monthly job container
- **FILE-034**: `jobs/job-era5-monthly/entrypoint.sh` - NEW - Monthly entry point
- **FILE-035**: `jobs/job-era5-monthly/src/process_monthly.py` - NEW - Monthly orchestrator
- **FILE-036**: `jobs/job-era5-yearly/Dockerfile` - NEW - Yearly job container
- **FILE-037**: `jobs/job-era5-yearly/src/process_yearly.py` - NEW - Yearly orchestrator

### GitHub Actions

- **FILE-038**: `.github/workflows/era5-daily-pipeline.yml` - NEW - Daily schedule
- **FILE-039**: `.github/workflows/era5-monthly-pipeline.yml` - NEW - Monthly schedule
- **FILE-040**: `.github/workflows/era5-yearly-pipeline.yml` - NEW - Yearly schedule

### Frontend Files

**Map Components:**
- **FILE-041**: `frontend/src/components/maps/ClimateMap/ClimateMap.tsx` - NEW - Map component
- **FILE-042**: `frontend/src/components/maps/ClimateMap/TileLayer.tsx` - NEW - Tile overlay
- **FILE-043**: `frontend/src/components/maps/ClimateMap/CityMarkers.tsx` - NEW - City markers
- **FILE-044**: `frontend/src/components/maps/ClimateMap/Legend.tsx` - NEW - Color legend
- **FILE-045**: `frontend/src/components/maps/ClimateMap/DateSelector.tsx` - NEW - Date picker

**Metric Cards (6):**
- **FILE-046**: `frontend/src/components/metrics/MetricsRow.tsx` - NEW - Horizontal layout
- **FILE-047**: `frontend/src/components/metrics/cards/FiveYearAnomalyCard.tsx` - NEW
- **FILE-048**: `frontend/src/components/metrics/cards/WarmingRateCard.tsx` - NEW
- **FILE-049**: `frontend/src/components/metrics/cards/WinterWarmingCard.tsx` - NEW
- **FILE-050**: `frontend/src/components/metrics/cards/RecordDaysCard.tsx` - NEW
- **FILE-051**: `frontend/src/components/metrics/cards/SnowDaysLostCard.tsx` - NEW
- **FILE-052**: `frontend/src/components/metrics/cards/ComfortableDaysCard.tsx` - NEW

**Narrative Plots (9):**
- **FILE-053**: `frontend/src/components/plots/narrative/NarrativeSection.tsx` - NEW - Tab container
- **FILE-054**: `frontend/src/components/plots/narrative/recognition/TemperatureEvolution.tsx` - NEW
- **FILE-055**: `frontend/src/components/plots/narrative/recognition/SeasonalWarming.tsx` - NEW
- **FILE-056**: `frontend/src/components/plots/narrative/understanding/MonthlyDistribution.tsx` - NEW
- **FILE-057**: `frontend/src/components/plots/narrative/understanding/ExtremesInverted.tsx` - NEW
- **FILE-058**: `frontend/src/components/plots/narrative/understanding/RecordBreakingReality.tsx` - NEW
- **FILE-059**: `frontend/src/components/plots/narrative/understanding/WinterForgotToCome.tsx` - NEW
- **FILE-060**: `frontend/src/components/plots/narrative/response/ComfortCalendar.tsx` - NEW
- **FILE-061**: `frontend/src/components/plots/narrative/response/TropicalNights.tsx` - NEW
- **FILE-062**: `frontend/src/components/plots/narrative/response/VegetationStress.tsx` - NEW

**Services & State:**
- **FILE-063**: `frontend/src/components/search/CitySearch.tsx` - NEW - City search
- **FILE-064**: `frontend/src/components/common/ExpandableText.tsx` - NEW - Read more toggle
- **FILE-065**: `frontend/src/services/MetricsService.ts` - NEW - Metrics fetching
- **FILE-066**: `frontend/src/services/NarrativePlotService.ts` - NEW - Plot data fetching
- **FILE-067**: `frontend/src/services/TileService.ts` - NEW - Tile URL generation
- **FILE-068**: `frontend/src/store/slices/mapSlice.ts` - NEW - Map state
- **FILE-069**: `frontend/src/store/slices/metricsSlice.ts` - NEW - Metrics state
- **FILE-070**: `frontend/src/store/slices/narrativePlotSlice.ts` - NEW - Plot data state
- **FILE-071**: `frontend/src/hooks/useMapTiles.ts` - NEW - Tile hook

### Documentation Files

- **FILE-072**: `documentation/architecture/era5-pipeline.md` - NEW
- **FILE-073**: `documentation/architecture/frontend.md` - NEW
- **FILE-074**: `documentation/data-formats/tiles.md` - NEW
- **FILE-075**: `documentation/data-formats/metrics.md` - NEW
- **FILE-076**: `documentation/data-formats/plot-data.md` - NEW - CSV schemas for all 9 plots
- **FILE-077**: `documentation/deployment/cloudflare.md` - NEW
- **FILE-078**: `documentation/deployment/runbook.md` - NEW

### Test Files

- **FILE-079**: `analysis/era5/tests/test_fetch_era5_data.py` - NEW
- **FILE-080**: `analysis/era5/tests/test_interpolate.py` - NEW
- **FILE-081**: `analysis/era5/tests/test_anomalies.py` - NEW
- **FILE-082**: `analysis/tiles/tests/test_generate_tiles.py` - NEW
- **FILE-083**: `analysis/metrics/tests/test_calculations.py` - NEW
- **FILE-084**: `analysis/plots/tests/test_generators.py` - NEW
- **FILE-085**: `frontend/src/components/maps/__tests__/ClimateMap.test.tsx` - NEW
- **FILE-086**: `frontend/src/components/metrics/__tests__/MetricsRow.test.tsx` - NEW
- **FILE-087**: `frontend/src/components/plots/narrative/__tests__/NarrativeSection.test.tsx` - NEW

## 6. Testing

### Unit Tests

- **TEST-001**: ERA5 data fetching correctly downloads and validates NetCDF files
- **TEST-002**: Grid interpolation produces correct 1km resolution output
- **TEST-003**: Land mask correctly includes German islands (Sylt, Rügen, Helgoland, etc.)
- **TEST-004**: Anomaly calculation matches reference values from HYRAS overlap
- **TEST-005**: Tile generation produces valid WebP files at expected zoom levels
- **TEST-006**: Color ramp mapping correctly handles edge cases (-3°C, +4°C, null values)
- **TEST-007**: All 6 static metric calculations produce correct values for known test data
- **TEST-008**: All 9 plot data generators produce correct CSV output
- **TEST-009**: R2 upload correctly sets content-type and cache headers
- **TEST-010**: Frontend components render without errors with mock data
- **TEST-011**: Redux slices handle loading, success, and error states correctly
- **TEST-012**: ExtremesInverted correctly displays all 4 metrics (ice, hot, dry spells, rain)

### Integration Tests

- **TEST-013**: Complete pipeline execution produces valid tiles for test month
- **TEST-014**: Frontend loads and displays tiles from R2 bucket
- **TEST-015**: City selection updates all components (map, metrics, 9 plots)
- **TEST-016**: Date selection correctly switches tile layer source
- **TEST-017**: Mobile responsive layout renders correctly at 375px width
- **TEST-018**: Tab navigation switches between Recognition/Understanding/Response

### End-to-End Tests

- **TEST-019**: User can load page, select city, and view city-specific data
- **TEST-020**: User can navigate date selector and see different month data
- **TEST-021**: User can search for city and select from results
- **TEST-022**: Shared URL with city parameter loads correct city
- **TEST-023**: Page load performance meets NFR-002 (< 3s on 4G)
- **TEST-024**: User can navigate all 3 narrative tabs and view 9 plots

### Validation Tests

- **TEST-025**: Generated tiles match visual reference (screenshot comparison)
- **TEST-026**: Metric values within expected ranges for test cities
- **TEST-027**: No console errors during normal operation
- **TEST-028**: Accessibility audit passes WCAG 2.1 AA
- **TEST-029**: All plots render with correct data for Berlin (reference city)

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
- TASK-001 to TASK-007 (Phase 1: Infrastructure) - independent setup tasks
- TASK-008 to TASK-014 (Phase 2: ERA5 Pipeline) - can start after dev environment
- TASK-051 to TASK-060 (Phase 6: Frontend Map) - independent of pipeline
- TASK-061 to TASK-071 (Phase 7: Frontend Metrics) - independent of map

**Sequential dependencies:**
- Phase 2 (ERA5 Pipeline) → Phase 3 (Tile Generation) → Phase 5 (Nightly Jobs)
- Phase 4 (Metrics + Plot Data) depends on Phase 2 completion
- Phase 6-9 (Frontend) can proceed in parallel with Phase 2-5 using mock data
- Phase 8 (Narrative Plots) has 9 plots across 3 tabs
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
