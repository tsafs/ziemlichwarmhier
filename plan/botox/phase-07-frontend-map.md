---
goal: Phase 7 - Frontend Map Visualization with MapLibre GL
version: 1.0
date_created: 2026-02-16
last_updated: 2026-02-16
owner: Sebastian
status: 'Planned'
tags: [phase-7, frontend, maplibre, visualization, map]
---

# Introduction

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

This phase implements the interactive climate map visualization using MapLibre GL JS. The map displays ERA5 temperature anomaly tiles overlaid on a base map of Germany, with clickable city markers, a color legend, and month/year date selection. The implementation follows existing codebase patterns (Redux slices, services, hooks) while introducing MapLibre GL for the first time.

**Key deliverables:**
- MapLibre GL integration with Germany-focused map
- Temperature anomaly tile overlay from Hetzner Object Storage
- Clickable city markers with selection state
- Color scale legend component
- Month/year date picker for historical navigation
- Redux state management for map view and selected date
- Responsive behavior (mobile pan/zoom/gestures)

## 1. Requirements & Constraints

### Functional Requirements (from Master Plan)
- **REQ-001**: Display temperature anomaly maps for Germany using ERA5 data at 1km visual resolution
- **REQ-002**: Support rolling 12-month anomaly visualization
- **REQ-009**: Provide responsive design for mobile and desktop

### Phase-Specific Requirements
- **REQ-P7-001**: Map must constrain view to Germany bounds (lat: 47.2-55.1, lon: 5.8-15.1)
- **REQ-P7-002**: Tile overlay must support zoom levels 6-10
- **REQ-P7-003**: City markers must be clickable and trigger `selectCity` action
- **REQ-P7-004**: Date selector must allow month/year navigation back to 2016
- **REQ-P7-005**: Legend must display diverging color scale (-3°C to +3°C)
- **REQ-P7-006**: Map performance must maintain 60fps on mobile during pan/zoom

### Technical Constraints
- **CON-001**: MapLibre GL JS requires WebGL support (90%+ browser coverage)
- **CON-002**: Tile size is 256×256 WebP images
- **CON-003**: Tile URL pattern: `{baseUrl}/{year}/{month:02d}/{z}/{x}/{y}.webp`

### Patterns to Follow
- **PAT-001**: Use `createDataSlice` factory for Redux state management
- **PAT-002**: Use service layer pattern for tile URL generation  
- **PAT-003**: Follow PlotView component pattern for layout containers
- **PAT-004**: Follow existing StationSearch pattern for city interaction
- **PAT-005**: Use design-system tokens for all styling

## 2. Implementation Steps

### Implementation Phase 7.1: MapLibre GL Setup & Dependencies

- GOAL-P7-001: Install MapLibre GL and configure TypeScript types

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-700 | Install `maplibre-gl` and `@types/maplibre-gl` via npm | | |
| TASK-701 | Add MapLibre CSS import to App.tsx or index.tsx | | |
| TASK-702 | Create `frontend/src/constants/mapConfig.ts` with Germany bounds, zoom levels, tile URL pattern | | |
| TASK-703 | Write type definitions for map state in `frontend/src/types/map.ts` | | |

**Completion Criteria:**
- `npm run build` succeeds with MapLibre imports
- TypeScript recognizes MapLibre types
- Map configuration constants accessible

---

### Implementation Phase 7.2: Map State Management

- GOAL-P7-002: Create Redux slice for map view state and selected date

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-704 | Create `frontend/src/store/slices/mapSlice.ts` using createDataSlice pattern | | |
| TASK-705 | Define map state interface: viewport, selectedYear, selectedMonth | | |
| TASK-706 | Create actions: setViewport, setSelectedDate, resetMapView | | |
| TASK-707 | Create selectors: selectMapViewport, selectSelectedDate, selectTileUrl | | |
| TASK-708 | Register mapSlice in store/index.ts | | |
| TASK-709 | Write unit tests for mapSlice reducers and selectors | | |

**Completion Criteria:**
- Map state stored in Redux
- Actions and selectors exported and tested
- State updates correctly on action dispatch

---

### Implementation Phase 7.3: Tile Service

- GOAL-P7-003: Create service for generating tile URLs

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-710 | Create `frontend/src/services/TileService.ts` with URL builder functions | | |
| TASK-711 | Implement `getTileUrl(year, month, z, x, y)` function | | |
| TASK-712 | Implement `getAvailableMonths()` to return valid date range | | |
| TASK-713 | Add tile URL validation and error handling | | |
| TASK-714 | Write unit tests for TileService | | |

**Completion Criteria:**
- Tile URLs generated correctly for all zoom levels
- Date range validation prevents invalid requests
- Tests cover edge cases (invalid dates, out-of-bounds tiles)

---

### Implementation Phase 7.4: ClimateMap Core Component

- GOAL-P7-004: Implement base map component with MapLibre GL

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-715 | Create `frontend/src/components/maps/ClimateMap/ClimateMap.tsx` base component | | |
| TASK-716 | Initialize MapLibre GL map with OpenStreetMap base layer | | |
| TASK-717 | Implement Germany bounds constraint using `maxBounds` | | |
| TASK-718 | Configure zoom constraints (min: 6, max: 10) | | |
| TASK-719 | Add map load and error event handlers | | |
| TASK-720 | Implement responsive container sizing | | |
| TASK-721 | Write integration tests for ClimateMap rendering | | |

**Completion Criteria:**
- Map renders centered on Germany
- Pan/zoom constrained to Germany region
- No console errors on mount/unmount

---

### Implementation Phase 7.5: Tile Layer Overlay

- GOAL-P7-005: Add temperature anomaly tile overlay

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-722 | Create `frontend/src/components/maps/ClimateMap/TileLayer.tsx` | | |
| TASK-723 | Add raster tile source to MapLibre map | | |
| TASK-724 | Configure tile source URL template from TileService | | |
| TASK-725 | Implement source update on date change | | |
| TASK-726 | Add tile loading state indicator | | |
| TASK-727 | Handle tile load errors gracefully | | |
| TASK-728 | Write tests for tile layer behavior | | |

