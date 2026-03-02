---
goal: "Sprint 3 — City Selection: Search, Select, and Deep-Link German Cities"
version: 1.0
date_created: 2026-03-02
last_updated: 2026-03-02
owner: phoenix
status: 'Planned'
tags: [feature, city-selection, search, url, sprint-3]
---

# Sprint 3 — City Selection

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Search and select any of ~2,949 German cities. Selection is reflected in the URL for sharing. City markers appear on the map. This sprint establishes the personalization axis — all subsequent sprints (metrics, plots) key off "selected city".

**Prerequisite**: Sprint 2 completed — map with temporal navigation.

**Architecture reference**: See `plan/phoenix/00-architecture.md`

## 1. Requirements & Constraints

- **REQ-001**: Autocomplete search input with debounced filtering (≤100ms response)
- **REQ-002**: Search scoring: exact match (100) > prefix (80) > contains (60), with length penalty for longer names
- **REQ-003**: Results limited to 15 items, keyboard navigable (↑/↓/Enter/Escape)
- **REQ-004**: City selection reflected in URL via `?city=<slug>` query parameter (react-router-dom)
- **REQ-005**: Deep linking: loading the page with `?city=muenchen` selects München
- **REQ-006**: City slug handles German umlauts and special characters: ä→ae, ö→oe, ü→ue, ß→ss, spaces→hyphens
- **REQ-007**: Map shows city markers (imperative MapLibre DOM markers). Selected city marker highlighted.
- **REQ-008**: Clicking a map marker selects that city
- **REQ-009**: Map pans/zooms to center on selected city
- **REQ-010**: Default city: Berlin (auto-selected on first load if no `?city` param)
- **REQ-011**: City data loaded from `/data/cities.json` (conforming to `city-correlation.schema.json`)
- **CON-001**: City index is fetched once and cached in Redux (it's a static file)
- **CON-002**: `react-router-dom` added as dependency (needed for URL management)
- **PAT-001**: City data flow: `CityService.fetch()` → `citySlice` (via `createDataSlice`) → components read via selectors
- **GUD-001**: Slug utility must be pure function with comprehensive tests (umlauts, edge cases)

## 2. Implementation Steps

### Phase 1: Backend — City Correlation Data (Dev Fixture)

- GOAL-001: Provide a realistic `cities.json` dev fixture so city search works during frontend development. Sprint 3b later replaces this with the full ~2,949-city file generated from the real pipeline.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-001 | Copy `analysis/geonames/` to `phoenix-backend/analysis/geonames/` | | |
| TASK-002 | Create `phoenix-frontend/public/data/cities.json` — a hand-crafted dev fixture conforming to `schemas/city-correlation.schema.json` with **30 major German cities**: Berlin, Hamburg, München, Köln, Frankfurt am Main, Stuttgart, Düsseldorf, Leipzig, Dortmund, Essen, Bremen, Dresden, Hannover, Nürnberg, Duisburg, Bochum, Wuppertal, Bielefeld, Bonn, Münster, Mannheim, Karlsruhe, Augsburg, Wiesbaden, Freiburg im Breisgau, Rostock, Kiel, Lübeck, Potsdam, Saarbrücken. For each city: (1) look up real lat/lon, (2) compute `grid_i`/`grid_j` from ERA5-Land 0.1° grid (grid_i = round((lon − 5.8) / 0.1), grid_j = round((lat − 47.2) / 0.1)), (3) compute `grid_lat`/`grid_lon` (snapped to grid), (4) generate `tile_id` as `"{grid_i}_{grid_j}"`, (5) generate `slug` (ä→ae, ö→oe, ü→ue, ß→ss). Include `meta` envelope: `{ grid_resolution: 0.1, bounds: { north: 55.1, south: 47.2, west: 5.8, east: 15.1 }, city_count: 30 }`. | | |
| TASK-003 | Validate the dev fixture against `schemas/city-correlation.schema.json`. Spot-check: Berlin slug is `"berlin"`, tile_id is `"76_53"`; München slug is `"muenchen"`. | | |

### Phase 2: City Slug Utility

- GOAL-002: Pure utility for converting city names to URL-safe slugs and back

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-004 | Create `src/utils/citySlug.ts` — `toSlug(name: string): string` (München → muenchen, Bad Wünnenberg → bad-wuennenberg, Gießen → giessen) and `findBySlug(cities: City[], slug: string): City | undefined` | | |
| TASK-005 | Create `src/utils/__tests__/citySlug.test.ts` — test all umlaut conversions (ä, ö, ü, Ä, Ö, Ü, ß), hyphenation, lowercase, edge cases (multiple spaces, leading/trailing whitespace, "Sankt" abbreviation) | | |

### Phase 3: City Service + Redux Slice

- GOAL-003: Fetch and cache city data in Redux, with search/filter capability

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-006 | Create `src/types/city.ts` — `City` interface matching the schema: `{ name, slug, lat, lon, grid_i, grid_j, grid_lat, grid_lon, tile_id }`. Also `CityIndex` for the full response: `{ meta, cities }` | | |
| TASK-007 | Create `src/services/CityService.ts` — `fetchCities(): Promise<CityIndex>` that GETs `/data/cities.json` (URL from `climateDataConfig` or hardcoded base). Parse and return typed data. | | |
| TASK-008 | Create `src/store/slices/citySlice.ts` via `createDataSlice` factory with shape `'simple'` and cache `'all'` — stores the full city index. Add additional synchronous state: `selectedCitySlug: string | null`, `searchQuery: string`. Add reducers: `selectCity(slug)`, `setSearchQuery(query)`, `clearSelection()`. Add selectors: `selectAllCities`, `selectSelectedCity`, `selectSearchResults` (filtered + scored list). | | |
| TASK-009 | Implement search scoring in `selectSearchResults` selector (or a utility): exact match (100), prefix (80), contains (60), with shorter names ranked higher. Limit results to 15. | | |
| TASK-010 | Register `citySlice` in `src/store/index.ts` | | |

### Phase 4: City Search Component

- GOAL-004: Autocomplete search UI with keyboard navigation

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-011 | Create `src/components/maps/ClimateMap/CitySearch.tsx` — search input + dropdown results list. Features: debounced input (150ms), keyboard navigation (↑/↓ to highlight, Enter to select, Escape to close), click to select. Positioned as map overlay (top-left, below or beside DateSelector). | | |
| TASK-012 | On city selection: dispatch `selectCity(slug)` → update URL via `react-router-dom` `useSearchParams` → map pans to city | | |
| TASK-013 | Style with design tokens: input matches app theme, dropdown has hover/focus states, mobile-friendly touch targets | | |

### Phase 5: City Markers on Map

- GOAL-005: Visual city markers on the map with selection highlighting

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-014 | Create `src/components/maps/ClimateMap/CityMarkers.tsx` — imperative MapLibre DOM markers. Use `useRef<Map<string, maplibregl.Marker>>()` to track marker instances. On city data load: create markers for visible cities (or all cities, depending on performance). Each marker is a small circle div; selected city gets a larger/highlighted marker. | | |
| TASK-015 | Clicking a marker dispatches `selectCity(slug)` | | |
| TASK-016 | On city selection: map calls `map.flyTo({ center: [lon, lat], zoom: 7 })` | | |
| TASK-017 | Add `CityMarkers` to the `ClimateMap` component | | |

### Phase 6: URL Deep Linking

- GOAL-006: City selection persisted in URL, shareable, restored on page load

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-018 | Add `react-router-dom` to `package.json` if not already present | | |
| TASK-019 | Update `src/App.tsx` to use `BrowserRouter` and define routes: `/` (main page), catch-all redirect to `/` | | |
| TASK-020 | Create `src/hooks/useCityFromUrl.ts` — reads `?city=<slug>` from URL on mount, dispatches `selectCity(slug)` if present. When city selection changes in Redux, updates the URL search param. Two-way sync. | | |
| TASK-021 | If no `?city` param on first load: auto-select Berlin as default | | |

### Phase 7: Integration + Tests

- GOAL-007: Everything wired together, all tests passing

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-022 | Wire up in `App.tsx` or `ClimateMap`: on mount, dispatch city data fetch. On city data loaded + URL parsed, select city. | | |
| TASK-023 | Create `src/services/__tests__/CityService.test.ts` — test fetch, parse, error handling | | |
| TASK-024 | Create `src/store/slices/__tests__/citySlice.test.ts` — test city selection, search query, search scoring (exact > prefix > contains), result limit (15) | | |
| TASK-025 | Create `src/components/maps/__tests__/CitySearch.test.tsx` — test rendering, search input, result display, keyboard navigation, city selection dispatches action | | |
| TASK-026 | Create `src/hooks/__tests__/useCityFromUrl.test.ts` — test URL → Redux sync and Redux → URL sync | | |
| TASK-027 | Verify: `npm run test` — all tests pass (Sprint 1 + 2 + 3). Manual test: type "Mün" → see "München" → click → URL updates → marker highlighted → map pans | | |

## 3. Alternatives

- **ALT-001**: Use a third-party autocomplete library (e.g., downshift, react-select) — rejected for simplicity; our requirements (15 results, keyboard nav) are straightforward enough to build in ~100 lines
- **ALT-002**: Store city selection in Redux only (no URL) — rejected because deep linking (shareable URLs) is a core requirement
- **ALT-003**: Use MapLibre GeoJSON source + symbol layer instead of DOM markers — viable for performance at scale, but DOM markers allow richer interactivity (hover, click, custom HTML). Can be revisited in Sprint 8 (polish) if 2,949 markers cause perf issues
- **ALT-004**: Lazy-load city markers (only visible in viewport) — defer to Sprint 8 if performance requires it

## 4. Dependencies

- **DEP-001**: Sprint 2 completed (map + date selector working)
- **DEP-002**: `react-router-dom` 7.6+ (new dependency for URL management)
- **DEP-003**: City correlation data file (`cities.json`) — generated from backend or using sample fixture

## 5. Files

### Backend
- **FILE-001**: `phoenix-backend/analysis/geonames/` — NEW (copied from `analysis/geonames/`)
- **FILE-002**: `phoenix-frontend/public/data/cities.json` — NEW (generated or sample data)

### Frontend — New
- **FILE-003**: `phoenix-frontend/src/types/city.ts` — NEW
- **FILE-004**: `phoenix-frontend/src/utils/citySlug.ts` — NEW
- **FILE-005**: `phoenix-frontend/src/services/CityService.ts` — NEW
- **FILE-006**: `phoenix-frontend/src/store/slices/citySlice.ts` — NEW
- **FILE-007**: `phoenix-frontend/src/components/maps/ClimateMap/CitySearch.tsx` — NEW
- **FILE-008**: `phoenix-frontend/src/components/maps/ClimateMap/CityMarkers.tsx` — NEW
- **FILE-009**: `phoenix-frontend/src/hooks/useCityFromUrl.ts` — NEW

### Frontend — Modified
- **FILE-010**: `phoenix-frontend/package.json` — MODIFY — add `react-router-dom`
- **FILE-011**: `phoenix-frontend/src/App.tsx` — MODIFY — add BrowserRouter, city data fetch, default city
- **FILE-012**: `phoenix-frontend/src/store/index.ts` — MODIFY — register `citySlice`
- **FILE-013**: `phoenix-frontend/src/components/maps/ClimateMap/ClimateMap.tsx` — MODIFY — add CityMarkers, CitySearch
- **FILE-014**: `phoenix-frontend/src/components/maps/ClimateMap/index.ts` — MODIFY — export new components

### Tests
- **FILE-015**: `phoenix-frontend/src/utils/__tests__/citySlug.test.ts` — NEW
- **FILE-016**: `phoenix-frontend/src/services/__tests__/CityService.test.ts` — NEW
- **FILE-017**: `phoenix-frontend/src/store/slices/__tests__/citySlice.test.ts` — NEW
- **FILE-018**: `phoenix-frontend/src/components/maps/__tests__/CitySearch.test.tsx` — NEW
- **FILE-019**: `phoenix-frontend/src/hooks/__tests__/useCityFromUrl.test.ts` — NEW

## 6. Testing

- **TEST-001**: `citySlug.test.ts` — `toSlug('München')` → `'muenchen'`, `toSlug('Bad Wünnenberg')` → `'bad-wuennenberg'`, `toSlug('Gießen')` → `'giessen'`, `toSlug('Königs Wusterhausen')` → `'koenigs-wusterhausen'`
- **TEST-002**: `CityService.test.ts` — fetches and parses cities.json; handles network errors; returns typed CityIndex
- **TEST-003**: `citySlice.test.ts` — initial state has no selection; `selectCity('berlin')` sets slug; search query filters results; scoring ranks exact > prefix > contains; max 15 results
- **TEST-004**: `CitySearch.test.tsx` — renders input; typing dispatches search query; results appear; keyboard ↓→Enter selects city; Escape closes dropdown
- **TEST-005**: `useCityFromUrl.test.ts` — URL `?city=muenchen` → dispatches `selectCity('muenchen')`; city selection in Redux → URL updates to `?city=muenchen`
- **TEST-006**: All Sprint 1 + 2 tests still pass (regression)

## 7. Risks & Assumptions

### Risks
- **RISK-001**: 2,949 DOM markers may cause performance issues on mobile — **Mitigation**: start with all markers; if perf degrades, cluster markers at low zoom or switch to GeoJSON symbol layer in Sprint 8
- **RISK-002**: `react-router-dom` v7 API may differ from examples — **Mitigation**: use `useSearchParams` hook which is stable across v6/v7
- **RISK-003**: City slug collisions (two cities with the same slug) — **Mitigation**: add population or state suffix for disambiguation; test with full dataset

### Assumptions
- **ASSUMPTION-001**: The 30-city dev fixture created in Phase 1 is sufficient for frontend development; Sprint 3b generates the full ~2,949-city file from the real pipeline
- **ASSUMPTION-002**: All ~2,949 German cities (population >5000) fit comfortably in a single JSON file (<500KB)
- **ASSUMPTION-003**: Berlin is always present in the cities dataset (used as default)

## 8. Multi-Agent Execution Notes

### Execution Order
- **Sequential**: Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6 → Phase 7
- **Parallel within Phase 1**: TASK-001 and TASK-002 can run simultaneously
- **Phase 2 + Phase 3 partially parallel**: TASK-004–005 (slug utility) has no dependency on TASK-006–010 (service + slice), but the slice uses the slug utility, so slug should be done first
- **Phase 4 + Phase 5 partially parallel**: CitySearch and CityMarkers can be built simultaneously after Phase 3

### Agent Context Requirements
- Read `plan/phoenix/00-architecture.md` §4.4 for city index schema
- Read `plan/phoenix/sprint-1-mvp-map.md` §10.2 for MapLibre patterns (marker creation follows similar imperative pattern)
- Read `phoenix-frontend/src/store/factories/createDataSlice.ts` for slice factory usage
- Read `schemas/city-correlation.schema.json` for city data shape

### Validation Checkpoints
- [After TASK-003]: `cities.json` exists at `phoenix-frontend/public/data/cities.json`
- [After TASK-005]: `npm run test -- citySlug` — slug tests pass
- [After TASK-010]: City slice registered, `npm run test -- citySlice` — slice tests pass
- [After TASK-021]: Loading `/?city=muenchen` selects München on the map
- [After TASK-027]: All tests pass, manual flow works end-to-end

## 9. Related Specifications / Further Reading

- `plan/phoenix/00-architecture.md` — architecture reference
- `plan/phoenix/sprint-1-mvp-map.md` — map foundation
- `plan/phoenix/sprint-2-temporal-nav.md` — temporal navigation
- `plan/phoenix/sprint-3b-data-pipeline.md` — generates the real ~2,949-city `cities.json` (replaces dev fixture from this sprint)
- `schemas/city-correlation.schema.json` — city data contract

## 10. Code Reference

### 10.1 City Type Definitions

**File**: `phoenix-frontend/src/types/city.ts` (to be created)

```typescript
export interface City {
  name: string;
  slug: string;
  lat: number;
  lon: number;
  grid_i: number;
  grid_j: number;
  grid_lat: number;
  grid_lon: number;
  tile_id: string;  // e.g., "76_53"
}

export interface CityIndexMeta {
  grid_resolution: number;
  bounds: { north: number; south: number; west: number; east: number };
  city_count: number;
}

export interface CityIndex {
  meta: CityIndexMeta;
  cities: City[];
}
```

### 10.2 City Slug Utility

**File**: `phoenix-frontend/src/utils/citySlug.ts` (to be created)

```typescript
const UMLAUT_MAP: Record<string, string> = {
  'ä': 'ae', 'ö': 'oe', 'ü': 'ue',
  'Ä': 'Ae', 'Ö': 'Oe', 'Ü': 'Ue',
  'ß': 'ss',
};

export function toSlug(name: string): string {
  return name
    .trim()
    .replace(/[äöüÄÖÜß]/g, (match) => UMLAUT_MAP[match] ?? match)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');
}

export function findBySlug(cities: City[], slug: string): City | undefined {
  return cities.find((c) => c.slug === slug);
}
```

### 10.3 Search Scoring

**File**: `phoenix-frontend/src/store/slices/citySlice.ts` (scoring logic)

```typescript
function scoreCity(city: City, query: string): number {
  const name = city.name.toLowerCase();
  const q = query.toLowerCase();

  if (name === q) return 100;
  if (name.startsWith(q)) return 80 - name.length * 0.1;
  if (name.includes(q)) return 60 - name.length * 0.1;
  return 0;
}

// Used in selectSearchResults selector:
// filter cities where score > 0, sort descending, take first 15
```

### 10.4 CityMarkers — Imperative MapLibre Pattern

**File**: `phoenix-frontend/src/components/maps/ClimateMap/CityMarkers.tsx` (to be created)

```typescript
// Pattern from existing frontend/src/components/maps/ClimateMap/CityMarkers.tsx
// Key approach: useRef to track marker instances, useEffect to create/update/remove

const markersRef = useRef<Map<string, maplibregl.Marker>>(new Map());

useEffect(() => {
  const map = mapRef.current;
  if (!map || cities.length === 0) return;

  // Create markers for all cities
  cities.forEach((city) => {
    if (markersRef.current.has(city.slug)) return;

    const el = document.createElement('div');
    el.className = 'city-marker';
    el.style.width = '10px';
    el.style.height = '10px';
    el.style.borderRadius = '50%';
    el.style.backgroundColor = theme.colors.primary;
    el.style.cursor = 'pointer';

    el.addEventListener('click', () => dispatch(selectCity(city.slug)));

    const marker = new maplibregl.Marker({ element: el })
      .setLngLat([city.lon, city.lat])
      .addTo(map);

    markersRef.current.set(city.slug, marker);
  });

  return () => {
    markersRef.current.forEach((marker) => marker.remove());
    markersRef.current.clear();
  };
}, [cities, dispatch]);

// Highlight selected marker
useEffect(() => {
  markersRef.current.forEach((marker, slug) => {
    const el = marker.getElement();
    const isSelected = slug === selectedCitySlug;
    el.style.width = isSelected ? '16px' : '10px';
    el.style.height = isSelected ? '16px' : '10px';
    el.style.backgroundColor = isSelected ? theme.colors.hot : theme.colors.primary;
    el.style.zIndex = isSelected ? '10' : '1';
  });
}, [selectedCitySlug]);
```

### 10.5 URL Sync Hook

**File**: `phoenix-frontend/src/hooks/useCityFromUrl.ts` (to be created)

```typescript
import { useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../store/hooks/useAppSelector';
import { selectCity, selectSelectedCity } from '../store/slices/citySlice';

export function useCityFromUrl() {
  const [searchParams, setSearchParams] = useSearchParams();
  const dispatch = useAppDispatch();
  const selectedCity = useAppSelector(selectSelectedCity);

  // URL → Redux (on mount)
  useEffect(() => {
    const citySlug = searchParams.get('city');
    if (citySlug) {
      dispatch(selectCity(citySlug));
    }
  }, []); // intentionally run only once on mount

  // Redux → URL (on selection change)
  useEffect(() => {
    const currentSlug = searchParams.get('city');
    if (selectedCity && selectedCity.slug !== currentSlug) {
      setSearchParams({ city: selectedCity.slug }, { replace: true });
    }
  }, [selectedCity, setSearchParams]);
}
```
