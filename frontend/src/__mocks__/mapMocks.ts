/**
 * Mock data for map component testing
 */

import { vi } from 'vitest';
import type { MapState, CityMarker } from '../types/map.js';
import { MAP_CONFIG } from '../constants/mapConfig.js';

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
