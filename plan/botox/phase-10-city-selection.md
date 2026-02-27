---
goal: Phase 10 - City Search and Selection with URL Integration
version: 1.0
date_created: 2026-02-16
last_updated: 2026-02-16
owner: Sebastian
status: 'Planned'
tags: [phase-10, frontend, search, city-selection, url, routing]
---

# Introduction

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

This phase implements the city search and selection functionality that connects all visualization components. It builds on the existing `StationSearch` component pattern, adds URL-based city parameter support for shareable links, creates the Python script to correlate cities with ERA5-Land grid cells, and ensures all components (map, metrics, narrative plots) respond to city selection changes.

**Key deliverables:**
- `CitySearch` autocomplete component (extending existing pattern)
- URL-based city selection via query parameter (`?city=berlin`)
- Deep-linking support for social sharing
- Python script to correlate GeoNames cities with ERA5-Land grid cells
- Enhanced `citySlice` with grid correlation data
- Integration testing for end-to-end city selection flow

## 0. Preflight & Self-Correction

> **Mandatory gate**: Before starting any task in this phase and after every change, run the preflight script and follow the self-correction loop.

1. **Run preflight**: `./scripts/run-preflight.sh` — all checks must pass before starting work
2. **After each change**: re-run preflight or the targeted test subset (see `docs/self-correct-playbook.md`)
3. **On failure**: follow retry guidance in the playbook (max 3 attempts per issue, then revert and re-analyze)
4. **Local CI parity**: optionally run `./scripts/act-local.sh build` to verify GHA workflows locally (requires Docker + act)

## 0.1 Regular Commits

Commit after each logical unit of work to maintain a clear and reviewable change history. Avoid accumulating large batches of uncommitted changes — they make it harder to understand what belongs to what, harder to review PRs, and harder to revert individual changes if something goes wrong.

