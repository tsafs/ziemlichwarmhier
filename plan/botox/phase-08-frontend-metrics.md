---
goal: Phase 8 - Frontend Static Metrics Cards with Redux Integration
version: 1.1
date_created: 2026-02-16
last_updated: 2026-02-17
owner: Sebastian
status: 'Planned'
tags: [phase-8, frontend, metrics, cards, redux]
---

# Introduction

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

This phase implements the climate metrics display cards that show key statistics for the selected city or Germany as a whole. The implementation extends the existing `StatCard` component with tilted labels, creates a new `MetricsRow` container for horizontal layout, and builds 6 individual metric card components. All cards integrate with Redux via a new `metricsSlice` built using the `createDataSlice` factory pattern.

**Key deliverables:**
- Extended `StatCard` with `labelTilt` prop for tilted titles
- `MetricsRow` container component with responsive 6-card layout
- 6 metric card components (Five-Year Anomaly, Warming Rate, Record Days, Winter Warming, Snow Days Lost, Comfortable Days)
- `MetricsService` for fetching pre-calculated metrics JSON
- `metricsSlice` using createDataSlice factory for state management
- City-specific metric loading on selection
- Loading/error states and info tooltips

## 1. Requirements & Constraints

### Functional Requirements (from Master Plan)
- **REQ-003**: Display 4-6 static climate metrics (temperature anomaly, warming rate, record days, etc.)
- **REQ-009**: Provide responsive design for mobile and desktop

### Phase-Specific Requirements
- **REQ-P8-001**: Display 6 climate metrics in a horizontal row on desktop
- **REQ-P8-002**: Stack metrics vertically (3×2 grid on tablet, single column on mobile)
- **REQ-P8-003**: Each card must show title, primary value, subtitle, and optional info tooltip
- **REQ-P8-004**: Cards must support tilted labels (5-10° rotation)
- **REQ-P8-005**: Metrics must update when city selection changes
- **REQ-P8-006**: Handle loading and error states gracefully
- **REQ-P8-007**: Show Germany-wide metrics when no city selected

### Technical Constraints
- **CON-P8-001**: Metrics data served as static JSON from Hetzner Object Storage
- **CON-P8-002**: Must use existing createDataSlice factory pattern
- **CON-P8-003**: Must use design-system tokens for all styling

### Patterns to Follow
- **PAT-P8-001**: Use `createDataSlice` factory for Redux state management
- **PAT-P8-002**: Use service layer pattern for metrics fetching
- **PAT-P8-003**: Extend existing StatCard component pattern
- **PAT-P8-004**: Follow existing responsive layout patterns using useBreakpoint

## 2. Implementation Steps

### Implementation Phase 8.1: StatCard Enhancement

- GOAL-P8-001: Extend StatCard component with labelTilt prop

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P8-001 | Add `labelTilt` prop to StatCardProps interface | | |
| TASK-P8-002 | Implement CSS transform rotation for title element | | |
| TASK-P8-003 | Add `valueSize` prop for configurable value font size | | |
| TASK-P8-004 | Add `accentColor` prop for value color customization | | |
| TASK-P8-005 | Update getTitleStyle to include rotation transform | | |
| TASK-P8-006 | Write tests for new StatCard props | | |

**Completion Criteria:**
- StatCard renders with tilted title when `labelTilt` prop provided
- Existing StatCard usages unaffected (default tilt = 0)
- All new props optional with sensible defaults

---

### Implementation Phase 8.2: MetricsRow Container

- GOAL-P8-002: Create responsive container for 6 metric cards

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P8-007 | Create `frontend/src/components/metrics/MetricsRow.tsx` container component | | |
| TASK-P8-008 | Implement flexbox layout with wrap for responsive behavior | | |
| TASK-P8-009 | Configure desktop: 6 cards in row | | |
| TASK-P8-010 | Configure tablet: 3×2 grid (breakpoint < 992px) | | |
| TASK-P8-011 | Configure mobile: single column stack (breakpoint < 576px) | | |
| TASK-P8-012 | Add gap spacing between cards using design tokens | | |
| TASK-P8-013 | Write tests for MetricsRow responsive behavior | | |

**Completion Criteria:**
- 6 cards display in row on desktop (>992px)
- 3×2 grid on tablet (576-992px)
- Single column on mobile (<576px)
- Consistent spacing at all breakpoints

---

### Implementation Phase 8.3: Metrics Type Definitions

- GOAL-P8-003: Define TypeScript interfaces for metrics data

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P8-014 | Create `frontend/src/types/metrics.ts` with metric interfaces | | |
| TASK-P8-015 | Define `FiveYearAnomalyMetric` interface | | |
| TASK-P8-016 | Define `WarmingRateMetric` interface | | |
| TASK-P8-017 | Define `RecordDaysMetric` interface | | |
| TASK-P8-018 | Define `WinterWarmingMetric` interface | | |
| TASK-P8-019 | Define `SnowDaysLostMetric` interface | | |
| TASK-P8-020 | Define `ComfortableDaysMetric` interface | | |
| TASK-P8-021 | Define `LocationMetrics` combined interface | | |

**Completion Criteria:**
- All metric interfaces defined with JSDoc documentation
- Interfaces match JSON schema from Phase 5

---

### Implementation Phase 8.4: Metrics Service

- GOAL-P8-004: Create service for fetching metrics JSON

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P8-022 | Create `frontend/src/services/MetricsService.ts` | | |
| TASK-P8-023 | Implement `fetchMetricsForLocation(locationId)` function | | |
| TASK-P8-024 | Implement `fetchNationalMetrics()` for Germany-wide data | | |
| TASK-P8-025 | Add URL construction using buildUrl utility | | |
| TASK-P8-026 | Implement JSON parsing with validation | | |
| TASK-P8-027 | Add error handling for missing/malformed data | | |
| TASK-P8-028 | Write unit tests for MetricsService | | |

