---
goal: Phase 9 - Frontend Narrative Plots with Tab Navigation
version: 1.1
date_created: 2026-02-16
last_updated: 2026-02-16
owner: Sebastian
status: 'Planned'
tags: [phase-9, frontend, plots, narrative, visualization, d3, observable-plot]
---

# Introduction

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

This phase implements the narrative plot section that tells the climate story through interactive visualizations. The plots are organized into three narrative tabs: **Recognition** (acknowledging warming), **Understanding** (causes and patterns), and **Response** (personal impacts and planning). Each tab contains multiple plot types rendered using Observable Plot (already installed) with D3 for data manipulation.

**Key deliverables:**
- `NarrativeSection` container with tab navigation
- Tab components for Recognition, Understanding, Response
- 7 plot components:
  - Recognition: Temperature Evolution, Seasonal Warming
  - Understanding: Monthly Distribution, Extremes Inverted
  - Response: Comfort Calendar, Tropical Nights, Vegetation Stress
- Plot data services and Redux state management
- `ExpandableText` component for "Read more" methodology descriptions
- Animations and transitions between tabs
- City-specific plot updates on selection

## 1. Requirements & Constraints

### Functional Requirements (from Master Plan)
- **REQ-005**: Implement narrative sections with interactive plots (Recognition, Understanding, Response)
- **REQ-004**: Support city selection with city-specific metrics and visualizations
- **REQ-009**: Provide responsive design for mobile and desktop

### Phase-Specific Requirements
- **REQ-P9-001**: Display 3 narrative tabs with smooth transitions
- **REQ-P9-002**: Recognition tab: Temperature Evolution scatter + Seasonal Warming multi-line chart
- **REQ-P9-003**: Understanding tab: Monthly Distribution box plots + Extremes diverging bars
- **REQ-P9-004**: Response tab: Comfort Calendar heatmap + Tropical Nights chart + Vegetation Stress chart
- **REQ-P9-005**: Each plot must include methodology info via ExpandableText
- **REQ-P9-006**: Plots update on city selection
- **REQ-P9-007**: Mobile: tabs become accordion-style collapsible sections
- **REQ-P9-008**: Include trend lines (LOWESS or rolling average) where appropriate

### Technical Constraints
- **CON-P9-001**: Must use existing Observable Plot (@observablehq/plot) library
- **CON-P9-002**: D3 already installed for data manipulation
- **CON-P9-003**: Plot data served as CSV from Hetzner Object Storage
- **CON-P9-004**: Follow existing PlotView and dark mode patterns

### Patterns to Follow
- **PAT-001**: Use createDataSlice factory for data state
- **PAT-002**: Follow existing iceAndHotDays plot component structure
- **PAT-003**: Use design-system tokens and theme for styling
- **PAT-004**: Use createStackedPlotView factory for two-panel layouts

## 2. Implementation Steps

### Implementation Phase 9.1: Tab Navigation Infrastructure

- GOAL-P9-001: Create tab navigation component and container

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-900 | Create `frontend/src/components/plots/narrative/NarrativeSection.tsx` container | | |
| TASK-901 | Create `frontend/src/components/plots/narrative/TabNavigation.tsx` tab bar | | |
| TASK-902 | Implement tab state management (local or Redux) | | |
| TASK-903 | Create tab transition animations (CSS transitions) | | |
| TASK-904 | Implement mobile accordion variant | | |
| TASK-905 | Write tests for NarrativeSection and TabNavigation | | |

**Completion Criteria:**
- 3 tabs display with correct labels
- Tab switching works with smooth transitions
- Mobile switches to accordion layout
- Each tab renders placeholder content

---

### Implementation Phase 9.2: ExpandableText Component

- GOAL-P9-002: Create component for "Read more" methodology text

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-906 | Create `frontend/src/components/common/ExpandableText.tsx` | | |
| TASK-907 | Implement collapsed state with "Read more" link | | |
| TASK-908 | Implement expanded state with full text and "Read less" | | |
| TASK-909 | Add smooth expand/collapse animation | | |
| TASK-910 | Write tests for ExpandableText | | |

**Completion Criteria:**
- Component shows truncated text by default
- Click toggles full text visibility
- Animation is smooth (height transition)

---

### Implementation Phase 9.3: Plot Data Types and Service

- GOAL-P9-003: Define plot data structures and fetching service

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-911 | Create `frontend/src/types/plotData.ts` with interfaces | | |
| TASK-912 | Create `frontend/src/services/NarrativePlotService.ts` | | |
| TASK-913 | Implement `fetchTemperatureEvolutionData(locationId)` | | |
| TASK-914 | Implement `fetchSeasonalWarmingData(locationId)` | | |
| TASK-915 | Implement `fetchMonthlyDistributionData(locationId)` | | |
| TASK-916 | Implement `fetchExtremesData(locationId)` | | |
| TASK-917 | Implement `fetchComfortCalendarData(locationId)` | | |
| TASK-918 | Implement `fetchTropicalNightsData(locationId)` | | |
| TASK-919 | Implement `fetchVegetationStressData(locationId)` | | |
| TASK-920 | Write unit tests for NarrativePlotService | | |

**Completion Criteria:**
- All 7 data fetchers implemented
- Data parsed and typed correctly
- Error handling for missing data

---

### Implementation Phase 9.4: Narrative Plot Slice

- GOAL-P9-004: Create Redux slice for narrative plot data

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-921 | Create `frontend/src/store/slices/narrativePlotSlice.ts` | | |
| TASK-922 | Configure keyed cache by location + plot type | | |
| TASK-923 | Create selectors for each plot data type (7 total) | | |
| TASK-924 | Create combined fetcher for all plots on location change | | |
| TASK-925 | Register slice in store/index.ts | | |
| TASK-926 | Write tests for narrativePlotSlice | | |

**Completion Criteria:**
- Plot data cached by location
- All selectors return typed data
- Location change triggers data fetch

---

### Implementation Phase 9.5: Temperature Evolution Plot

- GOAL-P9-005: Implement Recognition plot 1 - Temperature Evolution

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-927 | Create `frontend/src/components/plots/narrative/recognition/TemperatureEvolution.tsx` | | |
| TASK-928 | Render scatter plot of yearly temperatures using Observable Plot | | |
| TASK-929 | Add LOWESS or rolling average trend line | | |
| TASK-930 | Color code points by anomaly (warm = red, cool = blue) | | |
| TASK-931 | Add axis labels and title | | |
| TASK-932 | Include ExpandableText with methodology | | |
| TASK-933 | Write tests for TemperatureEvolution | | |

**Completion Criteria:**
- Scatter plot renders all years
- Trend line visible
- Color coding correct
- Responsive sizing

---

### Implementation Phase 9.6: Seasonal Warming Plot

- GOAL-P9-006: Implement Recognition plot 2 - Seasonal Warming

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-934 | Create `frontend/src/components/plots/narrative/recognition/SeasonalWarming.tsx` | | |
| TASK-935 | Render multi-line chart (4 lines for seasons) | | |
| TASK-936 | X-axis: years, Y-axis: temperature anomaly | | |
| TASK-937 | Add legend for season colors | | |
| TASK-938 | Highlight fastest-warming season | | |
| TASK-939 | Include ExpandableText with methodology | | |
| TASK-940 | Write tests for SeasonalWarming | | |

**Completion Criteria:**
- 4 season lines visible
- Legend displays correctly
- Fastest-warming season highlighted
- Responsive sizing

---

### Implementation Phase 9.7: Monthly Distribution Plot

- GOAL-P9-007: Implement Understanding plot 1 - Monthly Distribution

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-941 | Create `frontend/src/components/plots/narrative/understanding/MonthlyDistribution.tsx` | | |
| TASK-942 | Render box plots for each month using Observable Plot | | |
| TASK-943 | Show reference period vs. recent decade comparison | | |
| TASK-944 | Color code by temperature (cool months blue, warm red) | | |
| TASK-945 | Add axis labels (months, temperature) | | |
| TASK-946 | Include ExpandableText with methodology | | |
| TASK-947 | Write tests for MonthlyDistribution | | |

**Completion Criteria:**
- 12 box plots rendered (one per month)
- Reference vs. recent comparison visible
- Color coding correct
- Responsive sizing

---

### Implementation Phase 9.8: Extremes Plot

- GOAL-P9-008: Implement Understanding plot 2 - Extremes/Inverted

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-948 | Create `frontend/src/components/plots/narrative/understanding/ExtremesInverted.tsx` | | |
| TASK-949 | Render diverging bar chart (hot days right, cold days left) | | |
| TASK-950 | Y-axis: years, X-axis: days count | | |
| TASK-951 | Color code (red for hot, blue for cold) | | |
| TASK-952 | Add reference line for average | | |
| TASK-953 | Include ExpandableText with methodology | | |
| TASK-954 | Write tests for ExtremesInverted | | |

**Completion Criteria:**
- Diverging bars render correctly
- Hot days on right (red), cold on left (blue)
- Reference line visible
- Responsive sizing

---

### Implementation Phase 9.9: Comfort Calendar Plot

- GOAL-P9-009: Implement Response plot 1 - Comfort Calendar Heatmap

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-955 | Create `frontend/src/components/plots/narrative/response/ComfortCalendar.tsx` | | |
| TASK-956 | Render heatmap with decades (rows) x months (columns) | | |
| TASK-957 | Color cells by comfortable days count (green gradient) | | |
| TASK-958 | Display day count in each cell | | |
| TASK-959 | Add axis labels (decades, months) | | |
| TASK-960 | Include ExpandableText with methodology | | |
| TASK-961 | Write tests for ComfortCalendar | | |

**Completion Criteria:**
- Heatmap renders 7 decades × 12 months
- Color scale shows comfortable days (15-25°C)
- Cell annotations display day counts
- Responsive sizing

---

### Implementation Phase 9.10: Tropical Nights Plot

- GOAL-P9-010: Implement Response plot 2 - Sleep Interrupted (Tropical Nights + Heat Stress)

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-962 | Create `frontend/src/components/plots/narrative/response/TropicalNights.tsx` | | |
| TASK-963 | Render combined bar + line chart | | |
| TASK-964 | Bars: tropical nights (Tmin ≥ 20°C) per year | | |
| TASK-965 | Line: heat stress days (Tmax ≥ 32°C) per year | | |
| TASK-966 | Color bars by intensity (yellow to red gradient) | | |
| TASK-967 | Add reference annotations for historical averages | | |
| TASK-968 | Include ExpandableText with methodology | | |
| TASK-969 | Write tests for TropicalNights | | |

