/**
 * Tile Service Tests
 */

import { describe, it, expect } from 'vitest';
import {
    getTileUrl,
    getTileUrlTemplate,
    isDateAvailable,
    getAvailableYears,
    getAvailableMonths,
    getLatestAvailableDate,
} from '../TileService.js';

describe('TileService', () => {
    describe('getTileUrl', () => {
        it('generates correct URL with zero-padded month', () => {
            const url = getTileUrl(2024, 3, 8, 134, 84);
            expect(url).toContain('/2024/03/8/134/84.webp');
        });

        it('generates correct URL for December', () => {
            const url = getTileUrl(2024, 12, 7, 100, 50);
            expect(url).toContain('/2024/12/7/100/50.webp');
        });

        it('generates correct URL for January (01 padding)', () => {
            const url = getTileUrl(2023, 1, 6, 0, 0);
            expect(url).toContain('/2023/01/6/0/0.webp');
        });
    });

    describe('getTileUrlTemplate', () => {
        it('includes placeholder tokens', () => {
            const template = getTileUrlTemplate(2024, 6);
            expect(template).toContain('{z}');
            expect(template).toContain('{x}');
            expect(template).toContain('{y}');
            expect(template).toContain('/2024/06/');
        });

        it('zero-pads single-digit months', () => {
            const template = getTileUrlTemplate(2024, 9);
            expect(template).toContain('/2024/09/');
        });

        it('does not zero-pad two-digit months', () => {
            const template = getTileUrlTemplate(2024, 11);
            expect(template).toContain('/2024/11/');
        });
    });

    describe('isDateAvailable', () => {
        it('returns false for dates before 2016', () => {
            expect(isDateAvailable(2015, 12)).toBe(false);
        });

        it('returns false for year 2015', () => {
            expect(isDateAvailable(2015, 6)).toBe(false);
        });

        it('returns true for valid historical dates', () => {
            expect(isDateAvailable(2020, 6)).toBe(true);
        });

        it('returns true for 2016', () => {
            expect(isDateAvailable(2016, 6)).toBe(true);
        });
    });

    describe('getAvailableYears', () => {
        it('starts from 2016', () => {
            const years = getAvailableYears();
            expect(years[0]).toBe(2016);
        });

        it('includes recent years', () => {
            const years = getAvailableYears();
            expect(years).toContain(2024);
        });

        it('returns an array of numbers', () => {
            const years = getAvailableYears();
            expect(years.length).toBeGreaterThan(0);
            years.forEach(year => expect(typeof year).toBe('number'));
        });

        it('returns years in ascending order', () => {
            const years = getAvailableYears();
            for (let i = 1; i < years.length; i++) {
                expect(years[i]!).toBeGreaterThan(years[i - 1]!);
            }
        });
    });

    describe('getAvailableMonths', () => {
        it('returns all 12 months for a complete historical year', () => {
            const months = getAvailableMonths(2020);
            expect(months).toHaveLength(12);
            expect(months).toEqual([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]);
        });

        it('returns empty array for years before data start', () => {
            const months = getAvailableMonths(2010);
            expect(months).toHaveLength(0);
        });

        it('returns months in ascending order', () => {
            const months = getAvailableMonths(2022);
            for (let i = 1; i < months.length; i++) {
                expect(months[i]!).toBeGreaterThan(months[i - 1]!);
            }
        });
    });

    describe('getLatestAvailableDate', () => {
        it('returns valid year and month', () => {
            const { year, month } = getLatestAvailableDate();
            expect(year).toBeGreaterThanOrEqual(2016);
            expect(month).toBeGreaterThanOrEqual(1);
            expect(month).toBeLessThanOrEqual(12);
        });

        it('returns a date that is available', () => {
            const { year, month } = getLatestAvailableDate();
            expect(isDateAvailable(year, month)).toBe(true);
        });
    });
});
