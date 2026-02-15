import { DateTime } from 'luxon';
import deDict from '../i18n/de.json' assert { type: 'json' };
import { registerDictionary, t, type Locale } from '../i18n/i18n.js';

registerDictionary('de', deDict as any);

export type PlotContext = {
    plotId: 'monthlyTemps' | 'monthlyAnomalies';
    city?: string | null;
    locale?: Locale;
    stats?: Partial<{
        currentMonthIndex: number; // 0-11
        currentYear: number;
        currentMonthMean: number | null; // °C
        referenceMonthMean: number | null; // °C
        currentMonthAnomaly: number | null; // °C vs 1961–1990
        recentTrendPerDecade1991Plus: number; // °C/decade
        anomalyDomain: { min: number; max: number };
        completenessMonths: number; // number of months available in current year
        // anomalies plot additions
        isRecordWarmForMonth: boolean;
        isRecordColdForMonth: boolean;
        currentMonthAnomalyPercentile: number;
        streakMonthsAboveAnomaly0: number;
        streakMonthsBelowAnomaly0: number;
        streakMonthsAboveAnomaly0Range: { start: { year: number; month: number } | null; end: { year: number; month: number } | null } | null;
        streakMonthsBelowAnomaly0Range: { start: { year: number; month: number } | null; end: { year: number; month: number } | null } | null;
        shareAbove0Since1991: number;
        shareAbove15Last5y: number;
        // temps plot additions
        warmestMonthThisYear: { index: number; year: number; percentile?: number } | null;
        coldestMonthThisYear: { index: number; year: number; percentile?: number } | null;
        seasonalDeviationThisYear: { season: 'DJF' | 'MAM' | 'JJA' | 'SON'; diff: number } | null;
    }>;
};

export type DescriptionResult = {
    title: string;
    baseline: string;
    insights: string[];
};

export type DescriptionRule = (ctx: PlotContext) => string | null;

export function composeDescription(
    ns: string,
    titleKey: string,
    baselineKey: string,
    rules: DescriptionRule[],
    ctx: PlotContext,
    maxInsights = -1
): DescriptionResult {
    const city = ctx.city ?? 'dieser Stadt';
    const locale: Locale = ctx.locale ?? 'de';
    const title = t(ns, titleKey, { city }, locale) || `${city}`;
    const baseline = t(ns, baselineKey, {}, locale);
    const insights: string[] = [];
    for (const rule of rules) {
        const s = rule(ctx);
        if (s) insights.push(s);
        if (maxInsights >= 0 && insights.length >= maxInsights) break;
    }
    return { title, baseline, insights };
}

function monthNameDe(index?: number, year?: number) {
    if (index == null || year == null) return null;
    const dt = DateTime.fromObject({ year, month: index + 1 }).setLocale('de');
    return { month: dt.toFormat('LLLL'), year: dt.toFormat('yyyy') };
}

const hasNoAnomaly = (a: number | null): boolean => {
    return a != null && a >= -0.1 && a <= 0.1;
}
const hasPositiveAnomaly = (a: number | null): boolean => {
    return a != null && a > 0.1 && a < 1.5;
}
const hasHighPositiveAnomaly = (a: number | null): boolean => {
    return a != null && a >= 1.5;
}
const hasHighNegativeAnomaly = (a: number | null): boolean => {
    return a != null && a <= -1.5;
}
const hasNegativeAnomaly = (a: number | null): boolean => {
    return a != null && a < -0.1 && a > -1.5;
}

const hasNoTrend = (slope: number | null): boolean => {
    return slope != null && slope >= -0.1 && slope <= 0.1;
}
const hasPositiveTrend = (slope: number | null): boolean => {
    return slope != null && slope > 0.1 && slope < 0.3;
}
const hasHighPositiveTrend = (slope: number | null): boolean => {
    return slope != null && slope >= 0.3;
}
const hasHighNegativeTrend = (slope: number | null): boolean => {
    return slope != null && slope <= -0.3;
}
const hasNegativeTrend = (slope: number | null): boolean => {
    return slope != null && slope < -0.1 && slope > -0.3;
}

export const monthlyTempsRules: DescriptionRule[] = [
    (ctx) => {
        const m = monthNameDe(ctx.stats?.currentMonthIndex, ctx.stats?.currentYear);
        const completeness = ctx.stats?.completenessMonths;
        if (!m || !completeness || completeness >= 12) return null;
        return t('plots.monthlyTemps', 'insight.completeness', { month: m.month, year: m.year });
    },
    (ctx) => {
        const a = ctx.stats?.currentMonthAnomaly;
        if (a == null) return null;
        if (hasNoAnomaly(a)) return t('plots.monthlyTemps', 'insight.noAnomaly');
        if (hasHighPositiveAnomaly(a)) return t('plots.monthlyTemps', 'insight.highPositive');
        if (hasPositiveAnomaly(a)) return t('plots.monthlyTemps', 'insight.positive');
        if (hasHighNegativeAnomaly(a)) return t('plots.monthlyTemps', 'insight.highNegative');
        if (hasNegativeAnomaly(a)) return t('plots.monthlyTemps', 'insight.negative');
        return null;
    },
    (ctx) => {
        const p = ctx.stats?.warmestMonthThisYear?.percentile;
        const idx = ctx.stats?.currentMonthIndex;
        const year = ctx.stats?.currentYear;
        if (p == null || idx == null || year == null) return null;
        const m = monthNameDe(idx, year);
        if (!m) return null;
        const pct = Math.round(p);
        if (pct >= 50) return t('plots.monthlyTemps', 'insight.warmMonthPercentile', { month: m.month, percentile: pct });
        if (pct < 50) return t('plots.monthlyTemps', 'insight.coldMonthPercentile', { month: m.month, percentile: pct });
        return null;
    },
    (ctx) => {
        const s = ctx.stats?.seasonalDeviationThisYear;
        if (!s) return null;
        const diff = Math.round(s.diff * 10) / 10;
        if (Math.abs(diff) < 0.5) return null;
        const seasonKey = s.season.toLowerCase() as 'djf' | 'mam' | 'jja' | 'son';
        const seasonLabel = t('season', seasonKey);
        return t('plots.monthlyTemps', 'insight.seasonalDeviation', { season: seasonLabel, diff });
    },
];

