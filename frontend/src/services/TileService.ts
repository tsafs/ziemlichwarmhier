/**
 * Tile Service
 *
 * Generates URLs for ERA5-Land temperature anomaly tiles.
 */

import { TILE_BASE_URL, MAP_CONFIG } from '../constants/mapConfig.js';

/**
 * Generate tile URL for specific date and coordinates
 */
export const getTileUrl = (
    year: number,
    month: number,
    z: number,
    x: number,
    y: number,
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

    // Must be after data start and before current month (ERA5-Land has ~5 day delay)
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
    // ERA5-Land has ~5 day delay, so use previous month
    const month = now.getMonth() === 0 ? 12 : now.getMonth();
    const year = now.getMonth() === 0 ? now.getFullYear() - 1 : now.getFullYear();
    return { year, month };
};
