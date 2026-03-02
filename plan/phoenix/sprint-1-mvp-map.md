---
goal: "Sprint 1 — MVP: Anomaly Map (End-to-End Vertical Slice)"
version: 1.0
date_created: 2026-03-02
last_updated: 2026-03-02
owner: phoenix
status: 'Planned'
tags: [feature, mvp, map, sprint-1]
---

# Sprint 1 — MVP: Anomaly Map

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

A working page showing Germany's temperature anomaly map for a single month (July 2024). This is the first vertical slice — everything needed end-to-end: backend copied, frontend scaffolded, map rendered, tests passing.

**Architecture reference**: See `plan/phoenix/00-architecture.md` for all interface contracts, conventions, and directory structure.

## 1. Requirements & Constraints

- **REQ-001**: Page renders a MapLibre GL map bounded to Germany (5.8°E–15.1°E, 47.2°N–55.1°N)
- **REQ-002**: Map displays ERA5-Land temperature anomaly tiles as a raster overlay for July 2024
- **REQ-003**: Color scale legend component shows diverging blue-red ramp (-3°C to +3°C)
- **REQ-004**: Map fills viewport height, responsive pan/zoom at 60fps
- **REQ-005**: Mock tiles generated from backend scripts serve from `public/mock-tiles/`
- **REQ-006**: All existing backend tests (`pytest`) pass in `phoenix-backend/`
- **REQ-007**: Frontend tests cover map rendering, tile URL generation, and legend display
- **CON-001**: No date selector, city markers, metrics, header/footer, or routing in this sprint
- **CON-002**: Frontend must use React 19, TypeScript strict, Redux Toolkit, Vite 7
- **CON-003**: No legacy dependencies from old `frontend/` — start from only essential packages
- **PAT-001**: Use `createDataSlice` factory for all Redux state (port from existing `frontend/src/store/factories/`)
- **PAT-002**: Use design tokens from `design-system.ts` (port from existing `frontend/src/styles/`)
- **PAT-003**: Use `climateDataConfig` pattern for env-driven configuration
- **GUD-001**: Tests ship with features — no deferred testing

## 2. Implementation Steps

### Phase 1: Copy Backend

- GOAL-001: Establish `phoenix-backend/` with all proven pipeline code and passing tests

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-001 | Create `phoenix-backend/` directory structure (see architecture doc §11 for full list) | | |
| TASK-002 | Copy `analysis/__init__.py`, `analysis/era5/` (entire), `analysis/metrics/` (entire), `analysis/tiles/` (entire), `analysis/utilities/`, `analysis/rolling_average/`, `analysis/tests/` (entire) into `phoenix-backend/analysis/` | | |
| TASK-003 | Copy `schemas/` (all `.schema.json` files) into `phoenix-backend/schemas/` | | |
| TASK-004 | Copy `infrastructure/bucket/cors.json` into `phoenix-backend/infrastructure/bucket/` | | |
| TASK-005 | Copy `conftest.py` to `phoenix-backend/conftest.py` | | |
| TASK-006 | Copy `pyproject.toml` to `phoenix-backend/pyproject.toml` — then adapt: add missing runtime deps (`rasterio`, `rio-tiler`, `cdsapi`, `geopandas`, `shapely`, `pillow`) that were only in Docker files; update project name to `phoenix-backend`; update package paths | | |
| TASK-007 | Copy `scripts/validate-env.py` and `scripts/generate_mock_tiles.py` to `phoenix-backend/scripts/` | | |
| TASK-008 | Copy `jobs/job-era5-daily/`, `jobs/job-era5-monthly/`, `jobs/job-era5-yearly/` to `phoenix-backend/jobs/` | | |
| TASK-009 | Verify: run `cd phoenix-backend && pytest -x --tb=short` — all existing tests pass | | |

### Phase 2: Generate Mock Tiles

- GOAL-002: Create realistic dev tiles so the frontend can render immediately without real data

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-010 | Adapt `phoenix-backend/scripts/generate_mock_tiles.py` to output tiles into `phoenix-frontend/public/mock-tiles/` in the URL pattern `/{year}/{month:02d}/{z}/{x}/{y}.webp` for July 2024 (zoom 5–7) | | |
| TASK-011 | Run the script and verify tiles exist at the expected paths: `mock-tiles/2024/07/5/`, `mock-tiles/2024/07/6/`, `mock-tiles/2024/07/7/` | | |

