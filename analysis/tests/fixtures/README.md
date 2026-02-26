# Analysis Test Fixtures

All fixtures target the **new ERA5-Land product** (botox phases).

## Files

| File | Botox Phase | Description |
|------|-------------|-------------|
| `germany_metrics_sample.json` | Phase 5/8 | Full `MetricsFile` with 8 metric sub-objects |
| `city_grid_correlation_sample.json` | Phase 10 | City-to-grid mapping for 3 test cities |
| `temperature_evolution_sample.csv` | Phase 9 | Plot CSV: `year,temperature,anomaly,trend` |

## Usage

Fixtures are loaded by `conftest.py` via the `FIXTURES_DIR` path or as
in-memory dicts via pytest fixtures like `sample_location_metrics`.
