---
goal: "Phoenix Architecture — Interfaces, Conventions & Guidelines"
version: 1.0
date_created: 2026-03-02
last_updated: 2026-03-02
owner: phoenix
status: 'Planned'
tags: [architecture, guidelines, interfaces]
---

# Phoenix Architecture — Interfaces, Conventions & Guidelines

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

This document is the shared reference for all phoenix sprints. It defines the project goal, directory structure, interface contracts, technology choices, coding conventions, and LLM agent guidelines. Every sprint file references this document — it is the single source of truth for architectural decisions.

---

## 1. Project Goal

**"esistwarm.jetzt"** — a Germany-focused climate visualization platform showing ERA5-Land temperature anomalies on an interactive map, with 6 climate statistics cards and 9 narrative plots. The entire system runs on pre-generated static files (tiles, JSON, CSV) with zero runtime server. Target operational cost: €5–15/month.

### End-State Product

A public website where users can:

1. View a **temperature anomaly map** of Germany for any month since 2016
2. Select their **city** (from ~2,949 German cities) and see localized climate statistics
3. Browse **6 at-a-glance metric cards** (warming rate, winter warming, record days, etc.)
4. Explore a **narrative section** with 9 interactive plots across 3 tabs (Erkennen, Verstehen, Handeln)
5. **Share** a specific city view via URL deep link

Data updates automatically via nightly batch jobs — no human intervention required.

---

## 2. Iterative Approach — Why Phoenix

The previous "botox" plan followed a waterfall approach: define all 11 phases → implement horizontally (all infrastructure, then all pipeline, then all frontend). Result: working backend, fragmented frontend with 1 of 5 components visible, half the Redux store "legacy", and accumulating bugs.

**Phoenix builds vertically.** Each sprint produces a working, testable product:

```
Sprint 1:  Map renders                       ← MVP, demoable
Sprint 2:  + temporal navigation             ← browse months
Sprint 3:  + city selection                  ← personalized
Sprint 3b: + backend pipeline validation     ← real data artifacts
Sprint 4:  + 6 metric cards                  ← climate stats
Sprint 5:  + narrative section + 2 plots     ← storytelling begins
Sprint 6:  + remaining 7 plots              ← full narrative
Sprint 7:  + deployment + automation         ← production
Sprint 8:  + polish + docs + E2E            ← release-ready
```

Each sprint is self-contained: **tests ship with features, not after**. No dead code. No "add later" stubs.

---

## 3. Directory Structure

