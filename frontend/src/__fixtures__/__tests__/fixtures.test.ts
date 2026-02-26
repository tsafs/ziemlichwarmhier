import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
    GERMANY_METRICS_JSON,
    TILE_57_69_METRICS_JSON,
    TEMPERATURE_EVOLUTION_CSV,
    SEASONAL_WARMING_CSV,
    EXTREMES_CSV,
    MONTHLY_DISTRIBUTION_CSV,
    CITY_GRID_CORRELATION_JSON,
    SAMPLE_TILE_WEBP,
    parseGermanyMetrics,
    parseTileMetrics,
    parseCityGridCorrelation,
    FIXTURE_TILE_IDS,
    FIXTURE_CITY_SLUGS,
    mockFetchWithFixtures,
} from '../index.js';

// ── Fixture loading tests ───────────────────────────────────────────────

describe('Fixture loader — metrics (Phase 5/8)', () => {
    it('parses germany.json with all 8 metric sub-objects', () => {
        const data = parseGermanyMetrics();
        expect(data.version).toBe('1.0');
        expect(data.source).toBe('era5-land');
        expect(data.data).toHaveProperty('fiveYearAnomaly');
        expect(data.data).toHaveProperty('warmingRate');
        expect(data.data).toHaveProperty('recordDays');
        expect(data.data).toHaveProperty('winterWarming');
        expect(data.data).toHaveProperty('seasonalWarming');
        expect(data.data).toHaveProperty('thresholdDays');
        expect(data.data).toHaveProperty('snowDaysLost');
        expect(data.data).toHaveProperty('comfortableDays');
    });

    it('germany fiveYearAnomaly has correct shape', () => {
        const { fiveYearAnomaly } = parseGermanyMetrics().data;
        expect(fiveYearAnomaly).toMatchObject({
            value: expect.any(Number),
            periodStart: 2021,
            periodEnd: 2025,
            referenceStart: 1961,
            referenceEnd: 1990,
        });
    });

    it('parses tile 57_69 metrics (München)', () => {
        const data = parseTileMetrics();
        expect(data.version).toBe('1.0');
        expect(data.data.fiveYearAnomaly.value).toBeGreaterThan(0);
    });

    it('tile metrics differ from national metrics', () => {
        const national = parseGermanyMetrics().data.fiveYearAnomaly.value;
        const tile = parseTileMetrics().data.fiveYearAnomaly.value;
        expect(tile).not.toBe(national);
    });
});

describe('Fixture loader — plot CSVs (Phase 9)', () => {
    it('temperature_evolution CSV has correct headers', () => {
        const header = TEMPERATURE_EVOLUTION_CSV.trim().split('\n')[0];
        expect(header).toBe('year,temperature,anomaly,trend');
    });

    it('seasonal_warming CSV has correct headers', () => {
        const header = SEASONAL_WARMING_CSV.trim().split('\n')[0];
        expect(header).toBe('year,winter,spring,summer,fall');
    });

    it('extremes CSV has correct headers', () => {
        const header = EXTREMES_CSV.trim().split('\n')[0];
        expect(header).toBe('year,hot_days,cold_days,reference_hot,reference_cold');
    });

    it('monthly_distribution CSV has 12 data rows (months)', () => {
        const lines = MONTHLY_DISTRIBUTION_CSV.trim().split('\n');
        expect(lines.length).toBe(13); // header + 12 months
    });

    it('monthly_distribution CSV has correct headers', () => {
        const header = MONTHLY_DISTRIBUTION_CSV.trim().split('\n')[0];
        expect(header).toBe(
            'month,cur_min,cur_q1,cur_median,cur_q3,cur_max,cur_mean,ref_min,ref_q1,ref_median,ref_q3,ref_max,ref_mean'
        );
    });
});

describe('Fixture loader — city correlation (Phase 10)', () => {
    it('parses city_grid_correlation with meta and cities', () => {
        const data = parseCityGridCorrelation();
        expect(data.meta.grid_resolution).toBe(0.1);
        expect(data.cities).toHaveLength(3);
    });

    it('each city has required fields', () => {
        const { cities } = parseCityGridCorrelation();
        for (const city of cities) {
            expect(city).toHaveProperty('name');
            expect(city).toHaveProperty('slug');
            expect(city).toHaveProperty('lat');
            expect(city).toHaveProperty('lon');
            expect(city).toHaveProperty('grid_i');
            expect(city).toHaveProperty('grid_j');
            expect(city).toHaveProperty('tile_id');
        }
    });

    it('slug follows umlaut conversion rules', () => {
        const { cities } = parseCityGridCorrelation();
        const muenchen = cities.find((c: any) => c.name === 'München');
        expect(muenchen?.slug).toBe('muenchen');
    });
});

describe('Fixture loader — tile stub (Phase 4)', () => {
    it('sample.webp is a valid WebP (RIFF header)', () => {
        // WebP starts with RIFF....WEBP
        expect(SAMPLE_TILE_WEBP[0]).toBe(0x52); // R
        expect(SAMPLE_TILE_WEBP[1]).toBe(0x49); // I
        expect(SAMPLE_TILE_WEBP[2]).toBe(0x46); // F
        expect(SAMPLE_TILE_WEBP[3]).toBe(0x46); // F
    });

    it('sample.webp is under 50KB', () => {
        expect(SAMPLE_TILE_WEBP.length).toBeLessThan(51200);
    });
});

describe('Fixture loader — constants', () => {
    it('exports known tile IDs', () => {
        expect(FIXTURE_TILE_IDS).toContain('57_69');
    });

    it('exports known city slugs', () => {
        expect(FIXTURE_CITY_SLUGS).toContain('muenchen');
        expect(FIXTURE_CITY_SLUGS).toContain('berlin');
    });
});

// ── Fetch mock tests ────────────────────────────────────────────────────

describe('mockFetchWithFixtures', () => {
    beforeEach(() => mockFetchWithFixtures(vi));
    afterEach(() => vi.restoreAllMocks());

    it('returns germany metrics JSON', async () => {
        const res = await fetch('/data/metrics/germany.json');
        expect(res.ok).toBe(true);
        const json = await res.json();
        expect(json.source).toBe('era5-land');
    });

    it('returns tile metrics JSON', async () => {
        const res = await fetch('/data/metrics/tiles/57_69.json');
        expect(res.ok).toBe(true);
        const json = await res.json();
        expect(json.data.fiveYearAnomaly).toBeDefined();
    });

    it('returns temperature_evolution CSV', async () => {
        const res = await fetch('/data/plots/temperature_evolution/germany.csv');
        expect(res.ok).toBe(true);
        const text = await res.text();
        expect(text).toContain('year,temperature,anomaly,trend');
    });

    it('returns city_grid_correlation JSON', async () => {
        const res = await fetch('/data/cities/city_grid_correlation.json');
        expect(res.ok).toBe(true);
        const json = await res.json();
        expect(json.cities.length).toBe(3);
    });

    it('returns 404 for unknown URLs', async () => {
        const res = await fetch('/unknown/path');
        expect(res.status).toBe(404);
    });

    it('returns WebP for tile URLs', async () => {
        const res = await fetch('/2025/01/8/134/84.webp');
        expect(res.ok).toBe(true);
        expect(res.headers.get('Content-Type')).toBe('image/webp');
    });
});
