import { useMemo } from 'react';
import { useAppSelector } from '../../../../store/hooks/useAppSelector.js';
import { selectDataByStationId } from '../../monthlyTemperaturesPlot/slices/dataSlice.js';
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
export const CURRENT_YEAR_STROKE = '#ff5252';

export const usePlotData = (): IMonthsInYearsPlotData => {
    const stationId = useSelectedStationId();
    const data = useAppSelector((state) => selectDataByStationId(state, stationId));
    const dailyRecords = useHistoricalDailyDataForStation(stationId);

    return useMemo(() => {
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

        // Compute 1961–1990 baseline
        const referenceMonthlyMeans = computeMeansOfMonthsOverYears(monthlyMeans, REFERENCE_START_YEAR, REFERENCE_END_YEAR);

        const unifiedSeries: ILineSeries[] = [];

        // Reference years (1961-1990) as light gray lines
        const referenceYears = allYears.filter((year) => year >= REFERENCE_START_YEAR && year <= REFERENCE_END_YEAR);
        const referenceLabel = `${REFERENCE_START_YEAR}-${REFERENCE_END_YEAR}`;
        for (const year of referenceYears) {
            const values = monthlyMeans[year];
            if (!values) {
                continue;
            }
            const anomalyValues = toAnomalies(values, referenceMonthlyMeans);
            unifiedSeries.push({
                label: referenceLabel,
                strokeWidth: 1,
                strokeOpacity: 0.4,
                values: toLinePoint(anomalyValues, referenceLabel),
            });
        }

        // Recent N years as light gray lines
        const lastYear = allYears.slice(-1)[0]!;
        const values = monthlyMeans[lastYear];
        if (values) {
            const anomalyValues = toAnomalies(values, referenceMonthlyMeans);
            unifiedSeries.push({
                label: String(lastYear),
                strokeWidth: 2,
                strokeOpacity: 1,
                values: toLinePoint(anomalyValues, String(lastYear)),
            });
        }

        // Get monthly means of the current year
        const currentYear = new Date().getFullYear();
        const {
            means: currentYearMeans,
            completedMonths: currentYearCompletedMonths,
        } = computeMeansOfMonthsOfCurrentYear(dailyRecords, currentYear);
        if (currentYearMeans && currentYearCompletedMonths.size > 0) {
            const currentAnomalies = toAnomalies(currentYearMeans, referenceMonthlyMeans);
            unifiedSeries.push({
                label: String(currentYear),
                strokeWidth: 2,
                strokeOpacity: 1,
                values: toLinePoint(currentAnomalies, String(currentYear)),
            });
        }

        // Define color scale mapping for legend
        const colorForLabel = (label: string): string => {
            if (label === String(currentYear)) return '#ff5252';
            if (label === String(lastYear)) return '#ffaa00';
            if (label === referenceLabel) return '#999999';
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

        // Compute anomaly domain from unified series values
        const getDomainFromSeries = (series: ILineSeries[]): [number, number] => {
            let minY = Number.POSITIVE_INFINITY;
            let maxY = Number.NEGATIVE_INFINITY;
            for (const s of series) {
                for (const p of s.values) {
                    if (typeof p.y === 'number' && Number.isFinite(p.y)) {
                        if (p.y < minY) minY = p.y;
                        if (p.y > maxY) maxY = p.y;
                    }
                }
            }
            return minY === Number.POSITIVE_INFINITY || maxY === Number.NEGATIVE_INFINITY
                ? [0, 0]
                : [minY, maxY];
        };

        const computedDomain = getDomainFromSeries(unifiedSeries);

        // Compute stats for description
        const completenessMonths = currentYearCompletedMonths?.size ?? 0;
        const currentMonthIndex = completenessMonths > 0 ? Math.max(...Array.from(currentYearCompletedMonths)) : null;
        const currentMonthMean = (currentYearMeans && currentMonthIndex != null) ? currentYearMeans[currentMonthIndex] : null;
        const referenceMonthMean = (referenceMonthlyMeans && currentMonthIndex != null) ? referenceMonthlyMeans[currentMonthIndex] : null;
        const currentMonthAnomaly = (typeof currentMonthMean === 'number' && typeof referenceMonthMean === 'number')
            ? currentMonthMean - referenceMonthMean
            : null;

        // Build ordered anomaly series (year, month)
        const orderedAnomalies: { year: number; month: number; value: number }[] = [];
        for (const y of allYears) {
            const vals = monthlyMeans[y];
            if (!vals) continue;
            const anomalies = toAnomalies(vals, referenceMonthlyMeans);
            anomalies.forEach((v, m) => {
                if (typeof v === 'number') orderedAnomalies.push({ year: y, month: m, value: v });
            });
        }
        orderedAnomalies.sort((a, b) => (a.year - b.year) || (a.month - b.month));

        // Shares for baseline: since 1991 and last 5 years
        const anomaliesSince1991 = orderedAnomalies.filter(p => p.year >= 1991).map(p => p.value);
        const shareAbove0Since1991 = anomaliesSince1991.length
            ? (anomaliesSince1991.filter(v => v > 0).length / anomaliesSince1991.length) * 100
            : null;
        const maxYear = orderedAnomalies.length ? (orderedAnomalies[orderedAnomalies.length - 1]?.year ?? currentYear) : currentYear;
        const last5yStart = maxYear - 4;
        const anomaliesLast5y = orderedAnomalies.filter(p => p.year >= last5yStart).map(p => p.value);
        const shareAbove15Last5y = anomaliesLast5y.length
            ? (anomaliesLast5y.filter(v => v >= 1.5).length / anomaliesLast5y.length) * 100
            : null;

        // Streaks: consecutive anomalies >0 or <0 ending at last completed month
        const lastCompletedIdx = currentMonthIndex ?? null;
        const lastCompletedYear = currentYear;
        // Build recent sequence up to last completed
        const recentSeq: number[] = [];
        for (let y = maxYear; y >= REFERENCE_START_YEAR; y--) {
            const vals = monthlyMeans[y];
            if (!vals) continue;
            const anomalies = toAnomalies(vals, referenceMonthlyMeans);
            for (let m = 11; m >= 0; m--) {
                const cutoff = (y === lastCompletedYear && lastCompletedIdx != null) ? lastCompletedIdx : 11;
                if (y === lastCompletedYear && m > cutoff) continue;
                const v = anomalies[m];
                if (typeof v === 'number') recentSeq.push(v);
            }
        }
        // Compute streaks that END at the last completed month
        // recentSeq[0] corresponds to the last completed month, increasing offsets go backwards in time
        let streakAbove = 0;
        for (let i = 0; i < recentSeq.length; i++) {
            const v = recentSeq[i] as number | undefined;
            if (typeof v !== 'number') break;
            if (v > 0) {
                streakAbove++;
            } else {
                break;
            }
        }

        // Helper to convert offset to year/month from lastCompleted
        const indexToYearMonth = (offset: number | null): { year: number; month: number } | null => {
            if (offset == null || lastCompletedIdx == null) return null;
            // Build linear list of year-month from lastCompleted backwards
            const seqYM: { year: number; month: number }[] = [];
            for (let y = maxYear; y >= REFERENCE_START_YEAR; y--) {
                const cutoff = (y === lastCompletedYear && lastCompletedIdx != null) ? lastCompletedIdx : 11;
                for (let m = cutoff; m >= 0; m--) {
                    seqYM.push({ year: y, month: m });
                }
            }
            return seqYM[offset] ?? null;
        };
        const streakAboveRange = (streakAbove >= 2)
            ? { start: indexToYearMonth(streakAbove - 1), end: indexToYearMonth(0) }
            : null;
        const streakBelowRange = null;

        // Percentile for last completed month anomaly within that month's distribution
        let currentMonthAnomalyPercentile: number | null = null;
        let isRecordWarmForMonth = false;
        let isRecordColdForMonth = false;
        if (lastCompletedIdx != null) {
            const dist = orderedAnomalies.filter(p => p.month === lastCompletedIdx).map(p => p.value).sort((a, b) => a - b);
            const curr = orderedAnomalies.find(p => p.year === lastCompletedYear && p.month === lastCompletedIdx)?.value ?? null;
            if (curr != null && dist.length) {
                // percentile rank (mid-rank)
                const pos = dist.findIndex(v => v >= curr);
                const rank = pos === -1 ? dist.length : pos + 1;
                currentMonthAnomalyPercentile = (rank / dist.length) * 100;
                const lastVal = dist[dist.length - 1] as number | undefined;
                const firstVal = dist[0] as number | undefined;
                if (lastVal != null) isRecordWarmForMonth = curr >= lastVal;
                if (firstVal != null) isRecordColdForMonth = curr <= firstVal;
            }
        }

        return {
            stationId,
            domain: computedDomain,
            error: null,
            series: unifiedSeries,
            colorDomain,
            colorRange,
            stats: {
                currentYear,
                completenessMonths,
                anomalyDomain: { min: computedDomain[0], max: computedDomain[1] },
                ...(currentMonthIndex != null ? { currentMonthIndex } : {}),
                ...(currentMonthMean != null ? { currentMonthMean } : {}),
                ...(referenceMonthMean != null ? { referenceMonthMean } : {}),
                ...(currentMonthAnomaly != null ? { currentMonthAnomaly } : {}),
                ...(shareAbove0Since1991 != null ? { shareAbove0Since1991 } : {}),
                ...(shareAbove15Last5y != null ? { shareAbove15Last5y } : {}),
                ...(streakAbove ? { streakMonthsAboveAnomaly0: streakAbove } : {}),
                // remove below-0 streak reporting per new spec
                ...(streakAboveRange ? { streakMonthsAboveAnomaly0Range: streakAboveRange } : {}),
                ...(streakBelowRange ? { streakMonthsBelowAnomaly0Range: streakBelowRange } : {}),
                ...(currentMonthAnomalyPercentile != null ? { currentMonthAnomalyPercentile } : {}),
                ...(isRecordWarmForMonth ? { isRecordWarmForMonth } : {}),
                ...(isRecordColdForMonth ? { isRecordColdForMonth } : {}),
            },
        };
    }, [stationId, data, dailyRecords]);
};

const toAnomalies = (
    values: readonly (number | null)[],
    refMeans: readonly (number | null)[]
): (number | null)[] =>
    Array.from(values, (v, i) => {
        const ref = refMeans[i];
        return typeof v === 'number' && Number.isFinite(v) && typeof ref === 'number'
            ? v - ref
            : (v as number | null);
    });