### Phase 3: Scaffold Frontend

- GOAL-003: Create a minimal, clean React 19 + TypeScript app with Redux Toolkit, MapLibre GL, and Vitest

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-012 | Initialize `phoenix-frontend/` with Vite + React + TypeScript template. Create `package.json` with only essential deps: `react`, `react-dom`, `@reduxjs/toolkit`, `react-redux`, `maplibre-gl`, `luxon`, `@observablehq/plot`, `d3`, `vite`, `typescript`, `@vitejs/plugin-react`. Dev deps: `vitest`, `@vitest/coverage-v8`, `@testing-library/react`, `@testing-library/jest-dom`, `@testing-library/user-event`, `jsdom`, `@playwright/test`, `@types/react`, `@types/react-dom`, `@types/d3` | | |
| TASK-013 | Create `tsconfig.json` with strict config (see architecture doc §6.4) | | |
| TASK-014 | Create `vite.config.ts` with React plugin, dev proxy for `/data` to production URL | | |
| TASK-015 | Create `vitest.config.ts` with jsdom environment, v8 coverage, setupTests.ts | | |
| TASK-016 | Create `src/styles/design-system.ts` — port the theme object, `createStyles`, `media` queries, and `mixins` from existing `frontend/src/styles/design-system.ts` | | |
| TASK-017 | Create `src/config/climateDataConfig.ts` — port the `ClimateDataConfig` interface and env-resolved config object from existing `frontend/src/config/climateDataConfig.ts` | | |
| TASK-018 | Create `src/store/factories/` — port `createDataSlice.ts`, `cacheUtils.ts`, and `types.ts` from existing `frontend/src/store/factories/` | | |
| TASK-019 | Create `src/store/hooks/useAppSelector.ts` and `useAppDispatch.ts` | | |
| TASK-020 | Create `src/store/index.ts` with empty store configuration (no slices yet) | | |
| TASK-021 | Create `src/index.tsx` entry point with React 19 `createRoot`, `StrictMode`, Redux `Provider` | | |
| TASK-022 | Create `index.html` with minimal HTML shell | | |

### Phase 4: Build Map Components

- GOAL-004: Render the anomaly map with tile overlay and color scale legend

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-023 | Create `src/services/TileService.ts` — function `getTileUrl(baseUrl, year, month, z, x, y): string` using the URL pattern from `climateDataConfig.tileBaseUrl` | | |
| TASK-024 | Create `src/store/slices/mapSlice.ts` via `createDataSlice` factory — shape `'with-context'`, tracks `selectedYear` (default 2024), `selectedMonth` (default 7), map viewport state | | |
| TASK-025 | Create `src/hooks/useMapTiles.ts` — hook that reads `mapSlice` state and generates the tile URL template string for MapLibre's raster source | | |
| TASK-026 | Create `src/components/maps/ClimateMap/ClimateMap.tsx` — MapLibre GL map initialization, Germany bounds, raster tile source/layer using URL from `useMapTiles()`. Imperative `useRef<MapLibreMap>` pattern with `useEffect` for `map.addSource()`/`map.addLayer()` | | |
| TASK-027 | Create `src/components/maps/ClimateMap/Legend.tsx` — color gradient legend showing -3°C to +3°C with diverging blue-red ramp. Collapsible on mobile (use `useBreakpoint` hook or media query) | | |
| TASK-028 | Create `src/hooks/useBreakpoint.ts` — responsive breakpoint detection hook using `window.matchMedia` with the breakpoint values from `design-system.ts` | | |
| TASK-029 | Create `src/components/maps/ClimateMap/index.ts` — barrel export | | |
| TASK-030 | Register `mapSlice` in `src/store/index.ts` | | |
| TASK-031 | Create `src/App.tsx` — renders `ClimateMap` full viewport, no routing | | |
| TASK-032 | Verify: `npm run start` — map renders with anomaly tile overlay for July 2024, legend visible | | |

### Phase 5: Tests

- GOAL-005: Unit tests for all new frontend code

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-033 | Create `src/services/__tests__/TileService.test.ts` — test URL generation for various year/month/zoom/x/y combinations | | |
| TASK-034 | Create `src/store/slices/__tests__/mapSlice.test.ts` — test initial state, actions, selectors | | |
| TASK-035 | Create `src/components/maps/__tests__/Legend.test.tsx` — test legend renders, shows correct scale values, collapses on mobile | | |
| TASK-036 | Create `src/components/maps/__tests__/ClimateMap.test.tsx` — test map container renders (mock MapLibre GL) | | |
| TASK-037 | Create `src/hooks/__tests__/useBreakpoint.test.ts` — test breakpoint detection | | |
| TASK-038 | Verify: `npm run test` — all tests pass. `npm run test:coverage` — report generated | | |