**Completion Criteria:**
- Service fetches and parses metrics JSON correctly
- Handles city-specific and national metrics
- Proper error handling for network/parse failures

---

### Implementation Phase 8.5: Metrics Slice

- GOAL-P8-005: Create Redux slice for metrics state

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P8-029 | Create `frontend/src/store/slices/metricsSlice.ts` using createDataSlice | | |
| TASK-P8-030 | Configure 'keyed' state shape for caching per location | | |
| TASK-P8-031 | Create fetchMetrics async thunk | | |
| TASK-P8-032 | Create selectors for each metric type | | |
| TASK-P8-033 | Create selectMetricsForCurrentCity derived selector | | |
| TASK-P8-034 | Register metricsSlice in store/index.ts | | |
| TASK-P8-035 | Write unit tests for metricsSlice | | |

**Completion Criteria:**
- Metrics cached per location ID
- Selectors return correct metric subsets
- TTL prevents excessive refetching

---

### Implementation Phase 8.6: Individual Metric Cards

- GOAL-P8-006: Implement 6 metric card components

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P8-036 | Create `frontend/src/components/metrics/cards/FiveYearAnomalyCard.tsx` | | |
| TASK-P8-037 | Create `frontend/src/components/metrics/cards/WarmingRateCard.tsx` | | |
| TASK-P8-038 | Create `frontend/src/components/metrics/cards/RecordDaysCard.tsx` | | |
| TASK-P8-039 | Create `frontend/src/components/metrics/cards/WinterWarmingCard.tsx` | | |
| TASK-P8-040 | Create `frontend/src/components/metrics/cards/SnowDaysLostCard.tsx` | | |
| TASK-P8-041 | Create `frontend/src/components/metrics/cards/ComfortableDaysCard.tsx` | | |
| TASK-P8-042 | Add info text tooltips with methodology for each card | | |
| TASK-P8-043 | Implement value formatting (decimals, ± signs, units) | | |
| TASK-P8-044 | Write tests for each card component | | |

**Completion Criteria:**
- All 6 cards render with correct data binding
- Values formatted appropriately (±0.5°C, +1.2°C/decade)
- Info tooltips provide methodology context

---

### Implementation Phase 8.7: Custom Hook & Integration

- GOAL-P8-007: Create useMetrics hook and integrate with city selection

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P8-045 | Create `frontend/src/hooks/useMetrics.ts` hook | | |
| TASK-P8-046 | Auto-fetch metrics on city selection change | | |
| TASK-P8-047 | Return loading/error/data states for all 6 metrics | | |
| TASK-P8-048 | Create barrel export `frontend/src/components/metrics/index.ts` | | |
| TASK-P8-049 | Integrate MetricsRow into main page layout | | |
| TASK-P8-050 | Write E2E tests for metric loading flow | | |

**Completion Criteria:**
- Metrics auto-load when city changes
- Loading state shown during fetch
- Error state handles gracefully
- Full integration tested

## 3. Alternatives

- **ALT-P8-001**: **Separate cards vs. MetricsRow container** - Considered placing cards directly without container. Rejected because responsive behavior is easier to manage centrally.

- **ALT-P8-002**: **CSS Grid vs. Flexbox** - Considered CSS Grid for MetricsRow layout. Chose Flexbox for simpler wrap behavior and consistency with existing PlotView patterns.

- **ALT-P8-003**: **Individual slices per metric vs. combined slice** - Considered separate Redux slices per metric. Rejected due to unnecessary complexity; single slice with structured state is cleaner.

- **ALT-P8-004**: **Fetch all metrics in one request vs. individual** - Chose single combined JSON per location for fewer network requests and simpler caching.

## 4. Dependencies

### External Dependencies
- **DEP-P8-001**: Metrics JSON data from Hetzner Object Storage (Phase 5 output)

### Internal Dependencies
- **DEP-P8-002**: StatCard component (existing, to be extended)
- **DEP-P8-003**: createDataSlice factory (existing)
- **DEP-P8-004**: selectedCitySlice (existing) - for city selection state
- **DEP-P8-005**: Design system tokens (existing)

### Phase Dependencies
- **DEP-P8-006**: Phase 1 (Testing Infrastructure) - Vitest must be configured
- **DEP-P8-007**: Phase 5 (Metrics Calculation) - Metrics JSON must exist
- **DEP-P8-008**: Can develop with mock data before Phase 5 completes

## 5. Files

### New Files
- **FILE-P8-001**: `frontend/src/components/metrics/MetricsRow.tsx` - NEW - Row container
- **FILE-P8-002**: `frontend/src/components/metrics/cards/FiveYearAnomalyCard.tsx` - NEW
- **FILE-P8-003**: `frontend/src/components/metrics/cards/WarmingRateCard.tsx` - NEW
- **FILE-P8-004**: `frontend/src/components/metrics/cards/RecordDaysCard.tsx` - NEW
- **FILE-P8-005**: `frontend/src/components/metrics/cards/WinterWarmingCard.tsx` - NEW
- **FILE-P8-006**: `frontend/src/components/metrics/cards/SnowDaysLostCard.tsx` - NEW
- **FILE-P8-007**: `frontend/src/components/metrics/cards/ComfortableDaysCard.tsx` - NEW
- **FILE-P8-008**: `frontend/src/components/metrics/index.ts` - NEW - Barrel export
- **FILE-P8-009**: `frontend/src/services/MetricsService.ts` - NEW
- **FILE-P8-010**: `frontend/src/store/slices/metricsSlice.ts` - NEW
- **FILE-P8-011**: `frontend/src/types/metrics.ts` - NEW
- **FILE-P8-012**: `frontend/src/hooks/useMetrics.ts` - NEW

