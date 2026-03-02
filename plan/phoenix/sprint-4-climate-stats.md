---
goal: "Sprint 4 — Climate Statistics: 6 Metric Cards Below the Map"
version: 1.0
date_created: 2026-03-02
last_updated: 2026-03-02
owner: phoenix
status: 'Planned'
tags: [feature, metrics, stats, cards, sprint-4]
---

# Sprint 4 — Climate Statistics Cards

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Six metric cards below the map showing climate statistics for the selected city (or Germany-wide when no city is selected). Cards update when city selection changes. This sprint also creates the first LLM agent skill (`stats-section-cards`) after building the 2nd card — enabling efficient implementation of cards 3–6.

**Prerequisite**: Sprint 3 completed — map with city selection and URL deep linking. Sprint 3b recommended (provides real metrics JSON from the pipeline, replacing hand-crafted dev fixtures in Phase 1 below).

**Architecture reference**: See `plan/phoenix/00-architecture.md` §4.2 for metrics JSON contract, §6.1 for `createDataSlice` usage, §6.2 for design tokens.

## 1. Requirements & Constraints

- **REQ-001**: `MetricsService` fetches pre-generated JSON from `{metricsBaseUrl}/{tile_id}.json` for a selected city, or `{metricsBaseUrl}/germany.json` when no city is selected
- **REQ-002**: `metricsSlice` caches metrics per `tile_id` using `createDataSlice` with `'keyed'` shape and `'by-key'` cache strategy
- **REQ-003**: Reusable `StatCard` component with props: `title`, `value`, `subtitle`, `footnote`, `infoText` (tooltip), `isLoading`, `error`, `accentColor`, `valuePrefix` (for ± signs)
- **REQ-004**: 6 individual metric card components, each formatting its metric appropriately:
  1. `FiveYearAnomalyCard` — value with ± sign, 1 decimal, °C unit, accent color based on sign (hot/cold)
  2. `WarmingRateCard` — °C/decade, 2 decimals, confidence indicator
  3. `RecordDaysCard` — integer count, hot vs cold breakdown in subtitle
  4. `WinterWarmingCard` — value with ± sign, 1 decimal, °C unit
  5. `SnowDaysLostCard` — integer change, current vs reference in subtitle
  6. `ComfortableDaysCard` — integer count, long-term average in subtitle
- **REQ-005**: `MetricsRow` layout: 6 columns on desktop (≥1024px), 3×2 grid on tablet (≥768px), single column on mobile (<768px)
- **REQ-006**: Each card shows loading skeleton during fetch and error state on failure
- **REQ-007**: Cards update reactively when city selection changes in Redux
- **REQ-008**: When no city selected, display Germany-wide aggregate metrics
- **REQ-009**: Each card has an info tooltip (ℹ️ icon) explaining the metric in plain German
- **REQ-010**: Metric values formatted with German locale conventions (comma as decimal separator)
- **CON-001**: Metrics JSON must conform to `schemas/metrics.schema.json`
- **CON-002**: Dev fixtures placed in `phoenix-frontend/public/data/metrics/` — at minimum `germany.json` and one `{tile_id}.json`
- **PAT-001**: Use `createDataSlice<LocationMetrics, { tileId: string }, 'keyed'>` for the metrics slice
- **PAT-002**: Each card component is a thin wrapper around `StatCard` — extracts its metric from `LocationMetrics`, formats value, passes props
- **PAT-003**: Use `theme.colors.hot` / `theme.colors.cold` for positive/negative anomaly accent colors
- **GUD-001**: After building the 2nd card, extract the pattern into `.github/skills/stats-section-cards/SKILL.md`

## 2. Implementation Steps

### Phase 1: Dev Fixtures — Metrics JSON

- GOAL-001: Provide realistic metrics data for frontend development. If Sprint 3b is completed, **skip this phase** — real pipeline output already exists at `phoenix-frontend/public/data/metrics/`. Otherwise, create hand-crafted fixtures.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-001 | **If Sprint 3b completed**: verify `phoenix-frontend/public/data/metrics/germany.json` exists and is valid against `schemas/metrics.schema.json`. Skip TASK-002/003. **If Sprint 3b not completed**: Create `phoenix-frontend/public/data/metrics/germany.json` — valid against `schemas/metrics.schema.json`, with realistic Germany-wide values (e.g., fiveYearAnomaly: +1.2°C, warmingRate: 0.45°C/decade). Use the sample in `00-architecture.md` §4.2 as template. | | |
| TASK-002 | Create `phoenix-frontend/public/data/metrics/76_53.json` — per-tile metrics for Berlin's grid cell (tile_id from cities.json). Slightly different values than germany.json to verify city-specific loading. | | |
| TASK-003 | Create 1–2 more tile-specific fixtures for other test cities (München, Hamburg) to verify city switching updates metrics. | | |

