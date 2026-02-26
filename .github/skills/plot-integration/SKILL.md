```skill
---
name: plot-integration
description: Add a new Observable Plot visualization with data service, Redux slice, and React component. Use when integrating a new chart/plot that fetches CSV data per station and renders using @observablehq/plot.
---

# Plot Integration Skill

## Purpose

Wire a new Observable Plot visualization end-to-end: CSV data service → Redux slice → React component with plot rendering, loading/error states, and responsive layout. Includes CSV fixture creation and Vitest tests.

## Prerequisites

Gather context:

```
Subagent 1: "Read frontend/src/components/plots/registry.ts. Return: how plots are registered."
Subagent 2: "Read frontend/src/components/plots/TemperatureAnomaliesByDayOverYears/ — list all files, read View.tsx and plot.ts."
Subagent 3: "Read frontend/src/components/plots/iceAndHotDays/ — list all files, read View.tsx and plot.ts."
Subagent 4: "Read frontend/src/styles/design-system.ts. Return: color tokens for plots."
Subagent 5: "Read .github/skills/data-services-integration/SKILL.md. Return: service + slice pattern."
```

## Architecture

```
components/plots/<PlotName>/
├── View.tsx          # StackedPlotView wrapper, lazy-loaded from registry
├── LeftSide.tsx      # Plot description / controls (top on mobile)
├── RightSide.tsx     # Plot container (bottom on mobile)
├── plot.ts           # Observable Plot mark/scale definitions
├── hooks/            # Plot-specific data hooks
│   └── usePlotData.ts
└── __tests__/
    └── plot.test.ts
```

## Implementation Steps

### Step 1: Create CSV Fixture

**Location**: `frontend/src/__fixtures__/<plotName>/sample.csv`

```csv
date,stationId,metric1,metric2
2024-01-01,00044,5.2,-1.3
2024-06-15,00044,22.8,14.1
2024-12-31,00044,0.8,-5.1
```

Keep 5–15 rows covering edge cases (extreme values, missing data, year boundaries).

### Step 2: Create Data Service

Follow the `data-services-integration` skill for service creation. Key points:
- Use `fetchAndParseCSV` from `services/utils/csvUtils.js`
- Validate headers match fixture
- Return strongly typed record list

### Step 3: Create Redux Slice

Follow the `frontend-data-slice` skill. Use `createDataSlice` factory with appropriate cache strategy.

### Step 4: Create Plot Definition

**Location**: `frontend/src/components/plots/<PlotName>/plot.ts`

```typescript
import * as Plot from '@observablehq/plot';
import { theme } from '../../../styles/design-system.js';

export interface PlotConfig {
    data: MyPlotRecord[];
    width: number;
    height: number;
    isDarkMode?: boolean;
}

export function createMyPlot({ data, width, height, isDarkMode = false }: PlotConfig): SVGSVGElement | HTMLElement {
    const colors = isDarkMode ? theme.colors.plotDark : theme.colors.plotLight;

    return Plot.plot({
        width,
        height,
        marginLeft: 50,
        marginBottom: 40,
        x: {
            type: 'time',
            label: 'Datum',
        },
        y: {
            label: 'Temperatur (°C)',
            grid: true,
        },
        color: {
            scheme: 'RdBu',
            reverse: true,
        },
        marks: [
            Plot.dot(data, {
                x: 'date',
                y: 'value',
                fill: 'value',
                r: 3,
            }),
            Plot.ruleY([0], { stroke: colors.axis }),
        ],
        style: {
            background: 'transparent',
            color: colors.text,
            fontFamily: theme.typography.fontFamily,
        },
    });
}
```

### Step 5: Create Plot Data Hook

**Location**: `frontend/src/components/plots/<PlotName>/hooks/usePlotData.ts`

```typescript
import { useMemo } from 'react';
import { useAppSelector } from '../../../../store/hooks/useAppSelector.js';
import { selectMyData, selectMyDataStatus } from '../../../../store/slices/myDataSlice.js';

