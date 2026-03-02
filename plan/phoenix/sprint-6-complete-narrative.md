---
goal: "Sprint 6 — Complete Narrative: Remaining 7 Plots Across 3 Tabs"
version: 1.0
date_created: 2026-03-02
last_updated: 2026-03-02
owner: phoenix
status: 'Planned'
tags: [feature, narrative, plots, sprint-6]
---

# Sprint 6 — Complete Narrative (7 Remaining Plots)

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Complete all 9 narrative plots across 3 tabs using the `narrative-plot` skill established in Sprint 5. This sprint adds 4 plots to "Verstehen" and 3 plots to "Handeln". Each plot follows the proven pattern: row type → column types → component → PlotContainer → tests.

**Prerequisite**: Sprint 5 completed — narrative section with 2 reference plots + LLM skills.

**Architecture reference**: See `plan/phoenix/00-architecture.md` §4.3 for plot CSV contract. Use `.github/skills/narrative-plot/SKILL.md` for each plot.

## 1. Requirements & Constraints

- **REQ-001**: 4 plots in "Verstehen" tab:
  1. **Monthly Distribution** — 12-panel box plot grid showing temperature distribution per month across decades
  2. **Extremes Inverted** — diverging horizontal bars for 4 threshold metrics (hot days, tropical nights, ice days, frost days)
  3. **Record-Breaking Reality** — stacked area chart: hot vs cold records per year
  4. **Winter Forgot to Come** — dual-axis: snow days (bars) + transition days with rain (line)
- **REQ-002**: 3 plots in "Handeln" tab:
  1. **Comfort Calendar** — decade × month heatmap showing comfortable day frequency
  2. **Tropical Nights** — bars (count per year) + trend line overlay
  3. **Vegetation Stress** — stacked area: hot/dry days, extreme heat days, late frost days
- **REQ-003**: Each plot uses the `narrative-plot` skill pattern: row type in `types/plots.ts`, column types in `NarrativePlotService`, component with `usePlotData`, wrapped in `PlotContainer` with German narrative text
- **REQ-004**: Each plot has unit tests verifying rendering, loading, and error states
- **REQ-005**: All plots responsive to container width
- **REQ-006**: Dev CSV fixtures for all 7 plot types (germany + one test tile_id)
- **REQ-007**: "Verstehen" and "Handeln" tab placeholders replaced with actual plot components
- **CON-001**: Follow skill pattern exactly — no deviation from Sprint 5 reference
- **CON-002**: All German narrative text (introText, keyInsight, methodologyText) provided per plot
- **PAT-001**: Use `narrative-plot` skill for every plot (defined in Sprint 5)
- **GUD-001**: If a new chart type is needed (heatmap, stacked area, box plot), create a shared Observable Plot helper in `src/utils/plotHelpers.ts`

## 2. Implementation Steps

### Phase 1: Dev Fixtures for Remaining 7 Plot Types

- GOAL-001: CSV fixtures for all remaining plots

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-001 | Create CSV fixtures for "Verstehen" plots in `public/data/plots/germany/` and `public/data/plots/76_53/`: `monthly-distribution.csv` (columns: month, decade, q25, median, q75, min, max), `extremes-inverted.csv` (columns: year, hot_days, tropical_nights, ice_days, frost_days), `record-breaking-reality.csv` (columns: year, hot_records, cold_records), `winter-snow-loss.csv` (columns: year, snow_days, rain_transition_days) | | |
| TASK-002 | Create CSV fixtures for "Handeln" plots: `comfort-calendar.csv` (columns: decade, month, comfortable_days_pct), `tropical-nights.csv` (columns: year, count, trend), `vegetation-stress.csv` (columns: year, hot_dry_days, extreme_heat_days, late_frost_days) | | |

### Phase 2: Plot Type Definitions + Service Registration

- GOAL-002: Complete all plot type definitions and register column types

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-003 | Update `src/types/plots.ts` — add row types for all 7 remaining plots: `MonthlyDistributionRow`, `ExtremesInvertedRow`, `RecordBreakingRow`, `WinterSnowLossRow`, `ComfortCalendarRow`, `TropicalNightsRow`, `VegetationStressRow` | | |
| TASK-004 | Update `src/services/NarrativePlotService.ts` — add column type definitions for all 7 new plot types to the `COLUMN_TYPES` registry | | |

### Phase 3: Observable Plot Helpers