### Phase 2: Metrics Types + Service

- GOAL-002: TypeScript types and service to fetch metrics JSON

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-004 | Create `src/types/metrics.ts` — TypeScript interfaces matching `schemas/metrics.schema.json`. Types: `FiveYearAnomaly`, `WarmingRate`, `RecordDays`, `WinterWarming`, `SeasonalWarming`, `ThresholdDays`, `SnowDaysLost`, `ComfortableDays`, `LocationMetrics`, `MetricsCoverage`, `MetricsFile`. These mirror the Python `TypedDict` definitions in `phoenix-backend/analysis/metrics/types.py`. | | |
| TASK-005 | Create `src/services/MetricsService.ts` — `fetchMetrics(tileId: string): Promise<MetricsFile>` fetches from `{climateDataConfig.metricsBaseUrl}/{tileId}.json`. `fetchGermanyMetrics(): Promise<MetricsFile>` fetches `germany.json`. Both parse JSON, validate structure, throw typed errors on failure. | | |
| TASK-006 | Create `src/services/__tests__/MetricsService.test.ts` — test fetch success, JSON parsing, network error handling, 404 handling | | |

### Phase 3: Metrics Redux Slice

- GOAL-003: Redux state management for metrics data with per-city caching

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-007 | Create `src/store/slices/metricsSlice.ts` via `createDataSlice` factory: shape `'keyed'`, cache strategy `'by-key'`, key extractor `(args) => args.tileId`. Fetch function calls `MetricsService.fetchMetrics(tileId)`. Add a `'germany'` key for the fallback germany-wide metrics. | | |
| TASK-008 | Add selector `selectCurrentMetrics` — if a city is selected, return metrics for that city's `tile_id`; if no city selected, return Germany-wide metrics. This composes `citySlice.selectSelectedCity` and the keyed metrics data. | | |
| TASK-009 | Register `metricsSlice` in `src/store/index.ts` | | |
| TASK-010 | Create `src/store/slices/__tests__/metricsSlice.test.ts` — test: initial state is idle; fetch for tile_id caches by key; `selectCurrentMetrics` returns city-specific or germany fallback | | |

### Phase 4: StatCard Base Component

- GOAL-004: Reusable card component with loading, error, and info tooltip states

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-011 | Create `src/components/common/InfoTooltip.tsx` — small ℹ️ icon that shows a tooltip on hover/click with explanatory text. Uses `theme.colors`, `theme.spacing`, `theme.shadows`. Accessible: `aria-label`, keyboard focusable. | | |
| TASK-012 | Create `src/components/common/LoadingSkeleton.tsx` — animated placeholder matching `StatCard` dimensions. Uses CSS animation (keyframes via inline style or a single `@keyframes` rule). | | |
| TASK-013 | Create `src/components/stats/StatCard.tsx` — props: `{ title: string, value: string, subtitle?: string, footnote?: string, infoText?: string, isLoading: boolean, error: string | null, accentColor?: string, valuePrefix?: string }`. Renders: title (top), large value with optional prefix (center), subtitle (below value), footnote (bottom), InfoTooltip (top-right corner). When `isLoading`: show `LoadingSkeleton`. When `error`: show error message with theme.colors.hot. | | |
| TASK-014 | Create `src/components/stats/__tests__/StatCard.test.tsx` — test: renders title+value, shows loading skeleton when isLoading, shows error message, shows info tooltip, applies accent color | | |

### Phase 5: Metric Formatting Utility

- GOAL-005: Pure functions to format metric values for display

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-015 | Create `src/utils/formatMetric.ts` — functions: `formatAnomaly(value: number): string` (e.g., +1,2 °C), `formatRate(value: number): string` (e.g., 0,45 °C/Dekade), `formatInteger(value: number): string` (e.g., 42), `formatSignedInteger(value: number): string` (e.g., −18), `formatConfidence(value: number): string` (e.g., 87%). All use German locale (comma decimal separator). | | |
| TASK-016 | Create `src/utils/__tests__/formatMetric.test.ts` — test each formatter with positive, negative, zero values; German locale formatting | | |