export function usePlotData() {
    const rawData = useAppSelector(selectMyData);
    const status = useAppSelector(selectMyDataStatus);
    const isLoading = status === 'loading' || status === 'idle';
    const error = status === 'failed' ? 'Daten konnten nicht geladen werden.' : null;

    const plotData = useMemo(() => {
        if (rawData.length === 0) return [];
        return rawData.map(r => ({
            date: new Date(r.date),
            value: r.value,
        }));
    }, [rawData]);

    return { plotData, isLoading, error };
}
```

### Step 6: Create View Component

**Location**: `frontend/src/components/plots/<PlotName>/View.tsx`

```typescript
import { memo } from 'react';
import StackedPlotView from '../common/StackedPlotView.js';
import LeftSide from './LeftSide.js';
import RightSide from './RightSide.js';

const PlotNameView = memo(() => (
    <StackedPlotView leftSide={<LeftSide />} rightSide={<RightSide />} />
));

PlotNameView.displayName = 'PlotNameView';
export default PlotNameView;
```

**RightSide.tsx** — renders the Observable Plot into a ref:

```typescript
import { memo, useRef, useEffect, useState } from 'react';
import { usePlotData } from './hooks/usePlotData.js';
import { createMyPlot } from './plot.js';

const RightSide = memo(() => {
    const containerRef = useRef<HTMLDivElement>(null);
    const { plotData, isLoading, error } = usePlotData();
    const [dimensions, setDimensions] = useState({ width: 600, height: 400 });

    useEffect(() => {
        if (!containerRef.current || plotData.length === 0) return;
        const el = createMyPlot({ data: plotData, ...dimensions });
        containerRef.current.replaceChildren(el);
        return () => el.remove();
    }, [plotData, dimensions]);

    if (isLoading) return <div>Laden…</div>;
    if (error) return <div>{error}</div>;

    return <div ref={containerRef} />;
});
```

### Step 7: Register Plot

**File**: `frontend/src/components/plots/registry.ts`

```typescript
import { lazy } from 'react';

export const plots = [
    // ... existing plots
    {
        id: 'my-plot',
        component: lazy(() => import('./<PlotName>/View.js')),
    },
];
```

### Step 8: Write Tests

**Location**: `frontend/src/components/plots/<PlotName>/__tests__/plot.test.ts`

```typescript
import { describe, it, expect } from 'vitest';
import { createMyPlot } from '../plot.js';

const FIXTURE_DATA = [
    { date: new Date('2024-01-01'), value: 5.2 },
    { date: new Date('2024-06-15'), value: 22.8 },
    { date: new Date('2024-12-31'), value: -1.3 },
];

describe('createMyPlot', () => {
    it('returns an SVG/HTML element', () => {
        const el = createMyPlot({ data: FIXTURE_DATA, width: 600, height: 400 });
        expect(el).toBeDefined();
        expect(el.tagName).toMatch(/svg|figure/i);
    });

    it('handles empty data gracefully', () => {
        const el = createMyPlot({ data: [], width: 600, height: 400 });
        expect(el).toBeDefined();
    });
});
```

## Run Commands

```bash
cd frontend && npm run test -- --run src/components/plots/<PlotName>
cd frontend && npm run build
```

## Failure Modes & Self-Correction

| Failure | Cause | Fix |
|---------|-------|-----|
| Plot.plot throws in test | Missing jsdom SVG support | Ensure `vitest.config` uses `jsdom` env; may need to mock SVG APIs |
| Empty plot renders | Data not yet loaded when plot mounts | Check `isLoading` guard before calling `createMyPlot` |
| Type error on date field | String vs Date mismatch | Transform `string` → `new Date()` in hook, not service |
| Registry lazy import fails | Wrong path or missing default export | Ensure `View.tsx` has `export default` |
| Colors wrong in dark mode | Not reading theme tokens | Pass `isDarkMode` to `createMyPlot` |

## Checklist

- [ ] CSV fixture committed in `__fixtures__/<plotName>/`
- [ ] Data service + slice wired (per `data-services-integration` skill)
- [ ] `plot.ts` creates Observable Plot with proper scales/marks
- [ ] Data hook transforms raw records → plot-ready data
- [ ] View/LeftSide/RightSide components created
- [ ] Plot registered in `registry.ts`
- [ ] Plot unit test passes
- [ ] Loading and error states render correctly
- [ ] `npm run build` succeeds
```