**Guidelines:**
- Commit after completing each task group or implementation sub-section
- Use [Conventional Commits](https://www.conventionalcommits.org/) format: `feat(phase-X):`, `fix(phase-X):`, `chore(phase-X):`, `test(phase-X):`, etc.
- Each commit should pass the preflight checks (see § 0 above)
- Keep PRs focused — one logical concern per PR makes reviews faster and safer

## 1. Requirements & Constraints

### Functional Requirements (from Master Plan)
- **REQ-004**: Support city selection with tile-based metrics (cities map to grid tiles; multiple cities can share one tile's data)
- **REQ-009**: Provide responsive design for mobile and desktop

### Phase-Specific Requirements
- **REQ-P10-001**: City search must return results within 100ms for any query
- **REQ-P10-002**: URL parameter `?city=<slug>` must select correct city on page load
- **REQ-P10-003**: City selection must update URL for shareable links
- **REQ-P10-004**: Search results sorted by relevance (exact match > prefix > contains)
- **REQ-P10-005**: Mobile search must work with on-screen keyboard
- **REQ-P10-006**: Fallback to national metrics when city not found
- **REQ-P10-007**: All components (map, metrics, plots) must respond to city selection

### Technical Constraints
- **CON-P10-001**: Must use existing GeoNames city list (2,949 cities)
- **CON-P10-002**: City slugs must be URL-safe (lowercase, no special chars)
- **CON-P10-003**: Grid correlation data generated offline (Python script)
- **CON-P10-004**: Must not break existing station-based city selection

### Patterns to Follow
- **PAT-P10-001**: Follow existing StationSearch component structure
- **PAT-P10-002**: Use React Router for URL parameter handling
- **PAT-P10-003**: Use Redux for centralized city selection state
- **PAT-P10-004**: Use kebab-case for URL slugs (e.g., `bad-wuennenberg`)

## 2. Implementation Steps

### Implementation Phase 10.1: City Slug Generation

- GOAL-P10-001: Create utility for converting city names to URL-safe slugs

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P10-001 | Create `frontend/src/utils/citySlugUtils.ts` with slug generation | | |
| TASK-P10-002 | Implement `cityNameToSlug(name)` - handle umlauts, spaces, special chars | | |
| TASK-P10-003 | Implement `slugToCityName(slug)` - reverse mapping (best effort) | | |
| TASK-P10-004 | Create slug lookup map for exact city matching | | |
| TASK-P10-005 | Write unit tests for slug utilities | | |

**Completion Criteria:**
- "München" → "muenchen"
- "Bad Wünnenberg" → "bad-wuennenberg"
- Reverse lookup finds original city

---

### Implementation Phase 10.2: URL Parameter Integration

- GOAL-P10-002: Add URL parameter support for city selection

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P10-006 | Create `frontend/src/hooks/useCityUrlParam.ts` hook | | |
| TASK-P10-007 | Read `city` query parameter on initial page load | | |
| TASK-P10-008 | Update URL when city selection changes (without page reload) | | |
| TASK-P10-009 | Handle invalid/unknown city parameters gracefully | | |
| TASK-P10-010 | Sync URL parameter with Redux selectedCity state | | |
| TASK-P10-011 | Write tests for URL parameter handling | | |

**Completion Criteria:**
- `?city=berlin` selects Berlin on page load
- City selection updates URL to `?city=<slug>`
- Invalid slug shows national data with console warning

---

### Implementation Phase 10.3: CitySearch Component

- GOAL-P10-003: Create enhanced city search autocomplete

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P10-012 | Create `frontend/src/components/search/CitySearch.tsx` | | |
| TASK-P10-013 | Implement search input with debounced filtering | | |
| TASK-P10-014 | Implement dropdown with filtered/sorted results | | |
| TASK-P10-015 | Implement keyboard navigation (arrow keys, enter, escape) | | |
| TASK-P10-016 | Implement click-outside-to-close behavior | | |
| TASK-P10-017 | Add clear button to reset search | | |
| TASK-P10-018 | Add mobile-friendly styling and touch support | | |
| TASK-P10-019 | Write component tests for CitySearch | | |

**Completion Criteria:**
- Search filters as user types
- Results limited to 15 items
- Keyboard navigation works
- Touch/click selection works

---

### Implementation Phase 10.4: Search Result Scoring

- GOAL-P10-004: Implement relevance-based search result sorting

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P10-020 | Create `frontend/src/utils/citySearchUtils.ts` | | |
| TASK-P10-021 | Implement scoring: exact match (100), prefix (80), contains (60) | | |
| TASK-P10-022 | Add bonus for shorter names (prefer "Berlin" over "Berlin-Mitte") | | |
| TASK-P10-023 | Add length penalty to avoid generic substring matches | | |
| TASK-P10-024 | Implement case-insensitive matching | | |
| TASK-P10-025 | Write tests for search scoring | | |

**Completion Criteria:**
- "berlin" search shows "Berlin" first
- "bad" shows "Bad Aibling" before "Fischbachau" (contains "bad")
- Short city names ranked higher

---

### Implementation Phase 10.5: Python Grid Correlation Script

- GOAL-P10-005: Create script to map cities to nearest ERA5-Land grid cells

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P10-026 | Create `analysis/cities/correlate_cities_to_grid.py` (accept `ClimateDataProvider`) | | |
| TASK-P10-027 | Load Germany city list from `german_cities_p5000.csv` | | |
| TASK-P10-028 | Obtain grid resolution & bounds from provider (no hardcoded constants) | | |
| TASK-P10-029 | Calculate nearest grid cell for each city | | |
| TASK-P10-030 | Output correlation data as JSON (`city_grid_correlation.json`) | | |
| TASK-P10-031 | Include city slug in output for URL matching | | |
| TASK-P10-032 | Write pytest tests for correlation script | | |

**Completion Criteria:**
- All 2,949 cities mapped to grid cells
- Output includes: city_name, slug, lat, lon, grid_i, grid_j
- Script runs in < 10 seconds

---

### Implementation Phase 10.6: City Data Enhancement

- GOAL-P10-006: Enhance city data with grid correlation

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P10-033 | Update `frontend/src/types/city.ts` with grid correlation fields | | |
| TASK-P10-034 | Create/update `frontend/src/services/CityCorrelationService.ts` | | |
| TASK-P10-035 | Load correlation JSON on app init | | |
| TASK-P10-036 | Merge correlation data with existing city data | | |
| TASK-P10-037 | Create derived selectors for grid-correlated city lookup | | |
| TASK-P10-038 | Write tests for city data enhancement | | |

**Completion Criteria:**
- City objects include grid_i, grid_j, slug
- Selectors return cities by slug
- Correlation data loads without blocking UI

---

### Implementation Phase 10.7: City Selection Redux Updates

- GOAL-P10-007: Update Redux state to support slug-based selection

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P10-039 | Create `frontend/src/store/slices/citySlice.ts` - new city selection state for ERA5-Land feature (do NOT modify existing `selectedCitySlice.ts`) | | |
| TASK-P10-040 | Add `selectCityBySlug(slug)` action | | |
| TASK-P10-041 | Add `selectCitySelector` by slug | | |
| TASK-P10-042 | Ensure backward compatibility with ID-based selection | | |
| TASK-P10-043 | Add analytics-friendly city name to state | | |
| TASK-P10-044 | Write tests for updated slice | | |

**Completion Criteria:**
- `selectCityBySlug('berlin')` works
- Existing `selectCity(id)` still works
- State includes both ID and slug

---

### Implementation Phase 10.8: Component Integration

- GOAL-P10-008: Connect city selection to all visualization components

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P10-045 | Update ClimateMap to respond to city selection (zoom/pan to city) | | |
| TASK-P10-046 | Verify MetricsRow loads correct city metrics | | |
| TASK-P10-047 | Verify NarrativeSection loads correct city plot data | | |
| TASK-P10-048 | Add global loading indicator during city data fetch | | |
| TASK-P10-049 | Handle city selection error states | | |
| TASK-P10-050 | Write integration tests for full selection flow | | |

**Completion Criteria:**
- City selection updates all components
- Loading states shown during transition
- Error states handled gracefully

---

### Implementation Phase 10.9: Deep Linking & Share

- GOAL-P10-009: Implement share functionality and OG tags

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P10-051 | Create `frontend/src/components/common/ShareButton.tsx` | | |
| TASK-P10-052 | Implement copy-to-clipboard for current URL | | |
| TASK-P10-053 | Add social share links (Twitter, Facebook, WhatsApp) | | |
| TASK-P10-054 | Update document title based on selected city | | |
| TASK-P10-055 | Ensure proper Open Graph meta tags for shared links | | |
| TASK-P10-056 | Write tests for share functionality | | |

**Completion Criteria:**
- Share button copies URL with city parameter
- Social links open with correct URL
- Page title includes city name

---

### Implementation Phase 10.10: Polish & E2E Tests

- GOAL-P10-010: Finalize and test end-to-end flows

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P10-057 | Create E2E test: Load page with city URL → all components show city data | | |
| TASK-P10-058 | Create E2E test: Search city → select → URL updates → components update | | |
| TASK-P10-059 | Create E2E test: Invalid city URL → fallback to national | | |
| TASK-P10-060 | Performance test: Search responsiveness under 100ms | | |
| TASK-P10-061 | Accessibility audit for search component | | |
| TASK-P10-062 | Create barrel export for search components | | |

**Completion Criteria:**
- All E2E tests pass
- Search feels instant
- WCAG 2.1 AA compliance

## 3. Alternatives

- **ALT-P10-001**: **Path-based routing (`/city/berlin`) vs. query param (`?city=berlin`)** - Considered path-based for cleaner URLs. Chose query params to avoid React Router configuration complexity and allow multiple params (e.g., `?city=berlin&month=2025-01`).

- **ALT-P10-002**: **Fuzzy search (Fuse.js) vs. simple substring** - Considered fuzzy search for typo tolerance. Rejected because German city names have strict spellings; simple substring with scoring provides good UX without complexity.

- **ALT-P10-003**: **Local city search vs. API endpoint** - Considered server-side search for larger datasets. Rejected because 2,949 cities fits easily in memory; client-side search is faster and works offline.

- **ALT-P10-004**: **Store grid cell in URL vs. city slug** - Considered storing exact grid coordinates. Rejected because slugs are human-readable and shareable.

## 4. Dependencies

### External Dependencies
- **DEP-P10-001**: `react-router-dom` - Already installed, URL parameter handling
- **DEP-P10-002**: GeoNames city data - Already present (`german_cities_p5000.csv`)

### Internal Dependencies
- **DEP-P10-003**: `citySlice` - NEW file; `selectedCitySlice.ts` remains unchanged for backward compatibility
- **DEP-P10-004**: `cityDataSlice` - Existing, will merge correlation data
- **DEP-P10-005**: `ClimateMap` (Phase 7) - Will respond to city selection
- **DEP-P10-006**: `MetricsRow` (Phase 8) - Will respond to city selection
- **DEP-P10-007**: `NarrativeSection` (Phase 9) - Will respond to city selection

### Phase Dependencies
- **DEP-P10-008**: Phase 1 (Testing Infrastructure) - Vitest configured
- **DEP-P10-009**: Phase 5 (Metrics) - Grid correlation JSON must exist
- **DEP-P10-010**: Can develop with mock correlation data before Phase 5

## 5. Files

### New Files (Frontend)
- **FILE-P10-001**: `frontend/src/components/search/CitySearch.tsx` - NEW
- **FILE-P10-002**: `frontend/src/components/common/ShareButton.tsx` - NEW
- **FILE-P10-003**: `frontend/src/hooks/useCityUrlParam.ts` - NEW
- **FILE-P10-004**: `frontend/src/utils/citySlugUtils.ts` - NEW
- **FILE-P10-005**: `frontend/src/utils/citySearchUtils.ts` - NEW
- **FILE-P10-006**: `frontend/src/services/CityCorrelationService.ts` - NEW
- **FILE-P10-007**: `frontend/src/types/cityCorrelation.ts` - NEW

### New Files (Python)
- **FILE-P10-008**: `analysis/cities/correlate_cities_to_grid.py` - NEW
- **FILE-P10-009**: `analysis/cities/tests/test_correlate_cities.py` - NEW
- **FILE-P10-010**: `data/cities/city_grid_correlation.json` - NEW (generated)

### Modified Files
- **FILE-P10-011**: `frontend/src/store/slices/citySlice.ts` - NEW - ERA5-Land city selection state
- **FILE-P10-012**: `frontend/src/store/slices/cityDataSlice.ts` - MODIFY
- **FILE-P10-013**: `frontend/src/classes/City.ts` - MODIFY (add slug, grid fields)
- **FILE-P10-014**: `frontend/src/App.tsx` - MODIFY (add URL param handling)

### Test Files
- **FILE-P10-015**: `frontend/src/components/search/__tests__/CitySearch.test.tsx` - NEW
- **FILE-P10-016**: `frontend/src/hooks/__tests__/useCityUrlParam.test.ts` - NEW
- **FILE-P10-017**: `frontend/src/utils/__tests__/citySlugUtils.test.ts` - NEW
- **FILE-P10-018**: `frontend/src/utils/__tests__/citySearchUtils.test.ts` - NEW

## 6. Testing

### Unit Tests
- **TEST-P10-001**: citySlugUtils generates correct slugs for German city names
- **TEST-P10-002**: citySlugUtils handles umlauts (ä→ae, ö→oe, ü→ue, ß→ss)
- **TEST-P10-003**: citySearchUtils scores exact matches highest
- **TEST-P10-004**: citySearchUtils returns sorted results
- **TEST-P10-005**: CitySearch filters results as user types
- **TEST-P10-006**: useCityUrlParam reads URL parameter on mount
- **TEST-P10-007**: useCityUrlParam updates URL on city change

### Integration Tests
- **TEST-P10-008**: CitySearch selection dispatches selectCityBySlug action
- **TEST-P10-009**: URL parameter triggers city selection on app load
- **TEST-P10-010**: City selection updates all visualization components
- **TEST-P10-011**: Invalid city slug falls back to national

### E2E Tests
- **TEST-P10-012**: User navigates to `?city=muenchen`, sees Munich data
- **TEST-P10-013**: User searches "Ham", selects Hamburg, URL updates
- **TEST-P10-014**: User shares URL, recipient sees same city selected
- **TEST-P10-015**: User clears search, returns to national view

### Mock Data Requirements
- **MOCK-P10-001**: Mock city list with 50 cities including edge cases
- **MOCK-P10-002**: Mock correlation JSON for test cities
- **MOCK-P10-003**: Mock URL search params

## 7. Risks & Assumptions

### Risks
- **RISK-P10-001**: City name collisions (multiple cities with same name)
  - **Mitigation**: Use unique slug with state/region suffix if needed; prioritize by population

- **RISK-P10-002**: URL encoding issues with special characters
  - **Mitigation**: Use encodeURIComponent; test with all German special chars

- **RISK-P10-003**: Search performance with large result sets
  - **Mitigation**: Limit to 15 results; use debounced input (300ms)

- **RISK-P10-004**: Grid correlation mismatch with ERA5-Land updates
  - **Mitigation**: Regenerate correlation JSON when ERA5-Land grid changes; version the file

### Assumptions
- **ASSUMPTION-P10-001**: 2,949 cities sufficient for all user needs
- **ASSUMPTION-P10-002**: City names unique enough for slug generation
- **ASSUMPTION-P10-003**: Users expect city name (not coordinates) in URL
- **ASSUMPTION-P10-004**: Browser URL update without reload works in all targets

## 8. Multi-Agent Execution Notes

### Execution Order
**Parallel tasks (can run simultaneously):**
- Phase 10.1 (Slug Utils)
- Phase 10.4 (Search Scoring)
- Phase 10.5 (Python Script)

**Sequential dependencies:**
- Phase 10.2 (URL Params) depends on Phase 10.1 (Slugs)
- Phase 10.3 (CitySearch) depends on Phase 10.1 and Phase 10.4
- Phase 10.6 (Data Enhancement) depends on Phase 10.5 (Script output)
- Phase 10.7 (Redux Updates) depends on Phase 10.1 and Phase 10.6
- Phase 10.8 (Integration) requires Phases 7, 8, 9 and all Phase 10.1-10.7
- Phase 10.9-10.10 (Polish) requires all previous

### Agent Context Requirements
Provide these files for agent execution:
- This plan document
- `frontend/src/components/header/StationSearch.tsx` (existing search pattern)
- `frontend/src/store/slices/selectedCitySlice.ts` (existing selection state)
- `frontend/src/classes/City.ts` (existing city class)
- `frontend/public/german_cities_p5000.csv` (city data)

### Validation Checkpoints
- **After Phase 10.1**: Slug tests pass; roundtrip works for all sample cities
- **After Phase 10.3**: CitySearch renders and filters correctly
- **After Phase 10.5**: Python script generates valid JSON
- **After Phase 10.7**: Redux state updates correctly on slug selection
- **After Phase 10.10**: All E2E tests pass

## 9. Related Specifications / Further Reading

- [Existing StationSearch](../../frontend/src/components/header/StationSearch.tsx)
- [React Router Documentation](https://reactrouter.com/en/main)
- [GeoNames Data](http://www.geonames.org/)
- [Master Plan - City Selection](../botox/era5-germany-climate-visualization-1.md#implementation-phase-9)

## 10. Code Reference (REQUIRED)

### 10.1 City Slug Utilities

**File**: `frontend/src/utils/citySlugUtils.ts`

```typescript
/**
 * City Slug Utilities
 * 
 * Convert city names to URL-safe slugs and back.
 */

/**
 * German character replacements for URL slugs
 */
const GERMAN_CHAR_MAP: Record<string, string> = {
    'ä': 'ae',
    'ö': 'oe',
    'ü': 'ue',
    'ß': 'ss',
    'Ä': 'ae',
    'Ö': 'oe',
    'Ü': 'ue',
};

/**
 * Convert a city name to a URL-safe slug
 * 
 * @example
 * cityNameToSlug('München') // 'muenchen'
 * cityNameToSlug('Bad Wünnenberg') // 'bad-wuennenberg'
 * cityNameToSlug('Brake (Unterweser)') // 'brake-unterweser'
 */
export const cityNameToSlug = (name: string): string => {
    return name
        .toLowerCase()
        .trim()
        // Replace German characters
        .replace(/[äöüßÄÖÜ]/g, char => GERMAN_CHAR_MAP[char] || char)
        // Remove parentheses but keep content
        .replace(/[()]/g, '')
        // Replace spaces and multiple hyphens with single hyphen
        .replace(/\s+/g, '-')
        .replace(/-+/g, '-')
        // Remove other special characters
        .replace(/[^a-z0-9-]/g, '')
        // Remove leading/trailing hyphens
        .replace(/^-+|-+$/g, '');
};

/**
 * Normalize a slug (ensure consistent format)
 */
export const normalizeSlug = (slug: string): string => {
    return slug
        .toLowerCase()
        .trim()
        .replace(/\s+/g, '-')
        .replace(/-+/g, '-')
        .replace(/^-+|-+$/g, '');
};

/**
 * Check if a string is a valid slug format
 */
export const isValidSlug = (slug: string): boolean => {
    return /^[a-z0-9]+(-[a-z0-9]+)*$/.test(slug);
};

/**
 * Type for the city slug index
 */
export type CitySlugIndex = Map<string, { id: string; name: string }>;

/**
 * Build an index of slugs to city data for fast lookup
 */
export const buildCitySlugIndex = (
    cities: Array<{ id: string; name: string }>
): CitySlugIndex => {
    const index: CitySlugIndex = new Map();
    
    for (const city of cities) {
        const slug = cityNameToSlug(city.name);
        // Handle collisions by preferring first occurrence
        if (!index.has(slug)) {
            index.set(slug, { id: city.id, name: city.name });
        }
    }
    
    return index;
};

/**
 * Find a city by its slug
 */
export const findCityBySlug = (
    slug: string,
    index: CitySlugIndex
): { id: string; name: string } | undefined => {
    const normalized = normalizeSlug(slug);
    return index.get(normalized);
};
```

### 10.2 City Search Utilities

**File**: `frontend/src/utils/citySearchUtils.ts`

```typescript
/**
 * City Search Utilities
 * 
 * Scoring and filtering functions for city search.
 */

import type { ICity } from '../classes/City';

interface ScoredCity {
    city: ICity;
    score: number;
}

/**
 * Score a city against a search query
 * Higher score = better match
 */
export const scoreCityMatch = (city: ICity, query: string): number => {
    const nameLower = city.name.toLowerCase();
    const queryLower = query.toLowerCase().trim();
    
    if (!queryLower) return 0;
    
    // Exact match (case-insensitive)
    if (nameLower === queryLower) {
        return 100;
    }
    
    // Starts with query
    if (nameLower.startsWith(queryLower)) {
        // Shorter names get bonus (prefer "Berlin" over "Berlin-Mitte")
        const lengthBonus = Math.max(0, 10 - (city.name.length - query.length));
        return 80 + lengthBonus;
    }
    
    // Contains query (not at start)
    if (nameLower.includes(queryLower)) {
        // Penalize if match is deep in the string
        const position = nameLower.indexOf(queryLower);
        const positionPenalty = Math.min(position * 2, 20);
        return 60 - positionPenalty;
    }
    
    // No match
    return 0;
};

/**
 * Filter and sort cities by search query
 */
export const searchCities = (
    cities: ICity[] | Record<string, ICity>,
    query: string,
    limit: number = 15
): ICity[] => {
    const cityArray = Array.isArray(cities) ? cities : Object.values(cities);
    const trimmedQuery = query.trim();
    
    if (!trimmedQuery) {
        return [];
    }
    
    const scored: ScoredCity[] = cityArray
        .map(city => ({
            city,
            score: scoreCityMatch(city, trimmedQuery),
        }))
        .filter(item => item.score > 0);
    
    // Sort by score descending, then by name length ascending
    scored.sort((a, b) => {
        if (b.score !== a.score) {
            return b.score - a.score;
        }
        return a.city.name.length - b.city.name.length;
    });
    
    return scored.slice(0, limit).map(item => item.city);
};

/**
 * Highlight matching portion of city name
 */
export const highlightMatch = (
    cityName: string,
    query: string
): { before: string; match: string; after: string } | null => {
    const nameLower = cityName.toLowerCase();
    const queryLower = query.toLowerCase().trim();
    
    const index = nameLower.indexOf(queryLower);
    if (index === -1) {
        return null;
    }
    
    return {
        before: cityName.slice(0, index),
        match: cityName.slice(index, index + query.length),
        after: cityName.slice(index + query.length),
    };
};
```

### 10.3 useCityUrlParam Hook

**File**: `frontend/src/hooks/useCityUrlParam.ts`

```typescript
/**
 * useCityUrlParam Hook
 * 
 * Syncs city selection with URL query parameter.
 */

import { useEffect, useCallback, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useAppDispatch } from '../store/hooks/useAppDispatch';
import { useAppSelector } from '../store/hooks/useAppSelector';
import { selectCityBySlug, selectCurrentCitySlug } from '../store/slices/citySlice';
import { selectCitySlugIndex } from '../store/slices/cityDataSlice';
import { findCityBySlug } from '../utils/citySlugUtils';

const CITY_PARAM = 'city';

export interface UseCityUrlParamReturn {
    /** Current city slug from URL or state */
    citySlug: string | null;
    /** Update URL with new city */
    setCityUrl: (slug: string | null) => void;
    /** Whether URL has been synced with state */
    isSynced: boolean;
}

export function useCityUrlParam(): UseCityUrlParamReturn {
    const dispatch = useAppDispatch();
    const [searchParams, setSearchParams] = useSearchParams();
    const citySlugIndex = useAppSelector(selectCitySlugIndex);
    const currentCitySlug = useAppSelector(selectCurrentCitySlug);
    const hasSyncedRef = useRef(false);

    const urlCitySlug = searchParams.get(CITY_PARAM);

    // On mount: sync URL param to Redux state
    useEffect(() => {
        if (hasSyncedRef.current) return;
        if (!citySlugIndex || citySlugIndex.size === 0) return;

        if (urlCitySlug) {
            const city = findCityBySlug(urlCitySlug, citySlugIndex);
            if (city) {
                dispatch(selectCityBySlug(urlCitySlug));
            } else {
                console.warn(`City not found for slug: ${urlCitySlug}`);
                // Remove invalid param from URL
                setSearchParams(params => {
                    params.delete(CITY_PARAM);
                    return params;
                }, { replace: true });
            }
        }

        hasSyncedRef.current = true;
    }, [urlCitySlug, citySlugIndex, dispatch, setSearchParams]);

    // When Redux state changes: update URL
    useEffect(() => {
        if (!hasSyncedRef.current) return;

        const currentUrlSlug = searchParams.get(CITY_PARAM);
        
        if (currentCitySlug && currentCitySlug !== currentUrlSlug) {
            setSearchParams(params => {
                params.set(CITY_PARAM, currentCitySlug);
                return params;
            }, { replace: true });
        } else if (!currentCitySlug && currentUrlSlug) {
            setSearchParams(params => {
                params.delete(CITY_PARAM);
                return params;
            }, { replace: true });
        }
    }, [currentCitySlug, searchParams, setSearchParams]);

    const setCityUrl = useCallback((slug: string | null) => {
        if (slug) {
            dispatch(selectCityBySlug(slug));
        } else {
            // Clear selection - handled by selectCityBySlug with null
            dispatch(selectCityBySlug(''));
        }
    }, [dispatch]);

    return {
        citySlug: currentCitySlug || urlCitySlug,
        setCityUrl,
        isSynced: hasSyncedRef.current,
    };
}
```

### 10.4 CitySearch Component

**File**: `frontend/src/components/search/CitySearch.tsx`

```typescript
/**
 * CitySearch Component
 * 
 * Autocomplete search for German cities.
 */

import { useState, useRef, useEffect, useCallback, useMemo, memo } from 'react';
import type { CSSProperties, ChangeEvent, KeyboardEvent } from 'react';
import { FaSearch, FaTimes } from 'react-icons/fa';
import { useAppDispatch } from '../../store/hooks/useAppDispatch';
import { useAppSelector } from '../../store/hooks/useAppSelector';
import { selectCities } from '../../store/slices/cityDataSlice';
import { selectCityBySlug, selectSelectedCityName } from '../../store/slices/citySlice';
import { searchCities, highlightMatch } from '../../utils/citySearchUtils';
import { cityNameToSlug } from '../../utils/citySlugUtils';
import { theme, createStyles } from '../../styles/design-system';
import { useBreakpointDown } from '../../hooks/useBreakpoint';
import type { ICity } from '../../classes/City';

const styles = createStyles({
    container: {
        position: 'relative',
        width: '100%',
        maxWidth: 350,
    },
    inputWrapper: {
        position: 'relative',
        display: 'flex',
        alignItems: 'center',
    },
    input: {
        width: '100%',
        padding: '10px 35px 10px 40px',
        fontSize: theme.typography.fontSize.md,
        border: `1px solid ${theme.colors.border}`,
        borderRadius: theme.borderRadius?.md ?? '8px',
        backgroundColor: 'white',
        outline: 'none',
    },
    inputFocused: {
        borderColor: theme.colors.primary,
        boxShadow: `0 0 0 2px ${theme.colors.primary}22`,
    },
    searchIcon: {
        position: 'absolute',
        left: 12,
        color: theme.colors.textLight,
        pointerEvents: 'none',
    },
    clearButton: {
        position: 'absolute',
        right: 10,
        background: 'none',
        border: 'none',
        color: theme.colors.textLight,
        cursor: 'pointer',
        padding: 4,
        display: 'flex',
        alignItems: 'center',
    },
    dropdown: {
        position: 'absolute',
        top: '100%',
        left: 0,
        right: 0,
        marginTop: 4,
        backgroundColor: 'white',
        border: `1px solid ${theme.colors.border}`,
        borderRadius: theme.borderRadius?.md ?? '8px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
        maxHeight: 300,
        overflowY: 'auto',
        zIndex: 1000,
    },
    item: {
        padding: '10px 14px',
        cursor: 'pointer',
        borderBottom: `1px solid ${theme.colors.borderLight}`,
    },
    itemHighlighted: {
        backgroundColor: theme.colors.hover,
    },
    itemSelected: {
        backgroundColor: `${theme.colors.primary}11`,
    },
    matchHighlight: {
        fontWeight: theme.typography.fontWeight.bold,
        color: theme.colors.primary,
    },
    noResults: {
        padding: '10px 14px',
        color: theme.colors.textLight,
        fontStyle: 'italic',
    },
});

interface CitySearchProps {
    placeholder?: string;
    maxResults?: number;
}

const CitySearch = memo(({ 
    placeholder = 'Stadt suchen...', 
    maxResults = 15 
}: CitySearchProps) => {
    const dispatch = useAppDispatch();
    const cities = useAppSelector(selectCities);
    const selectedCityName = useAppSelector(selectSelectedCityName);
    const isMobile = useBreakpointDown('mobile');

    const [query, setQuery] = useState('');
    const [isOpen, setIsOpen] = useState(false);
    const [highlightedIndex, setHighlightedIndex] = useState(-1);
    const [isFocused, setIsFocused] = useState(false);

    const inputRef = useRef<HTMLInputElement>(null);
    const containerRef = useRef<HTMLDivElement>(null);

    // Filter cities based on query
    const results = useMemo(() => 
        searchCities(cities, query, maxResults),
        [cities, query, maxResults]
    );

    // Handle outside click
    useEffect(() => {
        const handleClickOutside = (e: MouseEvent) => {
            if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
                setIsOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const handleInputChange = useCallback((e: ChangeEvent<HTMLInputElement>) => {
        setQuery(e.target.value);
        setIsOpen(true);
        setHighlightedIndex(-1);
    }, []);

    const handleSelectCity = useCallback((city: ICity) => {
        const slug = cityNameToSlug(city.name);
        dispatch(selectCityBySlug(slug));
        setQuery('');
        setIsOpen(false);
        inputRef.current?.blur();
    }, [dispatch]);

    const handleKeyDown = useCallback((e: KeyboardEvent<HTMLInputElement>) => {
        if (!isOpen || results.length === 0) return;

        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                setHighlightedIndex(i => 
                    i < results.length - 1 ? i + 1 : 0
                );
                break;
            case 'ArrowUp':
                e.preventDefault();
                setHighlightedIndex(i => 
                    i > 0 ? i - 1 : results.length - 1
                );
                break;
            case 'Enter':
                e.preventDefault();
                if (highlightedIndex >= 0) {
                    handleSelectCity(results[highlightedIndex]);
                }
                break;
            case 'Escape':
                setIsOpen(false);
                break;
        }
    }, [isOpen, results, highlightedIndex, handleSelectCity]);

    const handleClear = useCallback(() => {
        setQuery('');
        inputRef.current?.focus();
    }, []);

    const inputStyle: CSSProperties = {
        ...styles.input,
        ...(isFocused ? styles.inputFocused : {}),
        fontSize: isMobile ? 16 : undefined, // Prevent iOS zoom
    };

    return (
        <div ref={containerRef} style={styles.container}>
            <div style={styles.inputWrapper}>
                <FaSearch style={styles.searchIcon} size={14} />
                <input
                    ref={inputRef}
                    type="text"
                    value={query}
                    onChange={handleInputChange}
                    onKeyDown={handleKeyDown}
                    onFocus={() => { setIsFocused(true); setIsOpen(true); }}
                    onBlur={() => setIsFocused(false)}
                    placeholder={placeholder}
                    style={inputStyle}
                    aria-label="Stadt suchen"
                    aria-autocomplete="list"
                    aria-expanded={isOpen}
                />
                {query && (
                    <button 
                        type="button"
                        style={styles.clearButton} 
                        onClick={handleClear}
                        aria-label="Suche löschen"
                    >
                        <FaTimes size={14} />
                    </button>
                )}
            </div>

            {isOpen && query && (
                <div style={styles.dropdown} role="listbox">
                    {results.length > 0 ? (
                        results.map((city, index) => {
                            const match = highlightMatch(city.name, query);
                            const isHighlighted = index === highlightedIndex;
                            const itemStyle: CSSProperties = {
                                ...styles.item,
                                ...(isHighlighted ? styles.itemHighlighted : {}),
                            };

                            return (
                                <div
                                    key={city.id}
                                    role="option"
                                    aria-selected={isHighlighted}
                                    style={itemStyle}
                                    onClick={() => handleSelectCity(city)}
                                    onMouseEnter={() => setHighlightedIndex(index)}
                                >
                                    {match ? (
                                        <>
                                            {match.before}
                                            <span style={styles.matchHighlight}>{match.match}</span>
                                            {match.after}
                                        </>
                                    ) : (
                                        city.name
                                    )}
                                </div>
                            );
                        })
                    ) : (
                        <div style={styles.noResults}>
                            Keine Städte gefunden
                        </div>
                    )}
                </div>
            )}
        </div>
    );
});

CitySearch.displayName = 'CitySearch';

export default CitySearch;
```

### 10.5 Python Grid Correlation Script

**File**: `analysis/cities/correlate_cities_to_grid.py`

```python
#!/usr/bin/env python3
"""
Correlate cities to ERA5-Land grid cells.

This script takes the GeoNames city list and finds the nearest
ERA5-Land grid cell for each city, outputting a JSON file with
city metadata and grid indices.
"""

import json
import csv
import math
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Tuple
import unicodedata
import re

from era5.providers import get_provider
from era5.providers.protocol import ClimateDataProvider


@dataclass
class CityCorrelation:
    """City with grid correlation data."""
    name: str
    slug: str
    lat: float
    lon: float
    grid_i: int  # Column index (lon)
    grid_j: int  # Row index (lat)
    grid_lat: float  # Grid cell center lat
    grid_lon: float  # Grid cell center lon
    tile_id: str  # Format: "{grid_i}_{grid_j}" - used to fetch per-tile data


def city_name_to_slug(name: str) -> str:
    """
    Convert city name to URL-safe slug.
    
    Handles German umlauts and special characters.
    """
    # German character replacements
    replacements = {
        'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss',
        'Ä': 'ae', 'Ö': 'oe', 'Ü': 'ue',
    }
    
    # Apply German replacements
    result = name.lower()
    for char, replacement in replacements.items():
        result = result.replace(char, replacement)
    
    # Remove diacritics from remaining characters
    result = unicodedata.normalize('NFD', result)
    result = ''.join(c for c in result if not unicodedata.combining(c))
    
    # Remove parentheses but keep content
    result = result.replace('(', '').replace(')', '')
    
    # Replace spaces with hyphens
    result = re.sub(r'\s+', '-', result)
    
    # Remove non-alphanumeric except hyphens
    result = re.sub(r'[^a-z0-9-]', '', result)
    
    # Clean up multiple hyphens
    result = re.sub(r'-+', '-', result)
    result = result.strip('-')
    
    return result


def lat_lon_to_grid_indices(
    lat: float, lon: float,
    bounds: dict, resolution: float,
) -> Tuple[int, int, float, float]:
    """
    Convert lat/lon to grid indices using provider bounds & resolution.
    
    Returns (i, j, grid_lat, grid_lon) where:
    - i is the column index (longitude)
    - j is the row index (latitude)
    - grid_lat/grid_lon are the grid cell center coordinates
    """
    # Calculate grid indices
    i = int((lon - bounds['west']) / resolution)
    j = int((bounds['north'] - lat) / resolution)
    
    # Calculate grid cell center
    grid_lon = bounds['west'] + (i + 0.5) * resolution
    grid_lat = bounds['north'] - (j + 0.5) * resolution
    
    return i, j, grid_lat, grid_lon


def load_cities(csv_path: Path) -> List[dict]:
    """Load cities from CSV file."""
    cities = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                cities.append({
                    'name': row['city_name'].strip(),
                    'lat': float(row['lat']),
                    'lon': float(row['lon']),
                })
            except (ValueError, KeyError) as e:
                print(f"Skipping invalid row: {row}, error: {e}")
    return cities


def correlate_cities(
    provider: ClimateDataProvider, cities: List[dict],
) -> List[CityCorrelation]:
    """Correlate cities to grid cells using provider configuration."""
    correlations = []
    seen_slugs = set()
    bounds = provider.bounds
    resolution = provider.native_resolution_deg
    
    for city in cities:
        slug = city_name_to_slug(city['name'])
        
        # Handle duplicate slugs by appending number
        original_slug = slug
        counter = 2
        while slug in seen_slugs:
            slug = f"{original_slug}-{counter}"
            counter += 1
        seen_slugs.add(slug)
        
        i, j, grid_lat, grid_lon = lat_lon_to_grid_indices(
            city['lat'], city['lon'], bounds, resolution,
        )
        tile_id = f"{i}_{j}"  # Multiple cities can share the same tile_id
        
        correlations.append(CityCorrelation(
            name=city['name'],
            slug=slug,
            lat=city['lat'],
            lon=city['lon'],
            grid_i=i,
            grid_j=j,
            grid_lat=round(grid_lat, 4),
            grid_lon=round(grid_lon, 4),
            tile_id=tile_id,
        ))
    
    return correlations


def main():
    """Main entry point."""
    # Paths
    project_root = Path(__file__).parent.parent.parent
    cities_csv = project_root / 'frontend' / 'public' / 'german_cities_p5000.csv'
    output_json = project_root / 'data' / 'cities' / 'city_grid_correlation.json'
    
    # Ensure output directory exists
    output_json.parent.mkdir(parents=True, exist_ok=True)
    
    provider = get_provider()  # resolved from CLIMATE_DATA_PROVIDER env var
    
    print(f"Loading cities from {cities_csv}")
    cities = load_cities(cities_csv)
    print(f"Loaded {len(cities)} cities")
    
    print(f"Correlating cities to {provider.display_name} grid...")
    correlations = correlate_cities(provider, cities)
    print(f"Generated {len(correlations)} correlations")
    
    # Convert to JSON-serializable format
    output_data = {
        'meta': {
            'grid_resolution': provider.native_resolution_deg,
            'bounds': provider.bounds,
            'city_count': len(correlations),
        },
        'cities': [asdict(c) for c in correlations],
    }
    
    print(f"Writing output to {output_json}")
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print("Done!")


if __name__ == '__main__':
    main()
```

### 10.6 citySlice.ts (New File)

**File**: `frontend/src/store/slices/citySlice.ts` (new file)

> **Note**: `selectedCitySlice.ts` is kept unchanged. `citySlice.ts` is a new, separate slice for ERA5-Land city selection state, ensuring backward compatibility with any existing consumers of `selectedCitySlice`.

```typescript
/**
 * City Slice
 * 
 * ERA5-Land-specific city selection state. Separate from the pre-existing
 * selectedCitySlice.ts to avoid breaking backward compatibility.
 */

import { createSlice, createAsyncThunk, type PayloadAction } from '@reduxjs/toolkit';
import type { RootState } from '../index';
import { cityNameToSlug, findCityBySlug, type CitySlugIndex } from '../../utils/citySlugUtils';

// Add to state interface
interface SelectedCityState {
    cityId: string | null;
    citySlug: string | null;  // NEW
    cityName: string | null;  // NEW - for display
    isLoading: boolean;       // NEW
}

const initialState: SelectedCityState = {
    cityId: null,
    citySlug: null,
    cityName: null,
    isLoading: false,
};

// New async thunk for slug-based selection
export const selectCityBySlug = createAsyncThunk<
    { cityId: string; citySlug: string; cityName: string } | null,
    string,
    { state: RootState }
>(
    'selectedCity/selectBySlug',
    async (slug, { getState }) => {
        if (!slug) return null;
        
        const state = getState();
        const slugIndex = selectCitySlugIndex(state);
        
        if (!slugIndex) {
            console.warn('City slug index not available');
            return null;
        }
        
        const city = findCityBySlug(slug, slugIndex);
        
        if (!city) {
            console.warn(`City not found for slug: ${slug}`);
            return null;
        }
        
        return {
            cityId: city.id,
            citySlug: slug,
            cityName: city.name,
        };
    }
);

// Add to slice reducers
const citySlice = createSlice({
    name: 'selectedCity',
    initialState,
    reducers: {
        // Keep existing selectCity reducer
        selectCity(
            state, 
            action: PayloadAction<string, unknown, { cityName?: string }>
        ) {
            state.cityId = action.payload;
            if (action.meta?.cityName) {
                state.cityName = action.meta.cityName;
                state.citySlug = cityNameToSlug(action.meta.cityName);
            }
        },
        clearCity(state) {
            state.cityId = null;
            state.citySlug = null;
            state.cityName = null;
        },
    },
    extraReducers: (builder) => {
        builder
            .addCase(selectCityBySlug.pending, (state) => {
                state.isLoading = true;
            })
            .addCase(selectCityBySlug.fulfilled, (state, action) => {
                state.isLoading = false;
                if (action.payload) {
                    state.cityId = action.payload.cityId;
                    state.citySlug = action.payload.citySlug;
                    state.cityName = action.payload.cityName;
                } else {
                    state.cityId = null;
                    state.citySlug = null;
                    state.cityName = null;
                }
            })
            .addCase(selectCityBySlug.rejected, (state) => {
                state.isLoading = false;
            });
    },
});

// New selectors
export const selectCurrentCitySlug = (state: RootState) => state.selectedCity.citySlug;
export const selectSelectedCityName = (state: RootState) => state.selectedCity.cityName;
export const selectCityIsLoading = (state: RootState) => state.selectedCity.isLoading;

export const { selectCity, clearCity } = citySlice.actions;
export default citySlice.reducer;
```

### 10.7 ShareButton Component

**File**: `frontend/src/components/common/ShareButton.tsx`

```typescript
/**
 * ShareButton Component
 * 
 * Copy current URL to clipboard or share via social media.
 */

import { useState, useCallback, memo } from 'react';
import type { CSSProperties } from 'react';
import { FaShare, FaCopy, FaCheck, FaTwitter, FaFacebook, FaWhatsapp } from 'react-icons/fa';
import { theme } from '../../styles/design-system';

const getContainerStyle = (): CSSProperties => ({
    position: 'relative',
    display: 'inline-block',
});

const getButtonStyle = (): CSSProperties => ({
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing.xs,
    padding: `${theme.spacing.sm}px ${theme.spacing.md}px`,
    backgroundColor: theme.colors.primary,
    color: 'white',
    border: 'none',
    borderRadius: theme.borderRadius?.sm ?? '4px',
    fontSize: theme.typography.fontSize.sm,
    cursor: 'pointer',
    transition: 'background-color 0.2s',
});

const getDropdownStyle = (isOpen: boolean): CSSProperties => ({
    position: 'absolute',
    top: '100%',
    right: 0,
    marginTop: theme.spacing.xs,
    backgroundColor: 'white',
    border: `1px solid ${theme.colors.border}`,
    borderRadius: theme.borderRadius?.sm ?? '4px',
    boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
    display: isOpen ? 'block' : 'none',
    zIndex: 100,
    minWidth: 180,
});

const getItemStyle = (): CSSProperties => ({
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing.sm,
    padding: `${theme.spacing.sm}px ${theme.spacing.md}px`,
    border: 'none',
    background: 'none',
    width: '100%',
    textAlign: 'left',
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.textDark,
    cursor: 'pointer',
});

interface ShareButtonProps {
    title?: string;
    text?: string;
}

const ShareButton = memo(({ 
    title = 'Klimadaten Deutschland',
    text = 'Entdecke die Klimaveränderungen in Deutschland:'
}: ShareButtonProps) => {
    const [isOpen, setIsOpen] = useState(false);
    const [copied, setCopied] = useState(false);

    const currentUrl = typeof window !== 'undefined' ? window.location.href : '';

    const handleCopyLink = useCallback(async () => {
        try {
            await navigator.clipboard.writeText(currentUrl);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch (err) {
            console.error('Failed to copy:', err);
        }
    }, [currentUrl]);

    const handleTwitterShare = useCallback(() => {
        const url = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(currentUrl)}`;
        window.open(url, '_blank', 'width=600,height=400');
    }, [currentUrl, text]);

    const handleFacebookShare = useCallback(() => {
        const url = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(currentUrl)}`;
        window.open(url, '_blank', 'width=600,height=400');
    }, [currentUrl]);

    const handleWhatsAppShare = useCallback(() => {
        const url = `https://wa.me/?text=${encodeURIComponent(`${text} ${currentUrl}`)}`;
        window.open(url, '_blank');
    }, [currentUrl, text]);

    return (
        <div style={getContainerStyle()}>
            <button
                type="button"
                style={getButtonStyle()}
                onClick={() => setIsOpen(!isOpen)}
                aria-label="Teilen"
            >
                <FaShare size={14} />
                Teilen
            </button>

            <div style={getDropdownStyle(isOpen)}>
                <button type="button" style={getItemStyle()} onClick={handleCopyLink}>
                    {copied ? <FaCheck size={14} /> : <FaCopy size={14} />}
                    {copied ? 'Kopiert!' : 'Link kopieren'}
                </button>
                <button type="button" style={getItemStyle()} onClick={handleTwitterShare}>
                    <FaTwitter size={14} />
                    Twitter
                </button>
                <button type="button" style={getItemStyle()} onClick={handleFacebookShare}>
                    <FaFacebook size={14} />
                    Facebook
                </button>
                <button type="button" style={getItemStyle()} onClick={handleWhatsAppShare}>
                    <FaWhatsapp size={14} />
                    WhatsApp
                </button>
            </div>
        </div>
    );
});

