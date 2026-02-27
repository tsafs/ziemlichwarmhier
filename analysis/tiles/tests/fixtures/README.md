# Test Fixtures – `analysis/tiles/tests/fixtures/`

This directory holds static reference data used by the tile-pipeline test suite.

---

## What "fixture" means here

A **pytest fixture** is a reusable piece of test setup (data, temporary files,
mock objects).  There are two kinds used in these tests:

| Kind | Location | Description |
|------|----------|-------------|
| **Code fixtures** | `conftest.py` | Python functions decorated with `@pytest.fixture` that create transient data at test time. |
| **File fixtures** | This directory | Static files committed to the repository and read by tests. |

---

## `sample_geotiff_path` (code fixture)

The primary GeoTIFF for tile-generation tests is **generated on-the-fly** in
`conftest.py → sample_geotiff_path`.  It is written to pytest's `tmp_path` so
it is cleaned up automatically.

Properties of the synthetic GeoTIFF:

| Property | Value |
|---|---|
| Format | GeoTIFF (float32) |
| CRS | EPSG:4326 |
| Extent | Germany bounds (W 5.8 / S 47.2 / E 15.1 / N 55.1) |
| Size | 200 × 200 pixels |
| Resolution | ≈ 0.047° × 0.046° (≈ 5 km) |
| Band 1 | Random anomalies in `[-2.5, +2.5]` °C (seed=42) |
| NoData column | Columns 0–39 set to `-9999.0` (simulates ocean/NoData) |
| NoData value | `-9999.0` |

---

## Adding file fixtures

If a future test requires a **pre-computed** reference file (e.g. a known-good
WebP tile for visual regression testing), place it here with a descriptive name
and document it in this README.

```
fixtures/
  README.md                     ← this file
  reference_tile_z8_135_85.webp ← example: known-good tile for regression test
```

When writing the fixture into a test, copy it to a temporary path via the
`tmp_path` fixture rather than reading it in-place, so the original is never
mutated.

---

## What the tile pipeline expects as input

Real tiles are generated from **ERA5-Land anomaly GeoTIFFs** produced by the
Phase-3 pipeline.  A typical production file:

| Property | Value |
|---|---|
| Format | Cloud-Optimised GeoTIFF (COG), float32 |
| CRS | EPSG:4326 |
| Extent | Germany bounds |
| Resolution | 0.1° × 0.1° (≈ 9 km – ERA5-Land native) |
| Band 1 | Monthly temperature anomaly (°C) vs. 1961-1990 baseline |
| NoData | `NaN` for ocean / outside Germany mask |

---

## Color ramp reference values

The `RdBu_r` matplotlib colormap used by the pipeline maps anomalies to these
representative colors (see `color_ramps.LEGEND_COLORS`):

| Anomaly | Direction | Hex (approx.) |
|---------|-----------|---------------|
| −3 °C   | Cold      | `#313695`     |
|  0 °C   | Neutral   | `#f7f7f7`     |
| +3 °C   | Warm      | `#a50026`     |
