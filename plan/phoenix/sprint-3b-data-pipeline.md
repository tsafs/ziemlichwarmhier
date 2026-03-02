---
goal: "Sprint 3b — Data Pipeline: Validate Backend, Generate Real Artifacts, Replace Fixtures"
version: 1.0
date_created: 2026-03-02
last_updated: 2026-03-02
owner: phoenix
status: 'Planned'
tags: [backend, pipeline, data, metrics, tiles, plots, sprint-3b]
---

# Sprint 3b — Data Pipeline Validation

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Light up the backend. This sprint takes the code copied in Sprint 1, verifies it runs end-to-end, fills gaps (plot CSV generation, city correlation JSON), produces every data artifact the frontend consumes (tiles, metrics JSON, plot CSV, cities.json), and replaces the hand-written dev fixtures with real pipeline output. After this sprint, the pipeline is proven — Sprint 7 merely deploys it.

**Prerequisite**: Sprint 1 completed (backend copied, `pytest` passing). Sprint 3 completed (city search working with dev fixture).

**Architecture reference**: See `plan/phoenix/00-architecture.md` §4 for all interface contracts, §7 for backend conventions, §9 for data flow.

---

## 1. Requirements & Constraints

- **REQ-001**: `phoenix-backend/pyproject.toml` includes **all** runtime dependencies (cdsapi, rasterio, rio-tiler, geopandas, shapely, pillow currently live only in Dockerfiles)
- **REQ-002**: A setup script (`scripts/setup-backend.sh`) installs the Python environment and validates it
- **REQ-003**: ERA5 pipeline smoke test: fetch 1 month → apply land mask → compute anomaly → export GeoTIFF — completes without error
- **REQ-004**: Tile generation: GeoTIFF → zoom 5–7 WebP tiles → passes `validate_tiles.py` coverage check
- **REQ-005**: City correlation: new script `generate_city_correlation.py` produces `cities.json` conforming to `schemas/city-correlation.schema.json` with all ~2,949 German cities
- **REQ-006**: Metrics pipeline: all 8 calculators → `aggregate_to_country` + `aggregate_to_cities` (subset) → `export_metrics_json` per tile + germany.json → valid against `schemas/metrics.schema.json`
- **REQ-007**: Plot CSV generation: **new module** `analysis/plots/` with `export_plot_data.py` produces the 4 CSV types defined in `schemas/plot-csv-headers.schema.json` (temperature_evolution, seasonal_warming, extremes, monthly_distribution) per tile + germany
- **REQ-008**: All generated artifacts copied to `phoenix-frontend/public/data/` and `phoenix-frontend/public/mock-tiles/`, replacing hand-crafted fixtures
- **REQ-009**: All 3 Docker jobs build and dry-run successfully with phoenix directory paths
- **REQ-010**: All existing backend tests still pass; new tests added for plot CSV generation and city correlation
- **CON-001**: ERA5-Land data requires a CDS API key (`CDS_API_KEY` env var). The pipeline needs sufficient historical data for metrics (at minimum 2020–2025 monthly, ideally 1961–2025 for reference period)
- **CON-002**: The metrics pipeline requires daily data (for threshold-based calculators: hot days, frost days, etc.) — not just monthly
- **CON-003**: Full pipeline run (all years, all metrics, all tiles) may take hours. The sprint uses a minimal representative run (1–2 years + reference climatology) to validate correctness, then optionally a full run for production data
- **PAT-001**: New code follows existing patterns: `TypedDict` for return types, `ClimateDataProvider` protocol for data access, existing test fixtures and mocking patterns
- **GUD-001**: Each pipeline stage has a validation checkpoint — no "trust that it worked" steps

---

## 2. Implementation Steps

### Phase 1: Backend Dependencies & Local Environment

- GOAL-001: A developer can `poetry install` and have a fully functional scientific Python environment

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-001 | Update `phoenix-backend/pyproject.toml` — add all runtime deps that currently only exist in Dockerfiles: `cdsapi`, `rasterio`, `rioxarray`, `rio-tiler`, `geopandas`, `shapely`, `pillow`. Group them under `[tool.poetry.group.pipeline.dependencies]` so tests-only devs can skip the heavy geospatial stack. Keep existing deps (`requests`, `bs4`, `matplotlib`, `xarray`, `numpy`, `boto3`, `tqdm`, `ephem`, `netcdf4`, `scipy`, `mercantile`) in main deps. | | |
| TASK-002 | Create `phoenix-backend/scripts/setup-backend.sh` — installs poetry env, checks Python ≥3.13, runs `poetry install --with pipeline`, validates CDS API key is set (warn if not, don't fail — tests don't need it), runs `pytest -x --tb=short` to verify setup. | | |
| TASK-003 | Create `phoenix-backend/.env.example` — documents all env vars: `CDS_API_KEY`, `ACCESS_KEY`, `SECRET_KEY`, `ENDPOINT_URL`, `BUCKET_NAME`, `CLIMATE_DATA_PROVIDER` (default `era5-land`), `FORCE_REPROCESS`. Include instructions as comments. | | |
| TASK-004 | Verify: `cd phoenix-backend && poetry install --with pipeline && pytest -x --tb=short` — all existing tests pass with the updated dependencies. | | |

### Phase 2: ERA5 Pipeline Smoke Test