### Phase 6: First Two Metric Cards

- GOAL-006: Build FiveYearAnomalyCard and WarmingRateCard as reference implementations

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-017 | Create `src/components/stats/FiveYearAnomalyCard.tsx` — reads `fiveYearAnomaly` from `selectCurrentMetrics`. Displays: title "5-Jahres-Anomalie", value formatted via `formatAnomaly`, subtitle "vs. {referenceStart}–{referenceEnd}", accent color hot (positive) or cold (negative), infoText explaining the metric in German. | | |
| TASK-018 | Create `src/components/stats/WarmingRateCard.tsx` — reads `warmingRate` from `selectCurrentMetrics`. Displays: title "Erwärmungsrate", value formatted via `formatRate`, subtitle "seit {startYear}", footnote with confidence percentage, infoText in German. | | |
| TASK-019 | Create `src/components/stats/__tests__/FiveYearAnomalyCard.test.tsx` — test: renders formatted value, correct accent color for positive/negative, loading state, error state | | |
| TASK-020 | Create `src/components/stats/__tests__/WarmingRateCard.test.tsx` — test: renders rate, confidence indicator, loading/error states | | |

### Phase 7: LLM Skill Extraction

- GOAL-007: Document the stat card pattern as a reusable LLM agent skill

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-021 | Create `.github/skills/stats-section-cards/SKILL.md` — document the pattern observed from building `FiveYearAnomalyCard` and `WarmingRateCard`. Include: architecture overview (StatCard → metric-specific wrapper), step-by-step instructions (1. create card component, 2. write tests, 3. add to MetricsRow), file path conventions, complete code example from one of the reference implementations. Reference: `FiveYearAnomalyCard.tsx` as the canonical example. | | |

### Phase 8: Remaining Four Cards (using skill)

- GOAL-008: Build the 4 remaining cards following the documented skill pattern

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-022 | Create `src/components/stats/RecordDaysCard.tsx` — title "Rekordtage", value = total count, subtitle "davon {hot} heiß, {cold} kalt", infoText in German | | |
| TASK-023 | Create `src/components/stats/WinterWarmingCard.tsx` — title "Wintererwärmung", value formatted via `formatAnomaly`, subtitle "DJF vs. {referenceStart}–{referenceEnd}", accent color by sign | | |
| TASK-024 | Create `src/components/stats/SnowDaysLostCard.tsx` — title "Verlorene Schneetage", value formatted via `formatSignedInteger`, subtitle "aktuell {currentAverage} vs. {referenceAverage} Ref." | | |
| TASK-025 | Create `src/components/stats/ComfortableDaysCard.tsx` — title "Behagliche Tage", value = count, subtitle "Ø {average} (15–25°C)" | | |
| TASK-026 | Create tests for each card: `RecordDaysCard.test.tsx`, `WinterWarmingCard.test.tsx`, `SnowDaysLostCard.test.tsx`, `ComfortableDaysCard.test.tsx` — following same pattern as Phase 6 tests | | |

### Phase 9: MetricsRow Layout + Integration

- GOAL-009: Assemble all 6 cards into a responsive row below the map

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-027 | Create `src/components/stats/MetricsRow.tsx` — renders all 6 cards in a responsive grid. Desktop (≥1024px): 6 columns. Tablet (≥768px): 3×2 grid. Mobile (<768px): single column. Uses `theme.spacing` for gaps, `theme.breakpoints` for responsive behavior. Section title: "Klimastatistiken". | | |
| TASK-028 | Create `src/components/stats/index.ts` — barrel export: `MetricsRow`, `StatCard`, all 6 individual cards | | |
| TASK-029 | Update `src/App.tsx` — render `MetricsRow` below the `ClimateMap`. On mount (or on city change): if city selected, dispatch `metricsSlice.actions.fetch({ tileId: city.tile_id })`; if no city, dispatch fetch for `'germany'`. | | |
| TASK-030 | Create `src/components/stats/__tests__/MetricsRow.test.tsx` — test: renders all 6 cards, responsive layout switching, handles loading/error propagation | | |
| TASK-031 | Verify: `npm run test` — all tests pass (Sprint 1 + 2 + 3 + 4). Manual test: select Berlin → see Berlin metrics; clear selection → see Germany metrics; select München → metrics update. | | |

