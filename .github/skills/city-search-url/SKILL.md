```skill
---
name: city-search-url
description: Add or extend city search, slug generation, and URL parameter handling. Use when implementing city selection via search, URL-based city routing, or slug-based deep linking.
---

# City Search / Slug / URL Param Skill

## Purpose

Wire city search, slug-based URLs, and deep linking so users can select cities via search input, share URLs with city context, and navigate directly to a city view. Covers: slug utility, search filtering, URL param sync, fixtures, and tests.

## Prerequisites

Gather context:

```
Subagent 1: "Read frontend/src/services/CityService.ts. Return: full contents, how cities are fetched/parsed."
Subagent 2: "Read frontend/src/classes/City.ts. Return: City class properties and methods."
Subagent 3: "Read frontend/src/store/slices/selectedCitySlice.ts. Return: selectCity thunk and city change flow."
Subagent 4: "Read frontend/src/App.tsx. Return: routing setup, BrowserRouter usage."
Subagent 5: "Read frontend/src/constants/map.tsx. Return: PREDEFINED_CITIES."
Subagent 6: "Read public/german_cities_p5000.csv. Return: first 10 lines (header + sample rows)."
```

## Concepts

| Term | Meaning |
|------|---------|
| **Slug** | URL-safe lowercase string derived from city name (e.g., `"Frankfurt am Main"` → `"frankfurt-am-main"`) |
| **Deep link** | URL like `/stadt/frankfurt-am-main` that resolves to a specific city on page load |
| **Search** | Text input filtering the city list by name prefix or fuzzy match |

## Implementation Steps

### Step 1: Create Slug Utility

**Location**: `frontend/src/utils/slugUtils.ts`

```typescript
/**
 * Convert a city name to a URL-safe slug.
 *
 * Rules:
 * - Lowercase
 * - Replace spaces/special chars with hyphens
 * - Normalize umlauts: ä→ae, ö→oe, ü→ue, ß→ss
 * - Collapse multiple hyphens
 * - Trim leading/trailing hyphens
 *
 * @example slugify("Frankfurt am Main") → "frankfurt-am-main"
 * @example slugify("Münster") → "muenster"
 * @example slugify("Garmisch-Partenkirchen") → "garmisch-partenkirchen"
 */
export function slugify(name: string): string {
    return name
        .toLowerCase()
        .replace(/ä/g, 'ae')
        .replace(/ö/g, 'oe')
        .replace(/ü/g, 'ue')
        .replace(/ß/g, 'ss')
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/^-+|-+$/g, '');
}

/**
 * Find a city by slug from a list.
 */
export function findCityBySlug(cities: Array<{ name: string; id: string }>, slug: string) {
    return cities.find(c => slugify(c.name) === slug) ?? null;
}
```

### Step 2: Write Slug Tests

**Location**: `frontend/src/utils/slugUtils.test.ts`

```typescript
import { describe, it, expect } from 'vitest';
import { slugify, findCityBySlug } from './slugUtils.js';

describe('slugify', () => {
    it.each([
        ['Berlin', 'berlin'],
        ['Frankfurt am Main', 'frankfurt-am-main'],
        ['München', 'muenchen'],
        ['Münster', 'muenster'],
        ['Garmisch-Partenkirchen', 'garmisch-partenkirchen'],
        ['Freiburg im Breisgau', 'freiburg-im-breisgau'],
        ['  Bad Homburg  ', 'bad-homburg'],
        ['Königs Wusterhausen', 'koenigs-wusterhausen'],
        ['Straße der Einheit', 'strasse-der-einheit'],
    ])('slugify(%j) → %j', (input, expected) => {
        expect(slugify(input)).toBe(expected);
    });
});

describe('findCityBySlug', () => {
    const cities = [
        { name: 'Berlin', id: '1' },
        { name: 'München', id: '2' },
        { name: 'Frankfurt am Main', id: '3' },
    ];

    it('finds city by slug', () => {
        expect(findCityBySlug(cities, 'muenchen')?.id).toBe('2');
    });

    it('returns null for unknown slug', () => {
        expect(findCityBySlug(cities, 'unknown')).toBeNull();
    });
});
```

### Step 3: Create Search Filter

**Location**: `frontend/src/utils/citySearchUtils.ts`

```typescript
import type { City } from '../classes/City.js';

/**
 * Filter cities by search query (case-insensitive prefix match).
 * Returns top `limit` results sorted by population (if available) or name.
 */
