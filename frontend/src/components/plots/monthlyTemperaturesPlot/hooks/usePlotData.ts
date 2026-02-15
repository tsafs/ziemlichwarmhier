import { useMemo } from 'react';
import { useAppSelector } from '../../../../store/hooks/useAppSelector.js';
import { selectDataByStationId } from '../slices/dataSlice.js';
import { useSelectedStationId } from '../../../../store/hooks/hooks.js';
import { useHistoricalDailyDataForStation } from '../../../../store/slices/historicalDataForStationSlice.js';
import {
    computeMeansOfMonthsOfCurrentYear,
    computeMeansOfMonthsOverYears,
    toLinePoint,
    type ILineSeries,
    type IMonthsInYearsPlotData
} from '../../utils/monthsInYearsPlotUtils.js';
import { theilSenSlope } from '../../../../services/description/stats.js';

const initialResult: IMonthsInYearsPlotData = {
    stationId: '',
    domain: [0, 0],
    error: null,
    series: [],
    colorDomain: [],
    colorRange: [],
};

const REFERENCE_START_YEAR = 1961;
const REFERENCE_END_YEAR = 1990;

export const usePlotData = (): IMonthsInYearsPlotData => {
    const stationId = useSelectedStationId();
    const data = useAppSelector((state) => selectDataByStationId(state, stationId));
    const dailyRecords = useHistoricalDailyDataForStation(stationId);

    return useMemo(() => {
        // Validate station ID
        if (!stationId || data.stationId !== stationId) {
            return initialResult;
        }

        const monthlyMeans = data.monthlyMeans ?? {};

        // Get all years as numbers and sorted
        const allYears = Object.keys(monthlyMeans)
            .map((year) => Number.parseInt(year, 10))
            .filter((year) => Number.isFinite(year))
            .sort((a, b) => a - b);

        // No data available
        if (!allYears.length) {
            return initialResult;
        }

        const unifiedSeries: ILineSeries[] = [];

        // Reference years (1961-1990) as light gray lines
        const referenceYears = allYears.filter((year) => year >= REFERENCE_START_YEAR && year <= REFERENCE_END_YEAR);
        const referenceLabel = `${REFERENCE_START_YEAR}-${REFERENCE_END_YEAR}`;
        for (const year of referenceYears) {
            const values = monthlyMeans[year];
            if (!values) {
                continue;
            }
            unifiedSeries.push({
                label: referenceLabel,
                strokeWidth: 1,
                strokeOpacity: 0.5,
                values: toLinePoint(values, referenceLabel),
            });
        }

        // Last year as yellow line
        const lastYear = allYears.slice(-1)[0]!;
        const values = monthlyMeans[lastYear];
        if (values) {
            unifiedSeries.push({
                label: String(lastYear),
                strokeWidth: 2,
                strokeOpacity: 1,
                values: toLinePoint(values, String(lastYear)),
            });
        }

        // Get monthly means of the current year
        const currentYear = new Date().getFullYear();
        const {
            means: currentYearMeans,
            completedMonths: currentYearCompletedMonths,
        } = computeMeansOfMonthsOfCurrentYear(dailyRecords, currentYear);
        if (currentYearMeans && currentYearCompletedMonths.size > 0) {
            unifiedSeries.push({
                label: String(currentYear),
                strokeWidth: 2,
                strokeOpacity: 1,
                values: toLinePoint(currentYearMeans, String(currentYear)),
            });
        }

        // Define color scale mapping for legend
        const colorForLabel = (label: string): string => {
            if (label === String(currentYear)) return '#ff5252';
            if (label === String(lastYear)) return '#ffcc00';
            if (label === referenceLabel) return '#666666';
            if (label.endsWith('Mittel')) return '#eeeeee';
            return '#666666';
        };
        const colorDomain: string[] = [];
        const colorRange: string[] = [];
        const seen = new Set<string>();
        for (const s of unifiedSeries) {
            if (!seen.has(s.label)) {
                seen.add(s.label);
                colorDomain.push(s.label);
                colorRange.push(colorForLabel(s.label));
            }
        }

        // Compute stats for description (maxima-focused percentile and seasonal deviation)
        const referenceMonthlyMeans = computeMeansOfMonthsOverYears(monthlyMeans, REFERENCE_START_YEAR, REFERENCE_END_YEAR);
        const completenessMonths = currentYearCompletedMonths?.size ?? 0;
        const currentMonthIndex = completenessMonths > 0 ? Math.max(...Array.from(currentYearCompletedMonths)) : null;
        const currentMonthMean = (currentYearMeans && currentMonthIndex != null) ? currentYearMeans[currentMonthIndex] : null;
        const referenceMonthMean = (referenceMonthlyMeans && currentMonthIndex != null) ? referenceMonthlyMeans[currentMonthIndex] : null;
        const currentMonthAnomaly = (typeof currentMonthMean === 'number' && typeof referenceMonthMean === 'number')
            ? currentMonthMean - referenceMonthMean
            : null;

        // Percentile of current month vs long-term month distribution
        let currentMonthPercentile: number | null = null;
        if (currentMonthIndex != null && typeof currentMonthMean === 'number') {
            const dist: number[] = [];
            for (let y = REFERENCE_START_YEAR; y <= REFERENCE_END_YEAR; y++) {
                const v = monthlyMeans[y]?.[currentMonthIndex];
                if (typeof v === 'number') dist.push(v);
            }
            dist.sort((a, b) => a - b);
            if (dist.length) {
                const pos = dist.findIndex(v => v >= (currentMonthMean as number));
                const rank = pos === -1 ? dist.length : pos + 1;
                currentMonthPercentile = (rank / dist.length) * 100;
            }
        }

        // Seasonal deviation for current year vs long-term mean
        const seasons: Record<'DJF' | 'MAM' | 'JJA' | 'SON', number[]> = {
            DJF: [11, 0, 1],
            MAM: [2, 3, 4],
            JJA: [5, 6, 7],
            SON: [8, 9, 10],
        };
        let seasonalDeviationThisYear: { season: 'DJF' | 'MAM' | 'JJA' | 'SON'; diff: number } | null = null;
        // Choose the season containing the last completed month (context stability)
        const seasonForMonth = (m: number | null): 'DJF' | 'MAM' | 'JJA' | 'SON' | null => {
            if (m == null) return null;
            if (m === 11 || m === 0 || m === 1) return 'DJF';
            if (m === 2 || m === 3 || m === 4) return 'MAM';
            if (m === 5 || m === 6 || m === 7) return 'JJA';
            if (m === 8 || m === 9 || m === 10) return 'SON';
            return null;
        };
        const targetSeason = seasonForMonth(currentMonthIndex);
        if (targetSeason) {
            const months = seasons[targetSeason];
            const yVals = months.map((m: number) => currentYearMeans?.[m]).filter((v: unknown) => typeof v === 'number') as number[];
            const cVals = months.map((m: number) => referenceMonthlyMeans?.[m]).filter((v: unknown) => typeof v === 'number') as number[];
            if (yVals.length === months.length && cVals.length === months.length) {
                const yMean = yVals.reduce((s, v) => s + v, 0) / yVals.length;
                const cMean = cVals.reduce((s, v) => s + v, 0) / cVals.length;
                seasonalDeviationThisYear = { season: targetSeason, diff: yMean - cMean };
            }
        }

        return {
            stationId,
            domain: data.domain,
            error: null,
            series: unifiedSeries,
            colorDomain,
            colorRange,
            stats: {
                currentYear,
                completenessMonths,
                ...(currentMonthIndex != null ? { currentMonthIndex } : {}),
                ...(currentMonthMean != null ? { currentMonthMean } : {}),
                ...(referenceMonthMean != null ? { referenceMonthMean } : {}),
                ...(currentMonthAnomaly != null ? { currentMonthAnomaly } : {}),
                ...(currentMonthPercentile != null ? { warmestMonthThisYear: { index: currentMonthIndex!, year: currentYear, percentile: currentMonthPercentile } } : {}),
                ...(seasonalDeviationThisYear ? { seasonalDeviationThisYear } : {}),
            },
        };
    }, [stationId, data, dailyRecords]);
};