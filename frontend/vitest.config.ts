import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
    plugins: [react()],
    test: {
        globals: true,
        environment: 'jsdom',
        setupFiles: ['./src/test-utils/setupTests.ts'],
        include: ['src/**/*.{test,spec}.{ts,tsx}'],
        coverage: {
            provider: 'v8',
            reporter: ['text', 'text-summary', 'lcov'],
            include: ['src/**/*.{ts,tsx}'],
            exclude: [
                'src/**/*.test.{ts,tsx}',
                'src/**/*.spec.{ts,tsx}',
                'src/test-utils/**',
                'src/__fixtures__/**',
                'src/__mocks__/**',
                'src/vite-env.d.tsx',

                // MapLibre components require WebGL context; covered by E2E tests
                'src/components/maps/ClimateMap/ClimateMap.tsx',
                'src/components/maps/ClimateMap/CityMarkers.tsx',
                'src/components/maps/ClimateMap/View.tsx',

                // ── Legacy (pre-botox) code ─────────────────────────
                // Components
                'src/components/header/**',
                'src/components/footer/**',
                'src/components/closing/**',
                'src/components/common/**',
                'src/components/plots/HeatmapGermany/**',
                'src/components/plots/TemperatureAnomaliesByDayOverYears/**',
                'src/components/plots/TemperaturePercentogram/**',
                'src/components/plots/iceAndHotDays/**',
                'src/components/plots/Stats/**',
                'src/pages/**',
                // Data model classes
                'src/classes/**',
                // Legacy slices (see store/index.ts "Legacy slices" section)
                'src/store/slices/YearlyMeanByDaySlice.ts',
                'src/store/slices/ReferenceYearlyHourlyInterpolatedByDaySlice.ts',
                'src/store/slices/selectedDateSlice.ts',
                'src/store/slices/historicalDataForStationSlice.ts',
                'src/store/slices/DailyRecentByDateSlice.ts',
                'src/store/slices/stationDateRangesSlice.ts',
                'src/store/slices/geoJsonSlice.ts',
                'src/store/slices/heatmapGermanySlice.ts',
                // Legacy selectors & hooks
                'src/store/selectors/**',
                'src/store/hooks/hooks.ts',
                // Legacy services
                'src/services/YearlyMeanByDayService.ts',
                'src/services/ReferenceYearlyHourlyInterpolatedByDayService.ts',
                'src/services/DailyRecentByDateService.ts',
                'src/services/GeoJSONService.ts',
                'src/services/HistoricalDataForStationService.ts',
                'src/services/CityService.ts',
                'src/services/LiveDataService.ts',
                'src/services/RollingAverageDataService.ts',
                'src/services/DailyAverageDataService.ts',
                'src/services/utils/**',
                // Legacy hooks & utils
                'src/hooks/useAsyncLoadingOverlay.ts',
                'src/hooks/useHardinessZone.ts',
                'src/utils/HardinessZoneUtils.ts',
                'src/utils/TemperatureUtils.ts',
                'src/utils/dateUtils.ts',
                'src/constants/page.tsx',
                'src/types/htl.d.ts',
            ],
            thresholds: {
                statements: 10,
                branches: 10,
                functions: 10,
                lines: 10,
            },
        },
    },
});