- GOAL-002: Prove the ERA5 fetch → anomaly → GeoTIFF pipeline runs end-to-end for 1 month

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-005 | Create `phoenix-backend/scripts/run_pipeline_smoke_test.py` — orchestration script that runs the full pipeline for a single month (default: July 2024). Steps: (1) `get_provider('era5-land')`, (2) `provider.fetch_monthly(2024, 7, output_dir, 't2m')`, (3) load reference climatology for July via `load_climatology()`, (4) `calculate_monthly_anomaly()`, (5) `apply_germany_land_mask()`, (6) `export_anomaly_geotiff()`. All outputs go to `phoenix-backend/output/smoke-test/`. Prints status at each step. | | |
| TASK-006 | Run the smoke test: `python scripts/run_pipeline_smoke_test.py`. Verify: GeoTIFF exists at `output/smoke-test/anomaly_2024_07.tif`, is a valid raster, covers Germany bounds, values are in plausible anomaly range (±5°C). | | |
| TASK-007 | If reference climatology (1961–1990 baseline) needs to be pre-fetched: document how to obtain it (either via `fetch_reference_climatology(provider)` or by downloading a pre-computed file). Add the reference climatology path to `.env.example`. | | |

### Phase 3: Tile Generation & Validation

- GOAL-003: Convert GeoTIFF to WebP tiles and verify they meet quality standards

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-008 | Run `generate_tiles_for_geotiff('output/smoke-test/anomaly_2024_07.tif', 'output/smoke-test/tiles/', 2024, 7)` — generates zoom 5–7 WebP tiles. | | |
| TASK-009 | Run `validate_tile_coverage('output/smoke-test/tiles/', 2024, 7)` — verify: directory exists, expected tile count per zoom level, all tiles are 256×256 RGBA WebP under 50KB. Print the `ValidationResult`. | | |
| TASK-010 | Visually verify via `create_preview_image('output/smoke-test/tiles/', 2024, 7, zoom=6)` — save composite PNG, check it looks like a Germany anomaly map (blue/red pattern, land-only, transparent ocean). | | |
| TASK-011 | Copy validated tiles to `phoenix-frontend/public/mock-tiles/2024/07/` — replacing the synthetic mock tiles for July 2024 with real data. Verify frontend renders them: `cd phoenix-frontend && npm run dev` — map shows real anomaly data. | | |

### Phase 4: City Correlation Generation

- GOAL-004: Generate the full `cities.json` mapping ~2,949 German cities to ERA5-Land grid cells

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-012 | Create `phoenix-backend/analysis/geonames/generate_city_correlation.py` — takes `german_cities_p5000.csv` (city name, lat, lon) + ERA5-Land grid resolution (0.1°) + Germany bounds → produces `cities.json` conforming to `schemas/city-correlation.schema.json`. For each city: (1) compute nearest grid cell indices `grid_i`, `grid_j` from lat/lon, (2) compute `grid_lat`, `grid_lon` (snapped to grid), (3) generate `tile_id` as `"{grid_i}_{grid_j}"`, (4) generate `slug` via umlaut-safe conversion (ä→ae, ö→oe, ü→ue, ß→ss, spaces→hyphens, lowercase). Output includes `meta` envelope with grid_resolution, bounds, city_count. | | |
| TASK-013 | Handle slug collisions: if two cities produce the same slug, append disambiguation suffix (e.g., state abbreviation or population rank). Log all collisions. | | |
| TASK-014 | Create `phoenix-backend/analysis/geonames/tests/test_generate_city_correlation.py` — test: grid cell assignment for known cities (Berlin ≈ 52.52°N 13.4°E → grid_i=76, grid_j=53), slug generation (München → muenchen), schema conformance of output, slug uniqueness. | | |
| TASK-015 | Run the generator: `python -m analysis.geonames.generate_city_correlation --input phoenix-backend/data/german_cities_p5000.csv --output output/cities.json`. Verify: ~2,949 cities, valid against schema, Berlin's tile_id is `"76_53"`. | | |
| TASK-016 | Copy `output/cities.json` → `phoenix-frontend/public/data/cities.json` — replacing the dev fixture from Sprint 3 with real data. Verify: city search in frontend now shows all ~2,949 cities. | | |

### Phase 5: Metrics Pipeline End-to-End

- GOAL-005: Run all 8 metric calculators, aggregate, export JSON, validate

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-017 | Fetch sufficient ERA5-Land data for metrics calculation. **Minimum viable**: monthly t2m for 1961–2025 (for reference period + trends), daily tmax/tmin for 2020–2025 (for threshold days, record days). This is a significant download (~2–4 GB). Document the fetch commands and expected duration. | | |
| TASK-018 | Create `phoenix-backend/scripts/run_metrics_pipeline.py` — orchestration script. Steps: (1) load monthly + daily datasets, (2) run each calculator: `calculate_five_year_anomaly`, `calculate_warming_rate`, `count_record_days`, `calculate_winter_warming`, `calculate_threshold_days`, `calculate_snow_days_lost`, `calculate_comfortable_days`, `calculate_decadal_aggregates`. (3) Compose results into `LocationMetrics` TypedDict. (4) Run `aggregate_to_country()` → `export_germany_metrics()`. (5) For a subset of tile_ids (from cities.json): run `aggregate_to_cities()` → `export_all_tile_metrics()`. All output to `output/metrics/`. | | |
| TASK-019 | Run the metrics pipeline. Verify: `output/metrics/germany.json` exists and is valid against `schemas/metrics.schema.json`. Spot-check values: Germany fiveYearAnomaly should be ~+1.0 to +1.5°C, warmingRate ~0.3 to 0.6°C/decade, comfortableDays ~70–100. | | |
| TASK-020 | Verify per-tile metrics: `output/metrics/tiles/76_53.json` (Berlin) exists and is valid. Values should differ slightly from Germany-wide. | | |
| TASK-021 | Copy `output/metrics/germany.json` → `phoenix-frontend/public/data/metrics/germany.json`. Copy a representative set of tile metrics (at minimum Berlin, München, Hamburg) → `phoenix-frontend/public/data/metrics/{tile_id}.json`. These replace Sprint 4's hand-crafted fixtures. | | |