**Completion Criteria:**
- Bar chart shows tropical nights trend
- Line overlay shows heat stress days
- Historical reference annotations visible
- Responsive sizing

---

### Implementation Phase 9.11: Vegetation Stress Plot

- GOAL-P9-011: Implement Response plot 3 - Green Crisis (Vegetation Stress)

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-970 | Create `frontend/src/components/plots/narrative/response/VegetationStress.tsx` | | |
| TASK-971 | Render stacked area chart with 3 stress types | | |
| TASK-972 | Brown area: hot & dry days (Tmax ≥30°C, 7-day precip <0.5mm) | | |
| TASK-973 | Red area: extreme heat days (Tmax ≥35°C) | | |
| TASK-974 | Blue markers: late spring frost (after Apr 15, Tmin ≤-2°C) | | |
| TASK-975 | Add legend for stress types | | |
| TASK-976 | Include ExpandableText with methodology | | |
| TASK-977 | Write tests for VegetationStress | | |

**Completion Criteria:**
- Stacked areas show cumulative stress burden
- Three stress types distinguishable by color
- Legend displays correctly
- Responsive sizing

---

### Implementation Phase 9.12: Tab Content Integration

- GOAL-P9-012: Integrate plots into tab panels

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-978 | Create `frontend/src/components/plots/narrative/tabs/RecognitionTab.tsx` | | |
| TASK-979 | Create `frontend/src/components/plots/narrative/tabs/UnderstandingTab.tsx` | | |
| TASK-980 | Create `frontend/src/components/plots/narrative/tabs/ResponseTab.tsx` with 3 Response plots | | |
| TASK-981 | Connect tabs to NarrativeSection container | | |
| TASK-982 | Implement lazy loading for inactive tabs | | |
| TASK-983 | Write integration tests for full narrative flow | | |

**Completion Criteria:**
- All tabs render correct plots
- Tab switching loads correct content
- Lazy loading prevents unnecessary renders
- Response tab shows all 3 Response plots

---

### Implementation Phase 9.13: Custom Hook & Polish

- GOAL-P9-013: Create useNarrativePlots hook and finalize

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-984 | Create `frontend/src/hooks/useNarrativePlots.ts` | | |
| TASK-985 | Implement auto-fetch on city selection | | |
| TASK-986 | Add plot loading skeleton/placeholder | | |
| TASK-987 | Create barrel export for narrative components | | |
| TASK-988 | Add E2E tests for narrative section | | |

**Completion Criteria:**
- Hook provides all narrative plot data
- Loading states display correctly
- City changes trigger plot updates
- Full integration tested

## 3. Alternatives

- **ALT-P9-001**: **Recharts instead of Observable Plot** - Considered for simpler React integration. Rejected because Observable Plot is already installed, more powerful for statistical visualizations, and aligns with existing codebase.

- **ALT-P9-002**: **All plots in one scrollable section vs. tabs** - Considered single-page layout. Rejected because tabs provide focused narrative flow and reduce initial render complexity.

- **ALT-P9-003**: **WebGL-based plots (deck.gl, Plotly GL)** - Considered for large datasets. Rejected because SVG-based Observable Plot is sufficient for yearly aggregated data (~100 points per plot).

- **ALT-P9-004**: **Server-side plot rendering** - Considered for faster initial load. Rejected because client-side rendering enables interactivity and reduces server costs.

- **ALT-P9-005**: **Climate Analog Map ("City X now feels like City Y")** - Original plan included a map showing which city's historical climate matches the current city's present climate. Rejected as too complex: requires extensive preprocessing of climate signatures for hundreds of European cities, complex matching algorithms, and map rendering infrastructure. May be reconsidered for future phases.

## 4. Dependencies

### External Dependencies
- **DEP-P9-001**: `@observablehq/plot` - Already installed, primary plotting library
- **DEP-P9-002**: `d3` - Already installed, data manipulation
- **DEP-P9-003**: Plot CSV data from Hetzner Object Storage (Phase 5 output)

### Internal Dependencies
- **DEP-P9-004**: createDataSlice factory (existing)
- **DEP-P9-005**: selectedCitySlice (existing) - city selection state
- **DEP-P9-006**: Design system tokens (existing)
- **DEP-P9-007**: PlotView components (existing) - layout patterns

### Phase Dependencies
- **DEP-P9-008**: Phase 1 (Testing Infrastructure) - Vitest configured
- **DEP-P9-009**: Phase 8 (Metrics Cards) - shared patterns
- **DEP-P9-010**: Can develop with mock data before Phase 5 completes

## 5. Files

### New Files
- **FILE-P9-001**: `frontend/src/components/plots/narrative/NarrativeSection.tsx` - NEW
- **FILE-P9-002**: `frontend/src/components/plots/narrative/TabNavigation.tsx` - NEW
- **FILE-P9-003**: `frontend/src/components/plots/narrative/tabs/RecognitionTab.tsx` - NEW
- **FILE-P9-004**: `frontend/src/components/plots/narrative/tabs/UnderstandingTab.tsx` - NEW
- **FILE-P9-005**: `frontend/src/components/plots/narrative/tabs/ResponseTab.tsx` - NEW
- **FILE-P9-006**: `frontend/src/components/plots/narrative/recognition/TemperatureEvolution.tsx` - NEW
- **FILE-P9-007**: `frontend/src/components/plots/narrative/recognition/SeasonalWarming.tsx` - NEW
- **FILE-P9-008**: `frontend/src/components/plots/narrative/understanding/MonthlyDistribution.tsx` - NEW
- **FILE-P9-009**: `frontend/src/components/plots/narrative/understanding/ExtremesInverted.tsx` - NEW
- **FILE-P9-010**: `frontend/src/components/plots/narrative/response/ComfortCalendar.tsx` - NEW
- **FILE-P9-011**: `frontend/src/components/plots/narrative/response/TropicalNights.tsx` - NEW
- **FILE-P9-012**: `frontend/src/components/plots/narrative/response/VegetationStress.tsx` - NEW
- **FILE-P9-013**: `frontend/src/components/plots/narrative/index.ts` - NEW - Barrel export
- **FILE-P9-014**: `frontend/src/components/common/ExpandableText.tsx` - NEW
- **FILE-P9-015**: `frontend/src/services/NarrativePlotService.ts` - NEW
- **FILE-P9-016**: `frontend/src/store/slices/narrativePlotSlice.ts` - NEW
- **FILE-P9-017**: `frontend/src/types/plotData.ts` - NEW
- **FILE-P9-018**: `frontend/src/hooks/useNarrativePlots.ts` - NEW

### Modified Files
- **FILE-P9-019**: `frontend/src/store/index.ts` - MODIFY - Add narrativePlotSlice

### Test Files
- **FILE-P9-020**: `frontend/src/components/plots/narrative/__tests__/NarrativeSection.test.tsx` - NEW
- **FILE-P9-021**: `frontend/src/components/plots/narrative/__tests__/TemperatureEvolution.test.tsx` - NEW
- **FILE-P9-022**: `frontend/src/components/plots/narrative/__tests__/ComfortCalendar.test.tsx` - NEW
- **FILE-P9-023**: `frontend/src/components/plots/narrative/__tests__/TropicalNights.test.tsx` - NEW
- **FILE-P9-024**: `frontend/src/components/plots/narrative/__tests__/VegetationStress.test.tsx` - NEW
- **FILE-P9-025**: `frontend/src/components/common/__tests__/ExpandableText.test.tsx` - NEW
- **FILE-P9-026**: `frontend/src/services/__tests__/NarrativePlotService.test.ts` - NEW
- **FILE-P9-027**: `frontend/src/store/slices/__tests__/narrativePlotSlice.test.ts` - NEW

## 6. Testing

### Unit Tests
- **TEST-P9-001**: TabNavigation renders 3 tabs with correct labels
- **TEST-P9-002**: Tab click changes active tab state
- **TEST-P9-003**: ExpandableText toggles correctly on click
- **TEST-P9-004**: NarrativePlotService fetches and parses CSV correctly
- **TEST-P9-005**: Each plot component (7 total) renders without errors with mock data
- **TEST-P9-006**: narrativePlotSlice caches data by location

### Integration Tests
- **TEST-P9-007**: NarrativeSection switches between tabs correctly
- **TEST-P9-008**: City selection triggers plot data refresh
- **TEST-P9-009**: Loading states display during fetch
- **TEST-P9-010**: Mobile accordion variant functions correctly
- **TEST-P9-011**: Response tab renders all 3 plots

### Mock Data Requirements
- **MOCK-P9-001**: Mock temperature evolution CSV (years, temperatures)
- **MOCK-P9-002**: Mock seasonal warming CSV (years, seasons, anomalies)
- **MOCK-P9-003**: Mock monthly distribution CSV (months, percentiles)
- **MOCK-P9-004**: Mock extremes CSV (years, hot days, cold days)
- **MOCK-P9-005**: Mock comfort calendar CSV (decades, months, comfortable days)
- **MOCK-P9-006**: Mock tropical nights CSV (years, tropical nights, heat stress days)
- **MOCK-P9-007**: Mock vegetation stress CSV (years, hot dry days, extreme heat, late frost)

### E2E Tests
- **TEST-P9-012**: User can navigate all 3 narrative tabs
- **TEST-P9-013**: Plot updates when different city selected
- **TEST-P9-014**: ExpandableText reveals methodology on click
- **TEST-P9-015**: Response tab displays all 3 plots with data

## 7. Risks & Assumptions

### Risks
- **RISK-P9-001**: Observable Plot renders differently across browsers
  - **Mitigation**: Test on Chrome, Firefox, Safari; use validated examples

- **RISK-P9-002**: Large number of data points causes slow rendering
  - **Mitigation**: Aggregate data to yearly; limit to ~100 points

- **RISK-P9-003**: Tab transitions cause layout shift
  - **Mitigation**: Set fixed minimum height for plot container

- **RISK-P9-004**: LOWESS calculation is computationally expensive
  - **Mitigation**: Pre-calculate trend line in data pipeline; fallback to rolling average