## 3. Alternatives

- **ALT-001**: Use Leaflet instead of MapLibre GL — rejected because MapLibre provides native raster tile performance, vector support for future use, and the existing codebase already uses it
- **ALT-002**: Use CSS modules or Tailwind instead of inline styles — rejected for consistency with existing design-system.ts pattern; switching costs not justified at this stage
- **ALT-003**: Use Zustand instead of Redux Toolkit — rejected because `createDataSlice` factory already built on RTK eliminates the boilerplate concern, and the factory provides mature caching/loading patterns

## 4. Dependencies

- **DEP-001**: Node.js ≥20, npm
- **DEP-002**: Python ≥3.13, Poetry ≥2.0 (for backend tests)
- **DEP-003**: MapLibre GL JS 4.7+ (WebGL-capable browser)
- **DEP-004**: Mock tile generation requires matplotlib + numpy (in `phoenix-backend/`)

## 5. Files

### Backend (copy operations)

- **FILE-001**: `phoenix-backend/analysis/` — NEW (copied from `analysis/`) — entire ERA5 + metrics + tiles pipeline
- **FILE-002**: `phoenix-backend/schemas/` — NEW (copied from `schemas/`) — all JSON schemas
- **FILE-003**: `phoenix-backend/infrastructure/bucket/cors.json` — NEW (copied)
- **FILE-004**: `phoenix-backend/conftest.py` — NEW (copied)
- **FILE-005**: `phoenix-backend/pyproject.toml` — NEW (copied + adapted)
- **FILE-006**: `phoenix-backend/scripts/validate-env.py` — NEW (copied)
- **FILE-007**: `phoenix-backend/scripts/generate_mock_tiles.py` — NEW (copied + adapted for phoenix-frontend output)
- **FILE-008**: `phoenix-backend/jobs/` — NEW (copied ERA5 jobs)

### Frontend (new files)

- **FILE-009**: `phoenix-frontend/package.json` — NEW
- **FILE-010**: `phoenix-frontend/tsconfig.json` — NEW
- **FILE-011**: `phoenix-frontend/vite.config.ts` — NEW
- **FILE-012**: `phoenix-frontend/vitest.config.ts` — NEW
- **FILE-013**: `phoenix-frontend/index.html` — NEW
- **FILE-014**: `phoenix-frontend/src/index.tsx` — NEW
- **FILE-015**: `phoenix-frontend/src/App.tsx` — NEW
- **FILE-016**: `phoenix-frontend/src/styles/design-system.ts` — NEW (ported)
- **FILE-017**: `phoenix-frontend/src/config/climateDataConfig.ts` — NEW (ported)
- **FILE-018**: `phoenix-frontend/src/store/factories/createDataSlice.ts` — NEW (ported)
- **FILE-019**: `phoenix-frontend/src/store/factories/cacheUtils.ts` — NEW (ported)
- **FILE-020**: `phoenix-frontend/src/store/factories/types.ts` — NEW (ported)
- **FILE-021**: `phoenix-frontend/src/store/hooks/useAppSelector.ts` — NEW
- **FILE-022**: `phoenix-frontend/src/store/hooks/useAppDispatch.ts` — NEW
- **FILE-023**: `phoenix-frontend/src/store/index.ts` — NEW
- **FILE-024**: `phoenix-frontend/src/services/TileService.ts` — NEW
- **FILE-025**: `phoenix-frontend/src/store/slices/mapSlice.ts` — NEW
- **FILE-026**: `phoenix-frontend/src/hooks/useMapTiles.ts` — NEW
- **FILE-027**: `phoenix-frontend/src/hooks/useBreakpoint.ts` — NEW
- **FILE-028**: `phoenix-frontend/src/components/maps/ClimateMap/ClimateMap.tsx` — NEW
- **FILE-029**: `phoenix-frontend/src/components/maps/ClimateMap/Legend.tsx` — NEW
- **FILE-030**: `phoenix-frontend/src/components/maps/ClimateMap/index.ts` — NEW
- **FILE-031**: `phoenix-frontend/src/services/__tests__/TileService.test.ts` — NEW
- **FILE-032**: `phoenix-frontend/src/store/slices/__tests__/mapSlice.test.ts` — NEW
- **FILE-033**: `phoenix-frontend/src/components/maps/__tests__/Legend.test.tsx` — NEW
- **FILE-034**: `phoenix-frontend/src/components/maps/__tests__/ClimateMap.test.tsx` — NEW
- **FILE-035**: `phoenix-frontend/src/hooks/__tests__/useBreakpoint.test.ts` — NEW