- GOAL-003: Shared chart rendering utilities for new chart types

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-005 | Create `src/utils/plotHelpers.ts` — shared Observable Plot configuration helpers: `createHeatmap(data, options)` for decade×month grids, `createStackedArea(data, options)` for stacked area charts, `createBoxPlot(data, options)` for box-and-whisker displays. Each returns Observable Plot mark arrays. Also: shared axis formatting, theme-aware color scales. | | |
| TASK-006 | Create `src/utils/__tests__/plotHelpers.test.ts` — test: each helper returns valid mark arrays, handles empty data | | |

### Phase 4: Verstehen Tab — 4 Plots

- GOAL-004: Build all 4 "Verstehen" plots following the narrative-plot skill

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-007 | Create `src/components/narrative/plots/MonthlyDistribution.tsx` — 12-panel box plot grid (one box per month, showing temperature distribution across decades). Uses Observable Plot `boxX` or custom mark. introText: "Die monatlichen Temperaturverteilungen zeigen, wie sich die Bandbreite der Temperaturen über die Jahrzehnte verschoben hat." keyInsight: "Insbesondere die Wintermonate zeigen eine deutliche Verschiebung zu wärmeren Temperaturen." | | |
| TASK-008 | Create `src/components/narrative/plots/ExtremesInverted.tsx` — diverging horizontal bar chart. Hot days and tropical nights extend right (red), ice days and frost days extend left (blue). Per-year or for most recent year with reference comparison. introText: "Hitzeextreme nehmen zu, während Kälteextreme deutlich abnehmen." keyInsight: "Die Zahl der heißen Tage hat sich seit den 1960ern verdoppelt, während Eistage um die Hälfte zurückgingen." | | |
| TASK-009 | Create `src/components/narrative/plots/RecordBreakingReality.tsx` — stacked area chart: hot records (red, above axis) vs cold records (blue, below axis or stacked). Shows acceleration of heat records. introText: "Temperaturrekorde werden immer häufiger gebrochen — aber vor allem auf der warmen Seite." keyInsight: "Seit 2000 überwiegen Hitzerekorde gegenüber Kälterekorden im Verhältnis 5:1." | | |
| TASK-010 | Create `src/components/narrative/plots/WinterSnowLoss.tsx` — dual display: snow day bars (blue) + rain-on-would-be-snow-days line (gray). Shows transition from snow to rain. introText: "Schneetage verschwinden — Niederschlag fällt zunehmend als Regen statt als Schnee." keyInsight: "Die Anzahl der Schneetage hat sich seit der Referenzperiode nahezu halbiert." | | |
| TASK-011 | Create tests for all 4 Verstehen plots: `MonthlyDistribution.test.tsx`, `ExtremesInverted.test.tsx`, `RecordBreakingReality.test.tsx`, `WinterSnowLoss.test.tsx` — each tests rendering, loading, error states | | |

### Phase 5: Handeln Tab — 3 Plots

- GOAL-005: Build all 3 "Handeln" plots following the narrative-plot skill

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-012 | Create `src/components/narrative/plots/ComfortCalendar.tsx` — decade × month heatmap. Cells colored by percentage of comfortable days (15–25°C). Green = high comfort, yellow = moderate, red = low. Uses `createHeatmap` helper. introText: "Der Komfortkalender zeigt, wann im Jahr angenehme Temperaturen herrschen — und wie sich dieses Fenster verschiebt." keyInsight: "Das Komfortfenster verschiebt sich: Frühjahr und Herbst werden angenehmer, der Sommer zunehmend heiß." | | |
| TASK-013 | Create `src/components/narrative/plots/TropicalNights.tsx` — bar chart (count per year, red) + trend line overlay. introText: "Tropennächte — Nächte, in denen die Temperatur nicht unter 20°C sinkt — waren in Deutschland einst die Ausnahme." keyInsight: "Die Häufigkeit von Tropennächten hat sich in den letzten 30 Jahren verdreifacht." | | |
| TASK-014 | Create `src/components/narrative/plots/VegetationStress.tsx` — stacked area: hot/dry days (orange), extreme heat days (red), late frost days (blue). Shows combined stress on vegetation. Uses `createStackedArea` helper. introText: "Pflanzenstress durch Hitze, Trockenheit und Spätfrost gefährdet Landwirtschaft und Ökosysteme." keyInsight: "Während Spätfrost abnimmt, überwiegt der Anstieg von Hitze- und Trockenstress deutlich." | | |
| TASK-015 | Create tests for all 3 Handeln plots: `ComfortCalendar.test.tsx`, `TropicalNights.test.tsx`, `VegetationStress.test.tsx` — each tests rendering, loading, error states | | |