### Phase 6: Plot CSV Generation (New Module)

- GOAL-006: Create the missing plot data export module and generate CSVs for all 4 defined plot types

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-022 | Create `phoenix-backend/analysis/plots/__init__.py` | | |
| TASK-023 | Create `phoenix-backend/analysis/plots/export_plot_data.py` with the following functions: | | |
| | **`export_temperature_evolution(monthly_ds, grid_i, grid_j, output_dir, reference_period)`** — Extracts annual mean temperature at the grid cell across all years. Computes anomaly vs reference period mean. Computes LOWESS trend (via `scipy.signal.savgol_filter` or `statsmodels.lowess`). Writes CSV: `year,temperature,anomaly,trend`. | | |
| | **`export_seasonal_warming(monthly_ds, grid_i, grid_j, output_dir, reference_period)`** — Groups months into seasons (DJF, MAM, JJA, SON), computes seasonal means per year, outputs as anomalies vs reference period. Writes CSV: `year,winter,spring,summer,fall`. | | |
| | **`export_extremes(daily_ds, grid_i, grid_j, output_dir, reference_period)`** — Counts hot days (tmax ≥ 30°C) and frost days (tmin ≤ 0°C) per year. Computes reference period averages. Writes CSV: `year,hot_days,cold_days,reference_hot,reference_cold`. | | |
| | **`export_monthly_distribution(monthly_ds, grid_i, grid_j, output_dir, reference_period, current_period)`** — For each calendar month (1–12), computes min/q1/median/q3/max/mean of temperatures across current period and reference period. Writes CSV: `month,cur_min,cur_q1,cur_median,cur_q3,cur_max,cur_mean,ref_min,ref_q1,ref_median,ref_q3,ref_max,ref_mean`. | | |
| | **`export_all_plots_for_location(monthly_ds, daily_ds, grid_i, grid_j, output_dir, reference_period, current_period)`** — Convenience function calling all 4 exporters. | | |
| | **`export_all_plots_for_germany(monthly_ds, daily_ds, output_dir, reference_period, current_period)`** — Aggregates across Germany (area-weighted mean) then exports all 4 CSVs to `{output_dir}/germany/`. | | |
| TASK-024 | Create `phoenix-backend/analysis/plots/types.py` — TypedDicts for plot data rows: `TemperatureEvolutionRow`, `SeasonalWarmingRow`, `ExtremesRow`, `MonthlyDistributionRow`. Also `PlotType` literal type. | | |
| TASK-025 | Create `phoenix-backend/analysis/plots/tests/__init__.py` and `phoenix-backend/analysis/plots/tests/test_export_plot_data.py` — Tests using synthetic xarray datasets (same `StubProvider` pattern from existing metric tests): (1) temperature_evolution CSV has correct columns, years span matches dataset, trend is monotonic or smooth, (2) seasonal_warming CSV has 4 seasons + year, values are plausible anomalies, (3) extremes CSV counts match manual threshold check on synthetic data, (4) monthly_distribution CSV has 12 rows (one per month), quantiles are ordered (min ≤ q1 ≤ median ≤ q3 ≤ max). | | |
| TASK-026 | Create `phoenix-backend/scripts/run_plot_pipeline.py` — orchestration script. Reads cities.json (from Phase 4), for germany + a configurable subset of cities (default: 10 largest), runs `export_all_plots_for_location()`. Output to `output/plots/{tile_id}/` and `output/plots/germany/`. | | |
| TASK-027 | Run the plot pipeline. Verify: `output/plots/germany/temperature_evolution.csv` exists, has years ~1961–2025, temperature values ~7–11°C for Germany, trend line is smooth. | | |
| TASK-028 | Validate all CSVs against `schemas/plot-csv-headers.schema.json` — headers match exactly, no missing columns, no empty required fields. | | |
| TASK-029 | Copy plot CSVs to `phoenix-frontend/public/data/plots/germany/` and `phoenix-frontend/public/data/plots/{tile_id}/` for test cities. These replace Sprint 5's hand-crafted fixtures. | | |

### Phase 7: Docker Job Dry-Run

- GOAL-007: Verify all 3 Docker batch jobs build and run with phoenix directory structure

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-030 | Update `phoenix-backend/jobs/job-era5-daily/Dockerfile` — verify COPY paths reference `phoenix-backend/analysis/` (not `analysis/`). If Sprint 1's copy was a flat copy, the Dockerfile paths may already be correct; verify and fix if needed. | | |
| TASK-031 | Update `phoenix-backend/jobs/job-era5-monthly/Dockerfile` — same verification. | | |
| TASK-032 | Update `phoenix-backend/jobs/job-era5-yearly/Dockerfile` — same verification. Ensure it includes `analysis/metrics/` and `analysis/plots/` for metrics + plot generation. | | |
| TASK-033 | Build all 3 Docker images locally: `docker build -t phoenix-era5-daily phoenix-backend/jobs/job-era5-daily/` (repeat for monthly, yearly). All must build without error. | | |
| TASK-034 | Dry-run daily job: `docker run --env-file .env phoenix-era5-daily`. If CDS API key is available, use `FORCE_REPROCESS=false` to skip already-processed months. If no key, verify the job validates env vars and exits with a clear error (not a crash). | | |
| TASK-035 | Dry-run yearly job: same approach. Verify it invokes metrics calculation + export. | | |
| TASK-036 | Document any Dockerfile changes needed for Sprint 7 (deployment). Note image sizes. | | |

