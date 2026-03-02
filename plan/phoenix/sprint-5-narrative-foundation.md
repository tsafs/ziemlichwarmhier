---
goal: "Sprint 5 — Narrative Foundation: Three-Tab Section with 2 Reference Plots"
version: 1.0
date_created: 2026-03-02
last_updated: 2026-03-02
owner: phoenix
status: 'Planned'
tags: [feature, narrative, plots, observable-plot, sprint-5]
---

# Sprint 5 — Narrative Foundation + First Plots

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Build the narrative section container (three tabs: Erkennen, Verstehen, Handeln) with 2 reference plots in the first tab. This sprint establishes the plot pattern — CSV data service, Redux slice, plot component, responsive container — and extracts it into an LLM agent skill for Sprint 6.

**Prerequisite**: Sprint 4 completed — map + city selection + 6 metric cards. Sprint 3b recommended (provides real plot CSVs from the pipeline, replacing hand-crafted dev fixtures in Phase 1 below).

**Architecture reference**: See `plan/phoenix/00-architecture.md` §4.3 for plot CSV contract, §6.1 for `createDataSlice`.

## 1. Requirements & Constraints

- **REQ-001**: `NarrativeSection` container with three-tab navigation using German labels: "Erkennen" (Recognize), "Verstehen" (Understand), "Handeln" (Act)
- **REQ-002**: Desktop: horizontal tab bar. Mobile (<768px): accordion-style collapsible sections
- **REQ-003**: Each tab contains a vertical stack of `PlotContainer` components
- **REQ-004**: `PlotContainer` wraps each plot with: narrative intro text (German), chart area, key insight callout, expandable methodology text
- **REQ-005**: `NarrativePlotService` fetches CSV data per city per plot type from `{plotDataBaseUrl}/{tile_id}/{plot_type}.csv`
- **REQ-006**: `narrativePlotSlice` caches by composite key `{tileId}:{plotType}` using `createDataSlice` with `'keyed'` shape
- **REQ-007**: Two plots implemented in the "Erkennen" tab:
  1. **Temperature Evolution** — scatter plot of annual mean temperature + LOWESS trend line (Observable Plot + D3)
  2. **Seasonal Warming** — 4-season multi-line chart showing warming trends per season (Observable Plot)