```
plan/phoenix/
  00-architecture.md            ← This file (shared reference)
  sprint-1-mvp-map.md
  sprint-2-temporal-nav.md
  sprint-3-city-selection.md
  sprint-3b-data-pipeline.md    ← Backend pipeline validation + real data generation
  sprint-4-climate-stats.md
  sprint-5-narrative-foundation.md
  sprint-6-complete-narrative.md
  sprint-7-infrastructure.md
  sprint-8-polish.md

phoenix-backend/                ← Copied from existing analysis/ (proven code)
  analysis/
    __init__.py
    era5/                       ← ERA5 pipeline (providers, anomalies, thresholds, etc.)
    metrics/                    ← 8 metric calculators + export
    tiles/                      ← WebP tile generation + upload
    utilities/                  ← S3 helpers
    rolling_average/
    geonames/                   ← City correlation (added Sprint 3)
    tests/                      ← Fixtures + integration tests
  schemas/                      ← JSON data contracts (metrics, city-correlation, tiles, etc.)
  jobs/                         ← Docker batch jobs (ERA5 daily/monthly/yearly)
  scripts/
    validate-env.py
    generate_mock_tiles.py
  infrastructure/
    bucket/cors.json
  conftest.py
  pyproject.toml

phoenix-frontend/               ← Fresh React app (zero legacy)
  src/
    config/
      climateDataConfig.ts      ← Env-driven data source config
    components/
      maps/                     ← ClimateMap, CityMarkers, DateSelector, Legend
      stats/                    ← StatCard, MetricsRow, 6 individual metric cards
      narrative/                ← NarrativeSection, PlotContainer, 9 plot components
      layout/                   ← Header, Footer, App shell
      common/                   ← LoadingError, InfoTooltip, ExpandableText
    store/
      index.ts                  ← Store configuration
      hooks/                    ← useAppSelector, useAppDispatch
      factories/
        createDataSlice.ts      ← Generic slice factory (ported from existing)
        cacheUtils.ts
        types.ts
      slices/
        mapSlice.ts
        citySlice.ts
        metricsSlice.ts
        narrativePlotSlice.ts
    services/
      TileService.ts
      CityService.ts
      MetricsService.ts
      NarrativePlotService.ts
    hooks/
      useMapTiles.ts
      useBreakpoint.ts
    styles/
      design-system.ts          ← Design tokens (ported from existing)
    types/                      ← Shared TypeScript types
    utils/
      citySlug.ts               ← Umlaut-safe URL slugs
      formatMetric.ts           ← Value formatting (±, decimals, units)
  public/
    mock-tiles/                 ← Generated WebP tiles for dev
    data/
      metrics/                  ← Static metrics JSON (dev fixtures)
      plots/                    ← Static plot CSV (dev fixtures)
      cities.json               ← City-grid correlation
  e2e/                          ← Playwright tests
  index.html
  package.json
  tsconfig.json
  vite.config.ts
  vitest.config.ts

.github/
  skills/                       ← LLM agent skills (created at Sprint 4+5)
    stats-section-cards/SKILL.md
    narrative-plot/SKILL.md
    data-services-integration/SKILL.md
```

---

## 4. Interface Contracts

The backend produces static files. The frontend consumes them. These are the contracts.

### 4.1 Anomaly Tiles

| Property | Value |
|----------|-------|
| Format | WebP, 256×256 px, quality 80, max 50 KB |
| URL pattern | `{tileBaseUrl}/{year}/{month:02d}/{z}/{x}/{y}.webp` |
| Zoom levels | 5–7 |
| Color ramp | RdBu_r diverging, -3°C to +3°C |
| NoData | Transparent (alpha=0) |
| Cache | `public, max-age=31536000, immutable` |
| Content-Type | `image/webp` |
| Schema | `schemas/tile-metadata.schema.json` |

### 4.2 Location Metrics (JSON)

| Property | Value |
|----------|-------|
| URL pattern | `{metricsBaseUrl}/{tile_id}.json` or `{metricsBaseUrl}/germany.json` |
| Schema | `schemas/metrics.schema.json` |
| Content-Type | `application/json` |

Structure:
```json
{
  "version": "1.0",
  "generatedAt": "ISO-8601",
  "source": "era5-land",
  "coverage": { "bounds": { "north": 55.1, "south": 47.2, "west": 5.8, "east": 15.1 }, "gridResolution": "0.1deg" },
  "data": {
    "calculatedAt": "ISO-8601",
    "fiveYearAnomaly": { "value": 1.2, "periodStart": 2021, "periodEnd": 2025, "referenceStart": 1961, "referenceEnd": 1990 },
    "warmingRate": { "value": 0.45, "startYear": 1995, "endYear": 2025, "confidence": 0.87 },
    "recordDays": { "total": 42, "hot": 35, "cold": 7, "year": 2025 },
    "winterWarming": { "value": 1.8, "periodStart": 2021, "periodEnd": 2025, "referenceStart": 1961, "referenceEnd": 1990 },
    "seasonalWarming": { "winter": 1.8, "spring": 1.1, "summer": 1.3, "fall": 0.9, "fastestSeason": "winter", "periodStart": 2021, "periodEnd": 2025, "referenceStart": 1961, "referenceEnd": 1990 },
    "thresholdDays": { "hotDays": 15, "tropicalNights": 8, "iceDays": 12, "frostDays": 55, "year": 2025 },
    "snowDaysLost": { "value": -18, "currentAverage": 22.0, "referenceAverage": 40.0, "periodStart": 2021, "periodEnd": 2025 },
    "comfortableDays": { "count": 85, "average": 78.0 }
  }
}
```

