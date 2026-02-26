# Frontend Test Fixtures

Minimal, realistic fixture files for offline Vitest tests. All data targets the **new ERA5-Land product** defined in the botox phase plans — not the legacy HYRAS/DWD station data.

## Fixture Index

| Directory | File | Format | Botox Source | Description |
|-----------|------|--------|--------------|-------------|
| `metrics/` | `germany.json` | JSON | Phase 5/8 | Country-level `MetricsFile` with all 8 metric sub-objects |
| `metrics/tiles/` | `57_69.json` | JSON | Phase 5/8 | Per-tile `MetricsFile` (München grid cell) |
| `plots/` | `temperature_evolution/germany.csv` | CSV | Phase 9 | 5-year sample: `year,temperature,anomaly,trend` |
| `plots/` | `seasonal_warming/germany.csv` | CSV | Phase 9 | 5-year sample: `year,winter,spring,summer,fall` |
| `plots/` | `extremes/germany.csv` | CSV | Phase 9 | 5-year sample: `year,hot_days,cold_days,reference_hot,reference_cold` |
| `plots/` | `monthly_distribution/germany.csv` | CSV | Phase 9 | 12-row sample: `month,cur_min,cur_q1,cur_median,...` |
| `cities/` | `city_grid_correlation.json` | JSON | Phase 10 | 3-city sample with grid mapping |
| `tiles/` | `sample.webp` | WebP | Phase 4 | 1×1 px transparent WebP stub for tile-loading tests |

## Seeds & Derivation

- **Metrics**: Synthetic values within plausible ranges for Germany (annual anomaly ~+2°C, warming rate ~0.4°C/decade). Matches `LocationMetrics` schema from Phase 5.
- **Plot CSVs**: 5-year windows (2021–2025) with realistic temperature/anomaly values. Column headers match Phase 9 plot dataset specs.
- **City correlation**: 3 well-known German cities (Berlin, München, Freiburg) with accurate coordinates and plausible grid cell assignments.
- **Tile stub**: Minimal valid WebP for testing tile-loading logic without real rendered content.

## Attribution

All values are synthetic. ERA5-Land fixtures (when added via CDS API pull per CON-001) will carry: "Contains modified Copernicus Climate Change Service information [year]; neither the European Commission nor ECMWF is responsible for any use of this information."