**Completion Criteria:**
- Anomaly tiles visible over base map
- Tiles refresh when selected date changes
- Loading indicator shown during tile fetch

---

### Implementation Phase 7.6: City Markers

- GOAL-P7-006: Add clickable city markers

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-729 | Create `frontend/src/components/maps/ClimateMap/CityMarkers.tsx` | | |
| TASK-730 | Render city markers from cityData Redux state | | |
| TASK-731 | Implement marker click handler to dispatch selectCity | | |
| TASK-732 | Style selected city marker differently (highlight) | | |
| TASK-733 | Add city name labels on hover/click | | |
| TASK-734 | Implement marker clustering for zoomed-out views | | |
| TASK-735 | Write tests for marker interaction | | |

**Completion Criteria:**
- City markers visible on map
- Click triggers city selection
- Selected city visually distinguished

---

### Implementation Phase 7.7: Color Legend

- GOAL-P7-007: Create color scale legend component

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-736 | Create `frontend/src/components/maps/ClimateMap/Legend.tsx` | | |
| TASK-737 | Render gradient bar with diverging color scale | | |
| TASK-738 | Add tick marks and labels (-3, -2, -1, 0, +1, +2, +3 °C) | | |
| TASK-739 | Position legend in bottom-right corner of map | | |
| TASK-740 | Make legend collapsible on mobile | | |
| TASK-741 | Write tests for Legend component | | |

**Completion Criteria:**
- Legend displays correct color gradient
- Labels at correct positions
- Responsive behavior on mobile

---

### Implementation Phase 7.8: Date Selector

- GOAL-P7-008: Create month/year date picker

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-742 | Create `frontend/src/components/maps/ClimateMap/DateSelector.tsx` | | |
| TASK-743 | Implement month selector dropdown | | |
| TASK-744 | Implement year selector dropdown | | |
| TASK-745 | Connect to mapSlice via setSelectedDate action | | |
| TASK-746 | Disable future dates beyond available data | | |
| TASK-747 | Add "Latest" button for quick navigation to most recent | | |
| TASK-748 | Write tests for DateSelector | | |

**Completion Criteria:**
- Month/year selection updates Redux state
- Invalid dates disabled
- Latest button works correctly

---

### Implementation Phase 7.9: Custom Hook & Integration

- GOAL-P7-009: Create useMapTiles hook and integrate all components

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-749 | Create `frontend/src/hooks/useMapTiles.ts` hook | | |
| TASK-750 | Combine map state selectors and city data | | |
| TASK-751 | Create `frontend/src/components/maps/ClimateMap/index.ts` barrel export | | |
| TASK-752 | Integrate ClimateMap into main page layout | | |
| TASK-753 | Write E2E tests for map interaction flow | | |

**Completion Criteria:**
- useMapTiles provides all data needed by map
- ClimateMap exports cleanly from index
- Full interaction flow tested

## 3. Alternatives

- **ALT-P7-001**: **deck.gl instead of MapLibre GL** - Considered for WebGL-accelerated rendering. Rejected for initial implementation due to larger bundle size (200KB+ vs 85KB) and complexity. Can migrate later if 3D globe view needed.

- **ALT-P7-002**: **Leaflet instead of MapLibre GL** - Considered for simpler API. Rejected because MapLibre GL has better WebGL performance for tile rendering and built-in vector tile support for future expansion.

- **ALT-P7-003**: **Observable Plot geo() instead of MapLibre** - Already used in HeatmapGermany. Rejected because it doesn't support raster tile overlays and has limited interactivity.

- **ALT-P7-004**: **Year slider instead of dual dropdown** - Considered for easier navigation. Rejected for initial implementation; can add as enhancement later.

## 4. Dependencies

### External Dependencies
- **DEP-P7-001**: `maplibre-gl` ^4.x - Map rendering library
- **DEP-P7-002**: `@types/maplibre-gl` - TypeScript types (peer of maplibre-gl in v4)
- **DEP-P7-003**: Tile data from Hetzner Object Storage (Phase 4 output)

### Internal Dependencies  
- **DEP-P7-004**: `cityDataSlice` - Provides city list and coordinates
- **DEP-P7-005**: `selectedCitySlice` - City selection state
- **DEP-P7-006**: Design system tokens - Consistent styling
- **DEP-P7-007**: Phase 4 completion - Tiles must exist to display

### Phase Dependencies
- **DEP-P7-008**: Phase 1 (Testing Infrastructure) - Vitest must be configured
- **DEP-P7-009**: Can develop with mock tiles before Phase 4 completes

## 5. Files

### New Files
- **FILE-P7-001**: `frontend/src/components/maps/ClimateMap/ClimateMap.tsx` - NEW - Main map component
- **FILE-P7-002**: `frontend/src/components/maps/ClimateMap/TileLayer.tsx` - NEW - Anomaly tile overlay
- **FILE-P7-003**: `frontend/src/components/maps/ClimateMap/CityMarkers.tsx` - NEW - City marker layer
- **FILE-P7-004**: `frontend/src/components/maps/ClimateMap/Legend.tsx` - NEW - Color legend
- **FILE-P7-005**: `frontend/src/components/maps/ClimateMap/DateSelector.tsx` - NEW - Date picker
- **FILE-P7-006**: `frontend/src/components/maps/ClimateMap/index.ts` - NEW - Barrel export
- **FILE-P7-007**: `frontend/src/store/slices/mapSlice.ts` - NEW - Map state
- **FILE-P7-008**: `frontend/src/services/TileService.ts` - NEW - Tile URL generation
- **FILE-P7-009**: `frontend/src/hooks/useMapTiles.ts` - NEW - Map data hook
- **FILE-P7-010**: `frontend/src/types/map.ts` - NEW - Map type definitions
- **FILE-P7-011**: `frontend/src/constants/mapConfig.ts` - NEW - Map constants

### Modified Files
- **FILE-P7-012**: `frontend/src/store/index.ts` - MODIFY - Add mapSlice
- **FILE-P7-013**: `frontend/package.json` - MODIFY - Add maplibre-gl dependency
- **FILE-P7-014**: `frontend/src/index.tsx` or `App.tsx` - MODIFY - Import MapLibre CSS