### Phase 8: Integration Verification

- GOAL-008: All tests pass, frontend works with real data, pipeline is documented

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-037 | Run full backend test suite: `cd phoenix-backend && pytest -x --tb=short` — all existing + new tests pass. | | |
| TASK-038 | Run frontend test suite: `cd phoenix-frontend && npm run test` — all Sprint 1–3 tests still pass (city search now loads real 2,949 cities instead of 3-city fixture; verify search still works). | | |
| TASK-039 | Manual integration check: start frontend dev server (`npm run dev`), verify: (1) map shows real anomaly tiles for July 2024, (2) city search returns results from all major German cities, (3) dev fixture metrics JSON loads for Berlin. | | |
| TASK-040 | Create `phoenix-backend/docs/pipeline-runbook.md` — document: how to set up the dev environment, how to run each pipeline stage, expected data volumes and durations, troubleshooting common errors (CDS API quota, missing reference climatology, S3 connectivity). | | |

---

## 3. Alternatives

- **ALT-001**: Skip real ERA5 data and continue with synthetic mock data through Sprint 7 — rejected because sprints 4–6 depend on realistic data shapes, and Sprint 7 would discover pipeline bugs too late
- **ALT-002**: Run the full pipeline for all years (1961–2025) in this sprint — rejected for time; a smoke test (1 month tile + sufficient years for metrics) validates correctness without multi-hour downloads. Full historical run is a Phase 2 "initial data upload" task in Sprint 7
- **ALT-003**: Generate plot CSVs by hand instead of building `analysis/plots/export_plot_data.py` — rejected because (a) 9 plot types × ~2,949 cities can't be hand-written, (b) the generation code is needed for automated nightly updates, (c) hand-written data won't reflect real climate patterns
- **ALT-004**: Use a different trend method (linear regression) instead of LOWESS for temperature evolution — LOWESS better captures non-linear warming acceleration; `scipy.signal.savgol_filter` is a lightweight alternative that's already a dependency
- **ALT-005**: Defer Docker job testing to Sprint 7 — rejected because Docker path issues are cheap to find now and expensive to debug during deployment

## 4. Dependencies

- **DEP-001**: Sprint 1 completed (`phoenix-backend/` exists with copied code, `pytest` passes)
- **DEP-002**: Sprint 3 completed (frontend city search works — verifies `cities.json` integration)
- **DEP-003**: CDS API key with sufficient quota (free tier provides adequate access for ERA5-Land)
- **DEP-004**: Python ≥3.13 with ability to install geospatial libraries (GDAL/rasterio may require system packages: `libgdal-dev`, `libproj-dev`)
- **DEP-005**: Docker (for Phase 7 dry-runs)
- **DEP-006**: `german_cities_p5000.csv` — exists at `frontend/public/german_cities_p5000.csv` (copy to `phoenix-backend/data/`)
- **DEP-007**: Germany GeoJSON boundary — exists at `frontend/public/germany_10m_admin_0_reduced.json` (needed for land mask)

## 5. Files

### New Backend Modules

- **FILE-001**: `phoenix-backend/analysis/plots/__init__.py` — NEW — Plot export package
- **FILE-002**: `phoenix-backend/analysis/plots/export_plot_data.py` — NEW — 4 CSV type generators + orchestrators
- **FILE-003**: `phoenix-backend/analysis/plots/types.py` — NEW — Plot data TypedDicts
- **FILE-004**: `phoenix-backend/analysis/plots/tests/__init__.py` — NEW — Test package
- **FILE-005**: `phoenix-backend/analysis/plots/tests/test_export_plot_data.py` — NEW — Unit tests for all 4 exporters
- **FILE-006**: `phoenix-backend/analysis/geonames/generate_city_correlation.py` — NEW — City-to-grid mapping + JSON generation
- **FILE-007**: `phoenix-backend/analysis/geonames/tests/test_generate_city_correlation.py` — NEW — Tests for city correlation

### New Scripts

- **FILE-008**: `phoenix-backend/scripts/setup-backend.sh` — NEW — Dev environment setup
- **FILE-009**: `phoenix-backend/scripts/run_pipeline_smoke_test.py` — NEW — ERA5 → GeoTIFF smoke test
- **FILE-010**: `phoenix-backend/scripts/run_metrics_pipeline.py` — NEW — Full metrics orchestration
- **FILE-011**: `phoenix-backend/scripts/run_plot_pipeline.py` — NEW — Plot CSV orchestration

### Modified Backend Files

- **FILE-012**: `phoenix-backend/pyproject.toml` — MODIFY — Add pipeline dependency group
- **FILE-013**: `phoenix-backend/.env.example` — NEW — Documented environment variables
- **FILE-014**: `phoenix-backend/jobs/job-era5-daily/Dockerfile` — MODIFY (if needed) — Fix COPY paths
- **FILE-015**: `phoenix-backend/jobs/job-era5-monthly/Dockerfile` — MODIFY (if needed) — Fix COPY paths
- **FILE-016**: `phoenix-backend/jobs/job-era5-yearly/Dockerfile` — MODIFY — Add `analysis/plots/` COPY