### 4.3 Plot Data (CSV)

| Property | Value |
|----------|-------|
| URL pattern | `{plotDataBaseUrl}/{tile_id}/{plot_type}.csv` |
| Schema | `schemas/plot-csv-headers.schema.json` |
| Content-Type | `text/csv` |

Plot types: `temperature-evolution`, `seasonal-warming`, `monthly-distribution`, `extremes-inverted`, `record-breaking-reality`, `winter-snow-loss`, `comfort-calendar`, `tropical-nights`, `vegetation-stress`

### 4.4 City Index (JSON)

| Property | Value |
|----------|-------|
| URL | `/data/cities.json` (or `{baseUrl}/cities.json`) |
| Schema | `schemas/city-correlation.schema.json` |

Structure:
```json
{
  "meta": { "grid_resolution": 0.1, "bounds": { "north": 55.1, "south": 47.2, "west": 5.8, "east": 15.1 }, "city_count": 2949 },
  "cities": [
    { "name": "Berlin", "slug": "berlin", "lat": 52.52, "lon": 13.405, "grid_i": 76, "grid_j": 53, "grid_lat": 52.5, "grid_lon": 13.4, "tile_id": "76_53" }
  ]
}
```

---

## 5. Technology Stack

### Backend (phoenix-backend/)

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | ≥3.13 | Runtime |
| Poetry | ≥2.0 | Build system / dependency management |
| xarray | ≥2025.6 | NetCDF / ERA5 data manipulation |
| numpy | ≥2.3 | Numerical computation |
| scipy | ≥1.17 | Linear regression (warming rate) |
| rasterio + rio-tiler | latest | GeoTIFF reading + tile generation |
| boto3 | ≥1.38 | S3-compatible upload/download |
| mercantile | ≥1.2 | XYZ tile math |
| matplotlib | ≥3.10 | Color ramps |
| cdsapi | latest | Copernicus Climate Data Store API |
| pytest | ≥8.0 | Testing |
| pytest-cov | ≥6.0 | Coverage |

### Frontend (phoenix-frontend/)

| Technology | Version | Purpose |
|------------|---------|---------|
| React | 19 | UI framework |
| TypeScript | 5.9+ | Language (strict mode) |
| Redux Toolkit | 2.8+ | State management (`createDataSlice` factory) |
| react-redux | 9.2+ | React bindings |
| MapLibre GL JS | 4.7+ | Interactive map |
| Observable Plot | 0.6+ | Charting / visualization |
| D3 | 7.9+ | Data manipulation, scales |
| Luxon | 3.7+ | Date/time handling |
| react-router-dom | 7.6+ | Routing + URL deep linking |
| Vite | 7+ | Build tool |
| Vitest | 4+ | Unit testing |
| Testing Library | latest | React component testing |
| Playwright | 1.58+ | E2E testing |

### Infrastructure

| Technology | Purpose |
|------------|---------|
| Hetzner Object Storage (fsn1) | Tile + data hosting (S3-compatible) |
| Cloudflare CDN + Pages | Edge caching + static site hosting |
| GitHub Actions | CI/CD + scheduled batch job execution |
| GHCR | Docker image registry for batch jobs |

---

## 6. Frontend Conventions

### 6.1 State Management — `createDataSlice` Factory

All async data fetching uses the `createDataSlice` factory. This eliminates boilerplate for loading, error, caching, and selector generation.

```typescript
// Example: creating a metrics slice
const metricsSlice = createDataSlice<LocationMetrics, { tileId: string }, 'keyed'>({
  name: 'metrics',
  fetchFn: (args) => MetricsService.fetchMetrics(args.tileId),
  stateShape: 'keyed',
  cache: { strategy: 'by-key', keyExtractor: (args) => args.tileId },
});

// Provides: metricsSlice.actions.fetch, metricsSlice.selectors.selectData, etc.
```