### Generated assets

- **FILE-036**: `phoenix-frontend/public/mock-tiles/2024/07/{z}/{x}/{y}.webp` — GENERATED

## 6. Testing

- **TEST-001**: `TileService.test.ts` — `getTileUrl()` produces correct URL for various inputs; respects `climateDataConfig.tileBaseUrl`
- **TEST-002**: `mapSlice.test.ts` — initial state has year=2024, month=7; selectors return correct values; actions update state
- **TEST-003**: `Legend.test.tsx` — renders gradient, shows -3°C and +3°C labels, shows intermediate values
- **TEST-004**: `ClimateMap.test.tsx` — map container renders with correct dimensions; MapLibre initialization called with Germany bounds
- **TEST-005**: `useBreakpoint.test.ts` — returns correct breakpoint for various viewport sizes
- **TEST-006**: Backend: `pytest -x --tb=short` in `phoenix-backend/` — all existing tests pass unchanged

## 7. Risks & Assumptions

### Risks
- **RISK-001**: `createDataSlice` factory (525 lines) may have undocumented dependencies on other store code — **Mitigation**: port the factory + its types + cacheUtils as a unit; verify with TypeScript compilation before building on it
- **RISK-002**: Mock tile generation may require large dependencies (rasterio, rio-tiler) not installed in frontend dev — **Mitigation**: generate tiles as a backend script, commit the generated tiles to `public/mock-tiles/` or gitignore and regenerate on demand
- **RISK-003**: MapLibre GL may have WebGL issues in CI (headless) — **Mitigation**: mock MapLibre in unit tests; real E2E map tests deferred to Sprint 8

### Assumptions
- **ASSUMPTION-001**: Existing backend tests pass without modification when copied to `phoenix-backend/`
- **ASSUMPTION-002**: The `createDataSlice` factory works standalone with just its 3 files (main + types + cacheUtils) + Redux Toolkit
- **ASSUMPTION-003**: Mock tiles at zoom 5–7 are sufficient for development; real tiles come from backend pipeline later
- **ASSUMPTION-004**: Developer has Node.js ≥20 and Python ≥3.13 installed

## 8. Multi-Agent Execution Notes

### Execution Order
- **Sequential**: Phase 1 (TASK-001–009) → Phase 2 (TASK-010–011) → Phase 3 (TASK-012–022) → Phase 4 (TASK-023–032) → Phase 5 (TASK-033–038)
- **Parallel within Phase 1**: TASK-002 through TASK-008 can run simultaneously (all are file copies)
- **Parallel within Phase 3**: TASK-012–015 (tooling config) can run simultaneously with TASK-016–020 (source code porting)
- **Parallel within Phase 5**: All test files (TASK-033–037) can be written simultaneously

### Agent Context Requirements
- Architecture reference: read `plan/phoenix/00-architecture.md` before starting
- For TASK-016: reference `frontend/src/styles/design-system.ts` for full porting
- For TASK-017: reference `frontend/src/config/climateDataConfig.ts` for full porting
- For TASK-018–020: reference `frontend/src/store/factories/` for full porting
- For TASK-026: reference `frontend/src/components/maps/ClimateMap/ClimateMap.tsx` for MapLibre integration pattern

### Validation Checkpoints
- [After TASK-009]: `cd phoenix-backend && pytest -x --tb=short` passes
- [After TASK-011]: Mock tiles exist at `phoenix-frontend/public/mock-tiles/2024/07/5/`
- [After TASK-022]: `cd phoenix-frontend && npx tsc --noEmit` compiles without errors
- [After TASK-032]: `npm run start` shows anomaly map with tiles
- [After TASK-038]: `npm run test` — all tests pass

## 9. Related Specifications / Further Reading

