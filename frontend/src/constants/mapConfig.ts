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
    MIN_ZOOM: 5,
    MAX_ZOOM: 7,
    INITIAL_ZOOM: 5,

    // Scroll-wheel zoom increment (fractional for smooth zooming)
    ZOOM_STEP: 0.25,

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

// Empty base style – no OSM or other background layers.
// Only the anomaly raster tiles (land silhouette) are rendered on the map.
export const BASE_MAP_STYLE = {
    version: 8 as const,
    sources: {},
    layers: [],
};
