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
} from '../mapSlice.js';
import type { MapState } from '../../../types/map.js';
import { MAP_CONFIG } from '../../../constants/mapConfig.js';

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
            const newViewport = { center: [10.0, 51.0] as [number, number], zoom: 6.5 };
            const state = mapReducer(initialState, setViewport(newViewport));
            expect(state.viewport.center).toEqual(newViewport.center);
            expect(state.viewport.zoom).toBe(6.5);
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

        it('should reject invalid month 0', () => {
            const state = mapReducer(initialState, setSelectedDate({ year: 2023, month: 0 }));
            expect(state.selectedDate.month).toBe(initialState.selectedDate.month);
        });

        it('should reject invalid month 13', () => {
            const state = mapReducer(initialState, setSelectedDate({ year: 2023, month: 13 }));
            expect(state.selectedDate.month).toBe(initialState.selectedDate.month);
        });

        it('should handle setLoading true', () => {
            const state = mapReducer(initialState, setLoading(true));
            expect(state.isLoading).toBe(true);
        });

        it('should handle setLoading false', () => {
            const loadingState = { ...initialState, isLoading: true };
            const state = mapReducer(loadingState, setLoading(false));
            expect(state.isLoading).toBe(false);
        });

        it('should handle setError', () => {
            const state = mapReducer(initialState, setError('Test error'));
            expect(state.error).toBe('Test error');
        });

        it('should handle setError null', () => {
            const errorState = { ...initialState, error: 'previous error' };
            const state = mapReducer(errorState, setError(null));
            expect(state.error).toBeNull();
        });

        it('should handle resetMapView', () => {
            const modifiedState = {
                ...initialState,
                viewport: { center: [12.0, 52.0] as [number, number], zoom: 7 },
            };
            const state = mapReducer(modifiedState, resetMapView());
            expect(state.viewport.center).toEqual(MAP_CONFIG.INITIAL_CENTER);
            expect(state.viewport.zoom).toBe(MAP_CONFIG.INITIAL_ZOOM);
        });

        it('should preserve selectedDate on resetMapView', () => {
            const modifiedState = {
                ...initialState,
                selectedDate: { year: 2022, month: 3 },
                viewport: { center: [12.0, 52.0] as [number, number], zoom: 7 },
            };
            const state = mapReducer(modifiedState, resetMapView());
            expect(state.selectedDate).toEqual({ year: 2022, month: 3 });
        });
    });

    describe('selectors', () => {
        it('selectMapViewport returns viewport', () => {
            const mockState = { map: initialState } as any;
            expect(selectMapViewport(mockState)).toEqual(initialState.viewport);
        });

        it('selectSelectedDate returns selected date', () => {
            const mockState = { map: initialState } as any;
            expect(selectSelectedDate(mockState)).toEqual(initialState.selectedDate);
        });
    });

    describe('data boundaries', () => {
        it('should accept date exactly at data start', () => {
            const state = mapReducer(
                initialState,
                setSelectedDate({ year: MAP_CONFIG.DATA_START_YEAR, month: MAP_CONFIG.DATA_START_MONTH }),
            );
            expect(state.selectedDate.year).toBe(MAP_CONFIG.DATA_START_YEAR);
        });
    });
});