- `plan/phoenix/00-architecture.md` — master architecture reference
- `schemas/metrics.schema.json` — metrics data contract (used in later sprints)
- `schemas/tile-metadata.schema.json` — tile metadata contract
- Existing `frontend/src/components/maps/ClimateMap/` — reference implementation for MapLibre patterns

## 10. Code Reference

### 10.1 TileService Pattern

**File**: `phoenix-frontend/src/services/TileService.ts` (to be created)

```typescript
import { climateDataConfig } from '../config/climateDataConfig';

/**
 * Generate tile URL for MapLibre raster source.
 * Pattern: {baseUrl}/{year}/{month:02d}/{z}/{x}/{y}.webp
 */
export function getTileUrl(year: number, month: number): string {
  const mm = String(month).padStart(2, '0');
  return `${climateDataConfig.tileBaseUrl}/${year}/${mm}/{z}/{x}/{y}.webp`;
}
```

### 10.2 MapLibre Raster Tile Integration Pattern

**File**: reference from existing `frontend/src/components/maps/ClimateMap/ClimateMap.tsx`

```typescript
// Key pattern: imperative MapLibre initialization with raster tile source
const mapRef = useRef<maplibregl.Map | null>(null);

useEffect(() => {
  const map = new maplibregl.Map({
    container: containerRef.current!,
    style: { version: 8, sources: {}, layers: [] },
    bounds: [5.8, 47.2, 15.1, 55.1], // Germany
    maxBounds: [4.0, 46.0, 16.5, 56.5],
  });

  map.on('load', () => {
    map.addSource('anomaly-tiles', {
      type: 'raster',
      tiles: [tileUrlTemplate],  // from useMapTiles() hook
      tileSize: 256,
    });
    map.addLayer({
      id: 'anomaly-layer',
      type: 'raster',
      source: 'anomaly-tiles',
      paint: { 'raster-opacity': 0.8 },
    });
  });

  mapRef.current = map;
  return () => map.remove();
}, []);
```

### 10.3 createDataSlice Usage for mapSlice

**File**: `phoenix-frontend/src/store/slices/mapSlice.ts` (to be created)

```typescript
import { createSlice, type PayloadAction } from '@reduxjs/toolkit';

// Note: mapSlice is a simple synchronous slice (no async fetching).
// It does NOT use createDataSlice factory since it only tracks UI state.
interface MapState {
  selectedYear: number;
  selectedMonth: number;
  isLoading: boolean;
}

const initialState: MapState = {
  selectedYear: 2024,
  selectedMonth: 7,
  isLoading: false,
};

const mapSlice = createSlice({
  name: 'map',
  initialState,
  reducers: {
    setDate(state, action: PayloadAction<{ year: number; month: number }>) {
      state.selectedYear = action.payload.year;
      state.selectedMonth = action.payload.month;
    },
    setLoading(state, action: PayloadAction<boolean>) {
      state.isLoading = action.payload;
    },
  },
});

export const { setDate, setLoading } = mapSlice.actions;
export const selectSelectedYear = (state: { map: MapState }) => state.map.selectedYear;
export const selectSelectedMonth = (state: { map: MapState }) => state.map.selectedMonth;
export const selectIsMapLoading = (state: { map: MapState }) => state.map.isLoading;
export default mapSlice.reducer;
```

### 10.4 ClimateDataConfig

**File**: `phoenix-frontend/src/config/climateDataConfig.ts` (to be created — port from existing)

```typescript
export interface ClimateDataConfig {
  datasetId: string;
  displayName: string;
  tileBaseUrl: string;
  metricsBaseUrl: string;
  plotDataBaseUrl: string;
  nativeResolution: number;
  dataDelayDays: number;
  gridResolutionLabel: string;
}

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

### 10.5 Tile Config (Backend Reference)

**File**: `phoenix-backend/analysis/tiles/tile_config.py` (already exists — copied)

```python
TILE_SIZE: int = 256
TILE_FORMAT: str = "webp"
WEBP_QUALITY: int = 80
MIN_ZOOM: int = 5
MAX_ZOOM: int = 7

GERMANY_BOUNDS: dict[str, float] = {
    "north": 55.1, "south": 47.2, "west": 5.8, "east": 15.1,
}

URL_PATTERN: str = "{base_url}/{year}/{month:02d}/{z}/{x}/{y}.webp"
ANOMALY_VMIN: float = -3.0
ANOMALY_VMAX: float = 3.0
```
