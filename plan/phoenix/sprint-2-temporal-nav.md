---
goal: "Sprint 2 — Temporal Navigation: Browse Anomaly Maps Month-by-Month"
version: 1.0
date_created: 2026-03-02
last_updated: 2026-03-02
owner: phoenix
status: 'Planned'
tags: [feature, temporal, date-selector, sprint-2]
---

# Sprint 2 — Temporal Navigation

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Browse anomaly maps month-by-month from 2016 to 2025. The user can select any month/year combination and the map updates with the corresponding anomaly tiles.

**Prerequisite**: Sprint 1 completed — map renders with tiles for a single month.

**Architecture reference**: See `plan/phoenix/00-architecture.md`

## 1. Requirements & Constraints

- **REQ-001**: Date selector component (month/year) overlaid on the map
- **REQ-002**: Changing date updates the tile layer URL → map re-renders with new month's tiles
- **REQ-003**: Earliest selectable date: January 2016. Latest: dynamically computed (current date minus `dataDelayDays`)
- **REQ-004**: Loading spinner / dimmed overlay while tiles load for new date
- **REQ-005**: Graceful handling when tiles don't exist for a selected month (show empty map, not broken tiles)
- **REQ-006**: Mock tiles generated for at least 12 months (2024-01 through 2024-12) for dev, or 2020-01 through 2025-12 for full range
- **CON-001**: Date selector is a map overlay (positioned absolute/fixed over the map), not a separate page section
- **CON-002**: No calendar picker library — build a simple month/year dropdown or stepper
- **PAT-001**: Date changes dispatch Redux action → `mapSlice` updates → `useMapTiles` hook recomputes tile URL → MapLibre source updated
- **GUD-001**: Tile URL template must change reactively when date changes — no page reload

## 2. Implementation Steps

### Phase 1: Expand Mock Tiles

- GOAL-001: Generate mock tiles for a usable date range so temporal navigation is demoable

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-001 | Extend `phoenix-backend/scripts/generate_mock_tiles.py` to generate tiles for all 12 months of 2024 (minimum) or 2020–2025 (ideal). Use slightly different color distributions per month to visually confirm date switching works | | |
| TASK-002 | Run the script, verify tiles exist for the full date range at zoom 5–7 | | |

### Phase 2: Date Selector Component

- GOAL-002: Build a month/year selector that dispatches date changes to Redux

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-003 | Create `src/components/maps/ClimateMap/DateSelector.tsx` — a compact month/year selector. Two dropdowns or a stepper: one for month (Jan–Dec, German labels: "Januar" through "Dezember"), one for year (2016–computed max). Positioned as absolute overlay on the map (top-right or top-left). Style with design tokens. | | |
| TASK-004 | Wire `DateSelector` to dispatch `setDate({ year, month })` from `mapSlice` on change | | |
| TASK-005 | Compute the maximum selectable date dynamically: current date minus `climateDataConfig.dataDelayDays`, then floor to the previous complete month | | |
| TASK-006 | Add `DateSelector` to the `ClimateMap` component (rendered inside the map container) | | |

### Phase 3: Reactive Tile Updates

- GOAL-003: Map tiles update when the user changes the date

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-007 | Update `useMapTiles` hook to regenerate the tile URL template when `selectedYear` or `selectedMonth` changes in the store | | |
| TASK-008 | Update `ClimateMap.tsx` to **reactively update the MapLibre raster source URL** when the tile URL template changes. Pattern: on URL change, call `map.getSource('anomaly-tiles').setTiles([newUrl])` inside a `useEffect` that depends on the tile URL | | |
| TASK-009 | Add loading state: dispatch `setLoading(true)` when date changes, `setLoading(false)` when tiles finish loading (MapLibre `sourcedata` event with `isSourceLoaded`) | | |
| TASK-010 | Create `src/components/maps/ClimateMap/LoadingOverlay.tsx` — semi-transparent overlay with spinner, shown when `selectIsMapLoading` is true. Positioned over the map. | | |
| TASK-011 | Handle tile load errors: if tiles 404 for a selected month, show the map without the overlay (transparent/empty) rather than broken tile placeholders. Optionally show a small "No data available for this month" message. | | |

### Phase 4: Tests