## 3. Alternatives

- **ALT-001**: Fetch metrics inside each card component independently — rejected because all 6 metrics come from the same JSON file; one fetch populates all cards
- **ALT-002**: Use CSS Grid with `grid-template-columns: repeat(auto-fit, minmax(200px, 1fr))` instead of explicit breakpoint switching — viable, but explicit breakpoints give more control over the 6→3×2→1 transitions
- **ALT-003**: Build all 6 cards before creating the skill — rejected; the skill is most valuable when 4 cards still need building, and having 2 reference implementations provides enough pattern confidence
- **ALT-004**: Use a charting library (e.g., sparklines) inside cards — rejected for Sprint 4; cards show single values with context. Sparklines can be added in Sprint 8 (polish) if desired
- **ALT-005**: Use `Intl.NumberFormat('de-DE')` for German locale formatting — accepted, this is the approach in `formatMetric.ts`

## 4. Dependencies

- **DEP-001**: Sprint 3 completed (city selection provides `tile_id` for metrics lookup)
- **DEP-002**: Sprint 3b recommended (provides real metrics JSON from pipeline — Phase 1 fixtures become unnecessary)
- **DEP-003**: `schemas/metrics.schema.json` (defines the JSON contract)
- **DEP-004**: Backend metrics export (`phoenix-backend/analysis/metrics/export_metrics.py`) produces conforming JSON (already implemented)
- **DEP-005**: No new npm packages — all needed dependencies (Redux Toolkit, React) already installed

## 5. Files

### Frontend — Dev Fixtures
- **FILE-001**: `phoenix-frontend/public/data/metrics/germany.json` — NEW — Germany-wide metrics fixture
- **FILE-002**: `phoenix-frontend/public/data/metrics/76_53.json` — NEW — Berlin tile metrics fixture

### Frontend — Types + Service
- **FILE-003**: `phoenix-frontend/src/types/metrics.ts` — NEW — TypeScript metric interfaces
- **FILE-004**: `phoenix-frontend/src/services/MetricsService.ts` — NEW — Fetch metrics JSON
- **FILE-005**: `phoenix-frontend/src/services/__tests__/MetricsService.test.ts` — NEW

### Frontend — Redux
- **FILE-006**: `phoenix-frontend/src/store/slices/metricsSlice.ts` — NEW — Keyed metrics slice
- **FILE-007**: `phoenix-frontend/src/store/slices/__tests__/metricsSlice.test.ts` — NEW
- **FILE-008**: `phoenix-frontend/src/store/index.ts` — MODIFY — register metricsSlice

### Frontend — Common Components
- **FILE-009**: `phoenix-frontend/src/components/common/InfoTooltip.tsx` — NEW
- **FILE-010**: `phoenix-frontend/src/components/common/LoadingSkeleton.tsx` — NEW

### Frontend — Stats Components
- **FILE-011**: `phoenix-frontend/src/components/stats/StatCard.tsx` — NEW — Reusable card base
- **FILE-012**: `phoenix-frontend/src/components/stats/FiveYearAnomalyCard.tsx` — NEW
- **FILE-013**: `phoenix-frontend/src/components/stats/WarmingRateCard.tsx` — NEW
- **FILE-014**: `phoenix-frontend/src/components/stats/RecordDaysCard.tsx` — NEW
- **FILE-015**: `phoenix-frontend/src/components/stats/WinterWarmingCard.tsx` — NEW
- **FILE-016**: `phoenix-frontend/src/components/stats/SnowDaysLostCard.tsx` — NEW
- **FILE-017**: `phoenix-frontend/src/components/stats/ComfortableDaysCard.tsx` — NEW
- **FILE-018**: `phoenix-frontend/src/components/stats/MetricsRow.tsx` — NEW — Responsive grid layout
- **FILE-019**: `phoenix-frontend/src/components/stats/index.ts` — NEW — Barrel exports

### Frontend — Utilities
- **FILE-020**: `phoenix-frontend/src/utils/formatMetric.ts` — NEW — German locale value formatting
- **FILE-021**: `phoenix-frontend/src/utils/__tests__/formatMetric.test.ts` — NEW

