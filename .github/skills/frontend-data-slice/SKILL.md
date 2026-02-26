```skill
---
name: frontend-data-slice
description: Add a new data service with Redux slice, selectors, and hook — including Vitest tests, CSV/JSON fixtures, and schema validation. Use when adding a new data source that needs end-to-end wiring from fetch through store to component consumption.
---

# Frontend Data Service + Slice Skill

## Purpose

Wire a new CSV/JSON data source into the Redux store with full test coverage. Covers: TypeScript types, service, slice (via `createDataSlice` factory), selectors, custom hook, Vitest unit tests, and fixture/schema validation.

## Prerequisites

Gather context:

```
Subagent 1: "Read frontend/src/store/factories/createDataSlice.ts. Return: full contents."
Subagent 2: "Read frontend/src/store/index.ts. Return: how reducers are registered."
Subagent 3: "Read frontend/src/store/slices/selectedCitySlice.ts. Return: how data fetches are triggered on city change."
Subagent 4: "Read frontend/src/services/utils/csvUtils.ts and serviceUtils.ts. Return: utility functions."
Subagent 5: "Read schemas/ directory. Return: any existing JSON schemas for this data domain."
```

## Implementation Steps

### Step 1: Define Types

**Location**: `frontend/src/types/<Domain>.ts` or extend existing class in `frontend/src/classes/`

```typescript
export interface MyRecord {
    date: string;
    value: number;
}
export type MyRecordList = MyRecord[];
```

### Step 2: Create Data Service

**Location**: `frontend/src/services/<Domain>Service.ts`

```typescript
import { fetchAndParseCSV, parseOptionalFloat } from './utils/csvUtils.js';
import { buildUrl } from './utils/serviceUtils.js';
import type { MyRecordList } from '../types/MyDomain.js';

export const fetchMyDataForStation = async (stationId: string): Promise<MyRecordList> => {
    return fetchAndParseCSV<MyRecordList>(
        buildUrl(`/data/path/${stationId}_data.csv`, false),
        (rows, headers) => {
            if (!headers || headers[0] !== 'date') {
                throw new Error(`Unexpected header format for ${stationId}.`);
            }
            const records: MyRecordList = [];
            for (const columns of rows) {
                const dateRaw = columns[0];
                if (!dateRaw) continue;
                records.push({
                    date: dateRaw,
                    value: parseOptionalFloat(columns[1]) ?? 0,
                });
            }
            if (records.length === 0) {
                throw new Error(`No data found for ${stationId}.`);
            }
            return records;
        },
        { validateHeaders: ['date', 'value'], errorContext: `data for ${stationId}` }
    );
};
```

### Step 3: Create Redux Slice

**Location**: `frontend/src/store/slices/<domain>Slice.ts`

```typescript
import { fetchMyDataForStation } from '../../services/<Domain>Service.js';
import type { RootState } from '../index.js';
import type { MyRecordList } from '../../types/MyDomain.js';
import { createDataSlice } from '../factories/createDataSlice.js';

export interface FetchMyDataArgs { stationId: string; }

const { slice, actions, selectors } = createDataSlice<MyRecordList, FetchMyDataArgs, 'simple'>({
    name: 'myData',
    fetchFn: ({ stationId }) => fetchMyDataForStation(stationId),
    stateShape: 'simple',
    cache: { strategy: 'none' },
});

const EMPTY_DATA: MyRecordList = [];

export const fetchMyData = actions.fetch;
export const resetMyData = actions.reset;
export const selectMyData = (state: RootState): MyRecordList =>
    selectors.selectData(state) as MyRecordList ?? EMPTY_DATA;
export const selectMyDataStatus = selectors.selectStatus;
export const selectMyDataError = selectors.selectError;

export default slice.reducer;
```

### Step 4: Register in Store + Wire Triggers

**File**: `frontend/src/store/index.ts` — add reducer.
**File**: `frontend/src/store/slices/selectedCitySlice.ts` — add fetch/reset in `selectCity` thunk.

(See `data-services-integration` skill for detailed wiring.)

### Step 5: Create Custom Hook

**Location**: `frontend/src/hooks/useMyData.ts`

```typescript
import { useMemo } from 'react';
import { useAppSelector } from '../store/hooks/useAppSelector.js';
import { selectMyData, selectMyDataStatus, selectMyDataError } from '../store/slices/myDataSlice.js';
import type { MyRecordList } from '../types/MyDomain.js';

export interface MyDataState {
    data: MyRecordList;
    isLoading: boolean;
    error: string | null;
}

