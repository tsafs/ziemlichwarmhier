```skill
---
name: metrics-card
description: Add a new metrics card to the Klimastatistiken section with service/slice/card wiring, tooltips, loading/error states, and schema tests. Use when adding climate statistics like indices, averages, or classification systems.
---

# Metrics Card Skill

## Purpose

Add a new statistical card to the "Klimastatistiken" (Stats) section. Covers: calculation utility, unit tests, data hook, StatCard integration, tooltip text, loading/error states, and optional schema validation.

## Prerequisites

Gather context:

```
Subagent 1: "Read frontend/src/components/plots/Stats/Bottom.tsx. Return: existing StatCard instances and imports."
Subagent 2: "Read frontend/src/components/plots/Stats/StatCard.tsx. Return: props interface and full component."
Subagent 3: "Read frontend/src/hooks/useHardinessZone.ts. Return: full hook as reference pattern."
Subagent 4: "Read frontend/src/utils/HardinessZoneUtils.ts and HardinessZoneUtils.test.ts. Return: calculation + tests."
Subagent 5: "Read frontend/src/store/slices/dailyAverageDataSlice.ts. Return: selectors for daily data."
```

## Architecture

```
Metrics card addition touches 4 files:
  utils/MyMetricUtils.ts           — Pure calculation function
  utils/MyMetricUtils.test.ts      — Deterministic unit tests
  hooks/useMyMetric.ts             — Hook consuming Redux data + calculation
  components/plots/Stats/Bottom.tsx — Add <StatCard> instance
```

## Implementation Steps

### Step 1: Create Calculation Utility

**Location**: `frontend/src/utils/<MetricName>Utils.ts`

```typescript
import type { RollingAverageRecordList } from '../classes/RollingAverageRecord.js';

export interface MetricResult {
    value: number;
    displayValue: string;
    description: string;
}

/**
 * Calculate <metric description> from daily climate records.
 *
 * Algorithm: <brief description>
 *
 * @param data Daily records with tasmin, tasmax, tas fields
 * @param startYear First year of range (inclusive)
 * @param endYear Last year of range (inclusive)
 * @returns Calculated metric or null if insufficient data
 */
export function calculateMyMetric(
    data: RollingAverageRecordList,
    startYear: number,
    endYear: number,
): MetricResult | null {
    if (!data || data.length === 0) return null;

    // Filter to year range
    const filtered = data.filter(r => {
        const year = parseInt(r.date.substring(0, 4), 10);
        return year >= startYear && year <= endYear;
    });

    if (filtered.length === 0) return null;

    // Calculation logic
    const value = 0; // TODO: actual computation

    return {
        value,
        displayValue: `${value.toFixed(1)}°C`,
        description: `Berechnet aus ${filtered.length} Tagen (${startYear}–${endYear})`,
    };
}
```

### Step 2: Write Deterministic Unit Tests

**Location**: `frontend/src/utils/<MetricName>Utils.test.ts`

```typescript
import { describe, it, expect } from 'vitest';
import { calculateMyMetric } from './<MetricName>Utils.js';
import type { RollingAverageRecordList } from '../classes/RollingAverageRecord.js';

// Deterministic fixture — synthetic but realistic
function generateFixture(startYear: number, endYear: number): RollingAverageRecordList {
    const records: RollingAverageRecordList = [];
    for (let year = startYear; year <= endYear; year++) {
        for (let month = 1; month <= 12; month++) {
            for (let day = 1; day <= 28; day++) {
                const dateStr = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
                records.push({
                    date: dateStr,
                    tasmin: -5 + month * 2 + (day % 5) - 2,
                    tasmax: 5 + month * 3 + (day % 5),
                    tas: month * 2.5 + (day % 5) - 1,
                });
            }
        }
    }
    return records;
}

describe('calculateMyMetric', () => {
    it('returns null for empty data', () => {
        expect(calculateMyMetric([], 2000, 2020)).toBeNull();
    });

    it('returns null for null data', () => {
        expect(calculateMyMetric(null as any, 2000, 2020)).toBeNull();
    });

    it('calculates correctly for known dataset', () => {
        const data = generateFixture(2000, 2020);
        const result = calculateMyMetric(data, 2000, 2020);

        expect(result).not.toBeNull();
        expect(result!.value).toBeCloseTo(/* expected value */, 1);
        expect(result!.displayValue).toMatch(/°C$/);
    });

    it('respects year range boundaries', () => {
        const data = generateFixture(1990, 2025);
        const result = calculateMyMetric(data, 2000, 2010);

        expect(result).not.toBeNull();
        expect(result!.description).toContain('2000–2010');
    });
});
```

### Step 3: Create Data Hook

**Location**: `frontend/src/hooks/useMyMetric.ts`

```typescript
import { useMemo } from 'react';
import { useAppSelector } from '../store/hooks/useAppSelector.js';
import { useSelectedStationId } from '../store/hooks/hooks.js';
import {
    selectDailyAverageData,
    selectDailyAverageDataStatus,
    selectDailyAverageDataError,
} from '../store/slices/dailyAverageDataSlice.js';
import { calculateMyMetric } from '../utils/<MetricName>Utils.js';