### Backend Data

- **FILE-017**: `phoenix-backend/data/german_cities_p5000.csv` — NEW (copied from `frontend/public/`)
- **FILE-018**: `phoenix-backend/data/germany_10m_admin_0_reduced.json` — NEW (copied from `frontend/public/`)

### Generated Output (→ replaced frontend dev fixtures)

- **FILE-019**: `phoenix-frontend/public/data/cities.json` — MODIFY (replace fixture with real ~2,949 cities)
- **FILE-020**: `phoenix-frontend/public/data/metrics/germany.json` — MODIFY (replace hand-crafted with real)
- **FILE-021**: `phoenix-frontend/public/data/metrics/{tile_id}.json` — MODIFY (replace with real per-city)
- **FILE-022**: `phoenix-frontend/public/data/plots/germany/*.csv` — MODIFY (replace with real CSVs)
- **FILE-023**: `phoenix-frontend/public/data/plots/{tile_id}/*.csv` — MODIFY (replace with real CSVs)
- **FILE-024**: `phoenix-frontend/public/mock-tiles/2024/07/` — MODIFY (replace synthetic with real tiles)

### Documentation

- **FILE-025**: `phoenix-backend/docs/pipeline-runbook.md` — NEW — Operations documentation

---

## 6. Testing

- **TEST-001**: `test_generate_city_correlation.py` — Berlin maps to grid cell ~(76, 53); slug('München') → 'muenchen'; output has ~2,949 entries; no duplicate slugs; valid against `city-correlation.schema.json`
- **TEST-002**: `test_export_plot_data.py` — `export_temperature_evolution` produces CSV with columns `year,temperature,anomaly,trend`; year range matches dataset; trend values are smooth (low variance between adjacent years)
- **TEST-003**: `test_export_plot_data.py` — `export_seasonal_warming` produces CSV with columns `year,winter,spring,summer,fall`; 4 seasons sum to plausible values
- **TEST-004**: `test_export_plot_data.py` — `export_extremes` produces CSV with `year,hot_days,cold_days,reference_hot,reference_cold`; counts match manual threshold check on synthetic 5×5 grid
- **TEST-005**: `test_export_plot_data.py` — `export_monthly_distribution` produces 12 rows; quantiles ordered (min ≤ q1 ≤ median ≤ q3 ≤ max) for both current and reference periods
- **TEST-006**: Existing backend tests still pass — `pytest -x --tb=short` (all tests from Sprint 1)
- **TEST-007**: Smoke test GeoTIFF is a valid raster covering Germany bounds with anomaly values in ±5°C range
- **TEST-008**: Tile validation passes: correct count per zoom, all 256×256 RGBA WebP under 50KB
- **TEST-009**: `germany.json` metrics valid against `schemas/metrics.schema.json`; values in plausible ranges
- **TEST-010**: Frontend regression — all Sprint 1–3 frontend tests pass with real data fixtures

---

## 7. Risks & Assumptions

### Risks

- **RISK-001**: CDS API may be slow or rate-limited for large historical fetches — **Mitigation**: smoke test needs only 1 month; metrics pipeline needs ~60 monthly files (5 years) which is feasible in <1 hour. Full 1961–2025 fetch (~780 files) is deferred to pre-deployment in Sprint 7.
- **RISK-002**: Geospatial dependencies (GDAL, rasterio) are notoriously hard to install on some platforms — **Mitigation**: `setup-backend.sh` documents system prerequisites; Docker provides a fallback environment if local install fails.
- **RISK-003**: Reference climatology (1961–1990 baseline) may need to be pre-computed from 30 years of ERA5-Land data instead of fetched as a single file — **Mitigation**: document the process; if pre-computation is needed, add it as a one-time setup step with output cached to disk.
- **RISK-004**: Plot CSV generation for all ~2,949 cities is computationally expensive — **Mitigation**: Sprint 3b generates only for germany + ~10 test cities. Full coverage is a Sprint 7 batch job task.
- **RISK-005**: City slug collisions may exist among 2,949 cities — **Mitigation**: generator detects and resolves collisions with suffix; test verifies uniqueness.
- **RISK-006**: LOWESS trend calculation may require `statsmodels` (not currently a dependency) — **Mitigation**: use `scipy.signal.savgol_filter` as a pure-scipy alternative that's already in the dependency tree.

### Assumptions

