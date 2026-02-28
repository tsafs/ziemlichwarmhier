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