export interface MyMetricState {
    value: string;
    subtitle: string;
    footnote: string;
    isLoading: boolean;
    error: string | null;
}

export function useMyMetric(): MyMetricState {
    const stationId = useSelectedStationId();
    const dailyData = useAppSelector(selectDailyAverageData);
    const status = useAppSelector(selectDailyAverageDataStatus);
    const errorFromSlice = useAppSelector(selectDailyAverageDataError);

    const isLoading = status === 'loading' || status === 'idle';

    const result = useMemo(() => {
        if (!stationId || status !== 'succeeded' || dailyData.length === 0) {
            return null;
        }
        return calculateMyMetric(dailyData, 1991, 2020);
    }, [stationId, status, dailyData]);

    const error = useMemo(() => {
        if (errorFromSlice) return errorFromSlice;
        if (status === 'succeeded' && !result) {
            return 'Nicht genügend Daten für die Berechnung verfügbar.';
        }
        return null;
    }, [errorFromSlice, status, result]);

    return {
        value: result?.displayValue ?? '—',
        subtitle: result?.description ?? '',
        footnote: 'Basierend auf Wetterstationsdaten 1991–2020',
        isLoading,
        error,
    };
}
```

### Step 4: Add StatCard to Bottom.tsx

**File**: `frontend/src/components/plots/Stats/Bottom.tsx`

```typescript
// Add import
import { useMyMetric } from '../../../hooks/useMyMetric.js';

// Inside component, add hook call
const myMetric = useMyMetric();

// Add StatCard in JSX (alongside existing cards)
<StatCard
    title="Mein Klimaindex"
    value={myMetric.value}
    subtitle={myMetric.subtitle}
    footnote={myMetric.footnote}
    infoText="Erklärung: Was dieser Klimaindex bedeutet und wie er berechnet wird. Referenzzeitraum: 1991–2020."
    isLoading={myMetric.isLoading}
    error={myMetric.error}
/>
```

## StatCard Props Reference

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `title` | string | Yes | Card header (uppercase, small) |
| `value` | string | Yes | Main display value (large) |
| `subtitle` | string | No | Below value |
| `footnote` | string | No | Small italic at bottom |
| `infoText` | string | No | Tooltip text for ⓘ button |
| `isLoading` | boolean | No | Shows skeleton state |
| `error` | string \| null | No | Error message |
| `width` | number \| string | No | Card width (default: 280) |

## Schema Validation (Optional)

If the metric has a defined output contract, add schema test:

```typescript
// frontend/src/__tests__/schema/myMetric.schema.test.ts
import { describe, it, expect } from 'vitest';
import Ajv from 'ajv';

const schema = {
    type: 'object',
    required: ['value', 'displayValue', 'description'],
    properties: {
        value: { type: 'number' },
        displayValue: { type: 'string', pattern: '°C$' },
        description: { type: 'string' },
    },
    additionalProperties: false,
};

describe('MyMetric output schema', () => {
    it('calculation result conforms', () => {
        const ajv = new Ajv();
        const validate = ajv.compile(schema);
        const result = { value: 12.3, displayValue: '12.3°C', description: 'Test' };
        expect(validate(result)).toBe(true);
    });
});
```

## Run Commands

```bash
# Run metric tests only
cd frontend && npm run test -- --run src/utils/<MetricName>Utils

# Run all tests
cd frontend && npm run test

# Build check
cd frontend && npm run build
```

## Failure Modes & Self-Correction

| Failure | Cause | Fix |
|---------|-------|-----|
| `useMyMetric` returns `—` | Data not loaded or wrong status check | Verify `selectDailyAverageDataStatus` value |
| `calculateMyMetric` returns null | Year range outside data range | Check `startYear`/`endYear` vs fixture dates |
| StatCard not visible | Not added to Bottom.tsx JSX | Ensure card is inside the flex container |
| Tooltip not showing | Missing `infoText` prop | Add `infoText` string to StatCard |
| Test `toBeCloseTo` fails | Floating point or algorithm change | Recompute expected value from fixture |

## Checklist

- [ ] Calculation utility in `utils/` with pure function
- [ ] Unit tests with deterministic fixture (≥4 test cases)
- [ ] Data hook in `hooks/` consuming Redux selectors
- [ ] StatCard added to `Bottom.tsx` with all props
- [ ] `infoText` tooltip explains metric in German
- [ ] Loading state verified
- [ ] Error state verified (no data scenario)
- [ ] `npm run test` passes
- [ ] `npm run build` succeeds
```