### Assumptions
- **ASSUMPTION-P9-001**: Observable Plot works with React 19 without issues
- **ASSUMPTION-P9-002**: Yearly aggregated data fits well in box plots
- **ASSUMPTION-P9-003**: 7 plots (2+2+3) is sufficient for narrative (expandable later)
- **ASSUMPTION-P9-004**: Decadal aggregation for Comfort Calendar heatmap is meaningful

## 8. Multi-Agent Execution Notes

### Execution Order
**Parallel tasks (can run simultaneously):**
- Phase 9.1 (Tab Navigation) - no dependencies
- Phase 9.2 (ExpandableText) - no dependencies
- Phase 9.3 (Data Types & Service) - no dependencies

**Sequential dependencies:**
- Phase 9.4 (Slice) depends on Phase 9.3 (Service)
- Phase 9.5-9.8 (Recognition & Understanding Plots) depend on Phase 9.4 (Slice)
- Phase 9.9-9.11 (Response Plots) depend on Phase 9.4 (Slice)
- Phase 9.12 (Tab Integration) depends on Phase 9.1 and Phases 9.5-9.11
- Phase 9.13 (Hook & Polish) requires all previous phases

### Agent Context Requirements
Provide these files for agent execution:
- This plan document
- `frontend/src/components/plots/iceAndHotDays/` - reference plot structure
- `frontend/src/components/common/PlotView/PlotView.tsx` - layout pattern
- `frontend/src/styles/design-system.ts` - styling tokens
- Observable Plot documentation link

### Validation Checkpoints
- **After Phase 9.1**: Tabs render and switch correctly
- **After Phase 9.2**: ExpandableText animates correctly
- **After Phase 9.4**: Slice tests pass; data flows through Redux
- **After Phase 9.5-9.8**: Recognition and Understanding plots render with mock data
- **After Phase 9.9-9.11**: Response plots render with mock data
- **After Phase 9.13**: Full integration working with city selection

## 9. Related Specifications / Further Reading