### Modified Files
- **FILE-P8-013**: `frontend/src/components/plots/Stats/StatCard.tsx` - MODIFY - Add labelTilt
- **FILE-P8-014**: `frontend/src/store/index.ts` - MODIFY - Add metricsSlice

### Test Files
- **FILE-P8-015**: `frontend/src/components/metrics/__tests__/MetricsRow.test.tsx` - NEW
- **FILE-P8-016**: `frontend/src/components/metrics/cards/__tests__/FiveYearAnomalyCard.test.tsx` - NEW
- **FILE-P8-017**: `frontend/src/store/slices/__tests__/metricsSlice.test.ts` - NEW
- **FILE-P8-018**: `frontend/src/services/__tests__/MetricsService.test.ts` - NEW
- **FILE-P8-019**: `frontend/src/hooks/__tests__/useMetrics.test.ts` - NEW

## 6. Testing

### Unit Tests
- **TEST-P8-001**: StatCard renders with tilted label when labelTilt provided
- **TEST-P8-002**: StatCard renders normally when labelTilt omitted
- **TEST-P8-003**: MetricsRow renders 6 children with correct layout
- **TEST-P8-004**: MetricsService fetches and parses JSON correctly
- **TEST-P8-005**: MetricsService handles network errors gracefully
- **TEST-P8-006**: metricsSlice caches data by location key
- **TEST-P8-007**: Each metric card formats values correctly

### Integration Tests
- **TEST-P8-008**: MetricsRow responsive breakpoints work correctly
- **TEST-P8-009**: City selection triggers metrics fetch
- **TEST-P8-010**: Loading state displays during fetch
- **TEST-P8-011**: Error state displays on fetch failure

### Mock Data Requirements
- **MOCK-P8-001**: Mock LocationMetrics JSON for Berlin
- **MOCK-P8-002**: Mock LocationMetrics JSON for Germany (national)
- **MOCK-P8-003**: Mock network error response

### E2E Tests
- **TEST-P8-012**: User sees metrics update when selecting different city
- **TEST-P8-013**: Info tooltips are accessible via click/hover
- **TEST-P8-014**: Mobile layout stacks cards correctly

## 7. Risks & Assumptions

### Risks
- **RISK-P8-001**: Label tilt rotation affects layout on narrow cards
  - **Mitigation**: Test at various widths; use modest tilt angle (5-7°)

- **RISK-P8-002**: Six cards may not fit on smaller desktop screens
  - **Mitigation**: Use percentage widths with min-width; allow wrap

- **RISK-P8-003**: Metrics JSON schema changes breaking frontend
  - **Mitigation**: Validate JSON against TypeScript interface; version API

### Assumptions
- **ASSUMPTION-P8-001**: Metrics JSON available at predictable URLs per location
- **ASSUMPTION-P8-002**: StatCard styling works with rotation transform
- **ASSUMPTION-P8-003**: 6 metrics is final number (no dynamic metric count)
- **ASSUMPTION-P8-004**: City IDs in metrics match cityDataSlice IDs

## 8. Multi-Agent Execution Notes

### Execution Order
**Parallel tasks (can run simultaneously):**
- Phase 8.1 (StatCard Enhancement)
- Phase 8.2 (MetricsRow Container)  
- Phase 8.3 (Type Definitions)
- Phase 8.4 (Metrics Service)

**Sequential dependencies:**
- Phase 8.5 (Slice) depends on Phase 8.3 (Types) and Phase 8.4 (Service)
- Phase 8.6 (Cards) depends on Phase 8.1 (StatCard) and Phase 8.5 (Slice)
- Phase 8.7 (Integration) requires all previous phases

### Agent Context Requirements
Provide these files for agent execution:
- This plan document
- `frontend/src/components/plots/Stats/StatCard.tsx` (existing component to extend)
- `frontend/src/store/factories/createDataSlice.ts` (slice factory pattern)
- `frontend/src/styles/design-system.ts` (styling tokens)
- `frontend/src/hooks/useBreakpoint.ts` (responsive hook)

### Validation Checkpoints
- **After Phase 8.1**: StatCard with labelTilt renders correctly
- **After Phase 8.2**: MetricsRow responsive layout works at all breakpoints
- **After Phase 8.4**: MetricsService tests pass
- **After Phase 8.5**: Slice tests pass; store builds without errors
- **After Phase 8.7**: Full integration working with mock/real data

## 9. Related Specifications / Further Reading

