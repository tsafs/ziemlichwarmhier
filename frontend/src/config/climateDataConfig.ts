/**
 * Climate Data Configuration
 *
 * Provider-agnostic configuration resolved from environment at build time.
 * All services import this config instead of hardcoding dataset URLs and labels.
 * Swapping to a different data source = change env vars, no code changes.
 */

export interface ClimateDataConfig {
    /** Short identifier, e.g. 'era5-land' */
    datasetId: string;
    /** Human-readable name for UI display */
    displayName: string;
    /** Base URL for tile assets */
    tileBaseUrl: string;
    /** Base URL for metrics JSON */
    metricsBaseUrl: string;
    /** Base URL for plot CSV data */
    plotDataBaseUrl: string;
    /** Native grid resolution (degrees) */
    nativeResolution: number;
    /** Data availability delay (days) */
    dataDelayDays: number;
    /** Grid resolution label for display */
    gridResolutionLabel: string;
}

// Resolved from environment at build time
export const climateDataConfig: ClimateDataConfig = {
    datasetId: import.meta.env.VITE_CLIMATE_DATASET_ID ?? 'era5-land',
    displayName: import.meta.env.VITE_CLIMATE_DISPLAY_NAME ?? 'ERA5-Land',
    tileBaseUrl: import.meta.env.VITE_TILE_BASE_URL ?? '/mock-tiles',
    metricsBaseUrl: import.meta.env.VITE_METRICS_BASE_URL ?? '/data/metrics',
    plotDataBaseUrl: import.meta.env.VITE_PLOT_DATA_BASE_URL ?? '/data/plots',
    nativeResolution: parseFloat(import.meta.env.VITE_NATIVE_RESOLUTION ?? '0.1'),
    dataDelayDays: parseInt(import.meta.env.VITE_DATA_DELAY_DAYS ?? '5', 10),
    gridResolutionLabel: import.meta.env.VITE_GRID_RESOLUTION_LABEL ?? '~9 km',
};