- **REQ-008**: Plots render with Observable Plot + D3, responsive to container width
- **REQ-009**: Plots update when city selection changes
- **REQ-010**: Loading spinner and error state per plot
- **REQ-011**: When no city selected, show Germany-wide plot data
- **REQ-012**: Tab state persists during city changes (don't reset to first tab)
- **CON-001**: Plot CSV data must conform to `schemas/plot-csv-headers.schema.json`
- **CON-002**: Dev CSV fixtures placed in `phoenix-frontend/public/data/plots/`
- **PAT-001**: Each plot component receives parsed data as props — no direct Redux access inside plot rendering logic
- **PAT-002**: CSV parsing utility shared across all plot services
- **PAT-003**: Observable Plot renders imperatively into a `useRef` container div (not via JSX)
- **GUD-001**: After building both plots, extract the pattern into `.github/skills/narrative-plot/SKILL.md`
- **GUD-002**: After building `NarrativePlotService`, update `.github/skills/data-services-integration/SKILL.md` for phoenix

## 2. Implementation Steps

### Phase 1: Dev Fixtures — Plot CSV Data

- GOAL-001: Provide realistic CSV data for 2 plot types for frontend development. If Sprint 3b is completed, **skip this phase** — real pipeline output already exists at `phoenix-frontend/public/data/plots/`. Otherwise, create hand-crafted fixtures.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-001 | **If Sprint 3b completed**: verify `phoenix-frontend/public/data/plots/germany/temperature_evolution.csv` exists with correct headers (`year,temperature,anomaly,trend`). Skip TASK-002/003. **If Sprint 3b not completed**: Create `phoenix-frontend/public/data/plots/germany/temperature-evolution.csv` — columns: `year,temperature,anomaly,trend`. Years 1961–2025, realistic temperature values (Germany annual mean ~8–10°C with warming trend). | | |
| TASK-002 | Create `phoenix-frontend/public/data/plots/germany/seasonal-warming.csv` — columns: `year,winter,spring,summer,fall`. Years 1961–2025, seasonal mean temperatures as anomalies. | | |
| TASK-003 | Create same CSV files for a test tile_id (e.g., `76_53` for Berlin): `phoenix-frontend/public/data/plots/76_53/temperature-evolution.csv` and `seasonal-warming.csv` | | |

### Phase 2: CSV Parsing Utility

- GOAL-002: Shared utility for parsing CSV responses into typed arrays

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-004 | Create `src/utils/csvParser.ts` — `parseCSV<T>(csvText: string, columnTypes: ColumnTypeMap): T[]`. Parses CSV text with header row, converts values according to column type definitions (`'number'`, `'string'`, `'integer'`). Handles empty values as `null`. No external CSV library — simple split-based parser for well-structured data. | | |
| TASK-005 | Create `src/utils/__tests__/csvParser.test.ts` — test: parses header + rows, converts types, handles empty values, handles trailing newlines | | |

### Phase 3: Plot Types + Service

- GOAL-003: TypeScript types and service to fetch plot CSV data

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-006 | Create `src/types/plots.ts` — types for plot data: `PlotType` union literal (`'temperature-evolution' | 'seasonal-warming' | ...` for all 9 types), `TemperatureEvolutionRow { year: number, mean_temp: number, trend: number }`, `SeasonalWarmingRow { year: number, winter: number, spring: number, summer: number, fall: number }`. Add types for remaining 7 plots as stubs (just the type name, filled in Sprint 6). | | |
| TASK-007 | Create `src/services/NarrativePlotService.ts` — `fetchPlotData<T>(tileId: string, plotType: PlotType): Promise<T[]>`. Fetches CSV from `{climateDataConfig.plotDataBaseUrl}/{tileId}/{plotType}.csv`, parses via `csvParser`, returns typed array. Has a `columnTypes` registry mapping each `PlotType` to its column type definitions. | | |
| TASK-008 | Create `src/services/__tests__/NarrativePlotService.test.ts` — test: fetches and parses CSV, handles 404, handles network errors | | |

### Phase 4: Narrative Plot Redux Slice

- GOAL-004: Redux state management for plot data with per-city-per-plot caching

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-009 | Create `src/store/slices/narrativePlotSlice.ts` via `createDataSlice` factory: shape `'keyed'`, cache strategy `'by-key'`, key extractor `({tileId, plotType}) => \`${tileId}:${plotType}\``. Fetch function calls `NarrativePlotService.fetchPlotData(tileId, plotType)`. | | |
| TASK-010 | Register `narrativePlotSlice` in `src/store/index.ts` | | |
| TASK-011 | Create `src/store/slices/__tests__/narrativePlotSlice.test.ts` — test: fetch stores by composite key, cache hit skips re-fetch | | |

### Phase 5: Common Narrative Components

- GOAL-005: Reusable container and layout components for the narrative section

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-012 | Create `src/components/common/ExpandableText.tsx` — collapsed by default with "Methodik anzeigen" link, expands to show full text. Uses `theme.transitions.normal` for smooth expand/collapse. | | |
| TASK-013 | Create `src/components/narrative/NarrativeSection.tsx` — three-tab container. Props: none (reads from plot registry). Desktop: horizontal tab bar with "Erkennen", "Verstehen", "Handeln" labels. Mobile: accordion sections. Manages `activeTab` local state. Tab content rendered lazily (only active tab mounts). | | |
| TASK-014 | Create `src/components/narrative/PlotContainer.tsx` — wraps a single plot. Props: `{ title: string, introText: string, keyInsight: string, methodologyText: string, isLoading: boolean, error: string | null, children: ReactNode }`. Layout: intro paragraph → chart area (children) → key insight callout → expandable methodology. Loading and error states shown in chart area. | | |
| TASK-015 | Create `src/components/narrative/__tests__/NarrativeSection.test.tsx` — test: renders 3 tabs, clicking tab switches content, mobile renders accordion | | |
| TASK-016 | Create `src/components/narrative/__tests__/PlotContainer.test.tsx` — test: renders intro, chart area, key insight, expandable methodology, loading/error states | | |

### Phase 6: Two Reference Plot Components

- GOAL-006: Build TemperatureEvolution and SeasonalWarming as reference implementations

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-017 | Create `src/hooks/usePlotData.ts` — generic hook: `usePlotData<T>(plotType: PlotType): { data: T[] | null, isLoading: boolean, error: string | null }`. Reads selected city from `citySlice`, dispatches fetch to `narrativePlotSlice` on city change, returns typed data. | | |
| TASK-018 | Create `src/components/narrative/plots/TemperatureEvolution.tsx` — uses `usePlotData<TemperatureEvolutionRow>('temperature-evolution')`. Renders scatter plot (annual mean temp dots) + LOWESS trend line using Observable Plot. Chart: x=year, y=temperature, dots colored by value (cold→hot), trend line overlay. Responsive: re-renders on container resize via `ResizeObserver`. | | |
| TASK-019 | Create `src/components/narrative/plots/SeasonalWarming.tsx` — uses `usePlotData<SeasonalWarmingRow>('seasonal-warming')`. Renders 4-line chart (one line per season) using Observable Plot. Lines colored: winter=blue, spring=green, summer=red, fall=orange. Legend below chart. Responsive. | | |
| TASK-020 | Create `src/components/narrative/plots/__tests__/TemperatureEvolution.test.tsx` — test: renders with data, shows loading state, shows error state, renders Observable Plot into container | | |
| TASK-021 | Create `src/components/narrative/plots/__tests__/SeasonalWarming.test.tsx` — test: renders 4 lines, legend, loading/error states | | |

### Phase 7: LLM Skills Extraction

- GOAL-007: Document narrative plot and data service patterns as reusable skills

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-022 | Create `.github/skills/narrative-plot/SKILL.md` — document the pattern: 1. Define row type in `types/plots.ts`, 2. Add column types to `NarrativePlotService` registry, 3. Create plot component using `usePlotData` hook + Observable Plot, 4. Wrap in `PlotContainer` with German narrative text, 5. Register in tab content, 6. Write tests. Reference: `TemperatureEvolution.tsx`. | | |
| TASK-023 | Create `.github/skills/data-services-integration/SKILL.md` — updated for phoenix: document the pattern for adding data services (CSV or JSON) with `createDataSlice`. Reference: `NarrativePlotService.ts` + `narrativePlotSlice.ts`. | | |

### Phase 8: Integration + Wiring

- GOAL-008: Wire narrative section into the app, all tests passing

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-024 | Create `src/components/narrative/tabConfig.ts` — defines which plots go in which tab. Structure: `{ id: TabId, label: string, plots: { component: ComponentType, title: string, introText: string, keyInsight: string, methodologyText: string }[] }[]`. For Sprint 5: only "Erkennen" tab has 2 plots; "Verstehen" and "Handeln" show placeholder "Weitere Visualisierungen folgen in Sprint 6" message. | | |
| TASK-025 | Create `src/components/narrative/index.ts` — barrel exports | | |
| TASK-026 | Update `src/App.tsx` — render `NarrativeSection` below `MetricsRow`. Ensure plot data fetches are triggered on city selection change. | | |
| TASK-027 | Verify: `npm run test` — all tests pass (Sprint 1–5). Manual test: page shows map → date selector → city search → 6 metric cards → narrative section with 3 tabs. "Erkennen" tab shows 2 working plots. Switching cities updates plots. Mobile: tabs become accordion. | | |

## 3. Alternatives

- **ALT-001**: Use a dedicated CSV library (papaparse, d3-dsv) — rejected for simplicity; plot CSVs are well-structured with known columns, a simple parser suffices. Can switch to d3-dsv if edge cases arise.
- **ALT-002**: Render Observable Plot via React wrapper library — rejected; Observable Plot's imperative API (`Plot.plot()` → DOM node) is cleaner when used directly with `useRef` + `useEffect`. React wrappers add abstraction without benefit.
- **ALT-003**: Use a single Redux slice for all data (metrics + plots) — rejected; metrics (JSON, per-tile) and plots (CSV, per-tile-per-type) have different shapes and caching strategies. Separate slices are cleaner.
- **ALT-004**: Pre-render all 3 tabs (not lazy) — rejected; lazy rendering avoids fetching plot data for tabs the user hasn't clicked yet
- **ALT-005**: Use D3 directly instead of Observable Plot — rejected; Observable Plot provides a much more concise API for standard chart types (scatter, line, bar), with D3 used only for custom transformations

## 4. Dependencies

- **DEP-001**: Sprint 4 completed (metric cards + city selection → tile_id available)
- **DEP-002**: `@observablehq/plot` 0.6+ (already in package.json from Sprint 1)
- **DEP-003**: `d3` 7.9+ (already in package.json from Sprint 1)
- **DEP-004**: `schemas/plot-csv-headers.schema.json` (defines CSV column contract)
- **DEP-005**: No new npm packages required

## 5. Files

### Frontend — Dev Fixtures
- **FILE-001**: `phoenix-frontend/public/data/plots/germany/temperature-evolution.csv` — NEW
- **FILE-002**: `phoenix-frontend/public/data/plots/germany/seasonal-warming.csv` — NEW
- **FILE-003**: `phoenix-frontend/public/data/plots/76_53/temperature-evolution.csv` — NEW
- **FILE-004**: `phoenix-frontend/public/data/plots/76_53/seasonal-warming.csv` — NEW

### Frontend — Utilities
- **FILE-005**: `phoenix-frontend/src/utils/csvParser.ts` — NEW
- **FILE-006**: `phoenix-frontend/src/utils/__tests__/csvParser.test.ts` — NEW

### Frontend — Types
- **FILE-007**: `phoenix-frontend/src/types/plots.ts` — NEW

### Frontend — Service
- **FILE-008**: `phoenix-frontend/src/services/NarrativePlotService.ts` — NEW
- **FILE-009**: `phoenix-frontend/src/services/__tests__/NarrativePlotService.test.ts` — NEW

### Frontend — Redux
- **FILE-010**: `phoenix-frontend/src/store/slices/narrativePlotSlice.ts` — NEW
- **FILE-011**: `phoenix-frontend/src/store/slices/__tests__/narrativePlotSlice.test.ts` — NEW
- **FILE-012**: `phoenix-frontend/src/store/index.ts` — MODIFY — register narrativePlotSlice

### Frontend — Common Components
- **FILE-013**: `phoenix-frontend/src/components/common/ExpandableText.tsx` — NEW

### Frontend — Narrative Components
- **FILE-014**: `phoenix-frontend/src/components/narrative/NarrativeSection.tsx` — NEW
- **FILE-015**: `phoenix-frontend/src/components/narrative/PlotContainer.tsx` — NEW
- **FILE-016**: `phoenix-frontend/src/components/narrative/tabConfig.ts` — NEW
- **FILE-017**: `phoenix-frontend/src/components/narrative/index.ts` — NEW
- **FILE-018**: `phoenix-frontend/src/components/narrative/plots/TemperatureEvolution.tsx` — NEW
- **FILE-019**: `phoenix-frontend/src/components/narrative/plots/SeasonalWarming.tsx` — NEW

### Frontend — Hooks
- **FILE-020**: `phoenix-frontend/src/hooks/usePlotData.ts` — NEW

### Frontend — Tests
- **FILE-021**: `phoenix-frontend/src/components/narrative/__tests__/NarrativeSection.test.tsx` — NEW
- **FILE-022**: `phoenix-frontend/src/components/narrative/__tests__/PlotContainer.test.tsx` — NEW
- **FILE-023**: `phoenix-frontend/src/components/narrative/plots/__tests__/TemperatureEvolution.test.tsx` — NEW
- **FILE-024**: `phoenix-frontend/src/components/narrative/plots/__tests__/SeasonalWarming.test.tsx` — NEW
- **FILE-025**: `phoenix-frontend/src/hooks/__tests__/usePlotData.test.ts` — NEW

### Frontend — Modified
- **FILE-026**: `phoenix-frontend/src/App.tsx` — MODIFY — add NarrativeSection below MetricsRow

### LLM Skills
- **FILE-027**: `.github/skills/narrative-plot/SKILL.md` — NEW
- **FILE-028**: `.github/skills/data-services-integration/SKILL.md` — NEW (or MODIFY replacing existing)

## 6. Testing

- **TEST-001**: `csvParser.test.ts` — parses header row + data rows; converts number/string/integer types; handles empty values as null; handles Windows-style line endings; handles trailing newline
- **TEST-002**: `NarrativePlotService.test.ts` — fetches CSV for a given tile_id + plot type; parses into typed rows; handles 404; handles network errors
- **TEST-003**: `narrativePlotSlice.test.ts` — initial state idle; fetch stores by composite key `tileId:plotType`; cache hit skips re-fetch
- **TEST-004**: `NarrativeSection.test.tsx` — renders 3 tabs with German labels; clicking "Verstehen" tab switches content; active tab has visual indicator; mobile: renders as accordion
- **TEST-005**: `PlotContainer.test.tsx` — renders intro text + chart area + key insight; expandable methodology starts collapsed; clicking toggle shows methodology; loading state shows spinner; error state shows message
- **TEST-006**: `TemperatureEvolution.test.tsx` — renders SVG/canvas element (Observable Plot output); handles empty data gracefully; shows loading overlay; shows error state
- **TEST-007**: `SeasonalWarming.test.tsx` — renders chart with 4 data series; shows legend; loading/error states
- **TEST-008**: `usePlotData.test.ts` — dispatches fetch on mount with correct tileId + plotType; re-dispatches on city change; returns data/loading/error
- **TEST-009**: Regression — all Sprint 1–4 tests still pass

## 7. Risks & Assumptions

### Risks
- **RISK-001**: Observable Plot renders imperatively — React StrictMode double-renders may cause duplicate chart elements — **Mitigation**: use cleanup function in `useEffect` to remove previous chart before re-rendering
- **RISK-002**: CSV parsing edge cases (commas in values, special characters) — **Mitigation**: our CSVs are machine-generated with numeric/simple string columns; no quoted fields needed. If edge cases arise, switch to `d3-dsv`.
- **RISK-003**: Large CSV files (65 years × 12 months = 780 rows for monthly data) may cause slow chart rendering on mobile — **Mitigation**: profile and optimize in Sprint 8; 780 rows is well within Observable Plot's performance envelope
- **RISK-004**: Tab state lost on re-render — **Mitigation**: `activeTab` is local component state, persists across city changes

### Assumptions
- **ASSUMPTION-001**: Dev CSV fixtures with realistic but synthetic data are sufficient for development and testing
- **ASSUMPTION-002**: Observable Plot 0.6 API is stable — `Plot.plot()` returns a DOM element, appended to a ref container
- **ASSUMPTION-003**: Two reference plots (scatter + multi-line) cover the core rendering patterns needed for Sprint 6's remaining 7 plots
- **ASSUMPTION-004**: All plot CSVs use the same URL pattern: `{baseUrl}/{tile_id}/{plot_type}.csv`

## 8. Multi-Agent Execution Notes

### Execution Order
- **Phase 1** (fixtures): Independent, do first
- **Phase 2** (csvParser): Independent, can parallel with Phase 1
- **Phase 3** (types + service): Requires Phase 2 (uses csvParser)
- **Phase 4** (Redux slice): Requires Phase 3 (uses service)
- **Phase 5** (common components): Independent of Phase 3/4, can parallel
- **Phase 6** (2 plots): Requires Phase 4 + Phase 5
- **Phase 7** (skills): Requires Phase 6 (needs reference implementations)
- **Phase 8** (integration): Requires Phase 6

### Agent Context Requirements
- Read `plan/phoenix/00-architecture.md` §4.3 for plot CSV contract
- Read `plan/phoenix/00-architecture.md` §6.1 for `createDataSlice` keyed pattern
- Read `plan/phoenix/sprint-4-climate-stats.md` §10.3 for previous `createDataSlice` keyed usage (metricsSlice)
- Read `phoenix-frontend/src/store/slices/metricsSlice.ts` for working keyed slice example
- Read Observable Plot documentation: https://observablehq.com/plot/
- Read `schemas/plot-csv-headers.schema.json` for CSV column definitions

### Validation Checkpoints
- [After TASK-003]: CSV fixtures accessible at `http://localhost:5173/data/plots/germany/temperature-evolution.csv`
- [After TASK-005]: `npm run test -- csvParser` passes
- [After TASK-008]: `npm run test -- NarrativePlotService` passes
- [After TASK-011]: `npm run test -- narrativePlotSlice` passes
- [After TASK-016]: `npm run test -- NarrativeSection PlotContainer` passes
- [After TASK-021]: Both plots render with fixture data
- [After TASK-027]: Full integration — map + dates + cities + metrics + narrative with 2 plots

## 9. Related Specifications / Further Reading

- `plan/phoenix/00-architecture.md` — §4.3 Plot Data CSV, §6.1 createDataSlice
- `schemas/plot-csv-headers.schema.json` — CSV column contract
- `plan/phoenix/sprint-4-climate-stats.md` — metrics slice (same `createDataSlice` keyed pattern)
- Observable Plot docs: https://observablehq.com/plot/getting-started
- D3 docs: https://d3js.org/

## 10. Code Reference

### 10.1 Plot CSV Format — Temperature Evolution

**File**: `phoenix-frontend/public/data/plots/germany/temperature-evolution.csv` (to be created)

```csv
year,mean_temp,trend
1961,7.8,8.1
1962,7.5,8.1
...
2024,10.2,10.1
2025,10.5,10.2
```

### 10.2 Plot CSV Format — Seasonal Warming

**File**: `phoenix-frontend/public/data/plots/germany/seasonal-warming.csv` (to be created)

```csv
year,winter,spring,summer,fall
1961,0.1,-0.2,0.0,0.3
1962,-0.5,0.1,0.2,-0.1
...
2024,2.1,1.5,1.8,1.2
2025,1.9,1.6,2.0,1.3
```

### 10.3 NarrativePlotService Pattern

**File**: `phoenix-frontend/src/services/NarrativePlotService.ts` (to be created)

```typescript
import { climateDataConfig } from '../config/climateDataConfig';
import { parseCSV, type ColumnTypeMap } from '../utils/csvParser';
import type { PlotType } from '../types/plots';

const COLUMN_TYPES: Record<PlotType, ColumnTypeMap> = {
  'temperature-evolution': { year: 'integer', mean_temp: 'number', trend: 'number' },
  'seasonal-warming': { year: 'integer', winter: 'number', spring: 'number', summer: 'number', fall: 'number' },
  // Remaining 7 plot types added in Sprint 6
};

export const NarrativePlotService = {
  async fetchPlotData<T>(tileId: string, plotType: PlotType): Promise<T[]> {
    const url = `${climateDataConfig.plotDataBaseUrl}/${tileId}/${plotType}.csv`;
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Failed to fetch plot data: ${response.status} ${response.statusText}`);
    }
    const csvText = await response.text();
    const columnTypes = COLUMN_TYPES[plotType];
    if (!columnTypes) throw new Error(`Unknown plot type: ${plotType}`);
    return parseCSV<T>(csvText, columnTypes);
  },
};
```

### 10.4 usePlotData Hook

**File**: `phoenix-frontend/src/hooks/usePlotData.ts` (to be created)

```typescript
import { useEffect } from 'react';
import { useAppSelector } from '../store/hooks/useAppSelector';
import { useAppDispatch } from '../store/hooks/useAppDispatch';
import { narrativePlotActions, narrativePlotSelectors } from '../store/slices/narrativePlotSlice';
import { selectSelectedCity } from '../store/slices/citySlice';
import type { PlotType } from '../types/plots';