export function filterCities(
    cities: City[],
    query: string,
    limit: number = 10,
): City[] {
    if (!query || query.length < 2) return [];

    const normalized = query.toLowerCase().trim();

    return cities
        .filter(c => c.name.toLowerCase().startsWith(normalized))
        .slice(0, limit);
}
```

### Step 4: URL Parameter Sync Hook

**Location**: `frontend/src/hooks/useCityUrlParam.ts`

```typescript
import { useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useAppDispatch } from '../store/hooks/useAppDispatch.js';
import { useAppSelector } from '../store/hooks/useAppSelector.js';
import { selectSelectedCityName } from '../store/selectors/selectedItemSelectors.js';
import { slugify, findCityBySlug } from '../utils/slugUtils.js';

/**
 * Sync selected city with URL search param `?stadt=<slug>`.
 *
 * On mount: if `?stadt=` param exists, resolve slug to city and select it.
 * On city change: update URL param to reflect current city slug.
 */
export function useCityUrlParam(cities: Array<{ name: string; id: string }>) {
    const [searchParams, setSearchParams] = useSearchParams();
    const dispatch = useAppDispatch();
    const selectedCityName = useAppSelector(selectSelectedCityName);

    // On mount: resolve URL slug → city
    useEffect(() => {
        const stadtParam = searchParams.get('stadt');
        if (!stadtParam || cities.length === 0) return;

        const city = findCityBySlug(cities, stadtParam);
        if (city) {
            // dispatch selectCity thunk with city.id
            // (import from selectedCitySlice)
        }
    }, [cities]); // eslint-disable-line react-hooks/exhaustive-deps

    // On city change: update URL
    useEffect(() => {
        if (!selectedCityName) return;
        const slug = slugify(selectedCityName);
        const current = searchParams.get('stadt');
        if (current !== slug) {
            setSearchParams(prev => {
                prev.set('stadt', slug);
                return prev;
            }, { replace: true });
        }
    }, [selectedCityName]); // eslint-disable-line react-hooks/exhaustive-deps
}
```

### Step 5: Create City Search Fixture

**Location**: `frontend/src/__fixtures__/cities/sample_cities.csv`

```csv
name,lat,lon,population
Berlin,52.52,13.405,3644826
München,48.1351,11.582,1471508
Frankfurt am Main,50.1109,8.6821,753056
Freiburg im Breisgau,47.999,7.842,230241
Garmisch-Partenkirchen,47.4919,11.0947,26178
```

### Step 6: Write Integration Tests

**Location**: `frontend/src/hooks/__tests__/useCityUrlParam.test.ts`

```typescript
import { describe, it, expect, vi } from 'vitest';
import { renderHook } from '@testing-library/react';
// Test slug resolution and URL updates
// (Requires react-router MemoryRouter wrapper in test utils)

describe('useCityUrlParam', () => {
    it('resolves slug from URL param to city', () => {
        // Setup: render with ?stadt=muenchen
        // Assert: dispatch called with München city id
    });

    it('updates URL when city changes', () => {
        // Setup: select Berlin
        // Assert: URL contains ?stadt=berlin
    });

    it('ignores unknown slugs', () => {
        // Setup: render with ?stadt=unknown
        // Assert: no dispatch called
    });
});
```

## Routing Setup

If using path-based routes (e.g., `/stadt/:slug`):

```typescript
// In App.tsx or router config
import { Route, Routes } from 'react-router-dom';

<Routes>
    <Route path="/" element={<MainView />} />
    <Route path="/stadt/:slug" element={<MainView />} />
    <Route path="/impressum" element={<ImpressumPage />} />
</Routes>
```

Then use `useParams()` instead of `useSearchParams()` in the hook.

## Run Commands

```bash
cd frontend && npm run test -- --run src/utils/slugUtils
cd frontend && npm run test -- --run src/utils/citySearchUtils
cd frontend && npm run build
```

## Failure Modes & Self-Correction

| Failure | Cause | Fix |
|---------|-------|-----|
| Umlaut slug collision | `ö` not normalized | Check `slugify` replaces all German-specific chars |
| URL param loop | Setting param triggers re-render which re-sets | Use `replace: true` and guard against same-value |
| City not found from slug | City list not loaded yet | Guard on `cities.length === 0` |
| Route not matching | Missing `<Route>` for `/stadt/:slug` | Add route to App.tsx |
| Search returns wrong results | Case sensitivity issue | Normalize both query and city names to lowercase |

## Checklist

- [ ] `slugify()` handles all German umlauts + ß
- [ ] `findCityBySlug()` resolves slug → city
- [ ] `filterCities()` filters by prefix with limit
- [ ] URL param hook syncs bidirectionally
- [ ] Slug tests cover edge cases (umlauts, hyphens, spaces)
- [ ] City fixture CSV committed
- [ ] `npm run test` passes
- [ ] `npm run build` succeeds
```
