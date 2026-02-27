# ERA5-Land Test Fixtures

This directory holds **real** ERA5-Land NetCDF files used for integration
tests.  These files are **not** committed to the repository (they are listed
in `.gitignore`) and must be pulled separately using the helper script below.

## Required Fixture Files

| File | Dimensions | Description |
|------|-----------|-------------|
| `era5land_t2m_hourly_202401_germany.nc` | (time=24, lat≈82, lon≈94) | Hourly 2m temperature for January 2024 (single day excerpt), Germany bounding box |
| `era5land_t2m_daily_minmax_202401_germany.nc` | (time=31, lat≈82, lon≈94) | Pre-computed daily Tmin/Tmax for January 2024 |
| `era5land_tp_hourly_202401_germany.nc` | (time=24, lat≈82, lon≈94) | Hourly total precipitation for January 2024 (single day excerpt) |
| `era5land_t2m_monthly_clim_1961_1990_germany.nc` | (month=12, lat≈82, lon≈94) | 1961–1990 monthly climatology (t2m mean per calendar month) |

## Coordinate conventions

All files follow ERA5-Land conventions:
- **Latitude**: descending (north → south), range 55.1°N … 47.2°N
- **Longitude**: ascending (west → east), range 5.8°E … 15.1°E
- **Temperature**: Kelvin (`units = "K"`)
- **Precipitation**: metres per hour (`units = "m"`)
- **CRS**: EPSG:4326 (WGS-84)

## Obtaining the fixtures

### Prerequisites

1. A valid [Copernicus CDS](https://cds.climate.copernicus.eu/) account.
2. `CDS_API_KEY` environment variable set (format `uid:key`).
3. Python packages installed: `cdsapi`, `xarray`, `netCDF4`.

### Pull script

```bash
# From repo root:
CDS_API_KEY=your-uid:your-key python analysis/tests/fixtures/era5/pull_era5_fixtures.py
```

The script downloads the smallest possible ERA5-Land excerpts and saves them
to this directory.  Download size is approximately 2–5 MB total.

### Manual pull

If the script fails, download each variable manually via the
[CDS web interface](https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-land)
using the settings in `pull_era5_fixtures.py`.

## Using fixtures in tests

Integration tests that require these files should be marked with
`@pytest.mark.network` **or** guarded with a `pytest.importorskip`-style
check so they are automatically skipped when the files are absent:

```python
ERA5_FIXTURE = Path(__file__).parent / "fixtures/era5/era5land_t2m_hourly_202401_germany.nc"

@pytest.mark.skipif(not ERA5_FIXTURE.exists(), reason="ERA5 fixture not present")
def test_my_integration_test():
    ...
```