export function usePlotData<T>(plotType: PlotType): {
  data: T[] | null;
  isLoading: boolean;
  error: string | null;
} {
  const dispatch = useAppDispatch();
  const selectedCity = useAppSelector(selectSelectedCity);
  const tileId = selectedCity?.tile_id ?? 'germany';

  useEffect(() => {
    dispatch(narrativePlotActions.fetch({ tileId, plotType }));
  }, [dispatch, tileId, plotType]);

  const data = useAppSelector(state =>
    narrativePlotSelectors.selectDataByKey(state, `${tileId}:${plotType}`)
  ) as T[] | null;
  const isLoading = useAppSelector(narrativePlotSelectors.selectIsLoading);
  const error = useAppSelector(narrativePlotSelectors.selectError);

  return { data, isLoading, error };
}
```

### 10.5 Observable Plot Integration Pattern

**File**: `phoenix-frontend/src/components/narrative/plots/TemperatureEvolution.tsx` (to be created)

```typescript
import { useRef, useEffect } from 'react';
import * as Plot from '@observablehq/plot';
import { usePlotData } from '../../../hooks/usePlotData';
import { PlotContainer } from '../PlotContainer';
import { theme } from '../../../styles/design-system';
import type { TemperatureEvolutionRow } from '../../../types/plots';