**Three state shapes:**
- `'simple'` — single data value (e.g., city index loaded once)
- `'keyed'` — data indexed by string key (e.g., metrics per tile_id)
- `'with-context'` — data + tracking of fetch context (e.g., map tiles by date)

**Three cache strategies:**
- `'none'` — always fetch
- `'by-key'` — cache per key, optional TTL
- `'all'` — cache entire dataset

### 6.2 Styling — Design Tokens

All styling uses the centralized `theme` object from `design-system.ts`. No CSS-in-JS libraries (no styled-components, no Tailwind). Inline `CSSProperties` computed via pure functions.

```typescript
import { theme, createStyles, media } from '../styles/design-system';

const styles = createStyles({
  container: {
    padding: theme.spacing.md,
    color: theme.colors.textLight,
    backgroundColor: theme.colors.background,
  },
});
```

Key tokens:
- **Spacing**: `none(0)`, `xs(4)`, `sm(8)`, `md(15)`, `lg(20)`, `xl(30)`, `xxl(40)`
- **Colors**: `background(#222)`, `backgroundLight(#eee)`, `cold(#4575b4)`, `hot(#d73027)`, `neutral(#999)`, `primary(rgb(7,87,156))`
- **Breakpoints**: `mobile(480)`, `tablet(768)`, `desktop(1024)`, `wide(1440)`
- **Typography**: System font stack, sizes `xs(12)` through `title(1.5rem)`

### 6.3 Configuration — Environment-Driven

All data-source URLs and labels resolved from `import.meta.env.VITE_*` at build time:

```typescript
export const climateDataConfig: ClimateDataConfig = {
  datasetId: import.meta.env.VITE_CLIMATE_DATASET_ID ?? 'era5-land',
  displayName: import.meta.env.VITE_CLIMATE_DISPLAY_NAME ?? 'ERA5-Land',
  tileBaseUrl: import.meta.env.VITE_TILE_BASE_URL ?? '/mock-tiles',
  metricsBaseUrl: import.meta.env.VITE_METRICS_BASE_URL ?? '/data/metrics',
  plotDataBaseUrl: import.meta.env.VITE_PLOT_DATA_BASE_URL ?? '/data/plots',
  nativeResolution: parseFloat(import.meta.env.VITE_NATIVE_RESOLUTION ?? '0.1'),
  dataDelayDays: parseInt(import.meta.env.VITE_DATA_DELAY_DAYS ?? '5', 10),
  gridResolutionLabel: import.meta.env.VITE_GRID_RESOLUTION_LABEL ?? '~9 km',
};
```

For local dev, defaults point to `/mock-tiles` and `/data/metrics` (served from `public/`). For production, env vars point to Hetzner/CDN URLs.

### 6.4 TypeScript — Strict Configuration

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "verbatimModuleSyntax": true,
    "isolatedModules": true,
    "jsx": "react-jsx",
    "module": "esnext",
    "moduleResolution": "bundler"
  }
}
```

### 6.5 Component Patterns

- **Feature-organized** directories: `maps/`, `stats/`, `narrative/`, `layout/`, `common/`
- Each feature directory has: component files, `index.ts` barrel export, `__tests__/` directory
- Components receive data via Redux selectors or props — no direct service calls inside components
- Loading and error states handled per-component (not globally)

### 6.6 Testing

- **Unit tests**: co-located in `__tests__/` directories, written alongside the feature
- **Integration tests**: in `e2e/` via Playwright (Sprint 8)
- **Coverage**: enforced per-sprint, increasing threshold as sprints progress
- **Rule**: no PR/merge without passing tests for the sprint's scope

---

## 7. Backend Conventions

### 7.1 Provider Protocol

All climate data sources implement the `ClimateDataProvider` protocol (structural subtyping):

```python
@runtime_checkable
class ClimateDataProvider(Protocol):
    @property
    def dataset_id(self) -> str: ...
    @property
    def display_name(self) -> str: ...
    @property
    def native_resolution_deg(self) -> float: ...
    @property
    def bounds(self) -> BoundsDict: ...
    def fetch_monthly(self, year, month, output_dir, variable, force) -> Path: ...
    def fetch_daily(self, year, month, output_dir, force) -> Path: ...
    def load_dataset(self, file_path) -> xr.Dataset: ...