### Frontend — Tests
- **FILE-022**: `phoenix-frontend/src/components/stats/__tests__/StatCard.test.tsx` — NEW
- **FILE-023**: `phoenix-frontend/src/components/stats/__tests__/FiveYearAnomalyCard.test.tsx` — NEW
- **FILE-024**: `phoenix-frontend/src/components/stats/__tests__/WarmingRateCard.test.tsx` — NEW
- **FILE-025**: `phoenix-frontend/src/components/stats/__tests__/RecordDaysCard.test.tsx` — NEW
- **FILE-026**: `phoenix-frontend/src/components/stats/__tests__/WinterWarmingCard.test.tsx` — NEW
- **FILE-027**: `phoenix-frontend/src/components/stats/__tests__/SnowDaysLostCard.test.tsx` — NEW
- **FILE-028**: `phoenix-frontend/src/components/stats/__tests__/ComfortableDaysCard.test.tsx` — NEW
- **FILE-029**: `phoenix-frontend/src/components/stats/__tests__/MetricsRow.test.tsx` — NEW

### Frontend — Modified
- **FILE-030**: `phoenix-frontend/src/App.tsx` — MODIFY — add MetricsRow below ClimateMap, wire metrics fetch

### LLM Skill
- **FILE-031**: `.github/skills/stats-section-cards/SKILL.md` — NEW (or MODIFY if replacing existing)

## 6. Testing

- **TEST-001**: `MetricsService.test.ts` — fetches and parses metrics JSON; handles 404 (city not found) gracefully; handles network errors; returns typed `MetricsFile`
- **TEST-002**: `metricsSlice.test.ts` — initial state is idle; fetch stores by key; `selectCurrentMetrics` with selected city returns city metrics; `selectCurrentMetrics` without city returns germany metrics; cache hit skips re-fetch
- **TEST-003**: `formatMetric.test.ts` — `formatAnomaly(1.2)` → `'+1,2 °C'`; `formatAnomaly(-0.5)` → `'−0,5 °C'`; `formatRate(0.45)` → `'0,45 °C/Dekade'`; `formatInteger(42)` → `'42'`; `formatSignedInteger(-18)` → `'−18'`; `formatConfidence(0.87)` → `'87 %'`
- **TEST-004**: `StatCard.test.tsx` — renders title + value; shows LoadingSkeleton when isLoading=true; shows error message when error is set; renders InfoTooltip when infoText provided; applies accentColor to value
- **TEST-005**: `FiveYearAnomalyCard.test.tsx` — renders formatted anomaly value; uses `theme.colors.hot` accent for positive values; uses `theme.colors.cold` for negative; shows loading/error passthrough
- **TEST-006**: `WarmingRateCard.test.tsx` — renders rate with 2 decimals; shows confidence; loading/error states
- **TEST-007**: `RecordDaysCard.test.tsx` — renders total count; subtitle shows hot/cold breakdown
- **TEST-008**: `WinterWarmingCard.test.tsx` — renders anomaly; correct accent color
- **TEST-009**: `SnowDaysLostCard.test.tsx` — renders signed integer; subtitle shows current vs reference
- **TEST-010**: `ComfortableDaysCard.test.tsx` — renders count; subtitle shows average
- **TEST-011**: `MetricsRow.test.tsx` — renders all 6 cards; responsive layout at different viewport sizes
- **TEST-012**: Regression — all Sprint 1 + 2 + 3 tests still pass

## 7. Risks & Assumptions

### Risks
- **RISK-001**: Metrics JSON file might not exist for every tile_id — **Mitigation**: `MetricsService` handles 404 gracefully, card shows "Keine Daten verfügbar" instead of crashing
- **RISK-002**: German locale formatting differs across browsers — **Mitigation**: use `Intl.NumberFormat('de-DE')` which is universally supported in modern browsers
- **RISK-003**: StatCard design might feel cramped with 6 columns on small desktops (1024px) — **Mitigation**: test at 1024px width; if cramped, adjust breakpoint or switch to 3×2 at 1024px

### Assumptions
- **ASSUMPTION-001**: The metrics JSON structure matches `schemas/metrics.schema.json` exactly — any drift between backend export and frontend types will cause runtime errors
- **ASSUMPTION-002**: A single JSON file per tile_id contains all 8 metrics — no need for separate fetches per metric
- **ASSUMPTION-003**: Germany-wide metrics (`germany.json`) are always available as a fallback
- **ASSUMPTION-004**: The `tile_id` from `citySlice.selectSelectedCity` directly maps to a metrics file name