### Phase 6: Tab Configuration Update + Integration

- GOAL-006: Wire all 7 new plots into their respective tabs, full integration test

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-016 | Update `src/components/narrative/tabConfig.ts` — add all 4 Verstehen plots and 3 Handeln plots to their respective tab entries. Remove placeholder messages. | | |
| TASK-017 | Verify: `npm run test` — all tests pass (Sprint 1–6). Manual test: all 3 tabs populated with working plots. Switch between cities — all 9 plots update. Mobile accordion works for all tabs. | | |

## 3. Alternatives

- **ALT-001**: Use a dedicated heatmap library (e.g., nivo) for ComfortCalendar — rejected; Observable Plot's `cell` mark handles heatmaps well and keeps us on one charting library
- **ALT-002**: Build all 7 plots without the skill — possible but slower; the skill ensures consistent structure and reduces errors from deviating from the pattern
- **ALT-003**: Lazy-import each plot component — can be added in Sprint 8 (polish) if bundle size is a concern; for now, the 9 plots are small
- **ALT-004**: Combine Verstehen and Handeln into one implementation phase — rejected; separating by tab keeps phases manageable and testable

## 4. Dependencies

- **DEP-001**: Sprint 5 completed (narrative section container, 2 reference plots, skills)
- **DEP-002**: `.github/skills/narrative-plot/SKILL.md` (pattern for each plot)
- **DEP-003**: Observable Plot 0.6+ and D3 7.9+ (already installed)
- **DEP-004**: No new npm packages

## 5. Files

### Frontend — Dev Fixtures
- **FILE-001**: `phoenix-frontend/public/data/plots/germany/monthly-distribution.csv` — NEW
- **FILE-002**: `phoenix-frontend/public/data/plots/germany/extremes-inverted.csv` — NEW
- **FILE-003**: `phoenix-frontend/public/data/plots/germany/record-breaking-reality.csv` — NEW
- **FILE-004**: `phoenix-frontend/public/data/plots/germany/winter-snow-loss.csv` — NEW
- **FILE-005**: `phoenix-frontend/public/data/plots/germany/comfort-calendar.csv` — NEW
- **FILE-006**: `phoenix-frontend/public/data/plots/germany/tropical-nights.csv` — NEW
- **FILE-007**: `phoenix-frontend/public/data/plots/germany/vegetation-stress.csv` — NEW
- **FILE-008**: `phoenix-frontend/public/data/plots/76_53/` — NEW — same 7 CSVs for Berlin tile

### Frontend — Utilities
- **FILE-009**: `phoenix-frontend/src/utils/plotHelpers.ts` — NEW
- **FILE-010**: `phoenix-frontend/src/utils/__tests__/plotHelpers.test.ts` — NEW

### Frontend — Types + Service (Modified)
- **FILE-011**: `phoenix-frontend/src/types/plots.ts` — MODIFY — add 7 row types
- **FILE-012**: `phoenix-frontend/src/services/NarrativePlotService.ts` — MODIFY — add 7 column type entries

### Frontend — Plot Components
- **FILE-013**: `phoenix-frontend/src/components/narrative/plots/MonthlyDistribution.tsx` — NEW
- **FILE-014**: `phoenix-frontend/src/components/narrative/plots/ExtremesInverted.tsx` — NEW
- **FILE-015**: `phoenix-frontend/src/components/narrative/plots/RecordBreakingReality.tsx` — NEW
- **FILE-016**: `phoenix-frontend/src/components/narrative/plots/WinterSnowLoss.tsx` — NEW
- **FILE-017**: `phoenix-frontend/src/components/narrative/plots/ComfortCalendar.tsx` — NEW
- **FILE-018**: `phoenix-frontend/src/components/narrative/plots/TropicalNights.tsx` — NEW
- **FILE-019**: `phoenix-frontend/src/components/narrative/plots/VegetationStress.tsx` — NEW

### Frontend — Tests
- **FILE-020**: `phoenix-frontend/src/components/narrative/plots/__tests__/MonthlyDistribution.test.tsx` — NEW
- **FILE-021**: `phoenix-frontend/src/components/narrative/plots/__tests__/ExtremesInverted.test.tsx` — NEW
- **FILE-022**: `phoenix-frontend/src/components/narrative/plots/__tests__/RecordBreakingReality.test.tsx` — NEW
- **FILE-023**: `phoenix-frontend/src/components/narrative/plots/__tests__/WinterSnowLoss.test.tsx` — NEW
- **FILE-024**: `phoenix-frontend/src/components/narrative/plots/__tests__/ComfortCalendar.test.tsx` — NEW
- **FILE-025**: `phoenix-frontend/src/components/narrative/plots/__tests__/TropicalNights.test.tsx` — NEW
- **FILE-026**: `phoenix-frontend/src/components/narrative/plots/__tests__/VegetationStress.test.tsx` — NEW