- [Observable Plot Documentation](https://observablehq.com/plot/)
- [Observable Plot Examples](https://observablehq.com/@observablehq/plot-gallery)
- [Master Plan - Narrative Section](../botox/era5-germany-climate-visualization-1.md#implementation-phase-8)
- [Existing iceAndHotDays Plot](../../frontend/src/components/plots/iceAndHotDays/)

## 10. Code Reference (REQUIRED)

### 10.1 Plot Data Types

**File**: `frontend/src/types/plotData.ts`

```typescript
/**
 * Plot Data Type Definitions
 * 
 * Interfaces for narrative plot data.
 */

/** Temperature evolution data point (yearly) */
export interface TemperatureEvolutionPoint {
    year: number;
    temperature: number;
    anomaly: number;
    trendValue?: number;
}

/** Seasonal warming data for one year */
export interface SeasonalWarmingPoint {
    year: number;
    winter: number;  // DJF anomaly
    spring: number;  // MAM anomaly
    summer: number;  // JJA anomaly
    fall: number;    // SON anomaly
}

/** Monthly distribution statistics */
export interface MonthlyDistributionPoint {
    month: number;  // 1-12
    monthName: string;
    // Current period statistics
    current: {
        min: number;
        q1: number;
        median: number;
        q3: number;
        max: number;
        mean: number;
    };
    // Reference period statistics
    reference: {
        min: number;
        q1: number;
        median: number;
        q3: number;
        max: number;
        mean: number;
    };
}

/** Extremes data for one year */
export interface ExtremesPoint {
    year: number;
    hotDays: number;      // Days ≥ 30°C
    coldDays: number;     // Days ≤ 0°C (ice days)
    referenceHot: number;
    referenceCold: number;
}

/** Combined narrative plot data for a location */
export interface NarrativePlotData {
    locationId: string;
    temperatureEvolution: TemperatureEvolutionPoint[];
    seasonalWarming: SeasonalWarmingPoint[];
    monthlyDistribution: MonthlyDistributionPoint[];
    extremes: ExtremesPoint[];
}

/** Plot loading state */
export type PlotDataStatus = 'idle' | 'loading' | 'succeeded' | 'failed';

/** Keyed plot data state */
export interface NarrativePlotState {
    status: PlotDataStatus;
    error: string | undefined;
    data: Record<string, NarrativePlotData>;
    loadingKeys: string[];
}
```

### 10.2 Narrative Plot Service

**File**: `frontend/src/services/NarrativePlotService.ts`

```typescript
/**
 * Narrative Plot Service
 * 
 * Fetches plot data for narrative visualizations.
 */

import { fetchAndParseCSV, parseOptionalFloat } from './utils/csvUtils';
import { buildUrl } from './utils/serviceUtils';
import type {
    TemperatureEvolutionPoint,
    SeasonalWarmingPoint,
    MonthlyDistributionPoint,
    ExtremesPoint,
    NarrativePlotData,
} from '../types/plotData';

const PLOT_DATA_BASE_PATH = '/data/plots';

const MONTH_NAMES = [
    'Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun',
    'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez'
];

/**
 * Fetch temperature evolution data
 */
export const fetchTemperatureEvolutionData = async (
    locationId: string
): Promise<TemperatureEvolutionPoint[]> => {
    const url = buildUrl(`${PLOT_DATA_BASE_PATH}/temperature_evolution/${locationId}.csv`, false);
    
    return fetchAndParseCSV<TemperatureEvolutionPoint[]>(
        url,
        (rows) => rows.map(([year, temp, anomaly, trend]) => ({
            year: parseInt(year, 10),
            temperature: parseOptionalFloat(temp) ?? 0,
            anomaly: parseOptionalFloat(anomaly) ?? 0,
            trendValue: parseOptionalFloat(trend),
        })),
        {
            validateHeaders: ['year', 'temperature', 'anomaly'],
            errorContext: `temperature evolution for ${locationId}`,
        }
    );
};

/**
 * Fetch seasonal warming data
 */
export const fetchSeasonalWarmingData = async (
    locationId: string
): Promise<SeasonalWarmingPoint[]> => {
    const url = buildUrl(`${PLOT_DATA_BASE_PATH}/seasonal_warming/${locationId}.csv`, false);
    
    return fetchAndParseCSV<SeasonalWarmingPoint[]>(
        url,
        (rows) => rows.map(([year, winter, spring, summer, fall]) => ({
            year: parseInt(year, 10),
            winter: parseOptionalFloat(winter) ?? 0,
            spring: parseOptionalFloat(spring) ?? 0,
            summer: parseOptionalFloat(summer) ?? 0,
            fall: parseOptionalFloat(fall) ?? 0,
        })),
        {
            validateHeaders: ['year', 'winter', 'spring', 'summer', 'fall'],
            errorContext: `seasonal warming for ${locationId}`,
        }
    );
};

/**
 * Fetch monthly distribution data
 */
export const fetchMonthlyDistributionData = async (
    locationId: string
): Promise<MonthlyDistributionPoint[]> => {
    const url = buildUrl(`${PLOT_DATA_BASE_PATH}/monthly_distribution/${locationId}.csv`, false);
    
    return fetchAndParseCSV<MonthlyDistributionPoint[]>(
        url,
        (rows) => rows.map((cols) => {
            const month = parseInt(cols[0], 10);
            return {
                month,
                monthName: MONTH_NAMES[month - 1],
                current: {
                    min: parseOptionalFloat(cols[1]) ?? 0,
                    q1: parseOptionalFloat(cols[2]) ?? 0,
                    median: parseOptionalFloat(cols[3]) ?? 0,
                    q3: parseOptionalFloat(cols[4]) ?? 0,
                    max: parseOptionalFloat(cols[5]) ?? 0,
                    mean: parseOptionalFloat(cols[6]) ?? 0,
                },
                reference: {
                    min: parseOptionalFloat(cols[7]) ?? 0,
                    q1: parseOptionalFloat(cols[8]) ?? 0,
                    median: parseOptionalFloat(cols[9]) ?? 0,
                    q3: parseOptionalFloat(cols[10]) ?? 0,
                    max: parseOptionalFloat(cols[11]) ?? 0,
                    mean: parseOptionalFloat(cols[12]) ?? 0,
                },
            };
        }),
        {
            validateHeaders: ['month'],
            errorContext: `monthly distribution for ${locationId}`,
        }
    );
};

/**
 * Fetch extremes data
 */
export const fetchExtremesData = async (
    locationId: string
): Promise<ExtremesPoint[]> => {
    const url = buildUrl(`${PLOT_DATA_BASE_PATH}/extremes/${locationId}.csv`, false);
    
    return fetchAndParseCSV<ExtremesPoint[]>(
        url,
        (rows) => rows.map(([year, hot, cold, refHot, refCold]) => ({
            year: parseInt(year, 10),
            hotDays: parseOptionalFloat(hot) ?? 0,
            coldDays: parseOptionalFloat(cold) ?? 0,
            referenceHot: parseOptionalFloat(refHot) ?? 0,
            referenceCold: parseOptionalFloat(refCold) ?? 0,
        })),
        {
            validateHeaders: ['year', 'hot_days', 'cold_days'],
            errorContext: `extremes for ${locationId}`,
        }
    );
};

/**
 * Fetch all narrative plot data for a location
 */
export const fetchAllNarrativePlotData = async (
    locationId: string
): Promise<NarrativePlotData> => {
    const [temperatureEvolution, seasonalWarming, monthlyDistribution, extremes] = 
        await Promise.all([
            fetchTemperatureEvolutionData(locationId),
            fetchSeasonalWarmingData(locationId),
            fetchMonthlyDistributionData(locationId),
            fetchExtremesData(locationId),
        ]);

    return {
        locationId,
        temperatureEvolution,
        seasonalWarming,
        monthlyDistribution,
        extremes,
    };
};
```

### 10.3 Tab Navigation Component

**File**: `frontend/src/components/plots/narrative/TabNavigation.tsx`

```typescript
/**
 * TabNavigation Component
 * 
 * Horizontal tab bar for switching between narrative sections.
 */

import { memo, useMemo, useCallback } from 'react';
import type { CSSProperties } from 'react';
import { theme } from '../../../styles/design-system';

export type NarrativeTab = 'recognition' | 'understanding' | 'response';

interface TabConfig {
    id: NarrativeTab;
    label: string;
    labelDE: string;
}

const TABS: TabConfig[] = [
    { id: 'recognition', label: 'Recognition', labelDE: 'Erkennen' },
    { id: 'understanding', label: 'Understanding', labelDE: 'Verstehen' },
    { id: 'response', label: 'Response', labelDE: 'Handeln' },
];

const getContainerStyle = (): CSSProperties => ({
    display: 'flex',
    gap: 0,
    borderBottom: `2px solid ${theme.colors.border}`,
    marginBottom: theme.spacing.lg,
});

const getTabStyle = (isActive: boolean): CSSProperties => ({
    padding: `${theme.spacing.sm}px ${theme.spacing.lg}px`,
    border: 'none',
    background: 'none',
    fontSize: theme.typography.fontSize.md,
    fontWeight: isActive ? theme.typography.fontWeight.bold : theme.typography.fontWeight.normal,
    color: isActive ? theme.colors.primary : theme.colors.textDark,
    cursor: 'pointer',
    position: 'relative',
    transition: 'color 0.2s ease',
});

const getIndicatorStyle = (isActive: boolean): CSSProperties => ({
    position: 'absolute',
    bottom: -2,
    left: 0,
    right: 0,
    height: 3,
    backgroundColor: isActive ? theme.colors.primary : 'transparent',
    transition: 'background-color 0.2s ease',
});

interface TabNavigationProps {
    activeTab: NarrativeTab;
    onTabChange: (tab: NarrativeTab) => void;
    useGermanLabels?: boolean;
}

const TabNavigation = memo(({ 
    activeTab, 
    onTabChange,
    useGermanLabels = true 
}: TabNavigationProps) => {
    const containerStyle = useMemo(() => getContainerStyle(), []);

    return (
        <nav style={containerStyle} role="tablist" aria-label="Narrative sections">
            {TABS.map(tab => (
                <button
                    key={tab.id}
                    role="tab"
                    aria-selected={activeTab === tab.id}
                    aria-controls={`panel-${tab.id}`}
                    style={getTabStyle(activeTab === tab.id)}
                    onClick={() => onTabChange(tab.id)}
                    type="button"
                >
                    {useGermanLabels ? tab.labelDE : tab.label}
                    <span style={getIndicatorStyle(activeTab === tab.id)} />
                </button>
            ))}
        </nav>
    );
});

TabNavigation.displayName = 'TabNavigation';

export default TabNavigation;
export { TABS };
```

### 10.4 NarrativeSection Container

**File**: `frontend/src/components/plots/narrative/NarrativeSection.tsx`

```typescript
/**
 * NarrativeSection Component
 * 
 * Container for tabbed narrative visualizations.
 */

import { useState, useCallback, useMemo, memo, Suspense, lazy } from 'react';
import type { CSSProperties } from 'react';
import TabNavigation, { type NarrativeTab } from './TabNavigation';
import { theme } from '../../../styles/design-system';
import { useBreakpointDown } from '../../../hooks/useBreakpoint';

// Lazy load tab content for code splitting
const RecognitionTab = lazy(() => import('./tabs/RecognitionTab'));
const UnderstandingTab = lazy(() => import('./tabs/UnderstandingTab'));
const ResponseTab = lazy(() => import('./tabs/ResponseTab'));

const getContainerStyle = (): CSSProperties => ({
    padding: theme.spacing.lg,
    backgroundColor: theme.colors.backgroundLight,
    borderRadius: theme.borderRadius?.md ?? '8px',
});

const getPanelStyle = (isVisible: boolean): CSSProperties => ({
    display: isVisible ? 'block' : 'none',
    animation: isVisible ? 'fadeIn 0.3s ease' : undefined,
});

const LoadingFallback = () => (
    <div style={{ 
        padding: theme.spacing.xl, 
        textAlign: 'center',
        color: theme.colors.textLight 
    }}>
        Lädt...
    </div>
);

interface NarrativeSectionProps {
    locationId: string;
    className?: string;
}

const NarrativeSection = memo(({ locationId, className }: NarrativeSectionProps) => {
    const [activeTab, setActiveTab] = useState<NarrativeTab>('recognition');
    const isMobile = useBreakpointDown('mobile');

    const handleTabChange = useCallback((tab: NarrativeTab) => {
        setActiveTab(tab);
    }, []);

    const containerStyle = useMemo(() => getContainerStyle(), []);

    // On mobile, could render as accordion instead
    // For now, tabs still work but could be enhanced

    return (
        <section style={containerStyle} className={className}>
            <TabNavigation 
                activeTab={activeTab} 
                onTabChange={handleTabChange} 
            />

            <Suspense fallback={<LoadingFallback />}>
                <div
                    role="tabpanel"
                    id="panel-recognition"
                    aria-labelledby="tab-recognition"
                    style={getPanelStyle(activeTab === 'recognition')}
                >
                    {activeTab === 'recognition' && (
                        <RecognitionTab locationId={locationId} />
                    )}
                </div>

                <div
                    role="tabpanel"
                    id="panel-understanding"
                    aria-labelledby="tab-understanding"
                    style={getPanelStyle(activeTab === 'understanding')}
                >
                    {activeTab === 'understanding' && (
                        <UnderstandingTab locationId={locationId} />
                    )}
                </div>

                <div
                    role="tabpanel"
                    id="panel-response"
                    aria-labelledby="tab-response"
                    style={getPanelStyle(activeTab === 'response')}
                >
                    {activeTab === 'response' && (
                        <ResponseTab locationId={locationId} />
                    )}
                </div>
            </Suspense>
        </section>
    );
});

NarrativeSection.displayName = 'NarrativeSection';

export default NarrativeSection;
```

### 10.5 ExpandableText Component

**File**: `frontend/src/components/common/ExpandableText.tsx`

```typescript
/**
 * ExpandableText Component
 * 
 * Shows truncated text with "Read more" toggle.
 */

import { useState, useCallback, useMemo, memo, useRef, useEffect } from 'react';
import type { CSSProperties } from 'react';
import { theme } from '../../styles/design-system';

const getContainerStyle = (maxHeight: number | null, isExpanded: boolean): CSSProperties => ({
    overflow: 'hidden',
    maxHeight: isExpanded ? '1000px' : (maxHeight ? `${maxHeight}px` : undefined),
    transition: 'max-height 0.3s ease-out',
});

const getTextStyle = (): CSSProperties => ({
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.textDark,
    lineHeight: theme.typography.lineHeight?.relaxed ?? 1.6,
    marginBottom: theme.spacing.sm,
});

const getToggleStyle = (): CSSProperties => ({
    background: 'none',
    border: 'none',
    padding: 0,
    color: theme.colors.primary,
    fontSize: theme.typography.fontSize.sm,
    cursor: 'pointer',
    textDecoration: 'underline',
});

interface ExpandableTextProps {
    text: string;
    collapsedLines?: number;
    showMoreLabel?: string;
    showLessLabel?: string;
}

const ExpandableText = memo(({
    text,
    collapsedLines = 3,
    showMoreLabel = 'Mehr anzeigen',
    showLessLabel = 'Weniger anzeigen',
}: ExpandableTextProps) => {
    const [isExpanded, setIsExpanded] = useState(false);
    const [needsTruncation, setNeedsTruncation] = useState(false);
    const textRef = useRef<HTMLParagraphElement>(null);
    const lineHeight = 24; // Approximate line height in px
    const maxHeight = collapsedLines * lineHeight;

    // Check if text exceeds max height
    useEffect(() => {
        if (textRef.current) {
            setNeedsTruncation(textRef.current.scrollHeight > maxHeight);
        }
    }, [text, maxHeight]);

    const handleToggle = useCallback(() => {
        setIsExpanded(prev => !prev);
    }, []);

    const containerStyle = useMemo(
        () => getContainerStyle(needsTruncation ? maxHeight : null, isExpanded),
        [needsTruncation, maxHeight, isExpanded]
    );

    return (
        <div>
            <div style={containerStyle}>
                <p ref={textRef} style={getTextStyle()}>
                    {text}
                </p>
            </div>
            {needsTruncation && (
                <button
                    type="button"
                    style={getToggleStyle()}
                    onClick={handleToggle}
                    aria-expanded={isExpanded}
                >
                    {isExpanded ? showLessLabel : showMoreLabel}
                </button>
            )}
        </div>
    );
});

ExpandableText.displayName = 'ExpandableText';

export default ExpandableText;
```

### 10.6 Temperature Evolution Plot

**File**: `frontend/src/components/plots/narrative/recognition/TemperatureEvolution.tsx`

```typescript
/**
 * TemperatureEvolution Plot
 * 
 * Scatter plot showing yearly temperatures with trend line.
 */

import { useEffect, useRef, useMemo, memo } from 'react';
import type { CSSProperties } from 'react';
import * as Plot from '@observablehq/plot';
import { useAppSelector } from '../../../../store/hooks/useAppSelector';
import { selectTemperatureEvolution, selectNarrativePlotStatus } from '../../../../store/slices/narrativePlotSlice';
import ExpandableText from '../../../common/ExpandableText';
import { theme } from '../../../../styles/design-system';

const getContainerStyle = (): CSSProperties => ({
    marginBottom: theme.spacing.lg,
});

const getPlotContainerStyle = (): CSSProperties => ({
    width: '100%',
    display: 'flex',
    justifyContent: 'center',
});

const METHODOLOGY = `
Die Temperaturentwicklung zeigt die jährlichen Durchschnittstemperaturen seit Beginn der Aufzeichnungen. 
Jeder Punkt repräsentiert ein Jahr, farbcodiert nach der Abweichung vom langjährigen Mittel 
(1961-1990). Die Trendlinie basiert auf einem gleitenden 10-Jahres-Durchschnitt.
`;

interface TemperatureEvolutionProps {
    locationId: string;
    width?: number;
    height?: number;
}

const TemperatureEvolution = memo(({
    locationId,
    width = 600,
    height = 400,
}: TemperatureEvolutionProps) => {
    const plotRef = useRef<HTMLDivElement>(null);
    const data = useAppSelector(selectTemperatureEvolution(locationId));
    const status = useAppSelector(selectNarrativePlotStatus);

    const isLoading = status === 'loading';
    const hasData = data && data.length > 0;

    // Generate plot
    useEffect(() => {
        if (!plotRef.current || !hasData) return;

        // Clear previous plot
        plotRef.current.innerHTML = '';

        const plot = Plot.plot({
            width,
            height,
            marginLeft: 50,
            marginBottom: 40,
            style: {
                background: 'transparent',
                fontSize: '12px',
            },
            x: {
                label: 'Jahr',
                tickFormat: d => String(d),
            },
            y: {
                label: 'Temperatur (°C)',
                grid: true,
            },
            color: {
                type: 'diverging',
                scheme: 'RdBu',
                reverse: true,
                domain: [-2, 2],
                label: 'Anomalie (°C)',
            },
            marks: [
                // Scatter points colored by anomaly
                Plot.dot(data, {
                    x: 'year',
                    y: 'temperature',
                    fill: 'anomaly',
                    r: 5,
                    tip: true,
                    title: d => `${d.year}: ${d.temperature.toFixed(1)}°C (${d.anomaly >= 0 ? '+' : ''}${d.anomaly.toFixed(1)}°C)`,
                }),
                // Trend line (if available)
                ...(data.some(d => d.trendValue !== undefined) ? [
                    Plot.line(data.filter(d => d.trendValue !== undefined), {
                        x: 'year',
                        y: 'trendValue',
                        stroke: theme.colors.textDark,
                        strokeWidth: 2,
                        strokeDasharray: '4,4',
                    }),
                ] : []),
                // Reference line at 0 anomaly (if shown)
                Plot.ruleY([0], { stroke: theme.colors.neutral, strokeDasharray: '2,2' }),
            ],
        });

        plotRef.current.appendChild(plot);

        return () => {
            plot.remove();
        };
    }, [data, hasData, width, height]);

    if (isLoading) {
        return (
            <div style={getContainerStyle()}>
                <div style={{ textAlign: 'center', padding: theme.spacing.xl }}>
                    Lädt Temperaturdaten...
                </div>
            </div>
        );
    }

    if (!hasData) {
        return (
            <div style={getContainerStyle()}>
                <div style={{ textAlign: 'center', padding: theme.spacing.xl }}>
                    Keine Daten verfügbar
                </div>
            </div>
        );
    }

    return (
        <div style={getContainerStyle()}>
            <h3 style={{ marginBottom: theme.spacing.md }}>Temperaturentwicklung</h3>
            <div ref={plotRef} style={getPlotContainerStyle()} />
            <ExpandableText text={METHODOLOGY} collapsedLines={2} />
        </div>
    );
});

TemperatureEvolution.displayName = 'TemperatureEvolution';

export default TemperatureEvolution;
```

### 10.7 Seasonal Warming Plot

**File**: `frontend/src/components/plots/narrative/recognition/SeasonalWarming.tsx`

```typescript
/**
 * SeasonalWarming Plot
 * 
 * Multi-line chart showing seasonal anomalies over time.
 */

import { useEffect, useRef, memo } from 'react';
import type { CSSProperties } from 'react';
import * as Plot from '@observablehq/plot';
import { useAppSelector } from '../../../../store/hooks/useAppSelector';
import { selectSeasonalWarming, selectNarrativePlotStatus } from '../../../../store/slices/narrativePlotSlice';
import ExpandableText from '../../../common/ExpandableText';
import { theme } from '../../../../styles/design-system';

const SEASON_COLORS = {
    winter: '#4575b4',  // Blue
    spring: '#91cf60',  // Green
    summer: '#d73027',  // Red
    fall: '#fc8d59',    // Orange
};

const SEASON_LABELS = {
    winter: 'Winter (DJF)',
    spring: 'Frühling (MAM)',
    summer: 'Sommer (JJA)',
    fall: 'Herbst (SON)',
};

const METHODOLOGY = `
Die saisonale Erwärmung zeigt, wie sich die Temperaturen in den vier Jahreszeiten 
im Vergleich zum Referenzzeitraum (1961-1990) entwickelt haben. 
Winter: Dezember-Februar, Frühling: März-Mai, Sommer: Juni-August, Herbst: September-November.
`;

interface SeasonalWarmingProps {
    locationId: string;
    width?: number;
    height?: number;
}

const SeasonalWarming = memo(({
    locationId,
    width = 600,
    height = 400,
}: SeasonalWarmingProps) => {
    const plotRef = useRef<HTMLDivElement>(null);
    const rawData = useAppSelector(selectSeasonalWarming(locationId));
    const status = useAppSelector(selectNarrativePlotStatus);

    const isLoading = status === 'loading';
    const hasData = rawData && rawData.length > 0;

    useEffect(() => {
        if (!plotRef.current || !hasData) return;

        plotRef.current.innerHTML = '';

        // Transform data for multi-line chart
        const lineData = rawData.flatMap(d => [
            { year: d.year, season: 'winter', anomaly: d.winter },
            { year: d.year, season: 'spring', anomaly: d.spring },
            { year: d.year, season: 'summer', anomaly: d.summer },
            { year: d.year, season: 'fall', anomaly: d.fall },
        ]);

        const plot = Plot.plot({
            width,
            height,
            marginLeft: 50,
            marginRight: 100, // Space for legend
            marginBottom: 40,
            style: {
                background: 'transparent',
                fontSize: '12px',
            },
            x: {
                label: 'Jahr',
                tickFormat: d => String(d),
            },
            y: {
                label: 'Anomalie (°C)',
                grid: true,
            },
            color: {
                domain: ['winter', 'spring', 'summer', 'fall'],
                range: [SEASON_COLORS.winter, SEASON_COLORS.spring, SEASON_COLORS.summer, SEASON_COLORS.fall],
            },
            marks: [
                // Reference line at 0
                Plot.ruleY([0], { stroke: theme.colors.neutral, strokeDasharray: '2,2' }),
                // Season lines
                Plot.lineY(lineData, {
                    x: 'year',
                    y: 'anomaly',
                    stroke: 'season',
                    strokeWidth: 2,
                    tip: true,
                }),
                // Legend
                Plot.text(
                    Object.entries(SEASON_LABELS).map(([key, label], i) => ({
                        label,
                        season: key,
                        x: rawData[rawData.length - 1]?.year ?? 2025,
                        y: rawData[rawData.length - 1]?.[key as keyof typeof rawData[0]] ?? 0,
                    })),
                    {
                        x: 'x',
                        y: 'y',
                        text: 'label',
                        fill: 'season',
                        dx: 5,
                        dy: 0,
                        textAnchor: 'start',
                        fontSize: 10,
                    }
                ),
            ],
        });

        plotRef.current.appendChild(plot);

        return () => {
            plot.remove();
        };
    }, [rawData, hasData, width, height]);

    if (isLoading) {
        return <div style={{ textAlign: 'center', padding: theme.spacing.xl }}>Lädt...</div>;
    }

    if (!hasData) {
        return <div style={{ textAlign: 'center', padding: theme.spacing.xl }}>Keine Daten</div>;
    }

    return (
        <div style={{ marginBottom: theme.spacing.lg }}>
            <h3 style={{ marginBottom: theme.spacing.md }}>Saisonale Erwärmung</h3>
            <div ref={plotRef} style={{ width: '100%', display: 'flex', justifyContent: 'center' }} />
            <ExpandableText text={METHODOLOGY} collapsedLines={2} />
        </div>
    );
});

SeasonalWarming.displayName = 'SeasonalWarming';

export default SeasonalWarming;
```

### 10.8 Recognition Tab

**File**: `frontend/src/components/plots/narrative/tabs/RecognitionTab.tsx`

```typescript
/**
 * RecognitionTab Component
 * 
 * Contains plots that help recognize the warming trend.
 */

import { memo } from 'react';
import type { CSSProperties } from 'react';
import TemperatureEvolution from '../recognition/TemperatureEvolution';
import SeasonalWarming from '../recognition/SeasonalWarming';
import { theme } from '../../../../styles/design-system';

const getContainerStyle = (): CSSProperties => ({
    display: 'flex',
    flexDirection: 'column',
    gap: theme.spacing.xl,
});

interface RecognitionTabProps {
    locationId: string;
}

const RecognitionTab = memo(({ locationId }: RecognitionTabProps) => {
    return (
        <div style={getContainerStyle()}>
            <TemperatureEvolution locationId={locationId} />
            <SeasonalWarming locationId={locationId} />
        </div>
    );
});

RecognitionTab.displayName = 'RecognitionTab';

export default RecognitionTab;
```

### 10.9 useNarrativePlots Hook

**File**: `frontend/src/hooks/useNarrativePlots.ts`

```typescript
/**
 * useNarrativePlots Hook
 * 
 * Manages narrative plot data fetching and state.
 */

import { useEffect, useMemo } from 'react';
import { useAppDispatch } from '../store/hooks/useAppDispatch';
import { useAppSelector } from '../store/hooks/useAppSelector';
import {
    fetchNarrativePlotData,
    selectNarrativePlotData,
    selectNarrativePlotStatus,
    selectNarrativePlotError,
} from '../store/slices/narrativePlotSlice';
import type { NarrativePlotData } from '../types/plotData';

export interface UseNarrativePlotsOptions {
    locationId: string;
    autoFetch?: boolean;
}

export interface UseNarrativePlotsReturn {
    data: NarrativePlotData | undefined;
    isLoading: boolean;
    isReady: boolean;
    error: string | undefined;
    refetch: () => void;
}

export function useNarrativePlots({
    locationId,
    autoFetch = true,
}: UseNarrativePlotsOptions): UseNarrativePlotsReturn {
    const dispatch = useAppDispatch();
    const allData = useAppSelector(selectNarrativePlotData);
    const status = useAppSelector(selectNarrativePlotStatus);
    const error = useAppSelector(selectNarrativePlotError);

    const data = useMemo(() => allData?.[locationId], [allData, locationId]);
    const isLoading = status === 'loading';
    const isReady = status === 'succeeded' && data !== undefined;

    // Auto-fetch on location change
    useEffect(() => {
        if (autoFetch && locationId) {
            dispatch(fetchNarrativePlotData({ locationId }));
        }
    }, [dispatch, locationId, autoFetch]);

    const refetch = () => {
        if (locationId) {
            dispatch(fetchNarrativePlotData({ locationId }));
        }
    };

    return {
        data,
        isLoading,
        isReady,
        error,
        refetch,
    };
}

/**
 * Hook to get narrative plots for currently selected city
 */
export function useSelectedCityNarrativePlots(): UseNarrativePlotsReturn {
    const selectedCityId = useAppSelector(state => state.selectedCity.cityId);
    const locationId = selectedCityId ?? 'national';

    return useNarrativePlots({ locationId });
}
```

### 10.10 Mock Data for Testing

**File**: `frontend/src/__mocks__/narrativePlotMocks.ts`

```typescript
/**
 * Mock data for narrative plot testing
 */

import type {
    TemperatureEvolutionPoint,
    SeasonalWarmingPoint,
    MonthlyDistributionPoint,
    ExtremesPoint,
    NarrativePlotData,
} from '../types/plotData';

export const mockTemperatureEvolution: TemperatureEvolutionPoint[] = [
    { year: 2016, temperature: 9.5, anomaly: 0.8, trendValue: 9.3 },
    { year: 2017, temperature: 9.6, anomaly: 0.9, trendValue: 9.4 },
    { year: 2018, temperature: 10.4, anomaly: 1.7, trendValue: 9.5 },
    { year: 2019, temperature: 10.2, anomaly: 1.5, trendValue: 9.6 },
    { year: 2020, temperature: 10.3, anomaly: 1.6, trendValue: 9.8 },
    { year: 2021, temperature: 9.2, anomaly: 0.5, trendValue: 9.9 },
    { year: 2022, temperature: 10.5, anomaly: 1.8, trendValue: 10.0 },
    { year: 2023, temperature: 10.7, anomaly: 2.0, trendValue: 10.1 },
    { year: 2024, temperature: 11.0, anomaly: 2.3, trendValue: 10.3 },
    { year: 2025, temperature: 10.8, anomaly: 2.1, trendValue: 10.4 },
];

export const mockSeasonalWarming: SeasonalWarmingPoint[] = [
    { year: 2016, winter: 1.2, spring: 0.8, summer: 0.9, fall: 0.5 },
    { year: 2017, winter: 1.0, spring: 1.1, summer: 1.0, fall: 0.7 },
    { year: 2018, winter: 1.5, spring: 1.2, summer: 2.1, fall: 1.8 },
    { year: 2019, winter: 1.8, spring: 1.4, summer: 1.5, fall: 1.0 },
    { year: 2020, winter: 2.5, spring: 1.6, summer: 1.4, fall: 1.2 },
    { year: 2021, winter: 0.8, spring: 0.3, summer: 0.6, fall: 0.9 },
    { year: 2022, winter: 1.6, spring: 1.3, summer: 2.3, fall: 1.5 },
    { year: 2023, winter: 2.2, spring: 1.5, summer: 2.0, fall: 1.8 },
    { year: 2024, winter: 2.8, spring: 1.8, summer: 2.5, fall: 2.0 },
    { year: 2025, winter: 2.0, spring: 1.6, summer: 2.2, fall: 1.9 },
];

export const mockMonthlyDistribution: MonthlyDistributionPoint[] = Array.from({ length: 12 }, (_, i) => ({
    month: i + 1,
    monthName: ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez'][i],
    current: {
        min: -5 + i * 2,
        q1: 0 + i * 2,
        median: 5 + i * 2,
        q3: 10 + i * 2,
        max: 15 + i * 2,
        mean: 5.5 + i * 2,
    },
    reference: {
        min: -6 + i * 2,
        q1: -1 + i * 2,
        median: 4 + i * 2,
        q3: 9 + i * 2,
        max: 14 + i * 2,
        mean: 4.5 + i * 2,
    },
}));

export const mockExtremes: ExtremesPoint[] = [
    { year: 2016, hotDays: 12, coldDays: 20, referenceHot: 8, referenceCold: 25 },
    { year: 2017, hotDays: 14, coldDays: 18, referenceHot: 8, referenceCold: 25 },
    { year: 2018, hotDays: 25, coldDays: 12, referenceHot: 8, referenceCold: 25 },
    { year: 2019, hotDays: 22, coldDays: 15, referenceHot: 8, referenceCold: 25 },
    { year: 2020, hotDays: 18, coldDays: 16, referenceHot: 8, referenceCold: 25 },
    { year: 2021, hotDays: 10, coldDays: 22, referenceHot: 8, referenceCold: 25 },
    { year: 2022, hotDays: 28, coldDays: 8, referenceHot: 8, referenceCold: 25 },
    { year: 2023, hotDays: 30, coldDays: 6, referenceHot: 8, referenceCold: 25 },
    { year: 2024, hotDays: 35, coldDays: 5, referenceHot: 8, referenceCold: 25 },
    { year: 2025, hotDays: 32, coldDays: 7, referenceHot: 8, referenceCold: 25 },
];

export const mockNarrativePlotData: NarrativePlotData = {
    locationId: 'berlin',
    temperatureEvolution: mockTemperatureEvolution,
    seasonalWarming: mockSeasonalWarming,
    monthlyDistribution: mockMonthlyDistribution,
    extremes: mockExtremes,
};
```

### 10.11 Test Examples

**File**: `frontend/src/components/plots/narrative/__tests__/NarrativeSection.test.tsx`

```typescript
/**
 * NarrativeSection Tests
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import NarrativeSection from '../NarrativeSection';
import narrativePlotReducer from '../../../../store/slices/narrativePlotSlice';

// Mock the lazy-loaded tab components
vi.mock('../tabs/RecognitionTab', () => ({
    default: ({ locationId }: { locationId: string }) => (
        <div data-testid="recognition-tab">Recognition: {locationId}</div>
    ),
}));

vi.mock('../tabs/UnderstandingTab', () => ({
    default: ({ locationId }: { locationId: string }) => (
        <div data-testid="understanding-tab">Understanding: {locationId}</div>
    ),
}));

vi.mock('../tabs/ResponseTab', () => ({
    default: ({ locationId }: { locationId: string }) => (
        <div data-testid="response-tab">Response: {locationId}</div>
    ),
}));

const createMockStore = () => configureStore({
    reducer: {
        narrativePlot: narrativePlotReducer,
    },
});

describe('NarrativeSection', () => {
    it('renders tab navigation', () => {
        const store = createMockStore();
        
        render(
            <Provider store={store}>
                <NarrativeSection locationId="berlin" />
            </Provider>
        );

        expect(screen.getByRole('tab', { name: /erkennen/i })).toBeInTheDocument();
        expect(screen.getByRole('tab', { name: /verstehen/i })).toBeInTheDocument();
        expect(screen.getByRole('tab', { name: /handeln/i })).toBeInTheDocument();
    });

    it('shows Recognition tab by default', async () => {
        const store = createMockStore();
        
        render(
            <Provider store={store}>
                <NarrativeSection locationId="berlin" />
            </Provider>
        );

        // Wait for lazy load
        const recognitionTab = await screen.findByTestId('recognition-tab');
        expect(recognitionTab).toBeInTheDocument();
    });

    it('switches to Understanding tab on click', async () => {
        const store = createMockStore();
        
        render(
            <Provider store={store}>
                <NarrativeSection locationId="berlin" />
            </Provider>
        );

        const understandingButton = screen.getByRole('tab', { name: /verstehen/i });
        fireEvent.click(understandingButton);

        const understandingTab = await screen.findByTestId('understanding-tab');
        expect(understandingTab).toBeInTheDocument();
    });
});
```

**File**: `frontend/src/components/common/__tests__/ExpandableText.test.tsx`

```typescript
/**
 * ExpandableText Tests
 */

import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import ExpandableText from '../ExpandableText';

const longText = `
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor 
incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud 
exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute 
irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla 
pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia 
deserunt mollit anim id est laborum.
`;

describe('ExpandableText', () => {
    it('renders text content', () => {
        render(<ExpandableText text="Short text" />);
        expect(screen.getByText('Short text')).toBeInTheDocument();
    });

    it('shows "Mehr anzeigen" button for long text', () => {
        render(<ExpandableText text={longText} collapsedLines={2} />);
        // Button may or may not appear depending on scroll height calculation
        // This test verifies rendering doesn't crash
    });

    it('toggles expanded state on button click', () => {
        render(<ExpandableText text={longText} collapsedLines={1} />);
        
        const button = screen.queryByText(/mehr anzeigen/i);
        if (button) {
            fireEvent.click(button);
            expect(screen.getByText(/weniger anzeigen/i)).toBeInTheDocument();
        }
    });

    it('uses custom labels', () => {
        render(
            <ExpandableText 
                text={longText} 
                showMoreLabel="Read more" 
                showLessLabel="Read less" 
            />
        );
        // Custom labels would be used if text is truncated
    });
});
```

### 10.12 Response Plot Data Types

**File**: `frontend/src/types/plotData.ts` (additional interfaces)

```typescript
/** Comfort calendar data point (decadal aggregation) */
export interface ComfortCalendarPoint {
    decade: string;        // e.g., "1960s", "1970s"
    decadeStart: number;   // e.g., 1960
    months: {
        jan: number;
        feb: number;
        mar: number;
        apr: number;
        may: number;
        jun: number;
        jul: number;
        aug: number;
        sep: number;
        oct: number;
        nov: number;
        dec: number;
    };
}

/** Tropical nights data point (yearly) */
export interface TropicalNightsPoint {
    year: number;
    tropicalNights: number;    // Days with Tmin ≥ 20°C
    heatStressDays: number;    // Days with Tmax ≥ 32°C
    heatwaveLength?: number;   // Max consecutive days >32°C
    referenceTropical: number;
    referenceHeatStress: number;
}

/** Vegetation stress data point (yearly) */
export interface VegetationStressPoint {
    year: number;
    hotDryDays: number;        // Tmax ≥30°C AND 7-day precip <0.5mm
    extremeHeatDays: number;   // Tmax ≥35°C
    lateFrostDays: number;     // After Apr 15, Tmin ≤-2°C
}

/** Extended narrative plot data for a location */
export interface NarrativePlotData {
    locationId: string;
    // Recognition
    temperatureEvolution: TemperatureEvolutionPoint[];
    seasonalWarming: SeasonalWarmingPoint[];
    // Understanding
    monthlyDistribution: MonthlyDistributionPoint[];
    extremes: ExtremesPoint[];
    // Response
    comfortCalendar: ComfortCalendarPoint[];
    tropicalNights: TropicalNightsPoint[];
    vegetationStress: VegetationStressPoint[];
}
```

### 10.13 Comfort Calendar Plot

**File**: `frontend/src/components/plots/narrative/response/ComfortCalendar.tsx`

```typescript
/**
 * ComfortCalendar Plot
 * 
 * Heatmap showing comfortable days (15-25°C) by decade and month.
 */

import { useEffect, useRef, memo } from 'react';
import * as Plot from '@observablehq/plot';
import { useAppSelector } from '../../../../store/hooks/useAppSelector';
import { selectComfortCalendar, selectNarrativePlotStatus } from '../../../../store/slices/narrativePlotSlice';
import ExpandableText from '../../../common/ExpandableText';
import { theme } from '../../../../styles/design-system';

const MONTHS = ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez'];

const METHODOLOGY = `
Der Komfortkalender zeigt die durchschnittliche Anzahl behaglicher Tage (15-25°C Tagesmittel) 
pro Monat und Dekade. Dunkleres Grün bedeutet mehr behagliche Tage. Weiß oder Gelb zeigt 
Monate mit wenigen oder keinen behaglichen Tagen - entweder zu kalt (Winter) oder zu heiß (Hochsommer).
`;

interface ComfortCalendarProps {
    locationId: string;
    width?: number;
    height?: number;
}

const ComfortCalendar = memo(({
    locationId,
    width = 600,
    height = 300,
}: ComfortCalendarProps) => {
    const plotRef = useRef<HTMLDivElement>(null);
    const data = useAppSelector(selectComfortCalendar(locationId));
    const status = useAppSelector(selectNarrativePlotStatus);

    const isLoading = status === 'loading';
    const hasData = data && data.length > 0;

    useEffect(() => {
        if (!plotRef.current || !hasData) return;

        plotRef.current.innerHTML = '';

        // Transform data to flat array for heatmap
        const flatData = data.flatMap(row => 
            Object.entries(row.months).map(([month, value], i) => ({
                decade: row.decade,
                month: MONTHS[i],
                monthIndex: i,
                value,
            }))
        );

        const plot = Plot.plot({
            width,
            height,
            marginLeft: 60,
            marginBottom: 40,
            padding: 0.05,
            style: {
                background: 'transparent',
                fontSize: '11px',
            },
            x: {
                label: null,
                domain: MONTHS,
            },
            y: {
                label: null,
            },
            color: {
                type: 'linear',
                scheme: 'Greens',
                domain: [0, 25],
                label: 'Behagliche Tage',
            },
            marks: [
                Plot.cell(flatData, {
                    x: 'month',
                    y: 'decade',
                    fill: 'value',
                    tip: true,
                    title: d => `${d.decade} ${d.month}: ${d.value} Tage`,
                }),
                Plot.text(flatData, {
                    x: 'month',
                    y: 'decade',
                    text: d => String(Math.round(d.value)),
                    fill: d => d.value > 15 ? 'white' : 'black',
                    fontSize: 9,
                }),
            ],
        });

        plotRef.current.appendChild(plot);

        return () => {
            plot.remove();
        };
    }, [data, hasData, width, height]);

    if (isLoading) {
        return <div style={{ textAlign: 'center', padding: theme.spacing.xl }}>Lädt...</div>;
    }

    if (!hasData) {
        return <div style={{ textAlign: 'center', padding: theme.spacing.xl }}>Keine Daten</div>;
    }

    return (
        <div style={{ marginBottom: theme.spacing.lg }}>
            <h3 style={{ marginBottom: theme.spacing.md }}>Komfortkalender</h3>
            <p style={{ fontSize: theme.typography.fontSize.sm, color: theme.colors.textLight, marginBottom: theme.spacing.sm }}>
                Durchschnittliche Anzahl behaglicher Tage (15-25°C) pro Monat
            </p>
            <div ref={plotRef} style={{ width: '100%', display: 'flex', justifyContent: 'center' }} />
            <ExpandableText text={METHODOLOGY} collapsedLines={2} />
        </div>
    );
});

ComfortCalendar.displayName = 'ComfortCalendar';

export default ComfortCalendar;
```

### 10.14 Tropical Nights Plot

**File**: `frontend/src/components/plots/narrative/response/TropicalNights.tsx`

```typescript
/**
 * TropicalNights Plot
 * 
 * Combined bar + line chart showing tropical nights and heat stress days.
 */

import { useEffect, useRef, memo } from 'react';
import * as Plot from '@observablehq/plot';
import { useAppSelector } from '../../../../store/hooks/useAppSelector';
import { selectTropicalNights, selectNarrativePlotStatus } from '../../../../store/slices/narrativePlotSlice';
import ExpandableText from '../../../common/ExpandableText';
import { theme } from '../../../../styles/design-system';

const METHODOLOGY = `
Tropische Nächte sind Nächte, in denen die Temperatur nicht unter 20°C fällt. Diese sind 
besonders belastend für den Schlaf und die Gesundheit. Hitzestress-Tage (Tmax ≥32°C) zeigen 
zusätzlich die Tagesbelastung. Beide Metriken haben in den letzten Jahrzehnten deutlich zugenommen.
`;

interface TropicalNightsProps {
    locationId: string;
    width?: number;
    height?: number;
}

const TropicalNights = memo(({
    locationId,
    width = 600,
    height = 400,
}: TropicalNightsProps) => {
    const plotRef = useRef<HTMLDivElement>(null);
    const data = useAppSelector(selectTropicalNights(locationId));
    const status = useAppSelector(selectNarrativePlotStatus);

    const isLoading = status === 'loading';
    const hasData = data && data.length > 0;

    useEffect(() => {
        if (!plotRef.current || !hasData) return;

        plotRef.current.innerHTML = '';

        const plot = Plot.plot({
            width,
            height,
            marginLeft: 50,
            marginRight: 60,
            marginBottom: 40,
            style: {
                background: 'transparent',
                fontSize: '12px',
            },
            x: {
                label: 'Jahr',
                tickFormat: d => String(d),
            },
            y: {
                label: 'Tropische Nächte',
                grid: true,
            },
            color: {
                type: 'linear',
                scheme: 'YlOrRd',
                domain: [0, 20],
            },
            marks: [
                // Reference line for historical average
                Plot.ruleY(
                    [data[0]?.referenceTropical ?? 2], 
                    { stroke: theme.colors.neutral, strokeDasharray: '4,4', strokeWidth: 1 }
                ),
                // Bars for tropical nights
                Plot.barY(data, {
                    x: 'year',
                    y: 'tropicalNights',
                    fill: 'tropicalNights',
                    tip: true,
                    title: d => `${d.year}: ${d.tropicalNights} tropische Nächte`,
                }),
                // Line for heat stress days (secondary axis simulation)
                Plot.line(data, {
                    x: 'year',
                    y: d => d.heatStressDays * 1.5, // Scale to fit
                    stroke: theme.colors.error,
                    strokeWidth: 2,
                    curve: 'natural',
                }),
                Plot.dot(data, {
                    x: 'year',
                    y: d => d.heatStressDays * 1.5,
                    fill: theme.colors.error,
                    r: 3,
                    tip: true,
                    title: d => `${d.year}: ${d.heatStressDays} Hitzestress-Tage`,
                }),
                // Annotation
                Plot.text(
                    [{ x: data[data.length - 1]?.year, y: data[0]?.referenceTropical }],
                    {
                        x: 'x',
                        y: 'y',
                        text: ['Historisches Mittel'],
                        textAnchor: 'end',
                        dy: -8,
                        fontSize: 10,
                        fill: theme.colors.textLight,
                    }
                ),
            ],
        });

        plotRef.current.appendChild(plot);

        return () => {
            plot.remove();
        };
    }, [data, hasData, width, height]);

    if (isLoading) {
        return <div style={{ textAlign: 'center', padding: theme.spacing.xl }}>Lädt...</div>;
    }

    if (!hasData) {
        return <div style={{ textAlign: 'center', padding: theme.spacing.xl }}>Keine Daten</div>;
    }

    return (
        <div style={{ marginBottom: theme.spacing.lg }}>
            <h3 style={{ marginBottom: theme.spacing.md }}>Schlaflose Nächte</h3>
            <p style={{ fontSize: theme.typography.fontSize.sm, color: theme.colors.textLight, marginBottom: theme.spacing.sm }}>
                Tropische Nächte (Balken) und Hitzestress-Tage (rote Linie)
            </p>
            <div ref={plotRef} style={{ width: '100%', display: 'flex', justifyContent: 'center' }} />
            <ExpandableText text={METHODOLOGY} collapsedLines={2} />
        </div>
    );
});

TropicalNights.displayName = 'TropicalNights';

export default TropicalNights;
```

### 10.15 Vegetation Stress Plot

**File**: `frontend/src/components/plots/narrative/response/VegetationStress.tsx`

```typescript
/**
 * VegetationStress Plot
 * 
 * Stacked area chart showing vegetation stress metrics.
 */

import { useEffect, useRef, memo } from 'react';
import * as Plot from '@observablehq/plot';
import { useAppSelector } from '../../../../store/hooks/useAppSelector';
import { selectVegetationStress, selectNarrativePlotStatus } from '../../../../store/slices/narrativePlotSlice';
import ExpandableText from '../../../common/ExpandableText';
import { theme } from '../../../../styles/design-system';

const STRESS_COLORS = {
    hotDry: '#c9a227',      // Brown/tan for hot & dry
    extremeHeat: '#d73027', // Red for extreme heat
    lateFrost: '#4575b4',   // Blue for late frost
};

const METHODOLOGY = `
Vegetationsstress zeigt drei Belastungsfaktoren für Pflanzen: Heiß-trockene Tage (≥30°C ohne 
Niederschlag in der Vorwoche), extreme Hitzetage (≥35°C) und Spätfröste nach dem 15. April. 
Die Kombination dieser Faktoren macht Wachstumsperioden trotz längerer frostfreier Zeit zunehmend schwieriger.
`;

interface VegetationStressProps {
    locationId: string;
    width?: number;
    height?: number;
}

const VegetationStress = memo(({
    locationId,
    width = 600,
    height = 400,
}: VegetationStressProps) => {
    const plotRef = useRef<HTMLDivElement>(null);
    const data = useAppSelector(selectVegetationStress(locationId));
    const status = useAppSelector(selectNarrativePlotStatus);

    const isLoading = status === 'loading';
    const hasData = data && data.length > 0;

    useEffect(() => {
        if (!plotRef.current || !hasData) return;

        plotRef.current.innerHTML = '';

        // Transform data for stacked area
        const stackData = data.flatMap(d => [
            { year: d.year, type: 'hotDry', value: d.hotDryDays, label: 'Heiß & trocken' },
            { year: d.year, type: 'extremeHeat', value: d.extremeHeatDays, label: 'Extremhitze' },
        ]);

        // Late frost as separate markers (not stacked)
        const frostData = data.filter(d => d.lateFrostDays > 0);

        const plot = Plot.plot({
            width,
            height,
            marginLeft: 50,
            marginRight: 120,
            marginBottom: 40,
            style: {
                background: 'transparent',
                fontSize: '12px',
            },
            x: {
                label: 'Jahr',
                tickFormat: d => String(d),
            },
            y: {
                label: 'Stresstage',
                grid: true,
            },
            color: {
                domain: ['hotDry', 'extremeHeat'],
                range: [STRESS_COLORS.hotDry, STRESS_COLORS.extremeHeat],
            },
            marks: [
                // Stacked area for heat stress types
                Plot.areaY(stackData, Plot.stackY({
                    x: 'year',
                    y: 'value',
                    fill: 'type',
                    curve: 'natural',
                    fillOpacity: 0.7,
                    tip: true,
                    title: d => `${d.year} ${d.label}: ${d.value} Tage`,
                })),
                // Late frost markers
                Plot.dot(frostData, {
                    x: 'year',
                    y: d => -d.lateFrostDays * 2, // Below zero to show as separate
                    fill: STRESS_COLORS.lateFrost,
                    r: d => Math.sqrt(d.lateFrostDays) * 3,
                    tip: true,
                    title: d => `${d.year}: ${d.lateFrostDays} Spätfrost-Tage`,
                }),
                // Legend annotations
                Plot.text(
                    [{ x: data[data.length - 1]?.year, y: 35, label: 'Heiß & trocken', color: STRESS_COLORS.hotDry }],
                    { x: 'x', y: 'y', text: 'label', fill: 'color', dx: 10, textAnchor: 'start', fontSize: 10 }
                ),
                Plot.text(
                    [{ x: data[data.length - 1]?.year, y: 45, label: 'Extremhitze ≥35°C', color: STRESS_COLORS.extremeHeat }],
                    { x: 'x', y: 'y', text: 'label', fill: 'color', dx: 10, textAnchor: 'start', fontSize: 10 }
                ),
                Plot.text(
                    [{ x: data[data.length - 1]?.year, y: -8, label: 'Spätfrost', color: STRESS_COLORS.lateFrost }],
                    { x: 'x', y: 'y', text: 'label', fill: 'color', dx: 10, textAnchor: 'start', fontSize: 10 }
                ),
            ],
        });

        plotRef.current.appendChild(plot);

        return () => {
            plot.remove();
        };
    }, [data, hasData, width, height]);

    if (isLoading) {
        return <div style={{ textAlign: 'center', padding: theme.spacing.xl }}>Lädt...</div>;
    }

    if (!hasData) {
        return <div style={{ textAlign: 'center', padding: theme.spacing.xl }}>Keine Daten</div>;
    }

    return (
        <div style={{ marginBottom: theme.spacing.lg }}>
            <h3 style={{ marginBottom: theme.spacing.md }}>Vegetationsstress</h3>
            <p style={{ fontSize: theme.typography.fontSize.sm, color: theme.colors.textLight, marginBottom: theme.spacing.sm }}>
                Jährliche Stresstage für Pflanzen: Hitze, Trockenheit und Spätfröste
            </p>
            <div ref={plotRef} style={{ width: '100%', display: 'flex', justifyContent: 'center' }} />
            <ExpandableText text={METHODOLOGY} collapsedLines={2} />
        </div>
    );
});

VegetationStress.displayName = 'VegetationStress';

export default VegetationStress;
```

### 10.16 Response Tab

**File**: `frontend/src/components/plots/narrative/tabs/ResponseTab.tsx`

```typescript
/**
 * ResponseTab Component
 * 
 * Contains plots for the Response narrative section.
 * Theme: "Planning for Heat" - Personal impacts and adaptation.
 */

import { memo } from 'react';
import type { CSSProperties } from 'react';
import ComfortCalendar from '../response/ComfortCalendar';
import TropicalNights from '../response/TropicalNights';
import VegetationStress from '../response/VegetationStress';
import { theme } from '../../../../styles/design-system';

const getContainerStyle = (): CSSProperties => ({
    display: 'flex',
    flexDirection: 'column',
    gap: theme.spacing.xl,
});

const getIntroStyle = (): CSSProperties => ({
    fontSize: theme.typography.fontSize.md,
    color: theme.colors.textDark,
    lineHeight: 1.6,
    marginBottom: theme.spacing.lg,
    fontStyle: 'italic',
});

interface ResponseTabProps {
    locationId: string;
}

const ResponseTab = memo(({ locationId }: ResponseTabProps) => {
    return (
        <div style={getContainerStyle()}>
            <p style={getIntroStyle()}>
                Der Klimawandel verändert nicht nur Statistiken – er verändert den Alltag. 
                Wann können Sie draußen sein? Wie gut schlafen Sie im Sommer? 
                Wie entwickelt sich Ihr Garten?
            </p>
            
            <ComfortCalendar locationId={locationId} />
            <TropicalNights locationId={locationId} />
            <VegetationStress locationId={locationId} />
        </div>
    );
});

ResponseTab.displayName = 'ResponseTab';

export default ResponseTab;
```

### 10.17 Mock Data for Response Plots

**File**: `frontend/src/__mocks__/narrativePlotMocks.ts` (additions)

```typescript
export const mockComfortCalendar: ComfortCalendarPoint[] = [
    { decade: '1960er', decadeStart: 1960, months: { jan: 0, feb: 0, mar: 2, apr: 12, may: 20, jun: 18, jul: 15, aug: 16, sep: 18, oct: 10, nov: 2, dec: 0 } },
    { decade: '1970er', decadeStart: 1970, months: { jan: 0, feb: 0, mar: 3, apr: 13, may: 19, jun: 17, jul: 14, aug: 15, sep: 17, oct: 11, nov: 3, dec: 0 } },
    { decade: '1980er', decadeStart: 1980, months: { jan: 0, feb: 0, mar: 4, apr: 14, may: 18, jun: 16, jul: 12, aug: 14, sep: 16, oct: 12, nov: 4, dec: 0 } },
    { decade: '1990er', decadeStart: 1990, months: { jan: 0, feb: 1, mar: 5, apr: 15, may: 17, jun: 14, jul: 10, aug: 12, sep: 15, oct: 13, nov: 5, dec: 0 } },
    { decade: '2000er', decadeStart: 2000, months: { jan: 0, feb: 1, mar: 6, apr: 16, may: 16, jun: 12, jul: 8, aug: 10, sep: 14, oct: 14, nov: 6, dec: 1 } },
    { decade: '2010er', decadeStart: 2010, months: { jan: 0, feb: 2, mar: 7, apr: 17, may: 15, jun: 10, jul: 6, aug: 8, sep: 13, oct: 15, nov: 7, dec: 1 } },
    { decade: '2020er', decadeStart: 2020, months: { jan: 1, feb: 2, mar: 8, apr: 18, may: 14, jun: 8, jul: 4, aug: 6, sep: 12, oct: 16, nov: 8, dec: 2 } },
];

export const mockTropicalNights: TropicalNightsPoint[] = [
    { year: 2016, tropicalNights: 8, heatStressDays: 12, referenceTropical: 2, referenceHeatStress: 5 },
    { year: 2017, tropicalNights: 6, heatStressDays: 10, referenceTropical: 2, referenceHeatStress: 5 },
    { year: 2018, tropicalNights: 15, heatStressDays: 22, referenceTropical: 2, referenceHeatStress: 5 },
    { year: 2019, tropicalNights: 12, heatStressDays: 18, referenceTropical: 2, referenceHeatStress: 5 },
    { year: 2020, tropicalNights: 10, heatStressDays: 15, referenceTropical: 2, referenceHeatStress: 5 },
    { year: 2021, tropicalNights: 5, heatStressDays: 8, referenceTropical: 2, referenceHeatStress: 5 },
    { year: 2022, tropicalNights: 18, heatStressDays: 25, referenceTropical: 2, referenceHeatStress: 5 },
    { year: 2023, tropicalNights: 20, heatStressDays: 28, referenceTropical: 2, referenceHeatStress: 5 },
    { year: 2024, tropicalNights: 22, heatStressDays: 32, referenceTropical: 2, referenceHeatStress: 5 },
    { year: 2025, tropicalNights: 19, heatStressDays: 26, referenceTropical: 2, referenceHeatStress: 5 },
];

export const mockVegetationStress: VegetationStressPoint[] = [
    { year: 2016, hotDryDays: 15, extremeHeatDays: 3, lateFrostDays: 1 },
    { year: 2017, hotDryDays: 12, extremeHeatDays: 2, lateFrostDays: 0 },
    { year: 2018, hotDryDays: 28, extremeHeatDays: 8, lateFrostDays: 2 },
    { year: 2019, hotDryDays: 22, extremeHeatDays: 5, lateFrostDays: 1 },
    { year: 2020, hotDryDays: 18, extremeHeatDays: 4, lateFrostDays: 0 },
    { year: 2021, hotDryDays: 10, extremeHeatDays: 1, lateFrostDays: 3 },
    { year: 2022, hotDryDays: 32, extremeHeatDays: 10, lateFrostDays: 0 },
    { year: 2023, hotDryDays: 35, extremeHeatDays: 12, lateFrostDays: 1 },
    { year: 2024, hotDryDays: 40, extremeHeatDays: 15, lateFrostDays: 0 },
    { year: 2025, hotDryDays: 38, extremeHeatDays: 13, lateFrostDays: 0 },
];

// Update mockNarrativePlotData to include Response data
export const mockNarrativePlotData: NarrativePlotData = {
    locationId: 'berlin',
    temperatureEvolution: mockTemperatureEvolution,
    seasonalWarming: mockSeasonalWarming,
    monthlyDistribution: mockMonthlyDistribution,
    extremes: mockExtremes,
    comfortCalendar: mockComfortCalendar,
    tropicalNights: mockTropicalNights,
    vegetationStress: mockVegetationStress,
};
```