export function useMyData(): MyDataState {
    const data = useAppSelector(selectMyData);
    const status = useAppSelector(selectMyDataStatus);
    const error = useAppSelector(selectMyDataError);
    const isLoading = status === 'loading' || status === 'idle';
    return useMemo(() => ({ data, isLoading, error }), [data, isLoading, error]);
}
```

### Step 6: Create Test Fixture

**Location**: `frontend/src/__fixtures__/<domain>/sample.csv`

```csv
date,value
2024-01-01,5.2
2024-06-15,22.8
2024-12-31,-1.3
```

Keep fixtures small (3–10 rows), realistic, and deterministic. Document the source/seed:

**Location**: `frontend/src/__fixtures__/<domain>/README.md`

```markdown
# <Domain> Test Fixtures

- `sample.csv` — 3-row subset derived from station 00044, manually curated.
- Seed: rows selected for edge coverage (winter, summer, year-end).
```

### Step 7: Write Vitest Tests

**Location**: `frontend/src/services/__tests__/<Domain>Service.test.ts`

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { fetchMyDataForStation } from '../<Domain>Service.js';

// Mock fetch to return fixture CSV
const FIXTURE_CSV = `date,value\n2024-01-01,5.2\n2024-06-15,22.8\n2024-12-31,-1.3`;

beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
        ok: true,
        text: () => Promise.resolve(FIXTURE_CSV),
    }));
});

describe('fetchMyDataForStation', () => {
    it('parses fixture CSV into typed records', async () => {
        const records = await fetchMyDataForStation('00044');
        expect(records).toHaveLength(3);
        expect(records[0]).toEqual({ date: '2024-01-01', value: 5.2 });
    });

    it('throws on empty response', async () => {
        vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
            ok: true,
            text: () => Promise.resolve('date,value\n'),
        }));
        await expect(fetchMyDataForStation('00044')).rejects.toThrow('No data found');
    });

    it('throws on malformed headers', async () => {
        vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
            ok: true,
            text: () => Promise.resolve('wrong,headers\n1,2'),
        }));
        await expect(fetchMyDataForStation('00044')).rejects.toThrow('Unexpected header');
    });
});
```

**Location**: `frontend/src/store/slices/__tests__/<domain>Slice.test.ts`

```typescript
import { describe, it, expect } from 'vitest';
import { configureStore } from '@reduxjs/toolkit';
import myDataReducer, { selectMyData, selectMyDataStatus } from '../myDataSlice.js';

function createTestStore() {
    return configureStore({ reducer: { myData: myDataReducer } });
}

describe('myDataSlice', () => {
    it('has idle status and empty data initially', () => {
        const store = createTestStore();
        const state = store.getState() as { myData: ReturnType<typeof myDataReducer> };
        expect(selectMyDataStatus({ myData: state.myData } as any)).toBe('idle');
        expect(selectMyData({ myData: state.myData } as any)).toEqual([]);
    });
});
```

### Step 8: Schema Validation Test (optional)

If a JSON schema exists for this data domain in `schemas/`:

```typescript
import { describe, it, expect } from 'vitest';
import Ajv from 'ajv';
import schema from '../../../../schemas/<domain>.schema.json';

const ajv = new Ajv({ allErrors: true });
const validate = ajv.compile(schema);

describe('<domain> schema', () => {
    it('fixture conforms to schema', () => {
        const fixture = [
            { date: '2024-01-01', value: 5.2 },
            { date: '2024-06-15', value: 22.8 },
        ];
        expect(validate(fixture)).toBe(true);
    });
});
```

## Run Commands

```bash
# Run all tests
cd frontend && npm run test

# Run specific service test
cd frontend && npm run test -- --run src/services/__tests__/<Domain>Service

# Run with coverage
cd frontend && npm run test:coverage
```

## Failure Modes & Self-Correction

| Failure | Cause | Fix |
|---------|-------|-----|
| Import error `.js` extension | Missing `.js` in import path | Add `.js` to all relative imports |
| `createDataSlice` type error | Wrong generic params | Check `'simple' | 'keyed' | 'with-context'` and matching types |
| Fixture CSV mismatch | Header order differs from service parser | Align fixture headers with `validateHeaders` array |
| Store registration missed | Reducer not in `index.ts` | Add `myData: myDataReducer` to `configureStore` |
| Hook returns stale data | Missing selector dependency | Ensure `useMemo` deps include all selectors |

## Checklist

- [ ] Types defined in `types/` or `classes/`
- [ ] Service created with `fetchAndParseCSV` pattern
- [ ] Slice created via `createDataSlice` factory
- [ ] Reducer registered in `store/index.ts`
- [ ] Fetch wired in `selectedCitySlice.ts`
- [ ] Custom hook created in `hooks/`
- [ ] Fixture CSV committed in `__fixtures__/`
- [ ] Service unit test passes
- [ ] Slice unit test passes
- [ ] Schema validation test passes (if applicable)
- [ ] `npm run build` succeeds
```