- **ASSUMPTION-001**: The developer running this sprint has a CDS API key (free registration at https://cds.climate.copernicus.eu)
- **ASSUMPTION-002**: ERA5-Land monthly data for 2020–2025 is available via CDS API (typical ~5-day delay for most recent)
- **ASSUMPTION-003**: The existing `german_cities_p5000.csv` contains sufficient data (city name, lat, lon) for correlation generation
- **ASSUMPTION-004**: `generate_mock_tiles.py` (synthetic) is already adapted and working from Sprint 1 — this sprint adds real tiles alongside, not replacing the generation script
- **ASSUMPTION-005**: The `analysis/plots/` directory does not exist yet — this sprint creates it from scratch

---

## 8. Multi-Agent Execution Notes

### Execution Order

```
Phase 1 (deps/env)
    ↓
Phase 2 (ERA5 smoke) ──→ Phase 3 (tiles)
    ↓
Phase 4 (city correlation) ← independent of Phase 2/3
    ↓
Phase 5 (metrics) ← needs data from Phase 2 + cities from Phase 4
    ↓
Phase 6 (plots) ← needs data from Phase 2, can parallel with Phase 5
    ↓
Phase 7 (Docker) ← needs FILE changes from Phases 5+6
    ↓
Phase 8 (integration) ← after all phases
```

- **Parallel after Phase 1**: Phase 4 (city correlation) is independent of Phase 2/3 and can start immediately
- **Parallel after data fetch**: Phase 5 (metrics) and Phase 6 (plots) can run in parallel since they read the same ERA5 datasets
- **Sequential**: Phase 7 (Docker) needs the code from Phase 5+6 to be in place

### Agent Context Requirements

- Read `plan/phoenix/00-architecture.md` §4 for all data contracts
- Read `phoenix-backend/analysis/era5/providers/era5_land.py` for CDS API usage pattern
- Read `phoenix-backend/analysis/metrics/export_metrics.py` for JSON export pattern
- Read `phoenix-backend/analysis/tiles/generate_tiles.py` for tile generation API
- Read `phoenix-backend/analysis/tiles/validate_tiles.py` for tile validation API
- Read `phoenix-backend/analysis/metrics/aggregate_metrics.py` for city/country aggregation
- Read `phoenix-backend/conftest.py` for test fixture patterns (StubProvider, synthetic datasets)
- Read `schemas/metrics.schema.json`, `schemas/city-correlation.schema.json`, `schemas/plot-csv-headers.schema.json` for validation

### Validation Checkpoints

- [After TASK-004]: `poetry install --with pipeline && pytest` passes
- [After TASK-006]: GeoTIFF exists at `output/smoke-test/anomaly_2024_07.tif`
- [After TASK-009]: Tile validation passes with expected counts
- [After TASK-015]: `output/cities.json` has ~2,949 entries, valid against schema
- [After TASK-019]: `output/metrics/germany.json` valid against schema, plausible values
- [After TASK-028]: All plot CSVs valid against headers schema
- [After TASK-035]: Docker images build, dry-run exits cleanly
- [After TASK-038]: All backend + frontend tests pass

---

## 9. Related Specifications / Further Reading

- `plan/phoenix/00-architecture.md` — §4 Interface Contracts, §7 Backend Conventions, §9 Data Flow
- `plan/phoenix/sprint-1-mvp-map.md` — Phase 1 (backend copy), the starting point for this sprint
- `plan/phoenix/sprint-7-infrastructure.md` — Phase 2 (data upload) builds on the validated pipeline from this sprint
- `schemas/metrics.schema.json` — Metrics JSON contract
- `schemas/city-correlation.schema.json` — City correlation JSON contract
- `schemas/plot-csv-headers.schema.json` — Plot CSV header definitions
- `phoenix-backend/analysis/metrics/types.py` — Python TypedDict definitions for metrics
- `phoenix-backend/analysis/era5/providers/protocol.py` — ClimateDataProvider Protocol

---

## 10. Code Reference

### 10.1 ERA5 Pipeline Orchestration Pattern

**File**: `phoenix-backend/scripts/run_pipeline_smoke_test.py` (to be created)

```python
#!/usr/bin/env python3
"""Smoke test: run ERA5 pipeline for a single month end-to-end."""
import sys
from pathlib import Path

from analysis.era5 import get_provider, GERMANY_BOUNDS, REFERENCE_PERIOD
from analysis.era5.calculate_anomalies import (
    load_climatology,
    calculate_monthly_anomaly,
    export_anomaly_geotiff,
)
from analysis.era5.apply_land_mask import apply_germany_land_mask


def main(year: int = 2024, month: int = 7) -> None:
    output_dir = Path("output/smoke-test")
    output_dir.mkdir(parents=True, exist_ok=True)

    provider = get_provider("era5-land")
    print(f"[1/5] Fetching {year}-{month:02d} from {provider.display_name}...")
    monthly_path = provider.fetch_monthly(year, month, output_dir / "raw", "t2m")

    print("[2/5] Loading reference climatology...")
    reference_ds = load_climatology(output_dir / "climatology", month)

    print("[3/5] Calculating anomaly...")
    ds = provider.load_dataset(monthly_path)
    anomaly_ds = calculate_monthly_anomaly(ds, reference_ds, year, month)

    print("[4/5] Applying land mask...")
    masked_ds = apply_germany_land_mask(anomaly_ds, provider)

    geotiff_path = output_dir / f"anomaly_{year}_{month:02d}.tif"
    print(f"[5/5] Exporting GeoTIFF → {geotiff_path}")
    export_anomaly_geotiff(masked_ds, geotiff_path, year, month)

    print(f"✓ Smoke test complete. Output: {geotiff_path}")


if __name__ == "__main__":
    year = int(sys.argv[1]) if len(sys.argv) > 1 else 2024
    month = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    main(year, month)
```

### 10.2 City Correlation Generator

**File**: `phoenix-backend/analysis/geonames/generate_city_correlation.py` (to be created)

```python
#!/usr/bin/env python3
"""Generate cities.json mapping German cities to ERA5-Land grid cells."""
import csv
import json
import re
import unicodedata
from pathlib import Path

GRID_RESOLUTION = 0.1  # ERA5-Land native resolution in degrees
GERMANY_BOUNDS = {"north": 55.1, "south": 47.2, "west": 5.8, "east": 15.1}

UMLAUT_MAP = {
    "ä": "ae", "ö": "oe", "ü": "ue",
    "Ä": "Ae", "Ö": "Oe", "Ü": "Ue",
    "ß": "ss",
}


def to_slug(name: str) -> str:
    """Convert city name to URL-safe slug. München → muenchen."""
    slug = name
    for char, replacement in UMLAUT_MAP.items():
        slug = slug.replace(char, replacement)
    slug = unicodedata.normalize("NFKD", slug).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-zA-Z0-9\s-]", "", slug)
    slug = re.sub(r"[\s]+", "-", slug.strip())
    return slug.lower()


def nearest_grid_index(value: float, origin: float, resolution: float) -> int:
    """Find nearest grid cell index for a coordinate value."""
    return round((value - origin) / resolution)


def generate_city_correlation(
    cities_csv: Path,
    output_path: Path,
    grid_resolution: float = GRID_RESOLUTION,
    bounds: dict = GERMANY_BOUNDS,
) -> dict:
    cities = []
    slugs_seen: dict[str, str] = {}  # slug → city_name (for collision detection)

    with open(cities_csv, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["city_name"].strip()
            lat = float(row["lat"])
            lon = float(row["lon"])

            grid_j = nearest_grid_index(lat, bounds["south"], grid_resolution)
            grid_i = nearest_grid_index(lon, bounds["west"], grid_resolution)
            grid_lat = round(bounds["south"] + grid_j * grid_resolution, 1)
            grid_lon = round(bounds["west"] + grid_i * grid_resolution, 1)

            slug = to_slug(name)
            if slug in slugs_seen:
                # Disambiguate with grid coordinates
                slug = f"{slug}-{grid_i}-{grid_j}"
            slugs_seen[slug] = name

            cities.append({
                "name": name,
                "slug": slug,
                "lat": lat,
                "lon": lon,
                "grid_i": grid_i,
                "grid_j": grid_j,
                "grid_lat": grid_lat,
                "grid_lon": grid_lon,
                "tile_id": f"{grid_i}_{grid_j}",
            })

    result = {
        "meta": {
            "grid_resolution": grid_resolution,
            "bounds": bounds,
            "city_count": len(cities),
        },
        "cities": sorted(cities, key=lambda c: c["name"]),
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return result
```

### 10.3 Plot CSV Export — Temperature Evolution

**File**: `phoenix-backend/analysis/plots/export_plot_data.py` (to be created)

```python
"""Export plot CSV data from ERA5 datasets for frontend narrative section."""
import csv
from pathlib import Path
from typing import Literal

import numpy as np
import xarray as xr
from scipy.signal import savgol_filter

PlotType = Literal[
    "temperature_evolution",
    "seasonal_warming",
    "extremes",
    "monthly_distribution",
]

SEASONS = {"winter": [12, 1, 2], "spring": [3, 4, 5], "summer": [6, 7, 8], "fall": [9, 10, 11]}


def export_temperature_evolution(
    monthly_ds: xr.Dataset,
    grid_i: int,
    grid_j: int,
    output_dir: Path,
    reference_period: tuple[int, int] = (1961, 1990),
    variable: str = "t2m",
) -> Path:
    """Generate temperature_evolution.csv for a single grid cell."""
    # Extract time series at grid cell
    cell = monthly_ds[variable].isel(longitude=grid_i, latitude=grid_j)
    annual_mean = cell.groupby("time.year").mean("time")

    years = annual_mean.year.values
    temps = annual_mean.values

    # Reference period mean
    ref_mask = (years >= reference_period[0]) & (years <= reference_period[1])
    ref_mean = float(np.nanmean(temps[ref_mask]))
    anomalies = temps - ref_mean

    # Smoothed trend (Savitzky-Golay filter, window ~15 years)
    window = min(len(years) // 2 * 2 - 1, 15)
    if window >= 5:
        trend = savgol_filter(anomalies, window_length=window, polyorder=2)
    else:
        trend = anomalies  # fallback for very short series

    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "temperature_evolution.csv"
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["year", "temperature", "anomaly", "trend"])
        for y, t, a, tr in zip(years, temps, anomalies, trend):
            writer.writerow([int(y), round(float(t), 2), round(float(a), 2), round(float(tr), 2)])

    return path


def export_seasonal_warming(
    monthly_ds: xr.Dataset,
    grid_i: int,
    grid_j: int,
    output_dir: Path,
    reference_period: tuple[int, int] = (1961, 1990),
    variable: str = "t2m",
) -> Path:
    """Generate seasonal_warming.csv for a single grid cell."""
    cell = monthly_ds[variable].isel(longitude=grid_i, latitude=grid_j)
    years = sorted(set(cell.time.dt.year.values))

    # Compute reference seasonal means
    ref_seasonal = {}
    for season, months in SEASONS.items():
        mask = cell.time.dt.month.isin(months)
        ref_mask = mask & (cell.time.dt.year >= reference_period[0]) & (cell.time.dt.year <= reference_period[1])
        ref_seasonal[season] = float(cell.sel(time=ref_mask).mean().values)

    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "seasonal_warming.csv"
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["year", "winter", "spring", "summer", "fall"])
        for year in years:
            row = [int(year)]
            for season, months in SEASONS.items():
                mask = cell.time.dt.month.isin(months) & (cell.time.dt.year == year)
                val = cell.sel(time=mask)
                if len(val) > 0:
                    anomaly = float(val.mean().values) - ref_seasonal[season]
                    row.append(round(anomaly, 2))
                else:
                    row.append("")
            writer.writerow(row)

    return path
```

### 10.4 Metrics Pipeline Orchestration

**File**: `phoenix-backend/scripts/run_metrics_pipeline.py` (to be created)

```python
#!/usr/bin/env python3
"""Run all 8 metric calculators → aggregate → export JSON."""
import json
from pathlib import Path

from analysis.era5 import get_provider
from analysis.metrics.calculate_five_year_anomaly import calculate_five_year_anomaly
from analysis.metrics.calculate_warming_rate import calculate_warming_rate
from analysis.metrics.calculate_record_days import count_record_days
from analysis.metrics.calculate_winter_warming import calculate_winter_warming
from analysis.metrics.calculate_threshold_days import calculate_threshold_days
from analysis.metrics.calculate_snow_days_lost import calculate_snow_days_lost
from analysis.metrics.calculate_comfortable_days import calculate_comfortable_days
from analysis.metrics.calculate_decadal_aggregates import calculate_decadal_aggregates
from analysis.metrics.aggregate_metrics import aggregate_to_country
from analysis.metrics.export_metrics import export_germany_metrics, export_all_tile_metrics


def run_metrics(monthly_ds, daily_ds, provider, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    print("[1/8] Five-year anomaly...")
    five_year = calculate_five_year_anomaly(monthly_ds, "t2m")

    print("[2/8] Warming rate...")
    warming = calculate_warming_rate(monthly_ds, "t2m")

    print("[3/8] Record days...")
    records = count_record_days(daily_ds, 2025, "tmax", "tmin")

    print("[4/8] Winter warming...")
    winter = calculate_winter_warming(monthly_ds, "t2m")

    print("[5/8] Threshold days...")
    thresholds = calculate_threshold_days(daily_ds, 2025)

    print("[6/8] Snow days lost...")
    snow = calculate_snow_days_lost(daily_ds, "tmean", "tp")

    print("[7/8] Comfortable days...")
    comfort = calculate_comfortable_days(daily_ds, "tmean")

    print("[8/8] Decadal aggregates...")
    decadal = calculate_decadal_aggregates(monthly_ds, "t2m", "tmax")

    # Compose LocationMetrics
    from datetime import datetime, timezone
    metrics = {
        "calculatedAt": datetime.now(timezone.utc).isoformat(),
        "fiveYearAnomaly": five_year,
        "warmingRate": warming,
        "recordDays": records,
        "winterWarming": winter,
        "seasonalWarming": {},  # TODO: extract from calculate_winter_warming or add dedicated calculator
        "thresholdDays": thresholds,
        "snowDaysLost": snow,
        "comfortableDays": comfort,
    }

    print("Exporting germany.json...")
    export_germany_metrics(metrics, output_dir, provider)
    print(f"✓ Metrics exported to {output_dir}")
```

### 10.5 Existing Tile Generation API (reference)

**File**: `phoenix-backend/analysis/tiles/generate_tiles.py` (already exists)

```python
# Key function signatures:
def generate_tiles_for_geotiff(
    geotiff_path: str | Path,
    output_dir: str | Path,
    year: int,
    month: int,
    min_zoom: int = MIN_ZOOM,  # 5
    max_zoom: int = MAX_ZOOM,  # 7
) -> int:
    """Generate WebP tiles from a GeoTIFF anomaly file.
    Returns count of non-transparent tiles generated."""

def render_tile(src, x: int, y: int, z: int) -> np.ndarray | None:
    """Render a single tile using rio-tiler."""

def save_tile(image: np.ndarray, path: Path) -> bool:
    """Save RGBA array as WebP."""
```

### 10.6 Existing Metrics Aggregation API (reference)

**File**: `phoenix-backend/analysis/metrics/aggregate_metrics.py` (already exists)

```python
def aggregate_to_cities(
    grid_data: xr.DataArray,
    cities: pd.DataFrame,
) -> dict[str, float]:
    """Extract value at nearest grid cell for each city."""

def aggregate_to_country(
    grid_data: xr.DataArray,
    weights: xr.DataArray | None = None,
) -> float:
    """Area-weighted mean across Germany."""

def correlate_cities_to_grid(
    cities: pd.DataFrame,
    grid_lats: np.ndarray,
    grid_lons: np.ndarray,
) -> pd.DataFrame:
    """Add grid_lat_idx, grid_lon_idx, grid_lat, grid_lon columns to cities."""
```

### 10.7 Existing Tile Validation API (reference)

**File**: `phoenix-backend/analysis/tiles/validate_tiles.py` (already exists)

```python
@dataclass
class ValidationResult:
    is_valid: bool
    total_tiles: int
    invalid_tiles: list[str]
    zoom_counts: dict[int, int]
    errors: list[str]

def validate_tile_coverage(
    tile_dir: str | Path,
    year: int,
    month: int,
    min_zoom: int = 5,
    max_zoom: int = 7,
) -> ValidationResult:
    """Validate all tiles in a directory for a given year/month."""
```

### 10.8 Plot CSV Headers Schema (reference)

**File**: `phoenix-backend/schemas/plot-csv-headers.schema.json` (already exists)

```json
{
  "temperature_evolution": { "headers": ["year", "temperature", "anomaly", "trend"] },
  "seasonal_warming": { "headers": ["year", "winter", "spring", "summer", "fall"] },
  "extremes": { "headers": ["year", "hot_days", "cold_days", "reference_hot", "reference_cold"] },
  "monthly_distribution": { "headers": ["month", "cur_min", "cur_q1", "cur_median", "cur_q3", "cur_max", "cur_mean", "ref_min", "ref_q1", "ref_median", "ref_q3", "ref_max", "ref_mean"] }
}
```
