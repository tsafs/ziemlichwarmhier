/**
 * Fixture loader — provides raw fixture strings and a `mockFetchWithFixtures`
 * helper so Vitest tests can intercept `fetch()` calls and return deterministic
 * static data without network access.
 *
 * All fixtures target the NEW ERA5-Land product (botox plans):
 *   - LocationMetrics JSON (Phase 5/8)
 *   - Plot dataset CSVs (Phase 9)
 *   - City-grid correlation JSON (Phase 10)
 *   - WebP tile stub (Phase 4)
 *
 * Usage:
 *   import { mockFetchWithFixtures, GERMANY_METRICS_JSON } from '../__fixtures__';
 *   beforeEach(() => mockFetchWithFixtures(vi));
 *   afterEach(() => vi.restoreAllMocks());
 */

import { readFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dir = dirname(fileURLToPath(import.meta.url));
const read = (rel: string) => readFileSync(resolve(__dir, rel), 'utf-8');
const readBin = (rel: string) => readFileSync(resolve(__dir, rel));

// ── Raw fixture strings ────────────────────────────────────────────────

/** Country-level MetricsFile JSON (Phase 5/8) */
export const GERMANY_METRICS_JSON = read('metrics/germany.json');

/** Per-tile MetricsFile JSON — München grid cell 57_69 (Phase 5/8) */
export const TILE_57_69_METRICS_JSON = read('metrics/tiles/57_69.json');

/** Temperature evolution plot CSV (Phase 9) */
export const TEMPERATURE_EVOLUTION_CSV = read('plots/temperature_evolution/germany.csv');

/** Seasonal warming plot CSV (Phase 9) */
export const SEASONAL_WARMING_CSV = read('plots/seasonal_warming/germany.csv');

/** Extremes (inverted) plot CSV (Phase 9) */
export const EXTREMES_CSV = read('plots/extremes/germany.csv');

/** Monthly distribution plot CSV (Phase 9) */
export const MONTHLY_DISTRIBUTION_CSV = read('plots/monthly_distribution/germany.csv');

/** City-grid correlation JSON (Phase 10) */
export const CITY_GRID_CORRELATION_JSON = read('cities/city_grid_correlation.json');

/** Minimal valid WebP tile (Phase 4) */
export const SAMPLE_TILE_WEBP = readBin('tiles/sample.webp');

// ── Parsed helpers ─────────────────────────────────────────────────────

export const parseGermanyMetrics = () => JSON.parse(GERMANY_METRICS_JSON);
export const parseTileMetrics = () => JSON.parse(TILE_57_69_METRICS_JSON);
export const parseCityGridCorrelation = () => JSON.parse(CITY_GRID_CORRELATION_JSON);

// ── Constants ──────────────────────────────────────────────────────────

/** Sample tile IDs from fixtures */
export const FIXTURE_TILE_IDS = ['57_69'] as const;

/** Sample city slugs from fixtures */
export const FIXTURE_CITY_SLUGS = ['berlin', 'muenchen', 'freiburg-im-breisgau'] as const;

// ── Fetch mock helper ──────────────────────────────────────────────────

type VitestLike = { fn: (impl?: (...args: any[]) => any) => any; spyOn: (...a: any[]) => any };

/**
 * URL-pattern → fixture-content map used by the mock.
 * Patterns match the fetch URL conventions from the botox phase plans.
 */
const URL_FIXTURE_MAP: Array<[pattern: RegExp, content: string | Buffer, contentType: string]> = [
    // Metrics (Phase 5/8)
    [/\/data\/metrics\/germany\.json/, GERMANY_METRICS_JSON, 'application/json'],
    [/\/data\/metrics\/tiles\/57_69\.json/, TILE_57_69_METRICS_JSON, 'application/json'],
    // Plot CSVs (Phase 9)
    [/\/data\/plots\/temperature_evolution\/.*\.csv/, TEMPERATURE_EVOLUTION_CSV, 'text/csv'],
    [/\/data\/plots\/seasonal_warming\/.*\.csv/, SEASONAL_WARMING_CSV, 'text/csv'],
    [/\/data\/plots\/extremes\/.*\.csv/, EXTREMES_CSV, 'text/csv'],
    [/\/data\/plots\/monthly_distribution\/.*\.csv/, MONTHLY_DISTRIBUTION_CSV, 'text/csv'],
    // City correlation (Phase 10)
    [/\/data\/cities\/city_grid_correlation\.json/, CITY_GRID_CORRELATION_JSON, 'application/json'],
    // Tiles (Phase 4)
    [/\.webp$/, String.fromCharCode(...SAMPLE_TILE_WEBP), 'image/webp'],
];

/**
 * Replace `globalThis.fetch` with a mock that resolves fixture content for
 * known URL patterns, and returns 404 for unknown URLs.
 *
 * @example
 *   beforeEach(() => mockFetchWithFixtures(vi));
 */
export function mockFetchWithFixtures(vi: VitestLike) {
    const impl = async (input: RequestInfo | URL, _init?: RequestInit) => {
        const url = typeof input === 'string' ? input : String(input);

        for (const [pattern, content, contentType] of URL_FIXTURE_MAP) {
            if (pattern.test(url)) {
                return new Response(typeof content === 'string' ? content : content.toString(), {
                    status: 200,
                    headers: { 'Content-Type': contentType },
                });
            }
        }

        return new Response('Not Found (fixture miss)', { status: 404 });
    };

    const spy = vi.spyOn(globalThis, 'fetch').mockImplementation(impl as any);
    return spy;
}
