/**
 * useMapTiles Hook Tests
 *
 * Tests the custom hook that aggregates all map-related state from Redux.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import type { PropsWithChildren } from 'react';
import { createElement } from 'react';
import { useMapTiles } from '../useMapTiles.js';
import mapReducer, { setSelectedDate } from '../../store/slices/mapSlice.js';
import { MAP_CONFIG } from '../../constants/mapConfig.js';

// Minimal store with only the slices useMapTiles reads
function createTestStore(overrides: Record<string, any> = {}) {
    return configureStore({
        reducer: {
            map: mapReducer,
            cityData: () => ({
                status: 'succeeded',
                data: {
                    berlin: {
                        id: 'berlin',
                        name: 'Berlin',
                        lat: 52.52,
                        lon: 13.405,
                        stationId: 'S1',
                        distanceToStation: 3.2,
                    },
                },
                error: null,
                ...overrides.cityData,
            }),
            selectedCity: () => ({
                cityId: null,
                isCityChanging: false,
                ...overrides.selectedCity,
            }),
        },
    });
}

function createWrapper(store: ReturnType<typeof createTestStore>) {
    return ({ children }: PropsWithChildren) =>
        createElement(Provider, { store, children });
}

describe('useMapTiles', () => {
    let store: ReturnType<typeof createTestStore>;

    beforeEach(() => {
        store = createTestStore();
    });

    it('returns initial viewport from Redux', () => {
        const { result } = renderHook(() => useMapTiles(), {
            wrapper: createWrapper(store),
        });

        expect(result.current.viewport.center).toEqual(MAP_CONFIG.INITIAL_CENTER);
        expect(result.current.viewport.zoom).toBe(MAP_CONFIG.INITIAL_ZOOM);
    });

    it('returns the selected date', () => {
        store.dispatch(setSelectedDate({ year: 2022, month: 8 }));
        const { result } = renderHook(() => useMapTiles(), {
            wrapper: createWrapper(store),
        });

        expect(result.current.selectedDate).toEqual({ year: 2022, month: 8 });
    });

    it('generates a tile URL template matching the selected date', () => {
        store.dispatch(setSelectedDate({ year: 2023, month: 3 }));
        const { result } = renderHook(() => useMapTiles(), {
            wrapper: createWrapper(store),
        });

        expect(result.current.tileUrlTemplate).toContain('/2023/03/');
        expect(result.current.tileUrlTemplate).toContain('{z}');
        expect(result.current.tileUrlTemplate).toContain('{x}');
        expect(result.current.tileUrlTemplate).toContain('{y}');
    });

    it('builds city markers from Redux city data', () => {
        const { result } = renderHook(() => useMapTiles(), {
            wrapper: createWrapper(store),
        });

        expect(result.current.cityMarkers).toHaveLength(1);
        expect(result.current.cityMarkers[0]).toMatchObject({
            id: 'berlin',
            name: 'Berlin',
            coordinates: [13.405, 52.52],
            isSelected: false,
        });
    });

    it('marks the selected city as isSelected', () => {
        const storeWithSelection = createTestStore({
            selectedCity: { cityId: 'berlin', isCityChanging: false },
        });

        const { result } = renderHook(() => useMapTiles(), {
            wrapper: createWrapper(storeWithSelection),
        });

        expect(result.current.cityMarkers[0]!.isSelected).toBe(true);
    });

    it('reports citiesLoaded based on cityData status', () => {
        const { result } = renderHook(() => useMapTiles(), {
            wrapper: createWrapper(store),
        });

        expect(result.current.citiesLoaded).toBe(true);
    });

    it('reports citiesLoaded false when status is not succeeded', () => {
        const storeLoading = createTestStore({
            cityData: { status: 'loading', data: {}, error: null },
        });

        const { result } = renderHook(() => useMapTiles(), {
            wrapper: createWrapper(storeLoading),
        });

        expect(result.current.citiesLoaded).toBe(false);
    });

    it('validates date availability', () => {
        store.dispatch(setSelectedDate({ year: 2020, month: 6 }));
        const { result } = renderHook(() => useMapTiles(), {
            wrapper: createWrapper(store),
        });

        expect(result.current.isDateValid).toBe(true);
    });
});