## 8. Multi-Agent Execution Notes

### Execution Order
- **Phase 1** (fixtures): Independent, do first
- **Phase 2 + 3** (types/service + slice): Sequential — types before service, service before slice
- **Phase 4** (StatCard base): Can start parallel with Phase 3 after Phase 2 types are done
- **Phase 5** (formatMetric): Independent of Phase 3/4, can run in parallel
- **Phase 6** (first 2 cards): Requires Phase 3 + 4 + 5
- **Phase 7** (skill): Requires Phase 6 (needs reference implementations)
- **Phase 8** (remaining 4 cards): Requires Phase 7 (uses skill) — or can proceed without skill if faster
- **Phase 9** (layout + integration): Requires Phase 8

### Agent Context Requirements
- Read `plan/phoenix/00-architecture.md` §4.2 for metrics JSON structure
- Read `plan/phoenix/00-architecture.md` §6.1 for `createDataSlice` usage pattern
- Read `plan/phoenix/00-architecture.md` §6.2 for design token usage
- Read `phoenix-frontend/src/store/factories/createDataSlice.ts` for factory API
- Read `phoenix-frontend/src/store/slices/citySlice.ts` for city selection selectors
- Read `schemas/metrics.schema.json` for full JSON schema
- Read `phoenix-backend/analysis/metrics/types.py` for Python TypedDict definitions (mirror in TS)

### Validation Checkpoints
- [After TASK-003]: Metrics fixtures serve at `http://localhost:5173/data/metrics/germany.json`
- [After TASK-006]: `npm run test -- MetricsService` passes
- [After TASK-010]: `npm run test -- metricsSlice` passes
- [After TASK-014]: `npm run test -- StatCard` passes
- [After TASK-016]: `npm run test -- formatMetric` passes
- [After TASK-020]: First 2 cards render with test data
- [After TASK-021]: Skill file exists and is complete
- [After TASK-026]: All 6 card tests pass
- [After TASK-031]: Full integration — map + date selector + city search + 6 metric cards all working

## 9. Related Specifications / Further Reading

- `plan/phoenix/00-architecture.md` — §4.2 Location Metrics, §6.1 createDataSlice
- `plan/phoenix/sprint-3b-data-pipeline.md` — Backend pipeline that generates real metrics JSON (Phase 5)
- `schemas/metrics.schema.json` — Full JSON schema for metrics
- `phoenix-backend/analysis/metrics/types.py` — Python TypedDict definitions
- `phoenix-backend/analysis/metrics/export_metrics.py` — How metrics are exported
- `plan/phoenix/sprint-3-city-selection.md` — City selection (provides tile_id)

## 10. Code Reference

### 10.1 Metrics JSON Structure (from architecture doc)

**File**: `phoenix-frontend/public/data/metrics/germany.json` (to be created)

```json
{
  "version": "1.0",
  "generatedAt": "2025-12-01T00:00:00Z",
  "source": "era5-land",
  "coverage": {
    "bounds": { "north": 55.1, "south": 47.2, "west": 5.8, "east": 15.1 },
    "gridResolution": "0.1deg"
  },
  "data": {
    "calculatedAt": "2025-12-01T00:00:00Z",
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

### 10.2 Python TypedDict Definitions (mirror these in TypeScript)

**File**: `phoenix-backend/analysis/metrics/types.py`

```python
class FiveYearAnomaly(TypedDict):
    value: float
    periodStart: int
    periodEnd: int
    referenceStart: int
    referenceEnd: int

class WarmingRate(TypedDict):
    value: float
    startYear: int
    endYear: int
    confidence: float

class RecordDays(TypedDict):
    total: int
    hot: int
    cold: int
    year: int

class WinterWarming(TypedDict):
    value: float
    periodStart: int
    periodEnd: int
    referenceStart: int
    referenceEnd: int

class SnowDaysLost(TypedDict):
    value: int
    currentAverage: float
    referenceAverage: float
    periodStart: int
    periodEnd: int

class ComfortableDays(TypedDict):
    count: int
    average: float

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

### 10.3 createDataSlice Keyed Shape Pattern

**File**: `phoenix-frontend/src/store/slices/metricsSlice.ts` (to be created)

