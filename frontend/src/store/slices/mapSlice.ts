/**
 * Map Slice
 *
 * Redux state for the climate map component.
 * Manages viewport, selected date, and loading state.
 */

import { createSlice, type PayloadAction } from '@reduxjs/toolkit';
import type { RootState } from '../index.js';
import type { MapState, MapViewport, SelectedDate } from '../../types/map.js';
import { MAP_CONFIG } from '../../constants/mapConfig.js';

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
