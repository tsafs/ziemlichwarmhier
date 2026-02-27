# ERA5-Land Test Fixtures

Small Germany-subset NetCDF files from the Copernicus Climate Data Store (CDS),
used as pytest fixtures for offline testing of the ERA5-Land pipeline.

## Files

| File | Variable | Temporal | Size |
|------|----------|----------|------|
| `era5land_t2m_hourly_202401_germany.nc` | 2m temperature | Hourly (06, 12, 18 UTC) | ~1.0 MB |
| `era5land_t2m_daily_minmax_202401_germany.nc` | 2m temperature min/max | Daily aggregates | ~0.7 MB |
| `era5land_tp_hourly_202401_germany.nc` | Total precipitation | Hourly (06, 12, 18 UTC) | ~1.1 MB |

- **Period:** January 2024
- **Area:** Germany bounding box (N 55.1°, S 47.2°, W 5.8°, E 15.1°)
- **CRS:** Regular lat/lon (WGS 84)

## Provenance

- Files 1 and 3 were downloaded from `reanalysis-era5-land` via the CDS API.
- File 2 was downloaded from `derived-era5-land-daily-statistics` via the CDS
  API (two separate requests for `daily_minimum` and `daily_maximum`, merged
  into a single NetCDF file with `t2m_min` and `t2m_max` variables).

### How to regenerate

```bash
# Requires CDS_API_KEY in .env or environment
python analysis/tests/fixtures/era5/pull_era5_fixtures.py
```

The script skips files that already exist. Delete a file to re-download it.

## Attribution

Muñoz Sabater, J., (2019): ERA5-Land hourly data from 1950 to present.
Copernicus Climate Change Service (C3S) Climate Data Store (CDS).
DOI: [10.24381/cds.e2161bac](https://doi.org/10.24381/cds.e2161bac)

## Licence

Generated using Copernicus Climate Change Service information (2024).
Neither the European Commission nor ECMWF is responsible for any use that
may be made of the Copernicus information or data it contains.