export const monthlyAnomaliesRules: DescriptionRule[] = [
    // Record or percentile for last completed month
    (ctx) => {
        const idx = ctx.stats?.currentMonthIndex;
        const year = ctx.stats?.currentYear;
        if (idx == null || year == null) return null;
        const m = monthNameDe(idx, year);
        if (!m) return null;
        if (ctx.stats?.isRecordWarmForMonth) return t('plots.monthlyAnomalies', 'insight.recordWarm', { month: m.month, year: m.year });
        if (ctx.stats?.isRecordColdForMonth) return t('plots.monthlyAnomalies', 'insight.recordCold', { month: m.month, year: m.year });
        const p = ctx.stats?.currentMonthAnomalyPercentile;
        const a = ctx.stats?.currentMonthAnomaly;
        if (p != null && a != null) {
            if (a >= 0) return t('plots.monthlyAnomalies', 'insight.percentileWarm', { month: m.month, year: m.year, percentile: Math.round(100 - p) });
            return t('plots.monthlyAnomalies', 'insight.percentileCold', { month: m.month, year: m.year, percentile: Math.round(p) });
        }
        return null;
    },
    // Positive anomaly streak ending at last completed month
    (ctx) => {
        const sa = ctx.stats?.streakMonthsAboveAnomaly0 ?? 0;
        if (sa >= 2) {
            const r = ctx.stats?.streakMonthsAboveAnomaly0Range;
            if (r?.start && r?.end) {
                const start = DateTime.fromObject({ year: r.start.year, month: r.start.month + 1 }).setLocale('de').toFormat('LLLL yyyy');
                const end = DateTime.fromObject({ year: r.end.year, month: r.end.month + 1 }).setLocale('de').toFormat('LLLL yyyy');
                return t('plots.monthlyAnomalies', 'insight.streakAboveRange', { start, end, count: sa });
            }
            return t('plots.monthlyAnomalies', 'insight.streakAbove', { count: sa });
        }
        return null;
    },
    // Completeness
    (ctx) => {
        const m = monthNameDe(ctx.stats?.currentMonthIndex, ctx.stats?.currentYear);
        const completeness = ctx.stats?.completenessMonths;
        if (!m || !completeness || completeness >= 12) return null;
        return t('plots.monthlyAnomalies', 'insight.completeness', { month: m.month, year: m.year });
    },
];

export function getMonthlyTempsDescription(ctx: PlotContext): DescriptionResult {
    return composeDescription(
        'plots.monthlyTemps',
        'title',
        'baseline',
        monthlyTempsRules,
        ctx
    );
}

export function getMonthlyAnomaliesDescription(ctx: PlotContext): DescriptionResult {
    const ns = 'plots.monthlyAnomalies';
    const city = ctx.city ?? 'dieser Stadt';
    const locale: Locale = ctx.locale ?? 'de';
    const title = t(ns, 'title', { city }, locale);
    const shareAbove0 = ctx.stats?.shareAbove0Since1991;
    const shareAbove15 = ctx.stats?.shareAbove15Last5y;
    const baseline = t(ns, 'baseline', {
        shareAbove0: shareAbove0 != null ? Math.round(shareAbove0) : '—',
        shareAbove15: shareAbove15 != null ? Math.round(shareAbove15) : '—',
    }, locale);
    const insights: string[] = [];
    for (const rule of monthlyAnomaliesRules) {
        const s = rule(ctx);
        if (s) insights.push(s);
        if (insights.length >= 2) break;
    }
    const sa0 = shareAbove0 ?? 0;
    const sa15 = shareAbove15 ?? 0;
    const warm = (sa0 >= 60) || (sa15 >= 20) || ((ctx.stats?.streakMonthsAboveAnomaly0 ?? 0) >= 3);
    const cold = (sa0 <= 40) || ((ctx.stats?.streakMonthsBelowAnomaly0 ?? 0) >= 3);
    if (warm && !cold) insights.push(t(ns, 'conclusion.warmRegime'));
    else if (cold && !warm) insights.push(t(ns, 'conclusion.coldRegime'));
    else insights.push(t(ns, 'conclusion.mixedRegime'));
    return { title, baseline, insights };
}