- GOAL-004: Unit tests for temporal navigation

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-012 | Create `src/components/maps/__tests__/DateSelector.test.tsx` — renders month/year options, dispatches `setDate` on change, respects min/max date bounds, displays German month names | | |
| TASK-013 | Update `src/store/slices/__tests__/mapSlice.test.ts` — test `setDate` action updates both `selectedYear` and `selectedMonth`; test boundary dates (Jan 2016, computed max) | | |
| TASK-014 | Update `src/hooks/__tests__/useMapTiles.test.ts` (or create if not existing) — test that tile URL template updates when year/month change | | |
| TASK-015 | Create `src/components/maps/__tests__/LoadingOverlay.test.tsx` — renders when loading=true, hidden when loading=false | | |
| TASK-016 | Verify: `npm run test` — all tests pass (Sprint 1 + Sprint 2) | | |

## 3. Alternatives

- **ALT-001**: Use `react-day-picker` for calendar UI — rejected because we only need month/year granularity, not day-level. A simple dropdown is lighter and avoids an unnecessary dependency.
- **ALT-002**: Animate tile transitions (fade between months) — deferred to Sprint 8 (polish). For now, immediate swap with loading overlay is sufficient.
- **ALT-003**: Preload adjacent months' tiles — deferred to Sprint 8 (performance). Keep it simple now.

## 4. Dependencies

- **DEP-001**: Sprint 1 completed (map renders, `mapSlice` exists, `TileService` exists)
- **DEP-002**: Mock tiles for multiple months generated

## 5. Files

- **FILE-001**: `phoenix-backend/scripts/generate_mock_tiles.py` — MODIFY — extend to generate tiles for multiple months/years
- **FILE-002**: `phoenix-frontend/src/components/maps/ClimateMap/DateSelector.tsx` — NEW
- **FILE-003**: `phoenix-frontend/src/components/maps/ClimateMap/LoadingOverlay.tsx` — NEW
- **FILE-004**: `phoenix-frontend/src/components/maps/ClimateMap/ClimateMap.tsx` — MODIFY — add reactive tile URL update + loading state + DateSelector + LoadingOverlay
- **FILE-005**: `phoenix-frontend/src/hooks/useMapTiles.ts` — MODIFY — react to date changes
- **FILE-006**: `phoenix-frontend/src/components/maps/ClimateMap/index.ts` — MODIFY — export new components
- **FILE-007**: `phoenix-frontend/src/components/maps/__tests__/DateSelector.test.tsx` — NEW
- **FILE-008**: `phoenix-frontend/src/components/maps/__tests__/LoadingOverlay.test.tsx` — NEW
- **FILE-009**: `phoenix-frontend/src/store/slices/__tests__/mapSlice.test.ts` — MODIFY — add date action tests
- **FILE-010**: `phoenix-frontend/src/hooks/__tests__/useMapTiles.test.ts` — NEW or MODIFY
- **FILE-011**: `phoenix-frontend/public/mock-tiles/` — MODIFY — tiles for additional months

## 6. Testing

- **TEST-001**: `DateSelector.test.tsx` — renders 12 month options (Januar–Dezember), renders year options (2016–max), dispatches correct action on selection
- **TEST-002**: `mapSlice.test.ts` — `setDate({year: 2023, month: 3})` updates state; initial state is year=2024, month=7
- **TEST-003**: `useMapTiles.test.ts` — returns URL containing `/2023/03/` when date is March 2023
- **TEST-004**: `LoadingOverlay.test.tsx` — visible when `isLoading=true`, hidden when `false`
- **TEST-005**: All Sprint 1 tests still pass (regression)

## 7. Risks & Assumptions

### Risks
- **RISK-001**: MapLibre's `setTiles()` on an existing raster source may cause flicker — **Mitigation**: test this pattern; if needed, use two alternating sources and toggle visibility
- **RISK-002**: Generating mock tiles for 120 months (10 years × 12) may be slow or produce many files — **Mitigation**: start with 12 months (2024 only); extend to full range only if needed for testing

### Assumptions
- **ASSUMPTION-001**: MapLibre GL supports updating raster source tiles dynamically via `getSource().setTiles()`
- **ASSUMPTION-002**: ERA5-Land data has ~5 day delay, so the latest available month is computable from current date
- **ASSUMPTION-003**: German month names are hardcoded strings (no i18n library needed — single-language app)

## 8. Multi-Agent Execution Notes