```

### 7.2 Metrics Types

All metrics use `TypedDict` definitions in `analysis/metrics/types.py`. The `LocationMetrics` type is the primary data contract between backend and frontend:

```python
class LocationMetrics(TypedDict):
    calculatedAt: str
    fiveYearAnomaly: FiveYearAnomaly
    warmingRate: WarmingRate
    recordDays: RecordDays
    winterWarming: WinterWarming
    seasonalWarming: SeasonalWarming
    thresholdDays: ThresholdDays
    snowDaysLost: SnowDaysLost
    comfortableDays: ComfortableDays
```

### 7.3 Testing

- `conftest.py` provides: `no_network` auto-use fixture, mock S3, stub ERA5 provider, synthetic xarray datasets
- Tests run with `pytest -x --tb=short`
- All metric calculators must have dedicated test files

---

## 8. LLM Agent Guidelines

### 8.1 Sprint Execution Rules

1. **One sprint at a time** — complete and verify before starting next
2. **Tests ship with features** — never "add tests later"
3. **No dead code** — if it's not rendered/called, don't write it
4. **Interface-first** — define the data contract, then implement both sides
5. **Acceptance criteria are mandatory** — sprint is not done until all criteria pass

### 8.2 Code Quality Rules

1. **No `any` types** in TypeScript — use proper generics or `unknown`
2. **No `eslint-disable` or `@ts-ignore`** — fix the actual issue
3. **No inline magic numbers** — use design tokens, config, or named constants
4. **No copy-paste duplication** — extract to utility/hook/component after 2nd occurrence
5. **Error boundaries** — every async operation has loading + error states

### 8.3 Skill Creation Rules

Skills document proven, tested patterns — not speculative architecture:

1. **Create a skill after building the 2nd instance** of a pattern (not the 1st)
2. **Reference implementation must exist** and have passing tests
3. **Skills go in** `.github/skills/{skill-name}/SKILL.md`
4. **Skills define**: the pattern, step-by-step instructions, file paths, and a complete reference implementation
5. **Update skills** if the pattern evolves — never let them drift from reality

### 8.4 Commit Granularity

Each sprint should result in atomic, reviewable commits:

- `feat: scaffold phoenix-frontend with Vite + React 19 + TypeScript`
- `feat: add ClimateMap component with MapLibre + tile rendering`
- `test: add unit tests for ClimateMap, Legend, TileService`
- `chore: generate mock tiles for dev`

---

## 9. Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     phoenix-backend/ (Python batch)             │
│                                                                 │
│  CDS API ──► ERA5 Pipeline ──► GeoTIFF ──► Tile Generator      │
│                    │                            │               │
│                    ▼                            ▼               │
│         Metric Calculators              WebP Tiles (.webp)      │
│         Plot Data Generators            /{year}/{month}/{z}/... │
│                    │                                            │
│                    ▼                                            │
│         JSON files (.json)    CSV files (.csv)                  │
│         /metrics/germany.json /plots/{tile_id}/{type}.csv       │
│         /metrics/{tile_id}.json                                 │
└───────────────────┬──────────────────────┬──────────────────────┘
                    │    Static files       │
                    ▼                       ▼
         ┌─────────────────────────────────────────┐
         │  Hetzner Object Storage (S3-compatible)  │
         │  └── Cloudflare CDN (edge cache)         │
         └───────────────────┬─────────────────────┘
                             │  HTTP GET
                             ▼
         ┌─────────────────────────────────────────┐
         │       phoenix-frontend/ (React SPA)      │
         │                                          │
         │  TileService ──► MapLibre (tile layer)   │
         │  MetricsService ──► StatCards            │
         │  NarrativePlotService ──► Plot components│
         │  CityService ──► Search + Markers        │
         │                                          │
         │  All via Redux createDataSlice factory    │
         └──────────────────────────────────────────┘
```