### Frontend — Modified
- **FILE-027**: `phoenix-frontend/src/components/narrative/tabConfig.ts` — MODIFY — register all 7 plots

## 6. Testing

Each plot follows the same test pattern (from `narrative-plot` skill):
- **TEST-001**: `MonthlyDistribution.test.tsx` — renders box plot grid, 12 panels visible, loading/error states
- **TEST-002**: `ExtremesInverted.test.tsx` — renders diverging bars, 4 metrics visible, loading/error states
- **TEST-003**: `RecordBreakingReality.test.tsx` — renders stacked area, hot/cold series, loading/error states
- **TEST-004**: `WinterSnowLoss.test.tsx` — renders bars + line, loading/error states
- **TEST-005**: `ComfortCalendar.test.tsx` — renders heatmap grid, decade×month cells, loading/error states
- **TEST-006**: `TropicalNights.test.tsx` — renders bars + trend line, loading/error states
- **TEST-007**: `VegetationStress.test.tsx` — renders stacked area, 3 stress categories, loading/error states
- **TEST-008**: `plotHelpers.test.ts` — each helper returns valid mark arrays, handles empty data
- **TEST-009**: Regression — all Sprint 1–5 tests still pass; tab switching with all 9 plots works

## 7. Risks & Assumptions

### Risks
- **RISK-001**: Some chart types (box plots, heatmaps) may be complex in Observable Plot — **Mitigation**: `plotHelpers.ts` encapsulates complexity; if a particular chart type doesn't work well in Observable Plot, fall back to raw D3 SVG for that one chart
- **RISK-002**: 7 plots × 2 tile_ids = 14 CSV fixtures to maintain — **Mitigation**: fixtures are small, generated once, and don't change; a script could generate them from backend if needed
- **RISK-003**: Bundle size grows with 9 plot components — **Mitigation**: acceptable for Sprint 6; lazy imports can be added in Sprint 8 if needed

### Assumptions
- **ASSUMPTION-001**: The `narrative-plot` skill from Sprint 5 is correct and complete
- **ASSUMPTION-002**: Observable Plot 0.6 supports all needed chart types (scatter, line, bar, box, heatmap, stacked area) — verified for scatter and line in Sprint 5
- **ASSUMPTION-003**: `plotHelpers.ts` abstractions are reusable across all 7 plots that need them

## 8. Multi-Agent Execution Notes

### Execution Order
- **Phase 1** (fixtures): Do first, independent
- **Phase 2** (types + service update): Requires Phase 1 column knowledge
- **Phase 3** (plotHelpers): Can parallel with Phase 2
- **Phase 4** (4 Verstehen plots): Requires Phase 2 + 3. Plots can be built in parallel (each is independent)
- **Phase 5** (3 Handeln plots): Can parallel with Phase 4 (each is independent)
- **Phase 6** (integration): Requires Phase 4 + 5

### Parallel Plot Construction
All 7 plots are independent of each other. If using multiple agents:
- Agent A: MonthlyDistribution + ExtremesInverted + ComfortCalendar (use `createHeatmap`/box plot helpers)
- Agent B: RecordBreakingReality + VegetationStress (use `createStackedArea` helper)
- Agent C: WinterSnowLoss + TropicalNights (bar + line charts)

### Agent Context Requirements
- Read `.github/skills/narrative-plot/SKILL.md` for the plot construction pattern
- Read `phoenix-frontend/src/components/narrative/plots/TemperatureEvolution.tsx` as reference implementation
- Read `phoenix-frontend/src/types/plots.ts` for existing type patterns
- Read `phoenix-frontend/src/utils/plotHelpers.ts` (created in Phase 3) for shared helpers
- Read `phoenix-frontend/src/components/narrative/tabConfig.ts` for registration pattern

### Validation Checkpoints
- [After TASK-002]: All 14 CSV fixtures exist and are accessible via dev server
- [After TASK-004]: `NarrativePlotService` can parse all 9 plot types
- [After TASK-006]: `npm run test -- plotHelpers` passes
- [After TASK-011]: `npm run test` — all Verstehen plot tests pass
- [After TASK-015]: `npm run test` — all Handeln plot tests pass
- [After TASK-017]: Full integration — all 9 plots across 3 tabs render correctly