### Test Files
- **FILE-P7-015**: `frontend/src/components/maps/__tests__/ClimateMap.test.tsx` - NEW
- **FILE-P7-016**: `frontend/src/store/slices/__tests__/mapSlice.test.ts` - NEW
- **FILE-P7-017**: `frontend/src/services/__tests__/TileService.test.ts` - NEW
- **FILE-P7-018**: `frontend/src/hooks/__tests__/useMapTiles.test.ts` - NEW

## 6. Testing

### Unit Tests
- **TEST-P7-001**: mapSlice reducers update state correctly on actions
- **TEST-P7-002**: mapSlice selectors return correct derived state
- **TEST-P7-003**: TileService generates correct URLs for all inputs
- **TEST-P7-004**: TileService validates date ranges correctly
- **TEST-P7-005**: Legend component renders with correct colors and labels
- **TEST-P7-006**: DateSelector disables invalid dates

### Integration Tests
- **TEST-P7-007**: ClimateMap renders without errors with mock data
- **TEST-P7-008**: City marker click dispatches selectCity action
- **TEST-P7-009**: Date change updates tile source URL
- **TEST-P7-010**: Map respects Germany bounds constraint

### Mock Data Requirements
- **MOCK-P7-001**: Mock city list (10 cities with coordinates)
- **MOCK-P7-002**: Mock tile responses (256×256 WebP or PNG placeholders)
- **MOCK-P7-003**: Mock MapLibre GL map instance

### E2E Tests
- **TEST-P7-011**: User can pan and zoom map within Germany
- **TEST-P7-012**: User can select city by clicking marker
- **TEST-P7-013**: User can change date and see tiles update

## 7. Risks & Assumptions

### Risks
- **RISK-P7-001**: MapLibre GL version incompatibility with existing React version
  - **Mitigation**: Pin to known compatible version; test in CI before merge

- **RISK-P7-002**: Tile loading performance issues on slow connections
  - **Mitigation**: Implement progressive loading; use lower zoom tiles as placeholders

- **RISK-P7-003**: WebGL not supported in older browsers
  - **Mitigation**: Feature detection with fallback to static image; browser support banner

- **RISK-P7-004**: Memory leaks from MapLibre GL instance
  - **Mitigation**: Proper cleanup in useEffect return; follow MapLibre docs for React

### Assumptions
- **ASSUMPTION-P7-001**: MapLibre GL CSS can be imported without build config changes
- **ASSUMPTION-P7-002**: OpenStreetMap tiles available as base layer (free, no API key)
- **ASSUMPTION-P7-003**: Tile server (Hetzner) responds within 500ms
- **ASSUMPTION-P7-004**: 10 zoom levels (6-10) provide sufficient detail range

## 8. Multi-Agent Execution Notes

### Execution Order
**Parallel tasks (can run simultaneously):**
- TASK-700 to TASK-703 (Setup) - independent of other tasks
- TASK-704 to TASK-709 (State) - independent of other tasks
- TASK-710 to TASK-714 (Service) - independent of other tasks

**Sequential dependencies:**
- Phase 7.4 (ClimateMap) requires Phase 7.1 (Setup)
- Phase 7.5 (TileLayer) requires Phase 7.3 (Service) + Phase 7.4 (ClimateMap)
- Phase 7.6 (Markers) requires Phase 7.4 (ClimateMap)
- Phase 7.7-7.8 (Legend, DateSelector) require Phase 7.4 (ClimateMap)
- Phase 7.9 (Integration) requires all previous phases

### Agent Context Requirements
Provide these files for agent execution:
- This plan document
- `frontend/src/store/factories/createDataSlice.ts` (slice factory pattern)
- `frontend/src/components/header/StationSearch.tsx` (click handler pattern)
- `frontend/src/styles/design-system.ts` (styling tokens)
- `frontend/src/store/index.ts` (store registration pattern)

### Validation Checkpoints
- **After Phase 7.1**: `npm run build` succeeds; MapLibre imports work
- **After Phase 7.2**: `npm test` passes for mapSlice tests
- **After Phase 7.4**: Map renders in browser at localhost
- **After Phase 7.5**: Mock tiles visible on map
- **After Phase 7.9**: Full integration working with all interactions

## 9. Related Specifications / Further Reading

