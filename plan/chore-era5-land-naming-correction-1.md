---
goal: Correct ERA5 → ERA5-Land references, remove interpolation, and introduce data-source abstraction layer
version: 3.0
date_created: 2026-02-24
last_updated: 2026-02-24
owner: Internal
status: 'Planned'
tags: [chore, documentation, correction, era5-land, abstraction, architecture, resolution]
---

# Introduction

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

The plan documents consistently refer to "ERA5" when the intended dataset is **ERA5-Land**. Per the [ECMWF ERA5 family documentation](https://confluence.ecmwf.int/display/CKB/The+family+of+ERA5+datasets):

- **ERA5** — global atmospheric reanalysis at **0.25° (~31 km)** covering land + ocean + atmosphere
- **ERA5-Land** — land-only reanalysis at **0.1° (~9 km)** with improved land surface physics

This project uses **ERA5-Land** exclusively (land-only Germany visualization at **native 0.1° (~9 km) resolution**). All generic "ERA5" references to the dataset must be corrected to "ERA5-Land". File paths and code identifiers using `era5` as shorthand remain unchanged for brevity.

The current plans incorrectly specify interpolation from 0.1° to ~1 km (0.009°) and include an entire `interpolate_to_grid.py` module. **This interpolation step must be removed.** Data should be used at the provider's native grid resolution. Tile generation (Phase 4, via `rio-tiler`) handles visual upscaling during rendering — the data pipeline itself must not fabricate sub-grid resolution.

Additionally, the current plans hardwire ERA5-Land at every layer (fetch, config, grid, metrics, frontend) with **zero abstraction**. The data source must be plug-and-play replaceable so a future swap (e.g. to ERA5, CERRA, HYRAS, or a country-specific reanalysis) requires only a new adapter — not a codebase rewrite. This plan adds a data-source abstraction layer across the Python pipeline, grid/city correlation, and frontend service boundaries.

## 1. Requirements & Constraints

- **REQ-001**: Every reference to "ERA5" that means the dataset being fetched, processed, or displayed must read "ERA5-Land".
- **REQ-002**: Resolution references must state the provider's native resolution (0.1° / ~9 km for ERA5-Land), not 0.25° (~28 km) and not an interpolated "1 km".
- **REQ-002a**: Remove all references to "1 km visual resolution", "~1 km", "0.009°", the `OUTPUT_GRID` constant, `get_grid_dimensions()`, and the `interpolate_to_grid.py` module. The pipeline operates at native provider resolution; visual upscaling is handled by tile rendering.
- **REQ-002b**: Remove the entire Phase 3.3 (Grid Interpolation) from phase-03 — including TASK-P3-011 through TASK-P3-015, the `interpolate_to_grid.py` code reference, related tests (`test_interpolate.py`), and the `scipy` dependency (if only used for interpolation).
- **REQ-002c**: Remove `data/interpolated/` directory references from Docker/job plans and the interpolation pipeline step from nightly jobs.
- **REQ-003**: File paths using `era5` as a short identifier (e.g. `analysis/era5/`, `job-era5-daily/`, `era5-build.yml`) stay unchanged — they are project-internal names, not dataset labels.
- **REQ-004**: Code identifiers (variable names, function names) using `era5` (e.g. `ERA5_RESOLUTION`, `sample_era5_dataset`, `load_era5_data`) stay unchanged — rename during implementation if desired.
- **REQ-005**: The `source` type union `'era5' | 'era5-land'` in TypeScript/Python types should become a string identifier resolved from the active `ClimateDataProvider`, not a hardcoded literal.
- **REQ-006**: Introduce a `ClimateDataProvider` protocol (Python) / interface (TypeScript) that encapsulates: dataset identity, CDS fetch parameters, variable name mapping, native resolution, grid configuration, coordinate conventions, and unit conversions. All pipeline modules must depend on this protocol, not on concrete ERA5-Land constants.
- **REQ-007**: Provide a single concrete implementation `ERA5LandProvider` that satisfies the protocol. A second provider (e.g. `HYRASProvider` stub) should be planned as a validation test for the abstraction.
- **REQ-008**: Grid/city correlation must accept resolution and bounds from the active provider, not from hardcoded `ERA5_RESOLUTION` / `ERA5_GERMANY_BOUNDS` constants.
- **REQ-009**: Frontend services must parameterize data URLs and metadata labels via a provider configuration object, not hardcode `'era5-land'` strings.
- **REQ-010**: Provider selection must be configuration-driven (env var or config file), not code-driven, so swapping requires zero code changes.
- **CON-001**: Changes are limited to markdown plan files in `plan/` — no source code changes.
- **CON-002**: Abstraction must not add runtime overhead; provider is resolved once at startup/build time, not per-request.
- **GUD-001**: Where "ERA5-Land" already appears correctly, leave it. Where "ERA5/ERA5-Land" appears as a pair, simplify to "ERA5-Land".
- **GUD-002**: Follow the Dependency Inversion Principle: high-level pipeline modules depend on the `ClimateDataProvider` protocol; low-level ERA5-Land specifics live only in `ERA5LandProvider`.
- **GUD-003**: Follow the Strategy Pattern: provider implementations are interchangeable at configuration time.
- **PAT-001**: Python: use `typing.Protocol` for the provider interface (structural subtyping, no inheritance required).
- **PAT-002**: TypeScript: use a plain interface + factory function for provider instantiation.
- **PAT-003**: Keep provider implementations in a `providers/` subdirectory alongside the modules that consume them.

## 2. Implementation Steps

### Implementation Phase 1: Master plan and self-correction plan

- GOAL-001: Correct the two top-level plan files that define the project scope.

| Task     | Description | Completed | Date |
| -------- | ----------- | --------- | ---- |
| TASK-001 | **plan/botox/era5-germany-climate-visualization-1.md — front matter & introduction** — Change `goal:` to "ERA5-Land Climate Visualization…", tag `era5` → `era5-land`, change "using ERA5 reanalysis data" → "using ERA5-Land reanalysis data", change "Germany-focused ERA5 climate visualization" → "Germany-focused ERA5-Land climate visualization" in executive summary. | | |
| TASK-002 | **Master plan — CON-001/CON-002** — Remove CON-001 ("ERA5 native resolution is 0.25°…") entirely. Renumber CON-002 → CON-001 and reword: "ERA5-Land native resolution is 0.1° (~9 km); data is used at native resolution, visual upscaling handled by tile rendering". Remove any mention of "interpolation required". Adjust subsequent CON numbering. | | |
| TASK-003 | **Master plan — REQ-001** — Change "using ERA5 data at 1km visual resolution" → "using ERA5-Land data at native resolution (~9 km)". | | |
| TASK-004 | **Master plan — ALT-005** — Change "ERA5 provides global coverage for future expansion" → "ERA5-Land provides global land coverage for future expansion". | | |
| TASK-005 | **Master plan — DEP-001** — Change "ERA5/ERA5-Land data from Copernicus Climate Data Store" → "ERA5-Land data from Copernicus Climate Data Store (CDS)". | | |
| TASK-006 | **Master plan — ASSUMPTION-005** — Remove the assumption entirely ("1km visual resolution sufficient for climate data (actual ERA5 is 28km)"). Data is displayed at native resolution; no assumption about upscaling needed. | | |
| TASK-007 | **Master plan — Phase headings & goals** — Change "ERA5 Data Pipeline", "Build the core ERA5 data download", "processed ERA5 data", "ERA5 processing modules", "sample ERA5 data subset", "ERA5 grid correlation" → ERA5-Land equivalents. | | |
| TASK-008 | **Master plan — RISK-004** — Change "ERA5/ERA5-Land API rate limiting" → "ERA5-Land API rate limiting". | | |
| TASK-009 | **Master plan — ASSUMPTION-001** — Change "ERA5 data remains freely available" → "ERA5-Land data remains freely available". | | |
| TASK-010 | **Master plan — Code Reference 10.5** — Change comment "ADAPT for ERA5" → "ADAPT for ERA5-Land"; change function docstring "Load ERA5 NetCDF" → "Load ERA5-Land NetCDF"; change inline comments "ERA5 uses 'latitude'" → "ERA5-Land uses 'latitude'", "ERA5 uses 't2m'" → "ERA5-Land uses 't2m'", "ERA5: north first" → "ERA5-Land: north first". | | |
| TASK-011 | **Master plan — Code Reference 10.7 (GitHub Actions)** — Change all user-facing strings: "Build ERA5 Docker Image" → "Build ERA5-Land Docker Image", "ERA5 Daily Pipeline" → "ERA5-Land Daily Pipeline", "ERA5 data typically available" → "ERA5-Land data typically available", "Pull ERA5 daily image" → "Pull ERA5-Land daily image", "Run ERA5 pipeline" → "Run ERA5-Land pipeline", "ERA5 Pipeline Failed" → "ERA5-Land Pipeline Failed", "daily ERA5 pipeline failed" → "daily ERA5-Land pipeline failed". | | |
| TASK-012 | **Master plan — Code Reference 10.8 (entrypoint/process_daily)** — Change `echo "ERA5 daily pipeline completed successfully"` → `echo "ERA5-Land daily pipeline completed successfully"`; change docstring `"""ERA5 daily processing pipeline orchestrator."""` → `"""ERA5-Land daily processing pipeline orchestrator."""`; change `"""Run daily ERA5 processing pipeline."""` → `"""Run daily ERA5-Land processing pipeline."""`; change `logger.info(f"Processing ERA5 data for …")` → `logger.info(f"Processing ERA5-Land data for …")`; change comment `# Step 1: Fetch ERA5 data` → `# Step 1: Fetch ERA5-Land data`. | | |
| TASK-013 | **Master plan — MetricsFile type (§10.9)** — Change `source: 'era5' \| 'era5-land'` → `source: 'era5-land'`. | | |
| TASK-014 | **Master plan — Code Reference 10.6 (Dockerfile)** — Change comments `# Dockerfile pattern - REUSE for ERA5 jobs` → `# Dockerfile pattern - REUSE for ERA5-Land jobs`. | | |
| TASK-015 | **Master plan — Execution Order notes** — Change "Phase 2: ERA5 Pipeline" → "Phase 2: ERA5-Land Pipeline"; "Phase 2 (ERA5 Pipeline) → Phase 3" → "Phase 2 (ERA5-Land Pipeline) → Phase 3". | | |
| TASK-016 | **Master plan — External Documentation links** — Change link text `[ERA5 Documentation]` → `[ERA5-Land Monthly Documentation]`. Keep the ERA5-Land link. Remove or relabel the ERA5 single-levels link (we are not using that dataset). | | |
| TASK-017 | **Master plan — Task descriptions** — Change `download ERA5/ERA5-Land NetCDF from CDS` → `download ERA5-Land NetCDF from CDS`; **remove** the `interpolate_to_grid.py` task entirely (TASK-P3-003 in master plan); `Write unit tests for all ERA5 processing modules` → `Write unit tests for all ERA5-Land processing modules`; `Create integration test with sample ERA5 data subset` → `Create integration test with sample ERA5-Land data subset`. | | |
| TASK-017a | **Master plan — Remove interpolation artefacts** — Remove `FILE-003: analysis/era5/interpolate_to_grid.py` from Files section. Remove `DEP-006: scipy - Interpolation (bicubic, bilinear)` from dependencies (verify not used elsewhere first). Remove `RISK-002: Interpolation from 28km to 1km introduces visual artifacts` and its mitigation. Remove `TEST-002: Grid interpolation produces correct 1km resolution output`. Remove `import interpolate_to_1km` and the interpolation step from Code Reference 10.8 (`process_daily.py`). Remove `analysis/era5/tests/test_interpolate.py` from test files. | | |
| TASK-017b | **Master plan — Update introduction/executive summary** — Change "displayed at 1km tile resolution" → "displayed at native provider resolution". Change "~1 km interpolation" → remove from executive summary pipeline description. Update key outputs list to remove interpolation. | | |
| TASK-018 | **Master plan — File listing § 5** — Change `analysis/era5/config.py — Centralized ERA5 configuration` → `Centralized ERA5-Land configuration`; `analysis/era5/fetch_era5_data.py — CDS download (temp + precipitation)` description stays (path unchanged). Where file descriptions say "ERA5" as the dataset, change to "ERA5-Land". | | |
| TASK-019 | **plan/process-llm-self-correction-1.md** — Replace all 9 generic "ERA5" references with "ERA5-Land": fixture/attribution mentions, CDS fixture pull, `analysis/tests/fixtures/era5/**` description. See detailed list below. | | |

### Implementation Phase 2: Phase plan files (botox phases 01–06)

- GOAL-002: Correct dataset references in the data-pipeline-heavy phase plans.

| Task     | Description | Completed | Date |
| -------- | ----------- | --------- | ---- |
| TASK-020 | **phase-01-testing-infrastructure.md** — Change `pytest fixture for ERA5` → `pytest fixture for ERA5-Land`; `testing ERA5 downloads` → `testing ERA5-Land downloads`; `ERA5 data is in Kelvin` → `ERA5-Land data is in Kelvin`; `Temperature in Kelvin (ERA5 convention)` → `(ERA5-Land convention)`; `Copernicus Climate Data Store (CDS) - ERA5 Data Access` → `ERA5-Land Data Access`. Keep `sample_era5_dataset` function name and `ERA5-Land structure/resolution` references that are already correct. | | |
| TASK-021 | **phase-02-infrastructure.md** — Bulk-replace all ~30 "ERA5" dataset references: "ERA5 tiles" → "ERA5-Land tiles", "ERA5 Pipeline Access" → "ERA5-Land Pipeline Access", "Object Storage bucket for ERA5 tiles" → "for ERA5-Land tiles", "Cloudflare caching for ERA5 tiles" → "for ERA5-Land tiles", "CORS Configuration for ERA5 Bucket" → "for ERA5-Land Bucket", "ERA5 Climate Visualization" → "ERA5-Land Climate Visualization", "S3-compatible object storage utilities for ERA5 tile management" → "for ERA5-Land tile management", "Hetzner Object Storage (ERA5 tiles)" → "(ERA5-Land tiles)", "Copernicus Climate Data Store (ERA5 data)" → "(ERA5-Land data)", "Base URL for ERA5 tiles" → "for ERA5-Land tiles", "separation between Hetzner (ERA5)" → "(ERA5-Land)", "Purge Cloudflare cache for ERA5 tiles" → "for ERA5-Land tiles", "ERA5 Infrastructure Integration Test" → "ERA5-Land Infrastructure Integration Test", "setting up Hetzner Object Storage for ERA5" → "for ERA5-Land", "For ERA5 tiles (~500MB estimated)" → "For ERA5-Land tiles", "ERA5 Tiles (S3-compatible…)" → "ERA5-Land Tiles", "Copernicus CDS (for ERA5 downloads)" → "(for ERA5-Land downloads)", "future expansion beyond ERA5" → "beyond ERA5-Land". File path identifiers (`era5-cors.json`) unchanged. | | |
| TASK-022 | **phase-03-era5-data-pipeline.md** — This is the heaviest file (~137 occurrences). Apply the same rule: every "ERA5" that refers to the dataset → "ERA5-Land". This includes ~60 generic dataset references across goal statements, task descriptions, docstrings, comments, log messages, and documentation notes. Notable specific changes: heading "ERA5 Data Pipeline" → "ERA5-Land Data Pipeline"; ALT-P3-001 "Use ERA5 instead of ERA5-Land" must be **removed entirely** since we are committing to ERA5-Land (the alternative no longer applies). All `ERA5-Land` references that are already correct remain. File path identifiers (`analysis/era5/`) stay unchanged. | | |
| TASK-022a | **phase-03 — Remove entire Phase 3.3 (Grid Interpolation)** — Delete sub-phase 3.3 (GOAL-P3-003, TASK-P3-011 through TASK-P3-015). Remove REQ-P3-003 ("Interpolate from native 0.1° to ~1km using bicubic interpolation"). Remove ALT-P3-002 ("bilinear instead of bicubic"). Remove Code Reference 10.4 (`interpolate_to_grid.py` — ~200 lines). Remove FILE-P3-005 (`interpolate_to_grid.py`) and FILE-P3-011 (`test_interpolate.py`). Remove TEST-P3-006/007/008 (interpolation tests). Remove RISK-P3-002 ("Interpolation artifacts at boundaries"). Remove ASSUMPTION-P3-004 ("1km visual resolution is approximately 0.009°"). Remove `scipy` from Python dependencies (verify not needed elsewhere). Remove validation checkpoint "After Phase 3.3: Interpolated grid has shape ~(880, 1040)". | | |
| TASK-022b | **phase-03 — Remove OUTPUT_GRID and get_grid_dimensions() from config.py code reference** — Delete the `OUTPUT_GRID` dict (resolution_deg: 0.009) and `get_grid_dimensions()` function from Code Reference 10.1. The land mask and anomaly modules must use the provider's `native_resolution_deg` and the actual data grid shape instead. Remove `GridConfig` TypedDict from types.py code reference (10.2) since it encoded the interpolated grid. | | |
| TASK-022c | **phase-03 — Update land mask code reference** — In Code Reference 10.5 (`apply_land_mask.py`): remove `from .config import ... OUTPUT_GRID ... get_grid_dimensions`; rasterize land polygons to match the native data grid shape (read from the xarray dataset), not a hardcoded 878×1033 grid. Remove `_1km` from filename patterns. Update test assertion from "expected shape ~878 x 1033" to use native grid dimensions (~79 × 93 for ERA5-Land at 0.1°). | | |
| TASK-022d | **phase-03 — Update anomaly calculation code reference** — In Code Reference 10.6 (`calculate_anomalies.py`): remove `from .interpolate_to_grid import interpolate_from_xarray`; anomalies are computed directly on the native grid. Remove `OUTPUT_GRID` references from metadata. Remove `get_grid_dimensions()` usage. | | |
| TASK-022e | **phase-03 — Update introduction/key outputs** — Remove "Interpolation from 0.1° (~9km) to 1km grid" from key outputs list. Change introduction sentence to remove "interpolate it to 1km visual resolution". | | |
| TASK-023 | **phase-04-tile-generation.md** — Change ~8 generic references: "processed ERA5 anomaly GeoTIFFs" → "processed ERA5-Land anomaly GeoTIFFs"; "using ERA5 data at 1km visual resolution" → "using ERA5-Land data at native resolution"; "Phase 3 (ERA5 Pipeline)" → "Phase 3 (ERA5-Land Pipeline)"; "Converts processed ERA5 anomaly GeoTIFFs" → "ERA5-Land". Remove any mock data comments mentioning "Resolution ~1km (match Phase 3 output)" — change to native resolution. File path imports (`analysis.era5.config`) unchanged. Note: `rio-tiler` handles visual upscaling from native ~9 km to tile pixels during rendering — no change to tile gen logic needed, just input resolution description. | | |
| TASK-024 | **phase-05-metrics-calculation.md** — Change ~8 generic references: "processes ERA5 data" → "processes ERA5-Land data"; "Phase 3 (ERA5 Pipeline)" → "Phase 3 (ERA5-Land Pipeline)"; "ERA5 data format from Phase 3" → "ERA5-Land data format". Simplify `source: Literal['era5', 'era5-land']` → `source: Literal['era5-land']` and default parameter `source: str = 'era5-land'` (already correct). Remove or reword any "May need ERA5 hourly → derive Tmax/Tmin" since we use ERA5-Land which provides hourly data for Tmax/Tmin derivation. Change `'gridResolution': '~1km'` → `'gridResolution': '0.1deg'` (native). | | |
| TASK-025 | **phase-06-nightly-jobs.md** — Change ~75 generic references. All user-facing strings, descriptions, docstrings, log messages, and GitHub Actions names/titles must use "ERA5-Land" instead of "ERA5". File path identifiers (`job-era5-daily`, `era5-build.yml`, `era5-daily-pipeline.yml`) stay unchanged. | | |
| TASK-025a | **phase-06 — Remove interpolation pipeline step from nightly jobs** — In Code Reference for `process_daily.py`: remove `from era5.interpolate_to_grid import interpolate_to_1km`; remove Step 2 ("Interpolate to 1km grid") and all references to `interp_dir`, `interp_path`, `interpolate_to_1km()`. Pipeline goes directly from fetch → land mask → anomaly → tiles. Renumber remaining steps. In Dockerfile code reference: remove `mkdir -p ./data/interpolated`. Repeat for monthly pipeline code reference. | | |

### Implementation Phase 3: Frontend & remaining phase plan files

- GOAL-003: Correct dataset references in frontend-focused phase plans.

| Task     | Description | Completed | Date |
| -------- | ----------- | --------- | ---- |
| TASK-026 | **phase-07-frontend-map.md** — Change ~5 generic references: "displays ERA5 temperature anomaly tiles" → "ERA5-Land"; "using ERA5 data at 1km visual resolution" → "using ERA5-Land data at native resolution"; "Generates URLs for ERA5 temperature anomaly tiles" → "ERA5-Land"; "ERA5 has ~5 day delay" → "ERA5-Land has ~5 day delay" (×2); "Interactive map displaying ERA5 temperature anomaly tiles" → "ERA5-Land". | | |
| TASK-027 | **phase-08-frontend-metrics.md** — No dataset references to change (only contains a file path link). No action needed. | | |
| TASK-028 | **phase-09-frontend-narrative.md** — No dataset references to change (only contains a file path link). No action needed. | | |
| TASK-029 | **phase-10-city-selection.md** — Change ~15 generic references: "correlate cities with ERA5 grid cells" → "ERA5-Land grid cells"; "ERA5 grid (0.1° resolution)" → "ERA5-Land grid (0.1° resolution)"; "ERA5 city selection state" → "ERA5-Land city selection state"; "Grid correlation mismatch with ERA5 updates" → "ERA5-Land updates"; "Regenerate when ERA5 grid changes" → "ERA5-Land grid changes"; "citySlice.ts - ERA5 city selection state" → "ERA5-Land"; "Correlate cities to ERA5 grid cells" → "ERA5-Land grid cells"; "Convert lat/lon to ERA5 grid indices" → "ERA5-Land grid indices"; "ERA5-specific city selection state" → "ERA5-Land-specific city selection state". Code constants `ERA5_RESOLUTION`, `ERA5_GERMANY_BOUNDS` and comment `# ERA5-Land grid configuration` remain unchanged. | | |
| TASK-030 | **phase-11-documentation-deployment.md** — Change ~10 generic references: "ERA5 Germany Climate Visualization project" → "ERA5-Land"; "ERA5 Data Pipeline Architecture" → "ERA5-Land Data Pipeline Architecture"; "ERA5 Data Pipeline" → "ERA5-Land Data Pipeline"; "Downloads ERA5-Land monthly data" (already correct, keep); "Regenerate ERA5 tiles" → "ERA5-Land tiles"; service worker cache key `'era5-tiles-v1'` is a code identifier — keep. Remove `interpolate_to_grid.py` from the Mermaid data flow diagram (`B --> C[interpolate_to_grid.py]`); pipeline flow becomes fetch → land mask → anomalies → tiles. | | |

### Implementation Phase 4: Data-source abstraction layer (plan amendments)

- GOAL-004: Amend the botox phase plans to introduce a pluggable `ClimateDataProvider` abstraction so the data source is replaceable without code changes.

| Task     | Description | Completed | Date |
| -------- | ----------- | --------- | ---- |
| TASK-031 | **phase-03 — Add new Phase 3.0: Provider Protocol** — Insert a new sub-phase before Phase 3.1 that creates `analysis/era5/providers/protocol.py` defining `ClimateDataProvider(Protocol)` with methods/properties: `dataset_id`, `cds_dataset_names`, `variables`, `native_resolution_deg`, `bounds`, `coordinate_names`, `unit_conversions`, `variable_name_mapping`, `fetch_monthly(year, month, output_dir)`, `fetch_daily(year, month, output_dir)`, `load_dataset(file_path)`. Add `analysis/era5/providers/era5_land.py` implementing `ERA5LandProvider`. Move all ERA5-Land-specific constants from `config.py` into the provider. `config.py` becomes provider-agnostic (thresholds, color mapping, reference period stay; `OUTPUT_GRID` and `get_grid_dimensions()` are removed — no interpolation). | | |
| TASK-032 | **phase-03 — Refactor fetch_era5_data.py plan** — Amend TASK-P3-005 through TASK-P3-010 so `fetch_era5_data.py` accepts a `ClimateDataProvider` instance (injected, not imported). CDS dataset name, variable mapping, bounds, and retry config come from the provider. Function signatures become `fetch_monthly_data(provider, year, month, output_dir)`. Tests mock the provider protocol, not the CDS client directly. | | |
| TASK-034 | **phase-03 — Refactor types.py plan** — Replace `ERA5_TO_STANDARD` and `STANDARD_TO_ERA5` with `provider.variable_name_mapping`. Keep generic `BoundsDict`, `ProcessingResult`, `AnomalyMetadata` unchanged (they are already source-agnostic). Remove `GridConfig` TypedDict (was for the interpolated output grid). | | |
| TASK-035 | **phase-03 — Add provider tests** — Add tasks for testing the provider protocol: (1) `ERA5LandProvider` satisfies the protocol at type-check time, (2) a `StubProvider` fixture for offline tests that returns deterministic data, (3) provider-swap integration test proving pipeline works with the stub. | | |
| TASK-036 | **phase-05 — Metrics receive provider metadata** — Amend TASK-P5-016 through TASK-P5-018 so `aggregate_metrics.py` and `export_metrics.py` stamp `source: provider.dataset_id` on output JSON instead of hardcoded `'era5-land'`. The `source` field type becomes `str` (from provider) instead of a `Literal`. | | |
| TASK-037 | **phase-06 — Jobs instantiate provider** — Amend TASK-P6-003 (`process_daily.py`) so the job entry point instantiates the provider from an env var `CLIMATE_DATA_PROVIDER=era5-land` and passes it to all pipeline functions. Add env var to `.env.example` and `validate-env.py`. | | |
| TASK-038 | **phase-10 — Grid correlation accepts provider** — Amend TASK-P10-004 (`correlate_cities_to_grid.py`) so `ERA5_RESOLUTION` and `ERA5_GERMANY_BOUNDS` are read from `provider.native_resolution` and `provider.bounds`. Function becomes `correlate_cities(provider, cities_csv)`. | | |
| TASK-039 | **phase-07/08 — Frontend provider config** — Amend frontend phases to define a `ClimateDataConfig` interface (`{ datasetId, tileBaseUrl, metricsBaseUrl, nativeResolution, dataDelay }`) resolved from env/build config. `MetricsService.ts`, `NarrativePlotService.ts`, `useMapTiles.ts` read URLs and labels from this config instead of hardcoding. | | |
| TASK-040 | **Master plan — Add architectural guideline** — Add GUD-007: "All pipeline and frontend modules must depend on the `ClimateDataProvider` abstraction, not on concrete dataset constants. Provider selection is configuration-driven." Add PAT-006: "Use Strategy Pattern for data source providers; inject via constructor/function parameter." | | |
| TASK-041 | **Master plan — Add ALT-009** — Document: "ALT-009: Hardcode ERA5-Land throughout (no abstraction) — Rejected. Violates extensibility goal stated in ALT-005. Adding a second country or dataset would require touching every module. Provider abstraction costs ~2 files and zero runtime overhead." | | |
| TASK-042 | **Master plan — Update Files section** — Add `analysis/era5/providers/__init__.py`, `analysis/era5/providers/protocol.py`, `analysis/era5/providers/era5_land.py` as NEW files. | | |
| TASK-043 | **Self-correction plan — Add provider skill** — Add TASK-00I to Phase 0: "Create climate data provider skill (Protocol definition, provider implementation, injection pattern, provider-swap test, env-driven selection)." | | |

## 3. Alternatives

- **ALT-001**: **Rename all `era5` file paths to `era5_land`** — Rejected. The paths are project-internal identifiers, not dataset labels. Renaming would cascade across code imports, Docker paths, CI workflows, and ~200+ references for minimal clarity gain. The documentation in each file makes the dataset clear.
- **ALT-002**: **Keep the ERA5 vs ERA5-Land alternative (ALT-P3-001) in phase-03** — Rejected. Since the project commits exclusively to ERA5-Land, the alternative is no longer relevant and should be removed to avoid confusion.
- **ALT-003**: **Use ABC (Abstract Base Class) instead of Protocol** — Rejected. `typing.Protocol` provides structural subtyping (duck typing) which is more Pythonic; providers don't need to inherit from a base class, making them easier to test and compose.
- **ALT-004**: **Runtime provider dispatch (plugin registry)** — Rejected for now. A simple env-var → factory-function mapping is sufficient. A full plugin registry adds complexity without current benefit. Can be added later if >3 providers emerge.
- **ALT-005**: **Hardcode ERA5-Land throughout, abstract later** — Rejected. The abstraction is lightweight (~2 new files), prevents technical debt accumulation, and the interface is clear now. Retrofitting abstractions later is harder and riskier.
- **ALT-006**: **Keep interpolation to 1 km for visual quality** — Rejected. Interpolation from ~9 km to 1 km fabricates sub-grid detail that doesn't exist in the data. The tile renderer (`rio-tiler`) already handles smooth visual upscaling via bilinear/bicubic resampling when generating tile pixels. Keeping a separate interpolation step adds complexity, ~200 lines of code, a `scipy` dependency, and a `data/interpolated/` staging directory — all for no real visual benefit over tile-time resampling. Using native resolution is simpler, more honest, and provider-agnostic (each provider brings its own resolution).
- **ALT-007**: **Use `ecmwf-datastores-client` (advanced API) instead of `cdsapi`** — Rejected for now. The advanced client ([docs](https://ecmwf.github.io/ecmwf-datastores-client/)) offers async support, richer typing, and is ECMWF's forward-looking client, but has less community documentation and a smaller adoption base. The legacy `cdsapi` (≥ 0.7.0) is battle-tested, widely documented, and works with the current CDS infrastructure. Since the CDS client is an implementation detail of `ERA5LandProvider`, it can be swapped to `ecmwf-datastores-client` later without affecting any other module.

## 4. Dependencies

- **DEP-001**: All 13 affected plan files must be writable.
- **DEP-002**: Python `typing.Protocol` (available since Python 3.8; project uses 3.13).
- **DEP-003**: Understanding of existing `createDataSlice` factory pattern in frontend (see master plan Code Reference 10.1).
- **DEP-004**: `cdsapi >= 0.7.0` — Legacy CDS API client for Copernicus data downloads (see ALT-007).

## 5. Files

- **FILE-001**: `plan/botox/era5-germany-climate-visualization-1.md` — MODIFY — Correct ~90 ERA5 → ERA5-Land dataset references
- **FILE-002**: `plan/process-llm-self-correction-1.md` — MODIFY — Correct 9 ERA5 → ERA5-Land references
- **FILE-003**: `plan/botox/phase-01-testing-infrastructure.md` — MODIFY — Correct ~8 references
- **FILE-004**: `plan/botox/phase-02-infrastructure.md` — MODIFY — Correct ~25 references
- **FILE-005**: `plan/botox/phase-03-era5-data-pipeline.md` — MODIFY — Correct ~60 references + remove ALT-P3-001 + remove entire Phase 3.3 (interpolation) + remove OUTPUT_GRID/get_grid_dimensions + update land mask and anomaly code refs
- **FILE-006**: `plan/botox/phase-04-tile-generation.md` — MODIFY — Correct ~5 references
- **FILE-007**: `plan/botox/phase-05-metrics-calculation.md` — MODIFY — Correct ~8 references + simplify source type
- **FILE-008**: `plan/botox/phase-06-nightly-jobs.md` — MODIFY — Correct ~50 references + remove interpolation pipeline step
- **FILE-009**: `plan/botox/phase-07-frontend-map.md` — MODIFY — Correct ~5 references
- **FILE-010**: `plan/botox/phase-08-frontend-metrics.md` — NO CHANGE — only file path links
- **FILE-011**: `plan/botox/phase-09-frontend-narrative.md` — NO CHANGE — only file path links
- **FILE-012**: `plan/botox/phase-10-city-selection.md` — MODIFY — Correct ~15 references
- **FILE-013**: `plan/botox/phase-11-documentation-deployment.md` — MODIFY — Correct ~10 references + remove interpolate_to_grid.py from Mermaid diagram
- **FILE-014**: `plan/botox/phase-03-era5-data-pipeline.md` — MODIFY — Add provider protocol sub-phase, refactor fetch/types tasks, remove interpolation sub-phase
- **FILE-015**: `plan/botox/phase-05-metrics-calculation.md` — MODIFY — Amend export tasks for provider-sourced metadata
- **FILE-016**: `plan/botox/phase-06-nightly-jobs.md` — MODIFY — Add provider instantiation to job entry points
- **FILE-017**: `plan/botox/phase-10-city-selection.md` — MODIFY — Parameterize grid correlation with provider
- **FILE-018**: `plan/botox/phase-07-frontend-map.md` — MODIFY — Add ClimateDataConfig interface
- **FILE-019**: `plan/botox/phase-08-frontend-metrics.md` — MODIFY — Use config for service URLs
- **FILE-020**: `plan/botox/era5-germany-climate-visualization-1.md` — MODIFY — Add GUD-007, PAT-006, ALT-009, provider files
- **FILE-021**: `plan/process-llm-self-correction-1.md` — MODIFY — Add TASK-00I provider skill to Phase 0
- **FILE-022**: `analysis/era5/providers/__init__.py` — NEW (planned) — Provider package init
- **FILE-023**: `analysis/era5/providers/protocol.py` — NEW (planned) — ClimateDataProvider Protocol
- **FILE-024**: `analysis/era5/providers/era5_land.py` — NEW (planned) — ERA5LandProvider implementation

## 6. Testing

- **TEST-001**: After all edits, `grep -rn 'ERA5' plan/ --include='*.md' | grep -v 'ERA5-Land' | grep -v 'era5' | grep -v '/era5' | grep -v 'era5-'` should return zero lines (no standalone "ERA5" dataset references remain, only file path identifiers).
- **TEST-002**: Verify no broken markdown links by checking all `[…](…)` references still resolve.
- **TEST-003**: After Phase 4 amendments, verify that phase-03 plan includes `ClimateDataProvider` protocol definition and `ERA5LandProvider` implementation as tasks.
- **TEST-004**: After Phase 4 amendments, verify that `fetch_monthly_data`, `correlate_cities_to_grid` function signatures in code references accept a provider parameter. Verify no reference to `interpolate_to_grid` or `interpolate_to_1km` remains in any pipeline code reference.
- **TEST-005**: After Phase 4 amendments, verify that no pipeline code reference directly imports ERA5-Land-specific constants from `config.py` — all dataset-specific values must come from the provider.
- **TEST-006**: Verify phase-03 no longer contains Phase 3.3 (Grid Interpolation), `OUTPUT_GRID`, `get_grid_dimensions()`, `interpolate_to_grid.py`, or `test_interpolate.py`.
- **TEST-007**: Verify phase-06 pipeline code references show a 4-step pipeline (fetch → land mask → anomaly → tiles) with no interpolation step.
- **TEST-008**: Verify `gridResolutionLabel` defaults to native resolution label (not '~1 km') in frontend config.

## 7. Risks & Assumptions

### Risks
- **RISK-001**: Overzealous replacement breaks file path references — **Mitigation**: REQ-003/REQ-004 explicitly exclude paths and code identifiers. TEST-001 validates only dataset-meaning references are changed.
- **RISK-002**: Some "ERA5" references are intentionally generic (e.g. CDS API docs link) — **Mitigation**: External links to the ERA5 family overview page are acceptable; change only CDS dataset-specific links.
- **RISK-003**: Over-engineering the abstraction layer for a single-provider system — **Mitigation**: The protocol is minimal (~10 properties/methods). No plugin registry, no dynamic loading. Just a clean interface boundary.
- **RISK-004**: Abstraction leaks ERA5-Land assumptions (e.g. Kelvin units, CDS API) into the protocol — **Mitigation**: Protocol defines abstract contracts (`unit_conversions`, `fetch_monthly`); unit system and API backend are implementation details of each provider.

### Assumptions
- **ASSUMPTION-001**: "ERA5-Land" is the correct and complete name for the dataset per ECMWF documentation.
- **ASSUMPTION-002**: ERA5-Land provides all variables needed (t2m, tmax, tmin, precipitation, snow) at hourly/monthly resolution.
- **ASSUMPTION-003**: A single `ClimateDataProvider` protocol can express the interface for ERA5-Land, ERA5, CERRA, and HYRAS-like datasets without dataset-specific escape hatches.
- **ASSUMPTION-004**: Provider selection at startup/build time (not runtime) is sufficient; users don't need to switch providers mid-session.

## 8. Multi-Agent Execution Notes

### Execution Order
- **Parallel tasks**: TASK-001 through TASK-019 (Phase 1) can run in parallel across the two files.
- **Parallel tasks**: TASK-020 through TASK-025 (Phase 2) can all run in parallel.
- **Parallel tasks**: TASK-026 through TASK-030 (Phase 3) can all run in parallel.
- **Sequential dependency**: Phase 4 (TASK-031–TASK-043) should run AFTER Phases 1–3 naming corrections are complete, since it amends the same files. Within Phase 4, TASK-031 (protocol definition) must precede TASK-032–TASK-038 (consumer refactors). TASK-039–TASK-043 can run in parallel after TASK-031.

### Agent Context Requirements
- Agent must understand the distinction: change "ERA5" → "ERA5-Land" ONLY when it refers to the dataset, NOT in file paths or code identifiers.
- Key heuristic: if "ERA5" is inside backticks referencing a file path (e.g. `` `analysis/era5/config.py` ``), skip it. If it's in prose describing the dataset (e.g. "ERA5 data", "ERA5 tiles", "ERA5 pipeline"), change it.
- Exception: user-facing strings in code blocks (log messages, GitHub Actions `name:` fields, docstrings, titles) should also be changed.
- For Phase 4 abstraction amendments: the agent must understand the Strategy/Protocol pattern and produce plan-level amendments (new tasks, modified task descriptions, new code reference sections) — NOT actual source code.

### Validation Checkpoints
- After each file: run `grep -c 'ERA5[^-]' <file>` — remaining matches should only be in file paths, code identifiers, or the string "ERA5-Land".
- After all files: run TEST-001.
- After Phase 4: run TEST-003 through TEST-005.

## 9. Related Specifications / Further Reading

- [The family of ERA5 datasets (ECMWF)](https://confluence.ecmwf.int/display/CKB/The+family+of+ERA5+datasets)
- [ERA5-Land hourly data](https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-land)
- [ERA5-Land monthly averaged data](https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-land-monthly-means)

## 10. Code Reference (REQUIRED)

### 10.1 Correction rule — dataset references in prose

**Before:**
```markdown
This plan describes a comprehensive climate visualization platform for Germany using ERA5 reanalysis data, displayed at 1km tile resolution.
```

**After:**
```markdown
This plan describes a comprehensive climate visualization platform for Germany using ERA5-Land reanalysis data at native 0.1° (~9 km) resolution.
```

### 10.2 Correction rule — technical constraints

**Before:**
```markdown
- **CON-001**: ERA5 native resolution is 0.25° (~28km) - interpolation required for 1km display
- **CON-002**: ERA5-Land resolution is 0.1° (~9km) - can be interpolated to 1km
```

**After:**
```markdown
- **CON-001**: ERA5-Land native resolution is 0.1° (~9 km); data is used at native resolution, visual upscaling handled by tile rendering
```

**Notes:** CON-001 (ERA5 0.25°) removed entirely. Old CON-002 becomes new CON-001 without any interpolation mention. No separate interpolation step — `rio-tiler` handles visual upscaling at tile render time. Subsequent constraints renumbered.

### 10.3 Correction rule — alternatives (master plan)

**Before:**
```markdown
- **ALT-005**: **Keep HYRAS as data source** - … ERA5 provides global coverage for future expansion.
```

**After:**
```markdown
- **ALT-005**: **Keep HYRAS as data source** - … ERA5-Land provides global land coverage for future expansion.
```

### 10.4 Correction rule — dependencies

**Before:**
```markdown
- **DEP-001**: ERA5/ERA5-Land data from Copernicus Climate Data Store (CDS)
```

**After:**
```markdown
- **DEP-001**: ERA5-Land data from Copernicus Climate Data Store (CDS)
```

### 10.5 Correction rule — type definitions

**Before:**
```typescript
source: 'era5' | 'era5-land';
```

**After:**
```typescript
source: 'era5-land';
```

### 10.6 Correction rule — phase-03 ALT-P3-001 removal

**Before:**
```markdown
- **ALT-P3-001**: **Use ERA5 instead of ERA5-Land**
  - ERA5 has 0.25° (~28km) resolution vs ERA5-Land's 0.1° (~9km)
  - Rejected: More interpolation artifacts, ERA5-Land is better for land areas
```

**After:** Remove entirely (the project exclusively uses ERA5-Land; this alternative is moot).

### 10.7 Correction rule — ASSUMPTION-005 removal

**Before:**
```markdown
- **ASSUMPTION-005**: 1km visual resolution sufficient for climate data (actual ERA5 is 28km)
```

**After:** Remove entirely. Data is displayed at native provider resolution (~9 km for ERA5-Land). There is no upscaled "visual resolution" to assume sufficiency of — the data is what it is.

### 10.8 Correction rule — code block strings (keep file paths, change descriptions)

**Before:**
```python
# Existing NetCDF processing pattern - ADAPT for ERA5
```

**After:**
```python
# Existing NetCDF processing pattern - ADAPT for ERA5-Land
```

**Before:**
```python
def load_era5_data(file_path: Path, bounds: dict) -> xr.Dataset:
    """Load ERA5 NetCDF with geographic subsetting."""
```

**After (function name unchanged, docstring corrected):**
```python
def load_era5_data(file_path: Path, bounds: dict) -> xr.Dataset:
    """Load ERA5-Land NetCDF with geographic subsetting."""
```

### 10.9 Unchanged file paths (examples — do NOT modify these)

```
analysis/era5/config.py
analysis/era5/fetch_era5_data.py
jobs/job-era5-daily/Dockerfile
.github/workflows/era5-build.yml
infrastructure/bucket/era5-cors.json
data/era5/raw/
```

### 10.10 ClimateDataProvider Protocol (planned — to be added to phase-03 code references)

**File**: `analysis/era5/providers/protocol.py`

```python
#!/usr/bin/env python3
"""Climate data provider protocol.

Defines the interface that all climate data sources must satisfy.
Uses structural subtyping (typing.Protocol) — providers do not need
to inherit from this class, only implement its methods/properties.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

import xarray as xr

from ..types import BoundsDict


@runtime_checkable
class ClimateDataProvider(Protocol):
    """Interface for pluggable climate reanalysis data sources."""

    @property
    def dataset_id(self) -> str:
        """Short identifier, e.g. 'era5-land', 'cerra', 'hyras'."""
        ...

    @property
    def display_name(self) -> str:
        """Human-readable name, e.g. 'ERA5-Land'."""
        ...

    @property
    def native_resolution_deg(self) -> float:
        """Native grid resolution in degrees, e.g. 0.1 for ERA5-Land."""
        ...

    @property
    def bounds(self) -> BoundsDict:
        """Geographic bounds for data extraction."""
        ...

    @property
    def variables(self) -> dict[str, dict]:
        """Variable definitions: keys are internal names, values contain
        'cds_name', 'unit', 'description', optional 'derived'."""
        ...

    @property
    def coordinate_names(self) -> dict[str, str]:
        """Mapping of standard coord roles to dataset-specific names.
        E.g. {'latitude': 'latitude', 'longitude': 'longitude', 'time': 'time'}."""
        ...

    @property
    def latitude_descending(self) -> bool:
        """True if latitude is stored north-to-south (ERA5/ERA5-Land convention)."""
        ...

    @property
    def unit_conversions(self) -> dict[str, dict]:
        """Unit conversion rules. E.g. {'temperature': {'from': 'K', 'offset': -273.15},
        'precipitation': {'from': 'm', 'factor': 1000}}."""
        ...

    def fetch_monthly(
        self, year: int, month: int, output_dir: Path, variable: str = 't2m',
        force: bool = False,
    ) -> Path:
        """Download monthly aggregated data. Returns path to NetCDF."""
        ...

    def fetch_daily(
        self, year: int, month: int, output_dir: Path,
        force: bool = False,
    ) -> Path:
        """Download daily/hourly data for Tmin/Tmax derivation. Returns path to NetCDF."""
        ...

    def load_dataset(self, file_path: Path) -> xr.Dataset:
        """Load and subset a downloaded file to the provider's bounds."""
        ...
```

**Notes:** `@runtime_checkable` enables `isinstance(obj, ClimateDataProvider)` checks for validation. All ERA5-Land-specific constants (CDS dataset names, variable mappings, resolution, bounds) move into `ERA5LandProvider`. `config.py` retains only source-agnostic settings (thresholds, reference period, color mapping). No `OUTPUT_GRID` or `get_grid_dimensions()` — the pipeline uses the provider's `native_resolution_deg` and the actual data grid shape.

### 10.11 ERA5LandProvider sketch (planned — to be added to phase-03 code references)

**File**: `analysis/era5/providers/era5_land.py`

```python
#!/usr/bin/env python3
"""ERA5-Land climate data provider implementation."""

from pathlib import Path

import cdsapi
import xarray as xr

from ..types import BoundsDict


class ERA5LandProvider:
    """Concrete provider for Copernicus ERA5-Land reanalysis data."""

    dataset_id = 'era5-land'
    display_name = 'ERA5-Land'
    native_resolution_deg = 0.1  # ~9 km

    bounds = BoundsDict(north=55.1, south=47.2, west=5.8, east=15.1)

    coordinate_names = {
        'latitude': 'latitude',
        'longitude': 'longitude',
        'time': 'time',
    }

    latitude_descending = True  # ERA5-Land stores north first

    variables = {
        't2m': {'cds_name': '2m_temperature', 'unit': 'K', 'description': '2m air temperature'},
        'tp': {'cds_name': 'total_precipitation', 'unit': 'm', 'description': 'Total precipitation'},
        # ... (moved from config.py)
    }

    unit_conversions = {
        'temperature': {'from': 'K', 'offset': -273.15},
        'precipitation': {'from': 'm', 'factor': 1000},  # m → mm
    }

    CDS_DATASETS = {
        'monthly': 'reanalysis-era5-land-monthly-means',
        'hourly': 'reanalysis-era5-land',
    }

    def fetch_monthly(self, year, month, output_dir, variable='t2m', force=False):
        # CDS API call using self.CDS_DATASETS['monthly'], self.bounds, etc.
        ...

    def fetch_daily(self, year, month, output_dir, force=False):
        # CDS API call using self.CDS_DATASETS['hourly']
        ...

    def load_dataset(self, file_path: Path) -> xr.Dataset:
        ds = xr.open_dataset(file_path)
        lat_key = self.coordinate_names['latitude']
        lon_key = self.coordinate_names['longitude']
        if self.latitude_descending:
            ds = ds.sel(**{
                lat_key: slice(self.bounds['north'], self.bounds['south']),
                lon_key: slice(self.bounds['west'], self.bounds['east']),
            })
        return ds
```

**Notes:** This is a sketch. The actual implementation will be specified in the amended phase-03 plan. The key point is that ALL ERA5-Land-specific knowledge is encapsulated here.

### 10.12 Provider factory (planned)

**File**: `analysis/era5/providers/__init__.py`

```python
"""Climate data provider registry."""

import os
from .protocol import ClimateDataProvider
from .era5_land import ERA5LandProvider

_PROVIDERS: dict[str, type[ClimateDataProvider]] = {
    'era5-land': ERA5LandProvider,
}

def get_provider(provider_id: str | None = None) -> ClimateDataProvider:
    """Instantiate the configured climate data provider.
    
    Args:
        provider_id: Provider identifier. If None, reads from
                     CLIMATE_DATA_PROVIDER env var (default: 'era5-land').
    """
    pid = provider_id or os.environ.get('CLIMATE_DATA_PROVIDER', 'era5-land')
    if pid not in _PROVIDERS:
        raise ValueError(f"Unknown provider '{pid}'. Available: {list(_PROVIDERS)}")
    return _PROVIDERS[pid]()
```

**Notes:** Adding a new provider = implement the protocol + add one entry to `_PROVIDERS`. Zero changes to pipeline code.

### 10.13 Frontend ClimateDataConfig interface (planned)

```typescript
// frontend/src/config/climateDataConfig.ts

export interface ClimateDataConfig {
    /** Short identifier, e.g. 'era5-land' */
    datasetId: string;
    /** Human-readable name for UI display */
    displayName: string;
    /** Base URL for tile assets */
    tileBaseUrl: string;
    /** Base URL for metrics JSON */
    metricsBaseUrl: string;
    /** Base URL for plot CSV data */
    plotDataBaseUrl: string;
    /** Native grid resolution (degrees) */
    nativeResolution: number;
    /** Data availability delay (days) */
    dataDelayDays: number;
    /** Grid resolution label for display */
    gridResolutionLabel: string;
}

// Resolved from environment at build time
export const climateDataConfig: ClimateDataConfig = {
    datasetId: import.meta.env.VITE_CLIMATE_DATASET_ID ?? 'era5-land',
    displayName: import.meta.env.VITE_CLIMATE_DISPLAY_NAME ?? 'ERA5-Land',
    tileBaseUrl: import.meta.env.VITE_TILE_BASE_URL ?? '/data/tiles',
    metricsBaseUrl: import.meta.env.VITE_METRICS_BASE_URL ?? '/data/metrics',
    plotDataBaseUrl: import.meta.env.VITE_PLOT_DATA_BASE_URL ?? '/data/plots',
    nativeResolution: parseFloat(import.meta.env.VITE_NATIVE_RESOLUTION ?? '0.1'),
    dataDelayDays: parseInt(import.meta.env.VITE_DATA_DELAY_DAYS ?? '5', 10),
    gridResolutionLabel: import.meta.env.VITE_GRID_RESOLUTION_LABEL ?? '~9 km',
};
```

**Notes:** Services import `climateDataConfig` instead of hardcoding URLs and labels. `gridResolutionLabel` defaults to the provider's native resolution (~9 km for ERA5-Land), not an interpolated value. Swapping the frontend to a different data source = change env vars, no code changes.