### Execution Order
- **Sequential**: Phase 1 → Phase 2 → Phase 3 → Phase 4
- **Parallel within Phase 2**: TASK-003 (DateSelector component) and TASK-005 (max date computation) can be built simultaneously
- **Parallel within Phase 4**: All test files can be written simultaneously

### Agent Context Requirements
- Read `plan/phoenix/00-architecture.md` for conventions
- Read `plan/phoenix/sprint-1-mvp-map.md` §10.2 and §10.3 for the MapLibre and mapSlice patterns
- Read `phoenix-frontend/src/store/slices/mapSlice.ts` (created in Sprint 1) for current state shape
- Read `phoenix-frontend/src/hooks/useMapTiles.ts` (created in Sprint 1) for current hook implementation

### Validation Checkpoints
- [After TASK-002]: Mock tiles exist for 12+ months at `phoenix-frontend/public/mock-tiles/`
- [After TASK-006]: DateSelector visible on map in dev server
- [After TASK-011]: Changing date updates tiles, loading overlay shows/hides, missing months handled gracefully
- [After TASK-016]: `npm run test` — all tests pass

## 9. Related Specifications / Further Reading

- `plan/phoenix/00-architecture.md` — architecture reference
- `plan/phoenix/sprint-1-mvp-map.md` — prerequisite sprint
- MapLibre GL JS docs on raster sources: https://maplibre.org/maplibre-gl-js/docs/

## 10. Code Reference

### 10.1 DateSelector Pattern

**File**: `phoenix-frontend/src/components/maps/ClimateMap/DateSelector.tsx` (to be created)

```typescript
import { useAppDispatch, useAppSelector } from '../../../store/hooks/useAppSelector';
import { setDate, selectSelectedYear, selectSelectedMonth } from '../../../store/slices/mapSlice';
import { climateDataConfig } from '../../../config/climateDataConfig';
import { theme, createStyles } from '../../../styles/design-system';

const MONTHS_DE = [
  'Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
  'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember',
] as const;

const MIN_YEAR = 2016;

function getMaxDate(delayDays: number): { year: number; month: number } {
  const now = new Date();
  now.setDate(now.getDate() - delayDays);
  // Floor to previous complete month
  now.setMonth(now.getMonth() - 1);
  return { year: now.getFullYear(), month: now.getMonth() + 1 };
}

export function DateSelector() {
  const dispatch = useAppDispatch();
  const selectedYear = useAppSelector(selectSelectedYear);
  const selectedMonth = useAppSelector(selectSelectedMonth);
  const maxDate = getMaxDate(climateDataConfig.dataDelayDays);

  // ... render month/year dropdowns, dispatch setDate on change
}
```

### 10.2 Reactive Tile URL Update

**File**: `phoenix-frontend/src/components/maps/ClimateMap/ClimateMap.tsx` (modification)

```typescript
// Inside ClimateMap component — new useEffect for reactive tile updates
const tileUrl = useMapTiles(); // returns URL template string

useEffect(() => {
  const map = mapRef.current;
  if (!map || !map.isStyleLoaded()) return;

  const source = map.getSource('anomaly-tiles') as maplibregl.RasterTileSource | undefined;
  if (source) {
    source.setTiles([tileUrl]);
  }
}, [tileUrl]);

// Loading state via MapLibre events
useEffect(() => {
  const map = mapRef.current;
  if (!map) return;

  const onSourceData = (e: maplibregl.MapSourceDataEvent) => {
    if (e.sourceId === 'anomaly-tiles' && e.isSourceLoaded) {
      dispatch(setLoading(false));
    }
  };
  map.on('sourcedata', onSourceData);
  return () => { map.off('sourcedata', onSourceData); };
}, [dispatch]);
```

### 10.3 LoadingOverlay Pattern

**File**: `phoenix-frontend/src/components/maps/ClimateMap/LoadingOverlay.tsx` (to be created)

```typescript
import { useAppSelector } from '../../../store/hooks/useAppSelector';
import { selectIsMapLoading } from '../../../store/slices/mapSlice';
import { theme } from '../../../styles/design-system';

export function LoadingOverlay() {
  const isLoading = useAppSelector(selectIsMapLoading);
  if (!isLoading) return null;

  return (
    <div style={{
      position: 'absolute', inset: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.3)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      zIndex: 10,
    }}>
      <div style={{ color: theme.colors.white, fontSize: theme.typography.sizes.lg }}>
        Lade Daten…
      </div>
    </div>
  );
}
```