- [MapLibre GL JS Documentation](https://maplibre.org/maplibre-gl-js/docs/)
- [MapLibre GL JS Examples](https://maplibre.org/maplibre-gl-js/docs/examples/)
- [React + MapLibre GL Guide](https://maplibre.org/maplibre-gl-js/docs/examples/react-component/)
- [Master Plan](../botox/era5-germany-climate-visualization-1.md) - Overall architecture

## 10. Code Reference (REQUIRED)

### 10.1 Map Configuration Constants

**File**: `frontend/src/constants/mapConfig.ts`

```typescript
/**
 * Map Configuration Constants
 * 
 * Centralized configuration for the ClimateMap component.
 */

export const MAP_CONFIG = {
    // Germany bounding box [west, south, east, north]
    GERMANY_BOUNDS: [5.8, 47.2, 15.1, 55.1] as [number, number, number, number],
    
    // Initial map center (approximately center of Germany)
    INITIAL_CENTER: [10.45, 51.15] as [number, number],
    
    // Zoom constraints
    MIN_ZOOM: 6,
    MAX_ZOOM: 10,
    INITIAL_ZOOM: 7,
    
    // Tile configuration
    TILE_SIZE: 256,
    TILE_FORMAT: 'webp',
    
    // Available date range
    DATA_START_YEAR: 2016,
    DATA_START_MONTH: 1,
    
    // Color scale configuration (for legend)
    ANOMALY_MIN: -3, // °C below reference
    ANOMALY_MAX: 3,  // °C above reference
    ANOMALY_COLORS: {
        min: '#4575b4',    // Cold (blue)
        zero: '#ffffbf',   // Neutral (white/yellow)
        max: '#d73027',    // Hot (red)
    },
} as const;

// Base URL for tile server (from environment or default)
export const TILE_BASE_URL = import.meta.env.VITE_TILE_BASE_URL || 'https://tiles.itishotnow.de';

// OpenStreetMap base layer (free, no API key required)
export const BASE_MAP_STYLE = {
    version: 8 as const,
    sources: {
        osm: {
            type: 'raster' as const,
            tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
            tileSize: 256,
            attribution: '© OpenStreetMap contributors',
        },
    },
    layers: [
        {
            id: 'osm-tiles',
            type: 'raster' as const,
            source: 'osm',
            minzoom: 0,
            maxzoom: 19,
        },
    ],
};
```

### 10.2 Map Type Definitions

**File**: `frontend/src/types/map.ts`

```typescript
/**
 * Map Type Definitions
 */

import type { LngLatBoundsLike, LngLatLike } from 'maplibre-gl';

/** Map viewport state */
export interface MapViewport {
    center: LngLatLike;
    zoom: number;
    bounds?: LngLatBoundsLike;
}

/** Selected date for tile display */
export interface SelectedDate {
    year: number;
    month: number; // 1-12
}

/** Map slice state */
export interface MapState {
    viewport: MapViewport;
    selectedDate: SelectedDate;
    isLoading: boolean;
    error: string | null;
}

/** Map marker for a city */
export interface CityMarker {
    id: string;
    name: string;
    coordinates: [number, number]; // [lng, lat]
    isSelected: boolean;
}

/** Legend configuration */
export interface LegendConfig {
    min: number;
    max: number;
    unit: string;
    colors: {
        min: string;
        zero: string;
        max: string;
    };
    ticks: number[];
}
```

### 10.3 Map Slice (following createDataSlice pattern)

**File**: `frontend/src/store/slices/mapSlice.ts`

```typescript
/**
 * Map Slice
 * 
 * Redux state for the climate map component.
 * Manages viewport, selected date, and loading state.
 */

import { createSlice, type PayloadAction } from '@reduxjs/toolkit';
import type { RootState } from '../index';
import type { MapState, MapViewport, SelectedDate } from '../../types/map';
import { MAP_CONFIG } from '../../constants/mapConfig';

const now = new Date();
const initialState: MapState = {
    viewport: {
        center: MAP_CONFIG.INITIAL_CENTER,
        zoom: MAP_CONFIG.INITIAL_ZOOM,
    },
    selectedDate: {
        // Default to most recent complete month
        year: now.getMonth() === 0 ? now.getFullYear() - 1 : now.getFullYear(),
        month: now.getMonth() === 0 ? 12 : now.getMonth(),
    },
    isLoading: false,
    error: null,
};

const mapSlice = createSlice({
    name: 'map',
    initialState,
    reducers: {
        setViewport(state, action: PayloadAction<Partial<MapViewport>>) {
            state.viewport = { ...state.viewport, ...action.payload };
        },
        setSelectedDate(state, action: PayloadAction<SelectedDate>) {
            const { year, month } = action.payload;
            // Validate date is within available range
            if (year >= MAP_CONFIG.DATA_START_YEAR && month >= 1 && month <= 12) {
                state.selectedDate = { year, month };
            }
        },
        setLoading(state, action: PayloadAction<boolean>) {
            state.isLoading = action.payload;
        },
        setError(state, action: PayloadAction<string | null>) {
            state.error = action.payload;
        },
        resetMapView(state) {
            state.viewport = initialState.viewport;
        },
    },
});

// Actions
export const { setViewport, setSelectedDate, setLoading, setError, resetMapView } = mapSlice.actions;

// Selectors
export const selectMapViewport = (state: RootState) => state.map.viewport;
export const selectSelectedDate = (state: RootState) => state.map.selectedDate;
export const selectMapIsLoading = (state: RootState) => state.map.isLoading;
export const selectMapError = (state: RootState) => state.map.error;

// Derived selector for tile URL base path
export const selectTileBasePath = (state: RootState) => {
    const { year, month } = state.map.selectedDate;
    const monthStr = month.toString().padStart(2, '0');
    return `${year}/${monthStr}`;
};

export default mapSlice.reducer;
```

### 10.4 Tile Service

**File**: `frontend/src/services/TileService.ts`

```typescript
/**
 * Tile Service
 * 
 * Generates URLs for ERA5 temperature anomaly tiles.
 */

import { TILE_BASE_URL, MAP_CONFIG } from '../constants/mapConfig';

/**
 * Generate tile URL for specific date and coordinates
 */
export const getTileUrl = (
    year: number,
    month: number,
    z: number,
    x: number,
    y: number
): string => {
    const monthStr = month.toString().padStart(2, '0');
    return `${TILE_BASE_URL}/${year}/${monthStr}/${z}/${x}/${y}.${MAP_CONFIG.TILE_FORMAT}`;
};

/**
 * Generate tile URL template for MapLibre
 * Returns URL with {z}, {x}, {y} placeholders
 */
export const getTileUrlTemplate = (year: number, month: number): string => {
    const monthStr = month.toString().padStart(2, '0');
    return `${TILE_BASE_URL}/${year}/${monthStr}/{z}/{x}/{y}.${MAP_CONFIG.TILE_FORMAT}`;
};

/**
 * Check if a date has available tile data
 */
export const isDateAvailable = (year: number, month: number): boolean => {
    const now = new Date();
    const requestedDate = new Date(year, month - 1, 1);
    const startDate = new Date(MAP_CONFIG.DATA_START_YEAR, MAP_CONFIG.DATA_START_MONTH - 1, 1);
    
    // Must be after data start and before current month (ERA5 has ~5 day delay)
    const endDate = new Date(now.getFullYear(), now.getMonth() - 1, 1);
    
    return requestedDate >= startDate && requestedDate <= endDate;
};

/**
 * Get list of available months for a given year
 */
export const getAvailableMonths = (year: number): number[] => {
    const months: number[] = [];
    for (let month = 1; month <= 12; month++) {
        if (isDateAvailable(year, month)) {
            months.push(month);
        }
    }
    return months;
};

/**
 * Get list of available years
 */
export const getAvailableYears = (): number[] => {
    const now = new Date();
    const years: number[] = [];
    for (let year = MAP_CONFIG.DATA_START_YEAR; year <= now.getFullYear(); year++) {
        years.push(year);
    }
    return years;
};

/**
 * Get the most recent available date
 */
export const getLatestAvailableDate = (): { year: number; month: number } => {
    const now = new Date();
    // ERA5 has ~5 day delay, so use previous month
    const month = now.getMonth() === 0 ? 12 : now.getMonth();
    const year = now.getMonth() === 0 ? now.getFullYear() - 1 : now.getFullYear();
    return { year, month };
};
```

### 10.5 ClimateMap Component

**File**: `frontend/src/components/maps/ClimateMap/ClimateMap.tsx`

```typescript
/**
 * ClimateMap Component
 * 
 * Interactive map displaying ERA5 temperature anomaly tiles
 * for Germany using MapLibre GL JS.
 */

import { useRef, useEffect, useCallback, useMemo } from 'react';
import type { CSSProperties } from 'react';
import maplibregl, { Map as MapLibreMap } from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { useAppDispatch } from '../../../store/hooks/useAppDispatch';
import { useAppSelector } from '../../../store/hooks/useAppSelector';
import { selectMapViewport, selectSelectedDate, setViewport, setLoading } from '../../../store/slices/mapSlice';
import { MAP_CONFIG, BASE_MAP_STYLE } from '../../../constants/mapConfig';
import { getTileUrlTemplate } from '../../../services/TileService';
import { theme } from '../../../styles/design-system';
import Legend from './Legend';
import DateSelector from './DateSelector';
import CityMarkers from './CityMarkers';

const ANOMALY_LAYER_ID = 'anomaly-tiles';
const ANOMALY_SOURCE_ID = 'anomaly-source';

const getContainerStyle = (height: number | string): CSSProperties => ({
    position: 'relative',
    width: '100%',
    height,
    borderRadius: theme.borderRadius?.md ?? '8px',
    overflow: 'hidden',
});

const getMapStyle = (): CSSProperties => ({
    position: 'absolute',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
});

interface ClimateMapProps {
    height?: number | string;
    showControls?: boolean;
}

const ClimateMap = ({ height = 500, showControls = true }: ClimateMapProps) => {
    const dispatch = useAppDispatch();
    const mapContainerRef = useRef<HTMLDivElement>(null);
    const mapRef = useRef<MapLibreMap | null>(null);
    
    const viewport = useAppSelector(selectMapViewport);
    const selectedDate = useAppSelector(selectSelectedDate);
    
    const tileUrlTemplate = useMemo(() => 
        getTileUrlTemplate(selectedDate.year, selectedDate.month),
        [selectedDate.year, selectedDate.month]
    );

    // Initialize map
    useEffect(() => {
        if (!mapContainerRef.current || mapRef.current) return;

        const map = new maplibregl.Map({
            container: mapContainerRef.current,
            style: BASE_MAP_STYLE,
            center: viewport.center as [number, number],
            zoom: viewport.zoom,
            minZoom: MAP_CONFIG.MIN_ZOOM,
            maxZoom: MAP_CONFIG.MAX_ZOOM,
            maxBounds: MAP_CONFIG.GERMANY_BOUNDS,
        });

        map.on('load', () => {
            // Add anomaly tile source
            map.addSource(ANOMALY_SOURCE_ID, {
                type: 'raster',
                tiles: [tileUrlTemplate],
                tileSize: MAP_CONFIG.TILE_SIZE,
            });

            // Add anomaly tile layer
            map.addLayer({
                id: ANOMALY_LAYER_ID,
                type: 'raster',
                source: ANOMALY_SOURCE_ID,
                paint: {
                    'raster-opacity': 0.8,
                    'raster-fade-duration': 300,
                },
            });

            dispatch(setLoading(false));
        });

        map.on('moveend', () => {
            const center = map.getCenter();
            dispatch(setViewport({
                center: [center.lng, center.lat],
                zoom: map.getZoom(),
            }));
        });

        map.on('error', (e) => {
            console.error('Map error:', e);
        });

        mapRef.current = map;

        return () => {
            map.remove();
            mapRef.current = null;
        };
    }, []); // Only run once on mount

    // Update tile source when date changes
    useEffect(() => {
        const map = mapRef.current;
        if (!map || !map.isStyleLoaded()) return;

        const source = map.getSource(ANOMALY_SOURCE_ID);
        if (source && 'setTiles' in source) {
            dispatch(setLoading(true));
            (source as maplibregl.RasterTileSource).setTiles([tileUrlTemplate]);
            // Loading will be set to false on tile load (simplified here)
            setTimeout(() => dispatch(setLoading(false)), 500);
        }
    }, [tileUrlTemplate, dispatch]);

    const containerStyle = useMemo(() => getContainerStyle(height), [height]);

    return (
        <div style={containerStyle}>
            <div ref={mapContainerRef} style={getMapStyle()} />
            {mapRef.current && <CityMarkers map={mapRef.current} />}
            {showControls && (
                <>
                    <DateSelector />
                    <Legend />
                </>
            )}
        </div>
    );
};

export default ClimateMap;
```

### 10.6 Legend Component

**File**: `frontend/src/components/maps/ClimateMap/Legend.tsx`

```typescript
/**
 * Legend Component
 * 
 * Displays color scale legend for temperature anomaly tiles.
 */

import { useMemo } from 'react';
import type { CSSProperties } from 'react';
import { theme } from '../../../styles/design-system';
import { MAP_CONFIG } from '../../../constants/mapConfig';

const getContainerStyle = (): CSSProperties => ({
    position: 'absolute',
    bottom: 20,
    right: 20,
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    borderRadius: theme.borderRadius?.sm ?? '4px',
    padding: theme.spacing.sm,
    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.2)',
    zIndex: 10,
    minWidth: 200,
});

const getTitleStyle = (): CSSProperties => ({
    fontSize: theme.typography.fontSize.xs,
    fontWeight: theme.typography.fontWeight.medium,
    color: theme.colors.textDark,
    marginBottom: theme.spacing.xs,
    textAlign: 'center' as const,
});

const getGradientStyle = (): CSSProperties => ({
    height: 12,
    width: '100%',
    borderRadius: 2,
    background: `linear-gradient(to right, 
        ${MAP_CONFIG.ANOMALY_COLORS.min}, 
        ${MAP_CONFIG.ANOMALY_COLORS.zero} 50%, 
        ${MAP_CONFIG.ANOMALY_COLORS.max})`,
});

const getLabelsStyle = (): CSSProperties => ({
    display: 'flex',
    justifyContent: 'space-between',
    marginTop: theme.spacing.xs,
    fontSize: theme.typography.fontSize.xs,
    color: theme.colors.textDark,
});

interface LegendProps {
    title?: string;
}

const Legend = ({ title = 'Temperaturanomalie' }: LegendProps) => {
    const ticks = useMemo(() => {
        const { ANOMALY_MIN, ANOMALY_MAX } = MAP_CONFIG;
        return [ANOMALY_MIN, 0, ANOMALY_MAX].map(value => 
            `${value >= 0 ? '+' : ''}${value}°C`
        );
    }, []);

    return (
        <div style={getContainerStyle()}>
            <div style={getTitleStyle()}>{title}</div>
            <div style={getGradientStyle()} />
            <div style={getLabelsStyle()}>
                {ticks.map((tick, i) => (
                    <span key={i}>{tick}</span>
                ))}
            </div>
        </div>
    );
};

export default Legend;
```

### 10.7 DateSelector Component

**File**: `frontend/src/components/maps/ClimateMap/DateSelector.tsx`

```typescript
/**
 * DateSelector Component
 * 
 * Month/year picker for selecting which anomaly tiles to display.
 */

import { useMemo, useCallback } from 'react';
import type { CSSProperties, ChangeEvent } from 'react';
import { useAppDispatch } from '../../../store/hooks/useAppDispatch';
import { useAppSelector } from '../../../store/hooks/useAppSelector';
import { selectSelectedDate, setSelectedDate } from '../../../store/slices/mapSlice';
import { getAvailableYears, getAvailableMonths, getLatestAvailableDate } from '../../../services/TileService';
import { theme } from '../../../styles/design-system';

const MONTH_NAMES = [
    'Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
    'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'
];

const getContainerStyle = (): CSSProperties => ({
    position: 'absolute',
    top: 20,
    left: 20,
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    borderRadius: theme.borderRadius?.sm ?? '4px',
    padding: theme.spacing.sm,
    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.2)',
    zIndex: 10,
    display: 'flex',
    gap: theme.spacing.sm,
    alignItems: 'center',
});

const getSelectStyle = (): CSSProperties => ({
    padding: `${theme.spacing.xs}px ${theme.spacing.sm}px`,
    borderRadius: theme.borderRadius?.sm ?? '4px',
    border: `1px solid ${theme.colors.border}`,
    fontSize: theme.typography.fontSize.sm,
    backgroundColor: 'white',
    cursor: 'pointer',
});

const getButtonStyle = (): CSSProperties => ({
    padding: `${theme.spacing.xs}px ${theme.spacing.sm}px`,
    borderRadius: theme.borderRadius?.sm ?? '4px',
    border: 'none',
    backgroundColor: theme.colors.primary,
    color: 'white',
    fontSize: theme.typography.fontSize.sm,
    cursor: 'pointer',
    fontWeight: theme.typography.fontWeight.medium,
});

const DateSelector = () => {
    const dispatch = useAppDispatch();
    const selectedDate = useAppSelector(selectSelectedDate);
    
    const availableYears = useMemo(() => getAvailableYears(), []);
    const availableMonths = useMemo(
        () => getAvailableMonths(selectedDate.year),
        [selectedDate.year]
    );

    const handleYearChange = useCallback((e: ChangeEvent<HTMLSelectElement>) => {
        const year = parseInt(e.target.value, 10);
        const months = getAvailableMonths(year);
        // If current month not available in new year, use latest available
        const month = months.includes(selectedDate.month) 
            ? selectedDate.month 
            : months[months.length - 1];
        dispatch(setSelectedDate({ year, month }));
    }, [dispatch, selectedDate.month]);

    const handleMonthChange = useCallback((e: ChangeEvent<HTMLSelectElement>) => {
        const month = parseInt(e.target.value, 10);
        dispatch(setSelectedDate({ ...selectedDate, month }));
    }, [dispatch, selectedDate]);

    const handleLatestClick = useCallback(() => {
        const latest = getLatestAvailableDate();
        dispatch(setSelectedDate(latest));
    }, [dispatch]);

    return (
        <div style={getContainerStyle()}>
            <select 
                style={getSelectStyle()} 
                value={selectedDate.month}
                onChange={handleMonthChange}
            >
                {availableMonths.map(month => (
                    <option key={month} value={month}>
                        {MONTH_NAMES[month - 1]}
                    </option>
                ))}
            </select>
            
            <select 
                style={getSelectStyle()} 
                value={selectedDate.year}
                onChange={handleYearChange}
            >
                {availableYears.map(year => (
                    <option key={year} value={year}>{year}</option>
                ))}
            </select>

            <button 
                style={getButtonStyle()} 
                onClick={handleLatestClick}
                type="button"
            >
                Aktuell
            </button>
        </div>
    );
};

export default DateSelector;
```

### 10.8 CityMarkers Component

**File**: `frontend/src/components/maps/ClimateMap/CityMarkers.tsx`

```typescript
/**
 * CityMarkers Component
 * 
 * Renders clickable city markers on the map.
 */

import { useEffect, useRef } from 'react';
import maplibregl, { Map as MapLibreMap, Marker } from 'maplibre-gl';
import { useAppDispatch } from '../../../store/hooks/useAppDispatch';
import { useAppSelector } from '../../../store/hooks/useAppSelector';
import { selectCities } from '../../../store/slices/cityDataSlice';
import { selectCity } from '../../../store/slices/selectedCitySlice';
import type { ICity } from '../../../classes/City';
import { theme } from '../../../styles/design-system';

interface CityMarkersProps {
    map: MapLibreMap;
    maxMarkers?: number;
}

const createMarkerElement = (city: ICity, isSelected: boolean): HTMLDivElement => {
    const el = document.createElement('div');
    el.style.width = isSelected ? '16px' : '12px';
    el.style.height = isSelected ? '16px' : '12px';
    el.style.borderRadius = '50%';
    el.style.backgroundColor = isSelected ? theme.colors.primary : theme.colors.hot;
    el.style.border = `2px solid ${isSelected ? 'white' : 'rgba(255,255,255,0.7)'}`;
    el.style.cursor = 'pointer';
    el.style.boxShadow = '0 2px 4px rgba(0,0,0,0.3)';
    el.style.transition = 'all 0.2s ease';
    el.title = city.name;
    
    el.addEventListener('mouseenter', () => {
        el.style.transform = 'scale(1.2)';
    });
    el.addEventListener('mouseleave', () => {
        el.style.transform = 'scale(1)';
    });
    
    return el;
};

const CityMarkers = ({ map, maxMarkers = 50 }: CityMarkersProps) => {
    const dispatch = useAppDispatch();
    const cities = useAppSelector(selectCities);
    const selectedCityId = useAppSelector(state => state.selectedCity.cityId);
    const markersRef = useRef<Map<string, Marker>>(new Map());

    useEffect(() => {
        const cityList = Object.values(cities).slice(0, maxMarkers);
        
        // Remove old markers
        markersRef.current.forEach((marker, id) => {
            if (!cityList.find(c => c.id === id)) {
                marker.remove();
                markersRef.current.delete(id);
            }
        });

        // Add/update markers
        cityList.forEach(city => {
            const isSelected = city.id === selectedCityId;
            const existingMarker = markersRef.current.get(city.id);
            
            if (existingMarker) {
                // Update marker if selection changed
                const el = createMarkerElement(city, isSelected);
                el.addEventListener('click', () => dispatch(selectCity(city.id)));
                existingMarker.getElement().replaceWith(el);
            } else {
                // Create new marker
                const el = createMarkerElement(city, isSelected);
                el.addEventListener('click', () => dispatch(selectCity(city.id)));
                
                const marker = new maplibregl.Marker({ element: el })
                    .setLngLat([city.lon, city.lat])
                    .addTo(map);
                    
                markersRef.current.set(city.id, marker);
            }
        });

        return () => {
            markersRef.current.forEach(marker => marker.remove());
            markersRef.current.clear();
        };
    }, [cities, selectedCityId, map, dispatch, maxMarkers]);

    return null; // Markers are added directly to map
};

export default CityMarkers;
```

### 10.9 useMapTiles Hook

**File**: `frontend/src/hooks/useMapTiles.ts`

```typescript
/**
 * useMapTiles Hook
 * 
 * Custom hook providing all data needed for the ClimateMap component.
 */

import { useMemo } from 'react';
import { useAppSelector } from '../store/hooks/useAppSelector';
import { selectMapViewport, selectSelectedDate, selectMapIsLoading, selectMapError } from '../store/slices/mapSlice';
import { selectCities, selectCityDataStatus } from '../store/slices/cityDataSlice';
import { getTileUrlTemplate, isDateAvailable, getLatestAvailableDate } from '../services/TileService';
import type { MapViewport, SelectedDate, CityMarker } from '../types/map';

export interface UseMapTilesReturn {
    viewport: MapViewport;
    selectedDate: SelectedDate;
    tileUrlTemplate: string;
    isLoading: boolean;
    error: string | null;
    isDateValid: boolean;
    cityMarkers: CityMarker[];
    citiesLoaded: boolean;
}

export function useMapTiles(): UseMapTilesReturn {
    const viewport = useAppSelector(selectMapViewport);
    const selectedDate = useAppSelector(selectSelectedDate);
    const isLoading = useAppSelector(selectMapIsLoading);
    const error = useAppSelector(selectMapError);
    const cities = useAppSelector(selectCities);
    const cityDataStatus = useAppSelector(selectCityDataStatus);
    const selectedCityId = useAppSelector(state => state.selectedCity.cityId);

    const tileUrlTemplate = useMemo(
        () => getTileUrlTemplate(selectedDate.year, selectedDate.month),
        [selectedDate.year, selectedDate.month]
    );

    const isDateValid = useMemo(
        () => isDateAvailable(selectedDate.year, selectedDate.month),
        [selectedDate.year, selectedDate.month]
    );

    const cityMarkers = useMemo((): CityMarker[] => {
        return Object.values(cities).map(city => ({
            id: city.id,
            name: city.name,
            coordinates: [city.lon, city.lat] as [number, number],
            isSelected: city.id === selectedCityId,
        }));
    }, [cities, selectedCityId]);

    const citiesLoaded = cityDataStatus === 'succeeded';

    return {
        viewport,
        selectedDate,
        tileUrlTemplate,
        isLoading,
        error,
        isDateValid,
        cityMarkers,
        citiesLoaded,
    };
}
```

### 10.10 Test Examples

**File**: `frontend/src/store/slices/__tests__/mapSlice.test.ts`

```typescript
/**
 * Map Slice Tests
 */

import { describe, it, expect, beforeEach } from 'vitest';
import mapReducer, {
    setViewport,
    setSelectedDate,
    setLoading,
    setError,
    resetMapView,
    selectMapViewport,
    selectSelectedDate,
} from '../mapSlice';
import type { MapState } from '../../../types/map';
import { MAP_CONFIG } from '../../../constants/mapConfig';

describe('mapSlice', () => {
    let initialState: MapState;

    beforeEach(() => {
        initialState = {
            viewport: {
                center: MAP_CONFIG.INITIAL_CENTER,
                zoom: MAP_CONFIG.INITIAL_ZOOM,
            },
            selectedDate: { year: 2025, month: 12 },
            isLoading: false,
            error: null,
        };
    });

    describe('reducers', () => {
        it('should handle setViewport', () => {
            const newViewport = { center: [10.0, 51.0] as [number, number], zoom: 8 };
            const state = mapReducer(initialState, setViewport(newViewport));
            expect(state.viewport.center).toEqual(newViewport.center);
            expect(state.viewport.zoom).toBe(8);
        });

        it('should handle setSelectedDate', () => {
            const state = mapReducer(initialState, setSelectedDate({ year: 2023, month: 6 }));
            expect(state.selectedDate.year).toBe(2023);
            expect(state.selectedDate.month).toBe(6);
        });

        it('should reject invalid dates before data start', () => {
            const state = mapReducer(initialState, setSelectedDate({ year: 2010, month: 1 }));
            // Should not change from initial
            expect(state.selectedDate.year).toBe(initialState.selectedDate.year);
        });

        it('should handle setLoading', () => {
            const state = mapReducer(initialState, setLoading(true));
            expect(state.isLoading).toBe(true);
        });

        it('should handle setError', () => {
            const state = mapReducer(initialState, setError('Test error'));
            expect(state.error).toBe('Test error');
        });

        it('should handle resetMapView', () => {
            const modifiedState = {
                ...initialState,
                viewport: { center: [12.0, 52.0] as [number, number], zoom: 10 },
            };
            const state = mapReducer(modifiedState, resetMapView());
            expect(state.viewport.center).toEqual(MAP_CONFIG.INITIAL_CENTER);
            expect(state.viewport.zoom).toBe(MAP_CONFIG.INITIAL_ZOOM);
        });
    });

    describe('selectors', () => {
        const mockState = { map: initialState } as any;

        it('selectMapViewport returns viewport', () => {
            expect(selectMapViewport(mockState)).toEqual(initialState.viewport);
        });

        it('selectSelectedDate returns selected date', () => {
            expect(selectSelectedDate(mockState)).toEqual(initialState.selectedDate);
        });
    });
});
```

**File**: `frontend/src/services/__tests__/TileService.test.ts`

```typescript
/**
 * Tile Service Tests
 */

import { describe, it, expect } from 'vitest';
import {
    getTileUrl,
    getTileUrlTemplate,
    isDateAvailable,
    getAvailableYears,
    getAvailableMonths,
    getLatestAvailableDate,
} from '../TileService';

describe('TileService', () => {
    describe('getTileUrl', () => {
        it('generates correct URL with zero-padded month', () => {
            const url = getTileUrl(2024, 3, 8, 134, 84);
            expect(url).toContain('/2024/03/8/134/84.webp');
        });

        it('generates correct URL for December', () => {
            const url = getTileUrl(2024, 12, 7, 100, 50);
            expect(url).toContain('/2024/12/7/100/50.webp');
        });
    });

    describe('getTileUrlTemplate', () => {
        it('includes placeholder tokens', () => {
            const template = getTileUrlTemplate(2024, 6);
            expect(template).toContain('{z}');
            expect(template).toContain('{x}');
            expect(template).toContain('{y}');
            expect(template).toContain('/2024/06/');
        });
    });

    describe('isDateAvailable', () => {
        it('returns false for dates before 2016', () => {
            expect(isDateAvailable(2015, 12)).toBe(false);
        });

        it('returns true for valid historical dates', () => {
            expect(isDateAvailable(2020, 6)).toBe(true);
        });

        // Note: Future date tests depend on current date
    });

    describe('getAvailableYears', () => {
        it('starts from 2016', () => {
            const years = getAvailableYears();
            expect(years[0]).toBe(2016);
        });

        it('includes recent years', () => {
            const years = getAvailableYears();
            expect(years).toContain(2024);
        });
    });

    describe('getAvailableMonths', () => {
        it('returns all 12 months for complete historical year', () => {
            const months = getAvailableMonths(2020);
            expect(months).toHaveLength(12);
            expect(months).toEqual([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]);
        });

        it('returns empty array for years before data start', () => {
            const months = getAvailableMonths(2010);
            expect(months).toHaveLength(0);
        });
    });

    describe('getLatestAvailableDate', () => {
        it('returns valid year and month', () => {
            const { year, month } = getLatestAvailableDate();
            expect(year).toBeGreaterThanOrEqual(2016);
            expect(month).toBeGreaterThanOrEqual(1);
            expect(month).toBeLessThanOrEqual(12);
        });
    });
});
```

### 10.11 Mock Data for Testing

**File**: `frontend/src/__mocks__/mapMocks.ts`

```typescript
/**
 * Mock data for map component testing
 */

import type { MapState, CityMarker } from '../types/map';
import { MAP_CONFIG } from '../constants/mapConfig';

export const mockMapState: MapState = {
    viewport: {
        center: MAP_CONFIG.INITIAL_CENTER,
        zoom: MAP_CONFIG.INITIAL_ZOOM,
    },
    selectedDate: {
        year: 2024,
        month: 6,
    },
    isLoading: false,
    error: null,
};

export const mockCityMarkers: CityMarker[] = [
    { id: '1', name: 'Berlin', coordinates: [13.405, 52.52], isSelected: false },
    { id: '2', name: 'München', coordinates: [11.576, 48.137], isSelected: false },
    { id: '3', name: 'Hamburg', coordinates: [9.993, 53.551], isSelected: true },
    { id: '4', name: 'Köln', coordinates: [6.960, 50.938], isSelected: false },
    { id: '5', name: 'Frankfurt', coordinates: [8.682, 50.111], isSelected: false },
    { id: '6', name: 'Stuttgart', coordinates: [9.183, 48.783], isSelected: false },
    { id: '7', name: 'Düsseldorf', coordinates: [6.775, 51.227], isSelected: false },
    { id: '8', name: 'Leipzig', coordinates: [12.374, 51.340], isSelected: false },
    { id: '9', name: 'Dortmund', coordinates: [7.466, 51.514], isSelected: false },
    { id: '10', name: 'Dresden', coordinates: [13.738, 51.051], isSelected: false },
];

// Mock MapLibre Map instance for testing
export const createMockMap = () => ({
    on: vi.fn(),
    off: vi.fn(),
    remove: vi.fn(),
    addSource: vi.fn(),
    addLayer: vi.fn(),
    getSource: vi.fn(() => ({ setTiles: vi.fn() })),
    getCenter: vi.fn(() => ({ lng: 10.45, lat: 51.15 })),
    getZoom: vi.fn(() => 7),
    isStyleLoaded: vi.fn(() => true),
});
```
