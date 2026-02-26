/**
 * Schema validation tests — ensure fixture/golden data conforms to JSON schemas.
 *
 * All schemas and fixtures target the NEW ERA5-Land product (botox phases).
 * If any schema changes, or if output data drifts from the contracts, these
 * tests will catch it before commit.
 */

import { describe, it, expect } from 'vitest';
import Ajv from 'ajv';
import addFormats from 'ajv-formats';
import { readFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dir = dirname(fileURLToPath(import.meta.url));
const root = resolve(__dir, '..', '..', '..');  // -> project root

const readJson = (rel: string) => JSON.parse(readFileSync(resolve(root, rel), 'utf-8'));
const readCsvHeaders = (rel: string) =>
    readFileSync(resolve(root, rel), 'utf-8').split('\n')[0].split(',');

// ── Load schemas ────────────────────────────────────────────────────────

const metricsSchema = readJson('schemas/metrics.schema.json');
const cityCorrelationSchema = readJson('schemas/city-correlation.schema.json');
const plotCsvHeadersSchema = readJson('schemas/plot-csv-headers.schema.json');
const envSchema = readJson('schemas/env.schema.json');

// ── Load fixture data ───────────────────────────────────────────────────

const germanyMetrics = readJson('frontend/src/__fixtures__/metrics/germany.json');
const tileMetrics = readJson('frontend/src/__fixtures__/metrics/tiles/57_69.json');
const cityCorrelation = readJson('frontend/src/__fixtures__/cities/city_grid_correlation.json');

const tempEvolutionHeaders = readCsvHeaders('frontend/src/__fixtures__/plots/temperature_evolution/germany.csv');
const seasonalWarmingHeaders = readCsvHeaders('frontend/src/__fixtures__/plots/seasonal_warming/germany.csv');
const extremesHeaders = readCsvHeaders('frontend/src/__fixtures__/plots/extremes/germany.csv');
const monthlyDistHeaders = readCsvHeaders('frontend/src/__fixtures__/plots/monthly_distribution/germany.csv');

// ── Setup AJV ───────────────────────────────────────────────────────────

function createValidator() {
    const ajv = new Ajv({ allErrors: true });
    addFormats(ajv);
    return ajv;
}

// ── Tests ───────────────────────────────────────────────────────────────

describe('JSON Schema validation (ERA5-Land)', () => {
    const ajv = createValidator();

    describe('metrics.schema.json', () => {
        const validate = ajv.compile(metricsSchema);

        it('validates germany-level metrics fixture', () => {
            const valid = validate(germanyMetrics);
            expect(validate.errors).toBeNull();
            expect(valid).toBe(true);
        });

        it('validates per-tile metrics fixture', () => {
            const valid = validate(tileMetrics);
            expect(validate.errors).toBeNull();
            expect(valid).toBe(true);
        });

        it('rejects data with missing required field (no source)', () => {
            const { source, ...rest } = germanyMetrics;
            expect(validate(rest)).toBe(false);
        });

        it('rejects data with wrong source value', () => {
            const invalid = { ...germanyMetrics, source: 'hyras' };
            expect(validate(invalid)).toBe(false);
        });

        it('rejects data with missing metric sub-object', () => {
            const { data: { comfortableDays, ...restData }, ...envelope } = germanyMetrics;
            const invalid = { ...envelope, data: restData };
            expect(validate(invalid)).toBe(false);
        });
    });

    describe('city-correlation.schema.json', () => {
        const validate = ajv.compile(cityCorrelationSchema);

        it('validates the city correlation fixture', () => {
            const valid = validate(cityCorrelation);
            expect(validate.errors).toBeNull();
            expect(valid).toBe(true);
        });

        it('rejects city with invalid slug format', () => {
            const invalid = {
                ...cityCorrelation,
                cities: [{ ...cityCorrelation.cities[0], slug: 'Berlin (INVALID)' }],
            };
            expect(validate(invalid)).toBe(false);
        });

        it('rejects city with invalid tile_id format', () => {
            const invalid = {
                ...cityCorrelation,
                cities: [{ ...cityCorrelation.cities[0], tile_id: 'bad' }],
            };
            expect(validate(invalid)).toBe(false);
        });
    });

    describe('env.schema.json', () => {
        const validate = ajv.compile(envSchema);

        it('validates a correct env config', () => {
            const env = {
                ACCESS_KEY: 'test-key',
                SECRET_KEY: 'test-secret',
                BUCKET_NAME: 'climate-tiles',
                REGION: 'fsn1',
                ENDPOINT_URL: 'https://s3.example.com',
                CDS_API_KEY: '12345:abcdef-1234-5678',
                CLIMATE_DATA_PROVIDER: 'era5-land',
            };
            expect(validate(env)).toBe(true);
        });

        it('rejects env with invalid CDS_API_KEY format', () => {
            const env = {
                ACCESS_KEY: 'k', SECRET_KEY: 's', BUCKET_NAME: 'b',
                REGION: 'fsn1', ENDPOINT_URL: 'https://example.com',
                CDS_API_KEY: 'bad-format',
                CLIMATE_DATA_PROVIDER: 'era5-land',
            };
            expect(validate(env)).toBe(false);
        });

        it('rejects env with unsupported region', () => {
            const env = {
                ACCESS_KEY: 'k', SECRET_KEY: 's', BUCKET_NAME: 'b',
                REGION: 'us-east-1', ENDPOINT_URL: 'https://example.com',
                CDS_API_KEY: '12345:abc-def',
                CLIMATE_DATA_PROVIDER: 'era5-land',
            };
            expect(validate(env)).toBe(false);
        });
    });
});

describe('Plot CSV header contracts (Phase 9)', () => {
    const expectedHeaders = plotCsvHeadersSchema;

    it('temperature_evolution CSV has correct headers', () => {
        expect(tempEvolutionHeaders).toEqual(expectedHeaders.temperature_evolution.headers);
    });

    it('seasonal_warming CSV has correct headers', () => {
        expect(seasonalWarmingHeaders).toEqual(expectedHeaders.seasonal_warming.headers);
    });

    it('extremes CSV has correct headers', () => {
        expect(extremesHeaders).toEqual(expectedHeaders.extremes.headers);
    });

    it('monthly_distribution CSV has correct headers', () => {
        expect(monthlyDistHeaders).toEqual(expectedHeaders.monthly_distribution.headers);
    });
});