ShareButton.displayName = 'ShareButton';

export default ShareButton;
```

### 10.8 Test Examples

**File**: `frontend/src/utils/__tests__/citySlugUtils.test.ts`

```typescript
/**
 * City Slug Utilities Tests
 */

import { describe, it, expect } from 'vitest';
import { 
    cityNameToSlug, 
    normalizeSlug, 
    isValidSlug,
    buildCitySlugIndex,
    findCityBySlug,
} from '../citySlugUtils';

describe('citySlugUtils', () => {
    describe('cityNameToSlug', () => {
        it('converts simple names', () => {
            expect(cityNameToSlug('Berlin')).toBe('berlin');
            expect(cityNameToSlug('Hamburg')).toBe('hamburg');
        });

        it('handles German umlauts', () => {
            expect(cityNameToSlug('München')).toBe('muenchen');
            expect(cityNameToSlug('Düsseldorf')).toBe('duesseldorf');
            expect(cityNameToSlug('Köln')).toBe('koeln');
            expect(cityNameToSlug('Nürnberg')).toBe('nuernberg');
        });

        it('handles ß', () => {
            expect(cityNameToSlug('Großostheim')).toBe('grossostheim');
        });

        it('handles spaces', () => {
            expect(cityNameToSlug('Bad Aibling')).toBe('bad-aibling');
            expect(cityNameToSlug('Bad Wünnenberg')).toBe('bad-wuennenberg');
        });

        it('handles parentheses', () => {
            expect(cityNameToSlug('Brake (Unterweser)')).toBe('brake-unterweser');
            expect(cityNameToSlug('Frankfurt (Oder)')).toBe('frankfurt-oder');
        });

        it('handles hyphens', () => {
            expect(cityNameToSlug('Berlin-Mitte')).toBe('berlin-mitte');
            expect(cityNameToSlug('Wilhelmitor - Nord')).toBe('wilhelmitor-nord');
        });

        it('trims whitespace', () => {
            expect(cityNameToSlug('  Berlin  ')).toBe('berlin');
        });
    });

    describe('normalizeSlug', () => {
        it('normalizes slugs', () => {
            expect(normalizeSlug('BERLIN')).toBe('berlin');
            expect(normalizeSlug('bad--aibling')).toBe('bad-aibling');
            expect(normalizeSlug('-berlin-')).toBe('berlin');
        });
    });

    describe('isValidSlug', () => {
        it('validates correct slugs', () => {
            expect(isValidSlug('berlin')).toBe(true);
            expect(isValidSlug('bad-aibling')).toBe(true);
            expect(isValidSlug('frankfurt-am-main')).toBe(true);
        });

        it('rejects invalid slugs', () => {
            expect(isValidSlug('')).toBe(false);
            expect(isValidSlug('Berlin')).toBe(false);  // uppercase
            expect(isValidSlug('bad aibling')).toBe(false);  // space
            expect(isValidSlug('münchen')).toBe(false);  // umlaut
        });
    });

    describe('buildCitySlugIndex', () => {
        it('builds index from cities', () => {
            const cities = [
                { id: '1', name: 'Berlin' },
                { id: '2', name: 'München' },
            ];
            const index = buildCitySlugIndex(cities);
            
            expect(index.get('berlin')).toEqual({ id: '1', name: 'Berlin' });
            expect(index.get('muenchen')).toEqual({ id: '2', name: 'München' });
        });

        it('handles duplicate slugs by keeping first', () => {
            const cities = [
                { id: '1', name: 'Frankfurt' },
                { id: '2', name: 'Frankfurt' },  // duplicate
            ];
            const index = buildCitySlugIndex(cities);
            
            expect(index.get('frankfurt')).toEqual({ id: '1', name: 'Frankfurt' });
        });
    });

    describe('findCityBySlug', () => {
        const cities = [
            { id: '1', name: 'Berlin' },
            { id: '2', name: 'München' },
        ];
        const index = buildCitySlugIndex(cities);

        it('finds city by exact slug', () => {
            expect(findCityBySlug('berlin', index)).toEqual({ id: '1', name: 'Berlin' });
        });

        it('normalizes input slug', () => {
            expect(findCityBySlug('BERLIN', index)).toEqual({ id: '1', name: 'Berlin' });
        });

        it('returns undefined for unknown slug', () => {
            expect(findCityBySlug('unknown', index)).toBeUndefined();
        });
    });
});
```

**File**: `frontend/src/components/search/__tests__/CitySearch.test.tsx`

```typescript
/**
 * CitySearch Component Tests
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import { BrowserRouter } from 'react-router-dom';
import CitySearch from '../CitySearch';
import cityDataReducer from '../../../store/slices/cityDataSlice';
import cityReducer from '../../../store/slices/citySlice';

const mockCities = {
    '1': { id: '1', name: 'Berlin', lat: 52.52, lon: 13.405 },
    '2': { id: '2', name: 'Hamburg', lat: 53.55, lon: 9.993 },
    '3': { id: '3', name: 'München', lat: 48.14, lon: 11.58 },
    '4': { id: '4', name: 'Bad Aibling', lat: 47.86, lon: 12.01 },
};

const createMockStore = () => configureStore({
    reducer: {
        cityData: cityDataReducer,
        selectedCity: cityReducer,
    },
    preloadedState: {
        cityData: {
            status: 'succeeded',
            error: undefined,
            data: mockCities,
        },
        selectedCity: {
            cityId: null,
            citySlug: null,
            cityName: null,
            isLoading: false,
        },
    },
});

const renderWithProviders = (component: React.ReactNode) => {
    const store = createMockStore();
    return {
        ...render(
            <Provider store={store}>
                <BrowserRouter>
                    {component}
                </BrowserRouter>
            </Provider>
        ),
        store,
    };
};

describe('CitySearch', () => {
    it('renders search input', () => {
        renderWithProviders(<CitySearch />);
        expect(screen.getByRole('textbox')).toBeInTheDocument();
    });

    it('shows dropdown when typing', async () => {
        renderWithProviders(<CitySearch />);
        const input = screen.getByRole('textbox');
        
        await userEvent.type(input, 'Ber');
        
        expect(screen.getByRole('listbox')).toBeInTheDocument();
        expect(screen.getByText(/Berlin/)).toBeInTheDocument();
    });

    it('filters results based on query', async () => {
        renderWithProviders(<CitySearch />);
        const input = screen.getByRole('textbox');
        
        await userEvent.type(input, 'Ham');
        
        expect(screen.getByText(/Hamburg/)).toBeInTheDocument();
        expect(screen.queryByText(/Berlin/)).not.toBeInTheDocument();
    });

    it('shows no results message for unmatched query', async () => {
        renderWithProviders(<CitySearch />);
        const input = screen.getByRole('textbox');
        
        await userEvent.type(input, 'xyz');
        
        expect(screen.getByText(/Keine Städte gefunden/i)).toBeInTheDocument();
    });

    it('clears input when clear button clicked', async () => {
        renderWithProviders(<CitySearch />);
        const input = screen.getByRole('textbox');
        
        await userEvent.type(input, 'Berlin');
        
        const clearButton = screen.getByLabelText(/suche löschen/i);
        await userEvent.click(clearButton);
        
        expect(input).toHaveValue('');
    });

    it('supports keyboard navigation', async () => {
        renderWithProviders(<CitySearch />);
        const input = screen.getByRole('textbox');
        
        await userEvent.type(input, 'B');
        
        // Arrow down to highlight first item
        await userEvent.keyboard('{ArrowDown}');
        
        // The first option should be highlighted (Bad Aibling or Berlin depending on sort)
        const options = screen.getAllByRole('option');
        expect(options[0]).toHaveAttribute('aria-selected', 'true');
    });
});
```