export function TemperatureEvolution() {
  const { data, isLoading, error } = usePlotData<TemperatureEvolutionRow>('temperature-evolution');
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!data || !containerRef.current) return;

    const chart = Plot.plot({
      style: { background: 'transparent', color: theme.colors.textLight },
      x: { label: 'Jahr' },
      y: { label: '°C', grid: true },
      marks: [
        Plot.dot(data, { x: 'year', y: 'mean_temp', fill: theme.colors.hot, r: 3, opacity: 0.6 }),
        Plot.line(data, { x: 'year', y: 'trend', stroke: theme.colors.hot, strokeWidth: 2 }),
      ],
      width: containerRef.current.clientWidth,
      height: 300,
    });

    containerRef.current.replaceChildren(chart);
    return () => { chart.remove(); };
  }, [data]);

  return (
    <PlotContainer
      title="Temperaturentwicklung"
      introText="Die Jahresmitteltemperatur in Deutschland zeigt einen deutlichen Erwärmungstrend seit den 1960er Jahren."
      keyInsight="Die Erwärmung hat sich seit den 1990er Jahren beschleunigt."
      methodologyText="Dargestellt sind die Jahresmitteltemperaturen (Punkte) und ein geglätteter Trend (LOWESS). Datenquelle: ERA5-Land Reanalyse."
      isLoading={isLoading}
      error={error}
    >
      <div ref={containerRef} />
    </PlotContainer>
  );
}
```

### 10.6 Tab Configuration

**File**: `phoenix-frontend/src/components/narrative/tabConfig.ts` (to be created)

```typescript
import { TemperatureEvolution } from './plots/TemperatureEvolution';
import { SeasonalWarming } from './plots/SeasonalWarming';

export type TabId = 'erkennen' | 'verstehen' | 'handeln';

export interface PlotEntry {
  component: React.ComponentType;
  title: string;
  key: string; // unique key for React rendering
}

export interface TabConfig {
  id: TabId;
  label: string;
  plots: PlotEntry[];
  placeholder?: string; // shown when no plots yet
}

export const tabConfig: TabConfig[] = [
  {
    id: 'erkennen',
    label: 'Erkennen',
    plots: [
      { component: TemperatureEvolution, title: 'Temperaturentwicklung', key: 'temp-evolution' },
      { component: SeasonalWarming, title: 'Saisonale Erwärmung', key: 'seasonal-warming' },
    ],
  },
  {
    id: 'verstehen',
    label: 'Verstehen',
    plots: [],
    placeholder: 'Weitere Visualisierungen folgen in Sprint 6.',
  },
  {
    id: 'handeln',
    label: 'Handeln',
    plots: [],
    placeholder: 'Weitere Visualisierungen folgen in Sprint 6.',
  },
];
```