## 9. Related Specifications / Further Reading

- `.github/skills/narrative-plot/SKILL.md` — Plot construction skill
- `plan/phoenix/sprint-5-narrative-foundation.md` — Reference implementations
- `plan/phoenix/00-architecture.md` §4.3 — Plot CSV contract
- Observable Plot marks reference: https://observablehq.com/plot/marks

## 10. Code Reference

### 10.1 Plot Type Definitions (to add)

**File**: `phoenix-frontend/src/types/plots.ts` (modify — add these types)

```typescript
// --- Verstehen plots ---

export interface MonthlyDistributionRow {
  month: number;       // 1–12
  decade: string;      // e.g., "1961-1970"
  q25: number;         // 25th percentile °C
  median: number;      // median °C
  q75: number;         // 75th percentile °C
  min: number;         // minimum °C
  max: number;         // maximum °C
}

export interface ExtremesInvertedRow {
  year: number;
  hot_days: number;          // Tmax ≥ 30°C
  tropical_nights: number;   // Tmin > 20°C
  ice_days: number;          // Tmax ≤ 0°C
  frost_days: number;        // Tmin < 0°C
}

export interface RecordBreakingRow {
  year: number;
  hot_records: number;   // New Tmax records
  cold_records: number;  // New Tmin records
}

export interface WinterSnowLossRow {
  year: number;
  snow_days: number;
  rain_transition_days: number;
}

// --- Handeln plots ---

export interface ComfortCalendarRow {
  decade: string;              // e.g., "2011-2020"
  month: number;               // 1–12
  comfortable_days_pct: number; // 0–100
}

export interface TropicalNightsRow {
  year: number;
  count: number;
  trend: number;
}

export interface VegetationStressRow {
  year: number;
  hot_dry_days: number;
  extreme_heat_days: number;
  late_frost_days: number;
}
```

### 10.2 Column Types Registry (to add)

**File**: `phoenix-frontend/src/services/NarrativePlotService.ts` (modify — add to COLUMN_TYPES)

```typescript
const COLUMN_TYPES: Record<PlotType, ColumnTypeMap> = {
  // Sprint 5 (existing)
  'temperature-evolution': { year: 'integer', mean_temp: 'number', trend: 'number' },
  'seasonal-warming': { year: 'integer', winter: 'number', spring: 'number', summer: 'number', fall: 'number' },
  // Sprint 6 — Verstehen
  'monthly-distribution': { month: 'integer', decade: 'string', q25: 'number', median: 'number', q75: 'number', min: 'number', max: 'number' },
  'extremes-inverted': { year: 'integer', hot_days: 'integer', tropical_nights: 'integer', ice_days: 'integer', frost_days: 'integer' },
  'record-breaking-reality': { year: 'integer', hot_records: 'integer', cold_records: 'integer' },
  'winter-snow-loss': { year: 'integer', snow_days: 'integer', rain_transition_days: 'integer' },
  // Sprint 6 — Handeln
  'comfort-calendar': { decade: 'string', month: 'integer', comfortable_days_pct: 'number' },
  'tropical-nights': { year: 'integer', count: 'integer', trend: 'number' },
  'vegetation-stress': { year: 'integer', hot_dry_days: 'integer', extreme_heat_days: 'integer', late_frost_days: 'integer' },
};
```

### 10.3 Heatmap Helper Pattern

**File**: `phoenix-frontend/src/utils/plotHelpers.ts` (to be created)

```typescript
import * as Plot from '@observablehq/plot';
import { theme } from '../styles/design-system';

export interface HeatmapOptions {
  x: string;
  y: string;
  fill: string;
  xLabel?: string;
  yLabel?: string;
  colorScheme?: string;
}

export function createHeatmapMarks(data: Record<string, unknown>[], options: HeatmapOptions): Plot.Markish[] {
  return [
    Plot.cell(data, {
      x: options.x,
      y: options.y,
      fill: options.fill,
      inset: 0.5,
    }),
  ];
}

export interface StackedAreaOptions {
  x: string;
  series: string[];
  colors?: string[];
}

export function createStackedAreaMarks(data: Record<string, unknown>[], options: StackedAreaOptions): Plot.Markish[] {
  // Transform wide-format data to long format for Observable Plot
  const long = options.series.flatMap((key, i) =>
    data.map(d => ({ x: d[options.x], y: d[key] as number, series: key }))
  );
  return [
    Plot.areaY(long, Plot.stackY({ x: 'x', y: 'y', fill: 'series', order: 'appearance' })),
  ];
}
```