---

## 10. Sprint Dependency Graph

```
Sprint 1: MVP Map
    └── Sprint 2: Temporal Navigation
         └── Sprint 3: City Selection
              ├── Sprint 3b: Backend Pipeline Validation
              │    (replaces dev fixtures with real data;
              │     creates plot CSV generation module;
              │     validates Docker jobs)
              ├── Sprint 4: Climate Stats Cards
              │    └── Sprint 5: Narrative Foundation (2 plots)
              │         └── Sprint 6: Complete Narrative (7 plots)
              └── Sprint 7: Infrastructure + Automation
                   └── Sprint 8: Polish + Docs + E2E
```

Sprint 3b runs after Sprint 3 and feeds real data into Sprints 4–6 (replacing hand-crafted fixtures) and validates the pipeline that Sprint 7 deploys. Sprints 4–6 can start with hand-crafted fixtures before Sprint 3b completes, but the recommended order is Sprint 3 → 3b → 4 → 5 → 6 → 7 → 8.

---

## 11. Files Copied from Existing Codebase

The following are copied into `phoenix-backend/` from the existing project root:

| Source | Destination | Notes |
|--------|-------------|-------|
| `analysis/__init__.py` | `phoenix-backend/analysis/__init__.py` | Package root |
| `analysis/era5/` | `phoenix-backend/analysis/era5/` | Complete directory including providers/ and tests/ |
| `analysis/metrics/` | `phoenix-backend/analysis/metrics/` | Complete directory including tests/ |
| `analysis/tiles/` | `phoenix-backend/analysis/tiles/` | Complete directory including tests/ |
| `analysis/utilities/` | `phoenix-backend/analysis/utilities/` | S3 helpers |
| `analysis/rolling_average/` | `phoenix-backend/analysis/rolling_average/` | Rolling average calc |
| `analysis/tests/` | `phoenix-backend/analysis/tests/` | Integration tests + fixtures |
| `schemas/` | `phoenix-backend/schemas/` | All JSON schemas |
| `infrastructure/` | `phoenix-backend/infrastructure/` | CORS config |
| `conftest.py` | `phoenix-backend/conftest.py` | Root pytest config |
| `pyproject.toml` | `phoenix-backend/pyproject.toml` | Adapted for phoenix |
| `scripts/validate-env.py` | `phoenix-backend/scripts/validate-env.py` | Env validation |
| `scripts/generate_mock_tiles.py` | `phoenix-backend/scripts/generate_mock_tiles.py` | Mock tile generation |

Added at Sprint 3:
| `analysis/geonames/` | `phoenix-backend/analysis/geonames/` | City filtering for correlation |

Created new at Sprint 3b:
| (new code) | `phoenix-backend/analysis/plots/` | Plot CSV export module (temperature_evolution, seasonal_warming, extremes, monthly_distribution) |
| (new code) | `phoenix-backend/analysis/geonames/generate_city_correlation.py` | City-to-grid mapping JSON generator |

**NOT copied** (legacy/out-of-scope):
- `analysis/stations/` — legacy DWD station processing
- `analysis/hyras/` — HYRAS grid data (no tests, no `__init__.py`)
- `frontend/` — replaced by `phoenix-frontend/`
- `jobs/job-update-10min-station-data/` — legacy station job
- `jobs/job-update-daily-station-data/` — legacy station job
- `observable-testing/`, `playground/`, `topojson/` — not runtime dependencies