- [Master Plan - Static Metrics Section](../botox/era5-germany-climate-visualization-1.md#implementation-phase-7)
- [Existing StatCard Component](../../frontend/src/components/plots/Stats/StatCard.tsx)
- [createDataSlice Factory](../../frontend/src/store/factories/createDataSlice.ts)

## 10. Code Reference (REQUIRED)

### 10.1 Metrics Type Definitions

**File**: `frontend/src/types/metrics.ts`

```typescript
/**
 * Metrics Type Definitions
 * 
 * Interfaces for climate metrics returned by the metrics API.
 * Updated to match narrative spec metric names.
 */

/** Five-year temperature anomaly (2021-2025 vs 1961-1990) */
export interface FiveYearAnomalyMetric {
    /** Temperature anomaly in °C (positive = warmer) */
    value: number;
    /** Period start year (e.g., 2021) */
    periodStart: number;
    /** Period end year (e.g., 2025) */
    periodEnd: number;
    /** Reference period start year (1961) */
    referenceStart: number;
    /** Reference period end year (1990) */
    referenceEnd: number;
    /** Methodology description for info tooltip */
    methodology: string;
}

/** Long-term warming trend */
export interface WarmingRateMetric {
    /** Warming rate in °C per decade */
    value: number;
    /** Start year of trend calculation (1995) */
    startYear: number;
    /** End year of trend calculation (2025) */
    endYear: number;
    /** R² value of linear regression (0-1), indicating statistical confidence */
    confidence: number;
    /** Methodology description */
    methodology: string;
}

/** Count of record-breaking temperature days */
export interface RecordDaysMetric {
    /** Total record days in the year */
    total: number;
    /** Hot record days (new daily max) */
    hot: number;
    /** Cold record days (new daily min) */
    cold: number;
    /** Year for these records */
    year: number;
    /** Length of historical record in years */
    recordLength: number;
    /** Methodology description */
    methodology: string;
}

/** Winter (DJF) temperature anomaly */
export interface WinterWarmingMetric {
    /** Winter anomaly in °C */
    value: number;
    /** Period start year (2021) */
    periodStart: number;
    /** Period end year (2025) */
    periodEnd: number;
    /** Reference period start (1961) */
    referenceStart: number;
    /** Reference period end (1990) */
    referenceEnd: number;
    /** Methodology description */
    methodology: string;
}

/** Snow days lost vs reference period */
export interface SnowDaysLostMetric {
    /** Difference in snow days (negative = days lost) */
    value: number;
    /** Current period average snow days */
    currentAverage: number;
    /** Reference period average snow days */
    referenceAverage: number;
    /** Period start year */
    periodStart: number;
    /** Period end year */
    periodEnd: number;
    /** Methodology description */
    methodology: string;
}

/** Count of comfortable temperature days (15-25°C) */
export interface ComfortableDaysMetric {
    /** Days with mean temp 15-25°C */
    count: number;
    /** Average per year (2021-2025) */
    average: number;
    /** Reference period average */
    referenceAverage: number;
    /** Methodology description */
    methodology: string;
}

/** Combined metrics for a location */
export interface LocationMetrics {
    /** Location identifier (city ID or 'national') */
    locationId: string;
    /** Location name */
    locationName: string;
    /** Data timestamp (ISO string) */
    generatedAt: string;
    /** Individual metrics */
    fiveYearAnomaly: FiveYearAnomalyMetric;
    warmingRate: WarmingRateMetric;
    recordDays: RecordDaysMetric;
    winterWarming: WinterWarmingMetric;
    snowDaysLost: SnowDaysLostMetric;
    comfortableDays: ComfortableDaysMetric;
}

/** Keyed metrics state */
export interface MetricsState {
    status: 'idle' | 'loading' | 'succeeded' | 'failed';
    error: string | undefined;
    data: Record<string, LocationMetrics>;
    loadingKeys: string[];
}
```

### 10.2 Extended StatCard Component

**File**: `frontend/src/components/plots/Stats/StatCard.tsx` (modifications)

```typescript
/**
 * StatCard Enhanced Props
 * 
 * Add these props to existing StatCardProps interface:
 */

interface StatCardProps {
    // ... existing props ...
    
    /** Rotation angle for title label in degrees (default: 0) */
    labelTilt?: number;
    
    /** Font size for value (default: '3rem') */
    valueSize?: string;
    
    /** Accent color for value text (overrides default) */
    accentColor?: string;
}

// Update getTitleStyle to include rotation
const getTitleStyle = (darkMode: boolean, labelTilt: number = 0): CSSProperties => ({
    fontSize: theme.typography.fontSize.md,
    fontWeight: theme.typography.fontWeight.medium,
    color: getColors(darkMode).title,
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
    transform: labelTilt !== 0 ? `rotate(${labelTilt}deg)` : undefined,
    transformOrigin: 'center center',
});

// Update getValueStyle to accept custom size and color
const getValueStyle = (
    isLoading: boolean,
    hasError: boolean,
    darkMode: boolean,
    valueSize: string = '3rem',
    accentColor?: string
): CSSProperties => ({
    fontSize: valueSize,
    fontWeight: theme.typography.fontWeight.bold,
    color: hasError 
        ? theme.colors.neutral 
        : (accentColor ?? getColors(darkMode).value),
    marginBottom: theme.spacing.sm,
    opacity: isLoading ? 0.5 : 1,
    transition: 'opacity 0.2s ease-in-out',
});

// In component, update useMemo calls:
const titleStyle = useMemo(() => getTitleStyle(darkMode, labelTilt), [darkMode, labelTilt]);
const valueStyle = useMemo(() => getValueStyle(isLoading, !!error, darkMode, valueSize, accentColor), [isLoading, error, darkMode, valueSize, accentColor]);
```

### 10.3 MetricsRow Container

**File**: `frontend/src/components/metrics/MetricsRow.tsx`

```typescript
/**
 * MetricsRow Component
 * 
 * Responsive container for displaying 6 metric cards in a horizontal row.
 * Adapts layout based on screen size:
 * - Desktop (>992px): 6 cards in row
 * - Tablet (576-992px): 3x2 grid
 * - Mobile (<576px): single column
 */

import { useMemo, memo } from 'react';
import type { CSSProperties, ReactNode } from 'react';
import { theme } from '../../styles/design-system';
import { useBreakpointDown } from '../../hooks/useBreakpoint';

const getContainerStyle = (isMobile: boolean, isTablet: boolean): CSSProperties => ({
    display: 'flex',
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: theme.spacing.md,
    justifyContent: isMobile ? 'center' : 'space-between',
    padding: theme.spacing.lg,
    backgroundColor: theme.colors.background,
    borderRadius: theme.borderRadius?.md ?? '8px',
});

const getCardWrapperStyle = (isMobile: boolean, isTablet: boolean): CSSProperties => ({
    // Desktop: 6 equal cards (account for gaps)
    // Tablet: 3 per row
    // Mobile: full width
    flex: isMobile 
        ? '1 1 100%' 
        : isTablet 
            ? '1 1 calc(33.333% - 12px)' 
            : '1 1 calc(16.666% - 12px)',
    maxWidth: isMobile ? '100%' : isTablet ? 'calc(33.333% - 12px)' : 'calc(16.666% - 12px)',
    minWidth: isMobile ? 280 : 150,
});

interface MetricsRowProps {
    children: ReactNode;
    className?: string;
}

const MetricsRow = memo(({ children, className }: MetricsRowProps) => {
    const isMobile = useBreakpointDown('mobile');
    const isTablet = useBreakpointDown('desktop');

    const containerStyle = useMemo(
        () => getContainerStyle(isMobile, isTablet && !isMobile),
        [isMobile, isTablet]
    );

    const cardWrapperStyle = useMemo(
        () => getCardWrapperStyle(isMobile, isTablet && !isMobile),
        [isMobile, isTablet]
    );

    return (
        <div style={containerStyle} className={className}>
            {Array.isArray(children) 
                ? children.map((child, index) => (
                    <div key={index} style={cardWrapperStyle}>
                        {child}
                    </div>
                ))
                : <div style={cardWrapperStyle}>{children}</div>
            }
        </div>
    );
});

MetricsRow.displayName = 'MetricsRow';

export default MetricsRow;
```

### 10.4 Metrics Service

**File**: `frontend/src/services/MetricsService.ts`

```typescript
/**
 * Metrics Service
 * 
 * Fetches pre-calculated climate metrics for locations.
 */

import { buildUrl } from './utils/serviceUtils';
import type { LocationMetrics } from '../types/metrics';

const METRICS_BASE_PATH = '/data/metrics';

/**
 * Fetch metrics for a specific city/location
 * @param locationId - City ID or 'national' for Germany-wide
 */
export const fetchMetricsForLocation = async (
    locationId: string
): Promise<LocationMetrics> => {
    const url = buildUrl(`${METRICS_BASE_PATH}/${locationId}.json`, false);
    
    const response = await fetch(url);
    
    if (!response.ok) {
        if (response.status === 404) {
            throw new Error(`Metrics not available for location: ${locationId}`);
        }
        throw new Error(`Failed to fetch metrics: ${response.statusText}`);
    }
    
    const data = await response.json();
    
    // Validate required fields
    if (!data.locationId || !data.annualAnomaly || !data.warmingRate) {
        throw new Error('Invalid metrics data structure');
    }
    
    return data as LocationMetrics;
};

/**
 * Fetch national (Germany-wide) metrics
 */
export const fetchNationalMetrics = async (): Promise<LocationMetrics> => {
    return fetchMetricsForLocation('national');
};

/**
 * Check if metrics are available for a location
 */
export const checkMetricsAvailability = async (
    locationId: string
): Promise<boolean> => {
    try {
        const url = buildUrl(`${METRICS_BASE_PATH}/${locationId}.json`, false);
        const response = await fetch(url, { method: 'HEAD' });
        return response.ok;
    } catch {
        return false;
    }
};
```

### 10.5 Metrics Slice

**File**: `frontend/src/store/slices/metricsSlice.ts`

```typescript
/**
 * Metrics Slice
 * 
 * Redux state for climate metrics with per-location caching.
 */

import { createDataSlice } from '../factories/createDataSlice';
import { fetchMetricsForLocation } from '../../services/MetricsService';
import type { LocationMetrics } from '../../types/metrics';
import type { RootState } from '../index';
import { createSelector } from '@reduxjs/toolkit';

interface FetchMetricsArgs {
    locationId: string;
}

const {
    slice,
    actions,
    selectors,
    hooks,
    shouldFetch,
} = createDataSlice<LocationMetrics, FetchMetricsArgs, 'keyed', never, string>({
    name: 'metrics',
    fetchFn: async ({ locationId }) => {
        return fetchMetricsForLocation(locationId);
    },
    stateShape: 'keyed',
    cache: {
        strategy: 'by-key',
        keyExtractor: ({ locationId }) => locationId,
        ttl: 1000 * 60 * 60, // 1 hour
    },
});

// Export actions
export const fetchMetrics = actions.fetch;
export const resetMetrics = actions.reset;

// Export basic selectors
export const selectMetricsStatus = selectors.selectStatus;
export const selectMetricsError = selectors.selectError;
export const selectMetricsData = selectors.selectData;
export const selectMetricsIsLoading = selectors.selectIsLoading;

// Derived selectors for specific metrics
export const selectMetricsForLocation = (locationId: string) => 
    createSelector(
        [selectMetricsData],
        (data) => data?.[locationId]
    );

export const selectAnnualAnomaly = (locationId: string) =>
    createSelector(
        [selectMetricsForLocation(locationId)],
        (metrics) => metrics?.annualAnomaly
    );

export const selectWarmingRate = (locationId: string) =>
    createSelector(
        [selectMetricsForLocation(locationId)],
        (metrics) => metrics?.warmingRate
    );

export const selectRecordDays = (locationId: string) =>
    createSelector(
        [selectMetricsForLocation(locationId)],
        (metrics) => metrics?.recordDays
    );

export const selectSeasonalWarming = (locationId: string) =>
    createSelector(
        [selectMetricsForLocation(locationId)],
        (metrics) => metrics?.seasonalWarming
    );

export const selectThresholdDays = (locationId: string) =>
    createSelector(
        [selectMetricsForLocation(locationId)],
        (metrics) => metrics?.thresholdDays
    );

export const selectComfortableDays = (locationId: string) =>
    createSelector(
        [selectMetricsForLocation(locationId)],
        (metrics) => metrics?.comfortableDays
    );

// Hook exports
export const useMetricsData = hooks.useData;
export const useMetricsStatus = hooks.useStatus;
export const useMetricsError = hooks.useError;
export const useMetricsIsLoading = hooks.useIsLoading;

// Utility
export const shouldFetchMetrics = shouldFetch;

export default slice.reducer;
```

### 10.6 AnnualAnomalyCard Component

**File**: `frontend/src/components/metrics/cards/AnnualAnomalyCard.tsx`

```typescript
/**
 * Annual Anomaly Card
 * 
 * Displays the annual temperature anomaly relative to reference period.
 */

import { memo, useMemo } from 'react';
import StatCard from '../../plots/Stats/StatCard';
import { useAppSelector } from '../../../store/hooks/useAppSelector';
import { selectAnnualAnomaly, selectMetricsIsLoading, selectMetricsError } from '../../../store/slices/metricsSlice';
import { theme } from '../../../styles/design-system';

interface AnnualAnomalyCardProps {
    locationId: string;
}

const formatAnomaly = (value: number): string => {
    const sign = value >= 0 ? '+' : '';
    return `${sign}${value.toFixed(1)}°C`;
};

const getAnomalyColor = (value: number): string => {
    if (value > 1) return theme.colors.hot;
    if (value < -1) return theme.colors.cold;
    return theme.colors.neutral;
};

const AnnualAnomalyCard = memo(({ locationId }: AnnualAnomalyCardProps) => {
    const anomaly = useAppSelector(selectAnnualAnomaly(locationId));
    const isLoading = useAppSelector(selectMetricsIsLoading);
    const error = useAppSelector(selectMetricsError);

    const formattedValue = useMemo(() => 
        anomaly ? formatAnomaly(anomaly.value) : '—',
        [anomaly]
    );

    const accentColor = useMemo(() =>
        anomaly ? getAnomalyColor(anomaly.value) : undefined,
        [anomaly]
    );

    const subtitle = useMemo(() =>
        anomaly ? `vs. ${anomaly.referenceStart}-${anomaly.referenceEnd} Mittel` : undefined,
        [anomaly]
    );

    const infoText = anomaly?.methodology ?? 
        'Die jährliche Temperaturanomalie zeigt die Abweichung der Jahresmitteltemperatur vom langjährigen Referenzzeitraum (1961-1990).';

    return (
        <StatCard
            title="Jahresanomalie"
            value={formattedValue}
            subtitle={subtitle}
            footnote={anomaly ? `Jahr ${anomaly.year}` : undefined}
            infoText={infoText}
            isLoading={isLoading}
            error={error}
            labelTilt={-5}
            accentColor={accentColor}
            width="100%"
        />
    );
});

AnnualAnomalyCard.displayName = 'AnnualAnomalyCard';

export default AnnualAnomalyCard;
```

### 10.7 WarmingRateCard Component

**File**: `frontend/src/components/metrics/cards/WarmingRateCard.tsx`

```typescript
/**
 * Warming Rate Card
 * 
 * Displays the long-term warming trend.
 */

import { memo, useMemo } from 'react';
import StatCard from '../../plots/Stats/StatCard';
import { useAppSelector } from '../../../store/hooks/useAppSelector';
import { selectWarmingRate, selectMetricsIsLoading, selectMetricsError } from '../../../store/slices/metricsSlice';
import { theme } from '../../../styles/design-system';

interface WarmingRateCardProps {
    locationId: string;
}

const formatRate = (value: number): string => {
    const sign = value >= 0 ? '+' : '';
    return `${sign}${value.toFixed(2)}°C`;
};

const WarmingRateCard = memo(({ locationId }: WarmingRateCardProps) => {
    const warmingRate = useAppSelector(selectWarmingRate(locationId));
    const isLoading = useAppSelector(selectMetricsIsLoading);
    const error = useAppSelector(selectMetricsError);

    const formattedValue = useMemo(() =>
        warmingRate ? formatRate(warmingRate.value) : '—',
        [warmingRate]
    );

    const subtitle = useMemo(() =>
        warmingRate 
            ? `pro Dekade (${warmingRate.startYear}-${warmingRate.endYear})`
            : undefined,
        [warmingRate]
    );

    const footnote = useMemo(() =>
        warmingRate 
            ? `R² = ${warmingRate.rSquared.toFixed(2)}`
            : undefined,
        [warmingRate]
    );

    const infoText = warmingRate?.methodology ??
        'Die Erwärmungsrate basiert auf einer linearen Regression der Jahresmitteltemperaturen über den angegebenen Zeitraum. Der R²-Wert zeigt die Güte der Anpassung.';

    return (
        <StatCard
            title="Erwärmungsrate"
            value={formattedValue}
            subtitle={subtitle}
            footnote={footnote}
            infoText={infoText}
            isLoading={isLoading}
            error={error}
            labelTilt={-5}
            accentColor={theme.colors.hot}
            width="100%"
        />
    );
});

WarmingRateCard.displayName = 'WarmingRateCard';

export default WarmingRateCard;
```

### 10.8 ThresholdDaysCard Component

**File**: `frontend/src/components/metrics/cards/ThresholdDaysCard.tsx`

```typescript
/**
 * Threshold Days Card
 * 
 * Displays count of temperature threshold days (hot, ice, frost, etc.).
 */

import { memo, useMemo } from 'react';
import StatCard from '../../plots/Stats/StatCard';
import { useAppSelector } from '../../../store/hooks/useAppSelector';
import { selectThresholdDays, selectMetricsIsLoading, selectMetricsError } from '../../../store/slices/metricsSlice';
import { theme } from '../../../styles/design-system';

interface ThresholdDaysCardProps {
    locationId: string;
    /** Which threshold to display (default: hotDays) */
    threshold?: 'hotDays' | 'summerDays' | 'iceDays' | 'frostDays' | 'tropicalNights';
}

const THRESHOLD_CONFIG = {
    hotDays: {
        title: 'Heiße Tage',
        description: 'Tmax ≥ 30°C',
        info: 'Heiße Tage sind Tage, an denen die Höchsttemperatur mindestens 30°C erreicht.',
    },
    summerDays: {
        title: 'Sommertage',
        description: 'Tmax ≥ 25°C',
        info: 'Sommertage sind Tage, an denen die Höchsttemperatur mindestens 25°C erreicht.',
    },
    iceDays: {
        title: 'Eistage',
        description: 'Tmax < 0°C',
        info: 'Eistage sind Tage, an denen die Höchsttemperatur unter 0°C bleibt.',
    },
    frostDays: {
        title: 'Frosttage',
        description: 'Tmin < 0°C',
        info: 'Frosttage sind Tage, an denen die Tiefsttemperatur unter 0°C fällt.',
    },
    tropicalNights: {
        title: 'Tropennächte',
        description: 'Tmin ≥ 20°C',
        info: 'Tropennächte sind Nächte, in denen die Temperatur nicht unter 20°C fällt.',
    },
};

const ThresholdDaysCard = memo(({ locationId, threshold = 'hotDays' }: ThresholdDaysCardProps) => {
    const thresholdDays = useAppSelector(selectThresholdDays(locationId));
    const isLoading = useAppSelector(selectMetricsIsLoading);
    const error = useAppSelector(selectMetricsError);

    const config = THRESHOLD_CONFIG[threshold];

    const currentValue = useMemo(() =>
        thresholdDays ? thresholdDays[threshold] : undefined,
        [thresholdDays, threshold]
    );

    const referenceValue = useMemo(() =>
        thresholdDays?.reference?.[threshold],
        [thresholdDays, threshold]
    );

    const formattedValue = useMemo(() =>
        currentValue !== undefined ? `${currentValue}` : '—',
        [currentValue]
    );

    const subtitle = useMemo(() => config.description, [config]);

    const footnote = useMemo(() => {
        if (currentValue === undefined || referenceValue === undefined) return undefined;
        const diff = currentValue - referenceValue;
        const sign = diff >= 0 ? '+' : '';
        return `${sign}${diff} vs. Referenz`;
    }, [currentValue, referenceValue]);

    const accentColor = useMemo(() => {
        if (['hotDays', 'summerDays', 'tropicalNights'].includes(threshold)) {
            return theme.colors.hot;
        }
        return theme.colors.cold;
    }, [threshold]);

    return (
        <StatCard
            title={config.title}
            value={formattedValue}
            subtitle={subtitle}
            footnote={footnote}
            infoText={config.info}
            isLoading={isLoading}
            error={error}
            labelTilt={-5}
            accentColor={accentColor}
            width="100%"
        />
    );
});

ThresholdDaysCard.displayName = 'ThresholdDaysCard';

export default ThresholdDaysCard;
```

### 10.9 useMetrics Hook

**File**: `frontend/src/hooks/useMetrics.ts`

```typescript
/**
 * useMetrics Hook
 * 
 * Custom hook for managing metrics data fetching and state.
 * Auto-fetches metrics when location changes.
 */

import { useEffect, useMemo } from 'react';
import { useAppDispatch } from '../store/hooks/useAppDispatch';
import { useAppSelector } from '../store/hooks/useAppSelector';
import {
    fetchMetrics,
    selectMetricsForLocation,
    selectMetricsStatus,
    selectMetricsError,
    shouldFetchMetrics,
} from '../store/slices/metricsSlice';
import type { LocationMetrics } from '../types/metrics';

export interface UseMetricsOptions {
    /** Location ID to fetch metrics for */
    locationId: string;
    /** Whether to auto-fetch on mount/change (default: true) */
    autoFetch?: boolean;
}

export interface UseMetricsReturn {
    /** Full metrics data for the location */
    metrics: LocationMetrics | undefined;
    /** Loading status */
    isLoading: boolean;
    /** Whether data is ready */
    isReady: boolean;
    /** Error message if fetch failed */
    error: string | undefined;
    /** Manually trigger fetch */
    refetch: () => void;
}

export function useMetrics({ 
    locationId, 
    autoFetch = true 
}: UseMetricsOptions): UseMetricsReturn {
    const dispatch = useAppDispatch();
    const selector = useMemo(() => selectMetricsForLocation(locationId), [locationId]);
    const metrics = useAppSelector(selector);
    const status = useAppSelector(selectMetricsStatus);
    const error = useAppSelector(selectMetricsError);

    const isLoading = status === 'loading';
    const isReady = status === 'succeeded' && metrics !== undefined;

    // Auto-fetch when locationId changes
    useEffect(() => {
        if (autoFetch && locationId) {
            dispatch(fetchMetrics({ locationId }));
        }
    }, [dispatch, locationId, autoFetch]);

    const refetch = () => {
        if (locationId) {
            dispatch(fetchMetrics({ locationId }));
        }
    };

    return {
        metrics,
        isLoading,
        isReady,
        error,
        refetch,
    };
}

/**
 * Hook to get metrics for the currently selected city
 */
export function useSelectedCityMetrics(): UseMetricsReturn {
    const selectedCityId = useAppSelector(state => state.selectedCity.cityId);
    const locationId = selectedCityId ?? 'national';
    
    return useMetrics({ locationId });
}
```

### 10.10 Barrel Export

**File**: `frontend/src/components/metrics/index.ts`

```typescript
/**
 * Metrics Components Barrel Export
 */

export { default as MetricsRow } from './MetricsRow';
export { default as AnnualAnomalyCard } from './cards/AnnualAnomalyCard';
export { default as WarmingRateCard } from './cards/WarmingRateCard';
export { default as RecordDaysCard } from './cards/RecordDaysCard';
export { default as SeasonalWarmingCard } from './cards/SeasonalWarmingCard';
export { default as ThresholdDaysCard } from './cards/ThresholdDaysCard';
export { default as ComfortableDaysCard } from './cards/ComfortableDaysCard';
```

### 10.11 Mock Data for Testing

**File**: `frontend/src/__mocks__/metricsMocks.ts`

```typescript
/**
 * Mock metrics data for testing
 */

import type { LocationMetrics } from '../types/metrics';

export const mockLocationMetrics: LocationMetrics = {
    locationId: 'berlin',
    locationName: 'Berlin',
    generatedAt: '2026-02-15T10:00:00Z',
    annualAnomaly: {
        value: 1.2,
        year: 2025,
        referenceStart: 1961,
        referenceEnd: 1990,
        methodology: 'Mittelwert der Tagesmitteltemperaturen im Vergleich zum Referenzzeitraum.',
    },
    warmingRate: {
        value: 0.35,
        startYear: 1990,
        endYear: 2025,
        confidence: 0.95,
        rSquared: 0.87,
        methodology: 'Lineare Regression der Jahresmitteltemperaturen.',
    },
    recordDays: {
        total: 12,
        hot: 10,
        cold: 2,
        year: 2025,
        recordLength: 75,
        methodology: 'Vergleich mit allen Tageswerten seit 1951.',
    },
    seasonalWarming: {
        winter: 1.8,
        spring: 1.1,
        summer: 1.5,
        fall: 0.9,
        year: 2025,
        referenceStart: 1961,
        referenceEnd: 1990,
        methodology: 'Saisonmittel vs. Referenzzeitraum.',
    },
    thresholdDays: {
        summerDays: 78,
        hotDays: 22,
        iceDays: 8,
        frostDays: 52,
        tropicalNights: 5,
        year: 2025,
        reference: {
            summerDays: 45,
            hotDays: 8,
            iceDays: 22,
            frostDays: 85,
            tropicalNights: 1,
        },
        methodology: 'Tageszählung nach DWD-Definitionen.',
    },
    comfortableDays: {
        count: 92,
        year: 2025,
        referenceAverage: 105,
        methodology: 'Tage mit Höchsttemperatur zwischen 18°C und 25°C.',
    },
};

export const mockNationalMetrics: LocationMetrics = {
    ...mockLocationMetrics,
    locationId: 'national',
    locationName: 'Deutschland',
    annualAnomaly: {
        ...mockLocationMetrics.annualAnomaly,
        value: 1.0,
    },
    warmingRate: {
        ...mockLocationMetrics.warmingRate,
        value: 0.32,
    },
};
```

### 10.12 Test Examples

**File**: `frontend/src/components/metrics/__tests__/MetricsRow.test.tsx`

```typescript
/**
 * MetricsRow Component Tests
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import MetricsRow from '../MetricsRow';

// Mock useBreakpointDown hook
vi.mock('../../../hooks/useBreakpoint', () => ({
    useBreakpointDown: vi.fn((breakpoint) => {
        // Default to desktop
        return false;
    }),
}));

describe('MetricsRow', () => {
    it('renders all children', () => {
        render(
            <MetricsRow>
                <div data-testid="card-1">Card 1</div>
                <div data-testid="card-2">Card 2</div>
                <div data-testid="card-3">Card 3</div>
            </MetricsRow>
        );

        expect(screen.getByTestId('card-1')).toBeInTheDocument();
        expect(screen.getByTestId('card-2')).toBeInTheDocument();
        expect(screen.getByTestId('card-3')).toBeInTheDocument();
    });

    it('renders single child correctly', () => {
        render(
            <MetricsRow>
                <div data-testid="single-card">Single Card</div>
            </MetricsRow>
        );

        expect(screen.getByTestId('single-card')).toBeInTheDocument();
    });

    it('applies container styles', () => {
        const { container } = render(
            <MetricsRow>
                <div>Card</div>
            </MetricsRow>
        );

        const row = container.firstChild as HTMLElement;
        expect(row).toHaveStyle({ display: 'flex' });
    });
});
```

**File**: `frontend/src/services/__tests__/MetricsService.test.ts`

```typescript
/**
 * MetricsService Tests
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { fetchMetricsForLocation, fetchNationalMetrics } from '../MetricsService';
import { mockLocationMetrics } from '../../__mocks__/metricsMocks';

describe('MetricsService', () => {
    beforeEach(() => {
        global.fetch = vi.fn();
    });

    afterEach(() => {
        vi.resetAllMocks();
    });

    describe('fetchMetricsForLocation', () => {
        it('fetches and parses metrics correctly', async () => {
            (global.fetch as any).mockResolvedValue({
                ok: true,
                json: () => Promise.resolve(mockLocationMetrics),
            });

            const result = await fetchMetricsForLocation('berlin');

            expect(result.locationId).toBe('berlin');
            expect(result.annualAnomaly.value).toBe(1.2);
        });

        it('throws on 404', async () => {
            (global.fetch as any).mockResolvedValue({
                ok: false,
                status: 404,
            });

            await expect(fetchMetricsForLocation('unknown')).rejects.toThrow(
                'Metrics not available for location'
            );
        });

        it('throws on invalid data structure', async () => {
            (global.fetch as any).mockResolvedValue({
                ok: true,
                json: () => Promise.resolve({ invalid: 'data' }),
            });

            await expect(fetchMetricsForLocation('berlin')).rejects.toThrow(
                'Invalid metrics data structure'
            );
        });
    });

    describe('fetchNationalMetrics', () => {
        it('calls fetchMetricsForLocation with national', async () => {
            (global.fetch as any).mockResolvedValue({
                ok: true,
                json: () => Promise.resolve({ 
                    ...mockLocationMetrics, 
                    locationId: 'national' 
                }),
            });

            const result = await fetchNationalMetrics();
            expect(result.locationId).toBe('national');
        });
    });
});
```