```typescript
import { createDataSlice } from '../factories/createDataSlice';
import { MetricsService } from '../../services/MetricsService';
import type { MetricsFile } from '../../types/metrics';

const metricsSlice = createDataSlice<MetricsFile, { tileId: string }, 'keyed'>({
  name: 'metrics',
  fetchFn: async ({ tileId }) => {
    if (tileId === 'germany') {
      return MetricsService.fetchGermanyMetrics();
    }
    return MetricsService.fetchMetrics(tileId);
  },
  stateShape: 'keyed',
  cache: {
    strategy: 'by-key',
    keyExtractor: ({ tileId }) => tileId,
  },
});

export const { actions: metricsActions, selectors: metricsSelectors } = metricsSlice;
export default metricsSlice.slice.reducer;
```

### 10.4 StatCard Component Pattern

**File**: `phoenix-frontend/src/components/stats/StatCard.tsx` (to be created)

```typescript
import type { CSSProperties } from 'react';
import { theme, createStyles } from '../../styles/design-system';
import { InfoTooltip } from '../common/InfoTooltip';
import { LoadingSkeleton } from '../common/LoadingSkeleton';

interface StatCardProps {
  title: string;
  value: string;
  subtitle?: string;
  footnote?: string;
  infoText?: string;
  isLoading: boolean;
  error: string | null;
  accentColor?: string;
  valuePrefix?: string;
}

export function StatCard({ title, value, subtitle, footnote, infoText, isLoading, error, accentColor, valuePrefix }: StatCardProps) {
  if (isLoading) return <LoadingSkeleton />;
  if (error) return <div style={styles.error}>{error}</div>;

  return (
    <div style={styles.card}>
      <div style={styles.header}>
        <span style={styles.title}>{title}</span>
        {infoText && <InfoTooltip text={infoText} />}
      </div>
      <div style={{ ...styles.value, color: accentColor ?? theme.colors.textLight }}>
        {valuePrefix}{value}
      </div>
      {subtitle && <div style={styles.subtitle}>{subtitle}</div>}
      {footnote && <div style={styles.footnote}>{footnote}</div>}
    </div>
  );
}
```

### 10.5 Metric Card Wrapper Pattern (reference implementation)

**File**: `phoenix-frontend/src/components/stats/FiveYearAnomalyCard.tsx` (to be created)

```typescript
import { useAppSelector } from '../../store/hooks/useAppSelector';
import { metricsSelectors } from '../../store/slices/metricsSlice';
import { StatCard } from './StatCard';
import { formatAnomaly } from '../../utils/formatMetric';
import { theme } from '../../styles/design-system';

export function FiveYearAnomalyCard() {
  const metrics = useAppSelector(selectCurrentMetrics);
  const isLoading = useAppSelector(metricsSelectors.selectIsLoading);
  const error = useAppSelector(metricsSelectors.selectError);

  const data = metrics?.fiveYearAnomaly;
  const accentColor = data && data.value >= 0 ? theme.colors.hot : theme.colors.cold;

  return (
    <StatCard
      title="5-Jahres-Anomalie"
      value={data ? formatAnomaly(data.value) : '–'}
      subtitle={data ? `vs. ${data.referenceStart}–${data.referenceEnd}` : undefined}
      infoText="Durchschnittliche Temperaturabweichung der letzten 5 Jahre im Vergleich zur Referenzperiode 1961–1990."
      isLoading={isLoading}
      error={error}
      accentColor={accentColor}
      valuePrefix={data && data.value > 0 ? '+' : ''}
    />
  );
}
```

### 10.6 formatMetric Utility Pattern

**File**: `phoenix-frontend/src/utils/formatMetric.ts` (to be created)

```typescript
const deFormatter = new Intl.NumberFormat('de-DE', { minimumFractionDigits: 1, maximumFractionDigits: 1 });
const deFormatter2 = new Intl.NumberFormat('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const deIntFormatter = new Intl.NumberFormat('de-DE', { maximumFractionDigits: 0 });

export function formatAnomaly(value: number): string {
  const sign = value > 0 ? '+' : '';
  return `${sign}${deFormatter.format(value)} °C`;
}

export function formatRate(value: number): string {
  return `${deFormatter2.format(value)} °C/Dekade`;
}

export function formatInteger(value: number): string {
  return deIntFormatter.format(value);
}

export function formatSignedInteger(value: number): string {
  const sign = value > 0 ? '+' : '';
  return `${sign}${deIntFormatter.format(value)}`;
}

export function formatConfidence(value: number): string {
  return `${Math.round(value * 100)} %`;
}
```
