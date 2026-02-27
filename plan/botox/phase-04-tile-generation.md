---
goal: Phase 4 - Tile Generation Pipeline Implementation
version: 1.0
date_created: 2026-02-16
last_updated: 2026-02-27
owner: Sebastian
status: 'Completed'
tags: [phase-4, tiles, webp, rasterio, visualization, geotiff]
---

# Introduction

![Status: Completed](https://img.shields.io/badge/status-Completed-brightgreen)

This phase implements the map tile generation pipeline that converts processed ERA5-Land anomaly GeoTIFFs into WebP tile pyramids for web-based visualization. The tiles follow the standard XYZ tile scheme (slippy map) and are optimized for MapLibre GL rendering.

**Key outputs:**
- GeoTIFF to WebP tile conversion
- Diverging blue-red color ramp (cold-warm anomalies)
- Tile pyramid at zoom levels 6-10
- Transparency support for land-only display
- Upload functionality to Hetzner Object Storage
- Tile validation and integrity checking scripts

## 0. Preflight & Self-Correction

> **Mandatory gate**: Before starting any task in this phase and after every change, run the preflight script and follow the self-correction loop.

1. **Run preflight**: `./scripts/run-preflight.sh` — all checks must pass before starting work
2. **After each change**: re-run preflight or the targeted test subset (see `docs/self-correct-playbook.md`)
3. **On failure**: follow retry guidance in the playbook (max 3 attempts per issue, then revert and re-analyze)
4. **Local CI parity**: optionally run `./scripts/act-local.sh build` to verify GHA workflows locally (requires Docker + act)

## 0.1 Regular Commits

Commit after each logical unit of work to maintain a clear and reviewable change history. Avoid accumulating large batches of uncommitted changes — they make it harder to understand what belongs to what, harder to review PRs, and harder to revert individual changes if something goes wrong.

**Guidelines:**
- Commit after completing each task group or implementation sub-section
- Use [Conventional Commits](https://www.conventionalcommits.org/) format: `feat(phase-X):`, `fix(phase-X):`, `chore(phase-X):`, `test(phase-X):`, etc.
- Each commit should pass the preflight checks (see § 0 above)
- Keep PRs focused — one logical concern per PR makes reviews faster and safer

## 1. Requirements & Constraints

### From Master Plan

- **REQ-001**: Display temperature anomaly maps using ERA5-Land data at native resolution (~9 km)
- **NFR-003**: Map tile loading < 500ms per visible viewport
- **NFR-001**: Monthly operational costs ≤ €15/month

### Phase-Specific Requirements

- **REQ-P4-001**: Generate WebP tiles from anomaly GeoTIFFs at zoom levels 6-10
- **REQ-P4-002**: Apply diverging color ramp (-3°C to +3°C, blue to red). Range is configurable via `ANOMALY_VMIN` / `ANOMALY_VMAX` in `tile_config.py`.
- **REQ-P4-003**: Preserve transparency for ocean/NoData areas
- **REQ-P4-004**: Follow XYZ tile naming: `/{year}/{month:02d}/{z}/{x}/{y}.webp`
- **REQ-P4-005**: Set content-type headers correctly for WebP on upload
- **REQ-P4-006**: Generated tiles must be visually identical across runs (deterministic)
- **REQ-P4-007**: Tiles must work with MapLibre GL raster source

### Constraints

- **CON-P4-001**: WebP quality 80 for balance of size and quality
- **CON-P4-002**: Tile size 256x256 pixels (standard web tiles)
- **CON-P4-003**: Total tile storage should remain under 1GB per year of data
- **CON-P4-004**: Individual tile file size < 50KB for fast loading

## 2. Implementation Steps

### Implementation Phase 4.1: Tile Configuration

- GOAL-P4-001: Define tile generation parameters and color scales

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P4-001 | Create `analysis/tiles/__init__.py` with module exports | | |
| TASK-P4-002 | Create `analysis/tiles/tile_config.py` with zoom levels, tile size, bounds | | |
| TASK-P4-003 | Create `analysis/tiles/color_ramps.py` with diverging color definitions | | |
| TASK-P4-004 | Write unit tests for color ramp generation | | |

### Implementation Phase 4.2: Tile Generation Core

- GOAL-P4-002: Implement the core tile generation from GeoTIFF

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P4-005 | Create `analysis/tiles/generate_tiles.py` with main generation logic | | |
| TASK-P4-006 | Implement `get_tiles_for_bounds()` - calculate tile indices for Germany | | |
| TASK-P4-007 | Implement `render_tile()` - extract and colorize single tile | | |
| TASK-P4-008 | Implement `apply_colormap()` - apply diverging colormap to data | | |
| TASK-P4-009 | Implement `save_webp_tile()` - save with transparency and quality settings | | |
| TASK-P4-010 | Add progress logging for batch generation | | |
| TASK-P4-011 | Write comprehensive unit tests | | |

### Implementation Phase 4.3: Tile Upload

- GOAL-P4-003: Implement tile upload to Hetzner Object Storage

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P4-012 | Create `analysis/tiles/upload_tiles.py` with S3-compatible upload | | |
| TASK-P4-013 | Implement batch upload with parallel connections | | |
| TASK-P4-014 | Set correct content-type headers (image/webp) | | |
| TASK-P4-015 | Add cache-control headers for CDN caching | | |
| TASK-P4-016 | Implement upload progress reporting | | |
| TASK-P4-017 | Write unit tests with mocked S3 client | | |

### Implementation Phase 4.4: Validation & Utilities

- GOAL-P4-004: Create tile validation and utility scripts

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P4-018 | Create `analysis/tiles/validate_tiles.py` - verify tile coverage | | |
| TASK-P4-019 | Implement tile count verification per zoom level | | |
| TASK-P4-020 | Implement visual spot-check sample generation | | |
| TASK-P4-021 | Create `analysis/tiles/preview_tiles.py` - generate preview image | | |
| TASK-P4-022 | Write integration tests for full pipeline | | |

### Implementation Phase 4.5: Testing & Documentation

- GOAL-P4-005: Complete testing and documentation

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P4-023 | Create `analysis/tiles/tests/` directory structure | | |
| TASK-P4-024 | Create sample GeoTIFF fixtures for testing | | |
| TASK-P4-025 | Write integration test generating tiles from fixture | | |
| TASK-P4-026 | Add docstrings and README for tile module | | |

## 3. Alternatives

- **ALT-P4-001**: **PNG instead of WebP**
  - Better compatibility but 2-3x larger file sizes
  - Rejected: WebP has 95%+ browser support, size savings critical for performance

- **ALT-P4-002**: **Vector tiles (MVT) instead of raster**
  - Smaller files, client-side styling flexibility
  - Rejected: Climate data is inherently raster; pre-computed colors ensure consistency

- **ALT-P4-003**: **Use rio-tiler for tile generation**
  - Production-ready, optimized for Cloud Optimized GeoTIFFs
  - **Accepted**: rio-tiler reads actual GeoTIFF data values and applies the colormap consistently, ensuring natural color continuity at tile boundaries (adjacent tiles show matching colors because the underlying data is smooth — no explicit cross-tile blending code is needed). See master plan section 10.6 for reference implementation.

- **ALT-P4-004**: **JPEG tiles with separate mask**
  - Smaller files than WebP, simpler encoding
  - Rejected: Requires two requests per tile, WebP with alpha is cleaner

## 4. Dependencies

### Phase Dependencies

- **DEP-P4-001**: Phase 3 (ERA5-Land Pipeline) - produces anomaly GeoTIFFs
- **DEP-P4-002**: Phase 2 (Infrastructure) - Hetzner Object Storage configured

### Python Package Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `rasterio` | >=1.4.0 | GeoTIFF reading |
| `rio-tiler` | >=7.0.0 | Tile extraction + colormap from COG |
| `Pillow` | >=10.0.0 | WebP encoding |
| `numpy` | >=2.3.0 | Array operations |
| `matplotlib` | >=3.10.0 | Colormap definitions in `color_ramps.py` |
| `boto3` | >=1.38.0 | S3-compatible upload |
| `mercantile` | >=1.2.0 | Tile coordinate calculations (fallback) |
| `tqdm` | >=4.67.0 | Progress bars |
| `pytest` | >=8.0.0 | Testing |

## 5. Files

### New Files

| File ID | Path | Action | Description |
|---------|------|--------|-------------|
| FILE-P4-001 | `analysis/tiles/__init__.py` | NEW | Module exports |
| FILE-P4-002 | `analysis/tiles/tile_config.py` | NEW | Tile configuration |
| FILE-P4-003 | `analysis/tiles/color_ramps.py` | NEW | Color scale definitions |
| FILE-P4-004 | `analysis/tiles/generate_tiles.py` | NEW | Tile generation logic |
| FILE-P4-005 | `analysis/tiles/upload_tiles.py` | NEW | S3 upload functionality |
| FILE-P4-006 | `analysis/tiles/validate_tiles.py` | NEW | Validation utilities |
| FILE-P4-007 | `analysis/tiles/preview_tiles.py` | NEW | Preview generation |
| FILE-P4-008 | `analysis/tiles/tests/__init__.py` | NEW | Test module |
| FILE-P4-009 | `analysis/tiles/tests/conftest.py` | NEW | Test fixtures |
| FILE-P4-010 | `analysis/tiles/tests/test_generate_tiles.py` | NEW | Generation tests |
| FILE-P4-011 | `analysis/tiles/tests/test_upload_tiles.py` | NEW | Upload tests |
| FILE-P4-012 | `analysis/tiles/tests/test_color_ramps.py` | NEW | Colormap tests |
| FILE-P4-013 | `analysis/tiles/fixtures/` | NEW | Test data directory |

## 6. Testing

### Unit Tests

| Test ID | Description | File |
|---------|-------------|------|
| TEST-P4-001 | Color ramp generates correct RGBA for anomaly=-3°C | `test_color_ramps.py` |
| TEST-P4-002 | Color ramp generates correct RGBA for anomaly=0°C | `test_color_ramps.py` |
| TEST-P4-003 | Color ramp generates correct RGBA for anomaly=+3°C | `test_color_ramps.py` |
| TEST-P4-004 | NoData values produce transparent pixels | `test_color_ramps.py` |
| TEST-P4-005 | Tile bounds calculation covers Germany | `test_generate_tiles.py` |
| TEST-P4-006 | Generated tile has correct dimensions (256x256) | `test_generate_tiles.py` |
| TEST-P4-007 | Generated WebP has alpha channel | `test_generate_tiles.py` |
| TEST-P4-008 | WebP quality setting affects file size | `test_generate_tiles.py` |
| TEST-P4-009 | Upload sets correct content-type header | `test_upload_tiles.py` |
| TEST-P4-010 | Upload handles missing credentials gracefully | `test_upload_tiles.py` |

### Integration Tests

| Test ID | Description | File |
|---------|-------------|------|
| TEST-P4-011 | Full pipeline: GeoTIFF → tiles → validation | `test_integration.py` |
| TEST-P4-012 | Tile count matches expected for each zoom level | `test_integration.py` |
| TEST-P4-013 | All tiles within file size limit (<50KB) | `test_integration.py` |
| TEST-P4-014 | Tiles load correctly in browser (visual test reference) | Manual |

### Mock Data Requirements

```python
# fixtures/sample_anomaly.tif
# - GeoTIFF with anomaly values in range [-3, +3]
# - EPSG:4326, Germany bounds
# - Resolution native 0.1° (~9 km, match Phase 3 output)
# - Includes NaN for ocean areas
```

## 7. Risks & Assumptions

### Risks

| Risk ID | Description | Probability | Impact | Mitigation |
|---------|-------------|-------------|--------|------------|
| RISK-P4-001 | WebP encoding quality varies by library version | Low | Medium | Pin Pillow version, visual comparison tests |
| RISK-P4-002 | Tile coordinate errors at antimeridian | N/A | N/A | Germany doesn't cross antimeridian |
| RISK-P4-003 | Large memory usage for parallel tile generation | Medium | Medium | Limit concurrency, process in batches |
| RISK-P4-004 | S3 upload rate limiting | Low | Low | Add exponential backoff |

### Assumptions

- **ASSUMPTION-P4-001**: WebP browser support sufficient (95%+)
- **ASSUMPTION-P4-002**: Zoom levels 6-10 sufficient for intended use
- **ASSUMPTION-P4-003**: 256x256 tile size optimal (standard)
- **ASSUMPTION-P4-004**: Hetzner S3 API fully compatible with boto3
- **ASSUMPTION-P4-005**: Input GeoTIFFs are in EPSG:4326

## 8. Multi-Agent Execution Notes

### Execution Order

**Sequential tasks:**
1. TASK-P4-001 → TASK-P4-004 (Configuration and color ramps)
2. TASK-P4-005 → TASK-P4-011 (Core generation)
3. TASK-P4-012 → TASK-P4-017 (Upload)
4. TASK-P4-018 → TASK-P4-026 (Validation and testing)

**Parallel opportunities:**
- Color ramp tests can be written alongside implementation
- Upload module can be developed in parallel with generation module

### Agent Context Requirements

Each agent session needs:
- This phase plan document
- Phase 3 output format specification (GeoTIFF metadata)
- Hetzner S3 endpoint URL and bucket name from Phase 2

### Validation Checkpoints

- **After Phase 4.1**: Color ramp produces expected RGB at test values
- **After Phase 4.2**: Tiles generated for test GeoTIFF, visual inspection passes
- **After Phase 4.3**: Tiles uploaded, accessible via public URL
- **After Phase 4.4**: Validation script reports all tiles present
- **After Phase 4.5**: `pytest analysis/tiles/tests/ -v` passes

## 9. Related Specifications / Further Reading

- [XYZ Tile Standard](https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames)
- [Mercantile Documentation](https://mercantile.readthedocs.io/)
- [WebP Format](https://developers.google.com/speed/webp)
- [Pillow WebP Support](https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#webp)
- [Rasterio Documentation](https://rasterio.readthedocs.io/)
- Master Plan: `plan/botox/era5-germany-climate-visualization-1.md`

## 10. Code Reference

### 10.1 Tile Configuration

**File**: `analysis/tiles/tile_config.py`

```python
#!/usr/bin/env python3
"""
Tile generation configuration.

Defines parameters for XYZ map tile generation including
zoom levels, tile size, and geographic bounds.
"""

# Tile parameters
TILE_SIZE = 256  # pixels
TILE_FORMAT = 'webp'
WEBP_QUALITY = 80  # 0-100, balance of size and quality

# Zoom level range for Germany
# z6: ~8 tiles covering Germany
# z10: ~128 tiles, good detail without excessive count
MIN_ZOOM = 6
MAX_ZOOM = 10

# Import Germany bounds from Phase 3 config to avoid duplication
# from analysis.era5.config import GERMANY_BOUNDS
# Note: When implementing, import should look like:
# ```python
# from analysis.era5.config import GERMANY_BOUNDS
# ```
# The bounds are: north=55.1, south=47.2, west=5.8, east=15.1

# For reference only - actual import from analysis.era5.config
GERMANY_BOUNDS = {
    'north': 55.1,  # Import from analysis.era5.config in actual implementation
    'south': 47.2,
    'west': 5.8,
    'east': 15.1,
}

# Tile URL pattern
# {base_url}/{year}/{month:02d}/{z}/{x}/{y}.webp
URL_PATTERN = "{base_url}/{year}/{month:02d}/{z}/{x}/{y}.webp"

# Cache control header (1 year - tiles are immutable)
CACHE_CONTROL = "public, max-age=31536000, immutable"

# Content type for WebP
CONTENT_TYPE = "image/webp"

# Expected tile counts per zoom level for Germany
# Calculated using mercantile.tiles() for Germany bounds
EXPECTED_TILE_COUNTS = {
    6: 4,      # Approximate, varies slightly
    7: 12,
    8: 35,
    9: 110,
    10: 400,
}

# Maximum individual tile file size (bytes)
MAX_TILE_SIZE_BYTES = 50 * 1024  # 50KB


def get_tile_url(base_url: str, year: int, month: int, z: int, x: int, y: int) -> str:
    """Generate tile URL for given parameters.
    
    Args:
        base_url: Base URL for tile server
        year: Data year
        month: Data month (1-12)
        z: Zoom level
        x: Tile X coordinate
        y: Tile Y coordinate
        
    Returns:
        Complete tile URL
    """
    return URL_PATTERN.format(
        base_url=base_url.rstrip('/'),
        year=year,
        month=f"{month:02d}",
        z=z,
        x=x,
        y=y
    )


def get_output_path(base_dir: str, year: int, month: int, z: int, x: int, y: int) -> str:
    """Generate local file path for tile.
    
    Args:
        base_dir: Base directory for tiles
        year: Data year
        month: Data month
        z: Zoom level
        x: Tile X coordinate
        y: Tile Y coordinate
        
    Returns:
        Local file path
    """
    from pathlib import Path
    return Path(base_dir) / str(year) / f"{month:02d}" / str(z) / str(x) / f"{y}.{TILE_FORMAT}"
```

### 10.2 Color Ramps

**File**: `analysis/tiles/color_ramps.py`

```python
#!/usr/bin/env python3
"""
Color ramp definitions for climate anomaly visualization.

Implements diverging colormaps for temperature anomaly display.
"""

import numpy as np
from matplotlib import colormaps
from matplotlib.colors import Normalize, LinearSegmentedColormap


# Anomaly value range (configurable — matches ANOMALY_VMIN/ANOMALY_VMAX in tile_config.py)
ANOMALY_VMIN = -3.0  # °C  (must stay symmetric, e.g. -3 to +3)
ANOMALY_VMAX = 3.0   # °C  (adjust here to change color scale range)

# Default colormap: diverging blue (cold) to red (warm)
DEFAULT_COLORMAP = 'RdBu_r'


def get_diverging_colormap(name: str = DEFAULT_COLORMAP):
    """Get a matplotlib colormap by name.
    
    Args:
        name: Colormap name (e.g., 'RdBu_r', 'coolwarm')
        
    Returns:
        Matplotlib colormap object
    """
    return colormaps.get_cmap(name)


def create_custom_anomaly_colormap():
    """Create custom colormap optimized for temperature anomalies.
    
    Returns a diverging colormap with:
    - Deep blue at -3°C
    - Light blue/white at 0°C
    - Orange/red at +3°C
    
    Returns:
        Custom LinearSegmentedColormap
    """
    colors = [
        (0.0, '#2166ac'),   # -3°C: Deep blue
        (0.25, '#67a9cf'),  # -1.5°C: Medium blue
        (0.45, '#d1e5f0'),  # -0.3°C: Light blue
        (0.5, '#f7f7f7'),   # 0°C: Near white/gray
        (0.55, '#fddbc7'),  # +0.3°C: Light orange
        (0.75, '#ef8a62'),  # +1.5°C: Orange
        (1.0, '#b2182b'),   # +3°C: Deep red
    ]
    
    positions = [c[0] for c in colors]
    hex_colors = [c[1] for c in colors]
    
    # Convert hex to RGB
    rgb_colors = []
    for hex_color in hex_colors:
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
        rgb_colors.append(rgb)
    
    return LinearSegmentedColormap.from_list('anomaly', list(zip(positions, rgb_colors)))


def apply_colormap(
    data: np.ndarray,
    vmin: float = ANOMALY_VMIN,
    vmax: float = ANOMALY_VMAX,
    colormap_name: str = DEFAULT_COLORMAP,
) -> np.ndarray:
    """Apply colormap to anomaly data, producing RGBA array.
    
    Args:
        data: 2D array of anomaly values (°C)
        vmin: Minimum value for normalization
        vmax: Maximum value for normalization
        colormap_name: Name of colormap to use
        
    Returns:
        3D array of shape (H, W, 4) with uint8 RGBA values
    """
    # Get colormap
    cmap = get_diverging_colormap(colormap_name)
    
    # Normalize data to 0-1 range
    norm = Normalize(vmin=vmin, vmax=vmax, clip=True)
    normalized = norm(data)
    
    # Apply colormap (returns RGBA float array)
    rgba_float = cmap(normalized)
    
    # Convert to uint8
    rgba = (rgba_float * 255).astype(np.uint8)
    
    # Set NoData pixels to transparent
    # NaN values become 0 after normalization, but we need to detect them
    nodata_mask = np.isnan(data)
    rgba[nodata_mask, 3] = 0  # Set alpha to 0 for NoData
    
    return rgba


def anomaly_to_rgb(value: float) -> tuple:
    """Convert single anomaly value to RGB tuple.
    
    Useful for legend generation and testing.
    
    Args:
        value: Anomaly value in °C
        
    Returns:
        Tuple of (R, G, B) values in range 0-255
    """
    if np.isnan(value):
        return (0, 0, 0)  # Transparent in RGBA, black in RGB
    
    cmap = get_diverging_colormap(DEFAULT_COLORMAP)
    norm = Normalize(vmin=ANOMALY_VMIN, vmax=ANOMALY_VMAX, clip=True)
    
    rgba = cmap(norm(value))
    return tuple(int(c * 255) for c in rgba[:3])


# Predefined colors for legend
LEGEND_COLORS = {
    '-3': anomaly_to_rgb(-3.0),
    '-2': anomaly_to_rgb(-2.0),
    '-1': anomaly_to_rgb(-1.0),
    '0': anomaly_to_rgb(0.0),
    '+1': anomaly_to_rgb(1.0),
    '+2': anomaly_to_rgb(2.0),
    '+3': anomaly_to_rgb(3.0),
}


if __name__ == '__main__':
    # Print legend colors for documentation
    print("Legend colors (RGB):")
    for label, rgb in LEGEND_COLORS.items():
        print(f"  {label}°C: {rgb}")
```

### 10.3 Tile Generation

**File**: `analysis/tiles/generate_tiles.py`

> **Implementation note (ALT-P4-003 accepted):** The implementation should use **rio-tiler** for tile extraction and colormap application rather than the manual mercantile + rasterio approach shown below. rio-tiler reads directly from Cloud Optimized GeoTIFFs and naturally produces seamless color continuity at tile boundaries by applying the colormap consistently to the actual data values. See the reference implementation in master plan Section 10.6. The code below documents the fallback logic and data flow; adapt it using the rio-tiler API.

```python
#!/usr/bin/env python3
"""
Generate WebP map tiles from GeoTIFF anomaly data.

Converts processed ERA5-Land anomaly GeoTIFFs into XYZ tile pyramids
suitable for web map display with MapLibre GL.

NOTE: Implementation should use rio-tiler (see ALT-P4-003 in Alternatives section
and master plan Section 10.6 for the accepted reference implementation).
"""

import logging
from pathlib import Path
from typing import Iterator, Tuple

import mercantile
import numpy as np
import rasterio
from rasterio.warp import transform_bounds
from rasterio.windows import from_bounds as window_from_bounds
from PIL import Image
from tqdm import tqdm

from .tile_config import (
    TILE_SIZE,
    MIN_ZOOM,
    MAX_ZOOM,
    WEBP_QUALITY,
    GERMANY_BOUNDS,
    get_output_path,
    MAX_TILE_SIZE_BYTES,
)
from .color_ramps import apply_colormap, ANOMALY_VMIN, ANOMALY_VMAX

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_tiles_for_bounds(
    bounds: dict,
    min_zoom: int = MIN_ZOOM,
    max_zoom: int = MAX_ZOOM,
) -> Iterator[mercantile.Tile]:
    """Generate tile coordinates covering given bounds.
    
    Args:
        bounds: Dictionary with north, south, east, west keys
        min_zoom: Minimum zoom level
        max_zoom: Maximum zoom level
        
    Yields:
        mercantile.Tile objects for each tile
    """
    bbox = (bounds['west'], bounds['south'], bounds['east'], bounds['north'])
    
    for zoom in range(min_zoom, max_zoom + 1):
        for tile in mercantile.tiles(*bbox, zooms=zoom):
            yield tile


def count_tiles(bounds: dict, min_zoom: int = MIN_ZOOM, max_zoom: int = MAX_ZOOM) -> dict:
    """Count tiles per zoom level for given bounds.
    
    Args:
        bounds: Geographic bounds
        min_zoom: Minimum zoom level
        max_zoom: Maximum zoom level
        
    Returns:
        Dictionary of {zoom_level: tile_count}
    """
    counts = {}
    for zoom in range(min_zoom, max_zoom + 1):
        bbox = (bounds['west'], bounds['south'], bounds['east'], bounds['north'])
        tiles = list(mercantile.tiles(*bbox, zooms=zoom))
        counts[zoom] = len(tiles)
    return counts


def render_tile(
    src: rasterio.DatasetReader,
    tile: mercantile.Tile,
    colormap_name: str = 'RdBu_r',
) -> np.ndarray:
    """Render a single tile from GeoTIFF source.
    
    Args:
        src: Open rasterio dataset
        tile: Tile coordinates
        colormap_name: Name of colormap to apply
        
    Returns:
        RGBA array of shape (256, 256, 4)
    """
    # Get tile bounds in EPSG:4326
    tile_bounds = mercantile.bounds(tile)
    
    # Convert bounds to window in raster coordinates
    window = window_from_bounds(
        tile_bounds.west,
        tile_bounds.south,
        tile_bounds.east,
        tile_bounds.north,
        src.transform
    )
    
    # Read data for window
    # Handle case where tile extends beyond raster bounds
    try:
        data = src.read(
            1,
            window=window,
            out_shape=(TILE_SIZE, TILE_SIZE),
            resampling=rasterio.enums.Resampling.bilinear,
            boundless=True,
            fill_value=np.nan
        )
    except Exception as e:
        logger.warning(f"Error reading tile {tile}: {e}")
        data = np.full((TILE_SIZE, TILE_SIZE), np.nan)
    
    # Apply colormap
    rgba = apply_colormap(data, ANOMALY_VMIN, ANOMALY_VMAX, colormap_name)
    
    return rgba


def save_webp_tile(
    rgba: np.ndarray,
    output_path: Path,
    quality: int = WEBP_QUALITY,
) -> int:
    """Save RGBA array as WebP image.
    
    Args:
        rgba: RGBA array of shape (H, W, 4)
        output_path: Path to save WebP file
        quality: WebP quality (0-100)
        
    Returns:
        File size in bytes
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    img = Image.fromarray(rgba, mode='RGBA')
    img.save(output_path, format='WEBP', quality=quality, method=6)
    
    return output_path.stat().st_size


def generate_tiles_for_geotiff(
    geotiff_path: Path,
    output_dir: Path,
    year: int,
    month: int,
    min_zoom: int = MIN_ZOOM,
    max_zoom: int = MAX_ZOOM,
    colormap_name: str = 'RdBu_r',
) -> dict:
    """Generate all tiles for a GeoTIFF anomaly file.
    
    Args:
        geotiff_path: Path to input GeoTIFF
        output_dir: Base directory for tile output
        year: Year for directory structure
        month: Month for directory structure
        min_zoom: Minimum zoom level
        max_zoom: Maximum zoom level
        colormap_name: Colormap to use
        
    Returns:
        Dictionary with generation statistics
    """
    geotiff_path = Path(geotiff_path)
    output_dir = Path(output_dir)
    
    logger.info(f"Generating tiles for {geotiff_path}")
    
    stats = {
        'total_tiles': 0,
        'tiles_per_zoom': {},
        'total_bytes': 0,
        'oversized_tiles': 0,
    }
    
    with rasterio.open(geotiff_path) as src:
        # Get tiles for Germany bounds
        tiles = list(get_tiles_for_bounds(GERMANY_BOUNDS, min_zoom, max_zoom))
        
        logger.info(f"Generating {len(tiles)} tiles for zoom levels {min_zoom}-{max_zoom}")
        
        for tile in tqdm(tiles, desc=f"Generating tiles"):
            # Render tile
            rgba = render_tile(src, tile, colormap_name)
            
            # Check if tile has any visible data
            if rgba[:, :, 3].sum() == 0:
                # Skip fully transparent tiles
                continue
            
            # Save tile
            output_path = get_output_path(output_dir, year, month, tile.z, tile.x, tile.y)
            file_size = save_webp_tile(rgba, output_path)
            
            # Update stats
            stats['total_tiles'] += 1
            stats['tiles_per_zoom'][tile.z] = stats['tiles_per_zoom'].get(tile.z, 0) + 1
            stats['total_bytes'] += file_size
            
            if file_size > MAX_TILE_SIZE_BYTES:
                stats['oversized_tiles'] += 1
                logger.warning(f"Oversized tile: {output_path} ({file_size} bytes)")
    
    logger.info(f"Generated {stats['total_tiles']} tiles ({stats['total_bytes'] / 1024 / 1024:.1f} MB)")
    
    return stats


def generate_single_tile(
    geotiff_path: Path,
    z: int,
    x: int,
    y: int,
    output_path: Path = None,
    colormap_name: str = 'RdBu_r',
) -> np.ndarray:
    """Generate a single tile for testing/debugging.
    
    Args:
        geotiff_path: Path to GeoTIFF
        z, x, y: Tile coordinates
        output_path: Optional path to save tile
        colormap_name: Colormap to use
        
    Returns:
        RGBA array
    """
    tile = mercantile.Tile(x=x, y=y, z=z)
    
    with rasterio.open(geotiff_path) as src:
        rgba = render_tile(src, tile, colormap_name)
    
    if output_path:
        save_webp_tile(rgba, output_path)
        logger.info(f"Saved tile to {output_path}")
    
    return rgba


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate map tiles from GeoTIFF')
    parser.add_argument('geotiff', help='Input GeoTIFF file')
    parser.add_argument('--output-dir', default='./data/tiles', help='Output directory')
    parser.add_argument('--year', type=int, required=True, help='Data year')
    parser.add_argument('--month', type=int, required=True, help='Data month')
    parser.add_argument('--min-zoom', type=int, default=MIN_ZOOM)
    parser.add_argument('--max-zoom', type=int, default=MAX_ZOOM)
    args = parser.parse_args()
    
    stats = generate_tiles_for_geotiff(
        Path(args.geotiff),
        Path(args.output_dir),
        args.year,
        args.month,
        args.min_zoom,
        args.max_zoom
    )
    
    print(f"\nGeneration complete:")
    print(f"  Total tiles: {stats['total_tiles']}")
    print(f"  Total size: {stats['total_bytes'] / 1024 / 1024:.1f} MB")
    print(f"  Oversized tiles: {stats['oversized_tiles']}")
```

### 10.4 Tile Upload

**File**: `analysis/tiles/upload_tiles.py`

```python
#!/usr/bin/env python3
"""
Upload tiles to Hetzner Object Storage (S3-compatible).

Handles batch upload with parallel connections and correct headers.
"""

import os
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple

import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
from tqdm import tqdm

from .tile_config import CACHE_CONTROL, CONTENT_TYPE

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# S3-compatible storage endpoints
S3_ENDPOINTS = {
    'fsn1': 'https://fsn1.your-objectstorage.com',
    'hel1': 'https://hel1.your-objectstorage.com',
    'nbg1': 'https://nbg1.your-objectstorage.com',
}


def get_s3_client(
    endpoint_url: str = None,
    region: str = None,
):
    """Create S3 client for Hetzner Object Storage.
    
    Reads credentials from environment variables:
    - ACCESS_KEY: S3 access key
    - SECRET_KEY: S3 secret key
    - ENDPOINT_URL: S3 endpoint (optional if passed as arg)
    - REGION: Region (optional)
    
    Returns:
        boto3 S3 client
        
    Raises:
        RuntimeError: If credentials not found
    """
    access_key = os.environ.get('ACCESS_KEY')
    secret_key = os.environ.get('SECRET_KEY')
    
    if not access_key or not secret_key:
        raise RuntimeError(
            "S3 credentials not found. Set ACCESS_KEY and SECRET_KEY environment variables."
        )
    
    endpoint_url = endpoint_url or os.environ.get('ENDPOINT_URL')
    region = region or os.environ.get('REGION', 'eu-central-1')
    
    # Configure for Hetzner
    config = Config(
        retries={'max_attempts': 3, 'mode': 'adaptive'},
        max_pool_connections=25,
    )
    
    return boto3.client(
        's3',
        endpoint_url=endpoint_url,
        region_name=region,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=config
    )


def upload_file(
    client,
    file_path: Path,
    bucket: str,
    object_key: str,
) -> Tuple[bool, str]:
    """Upload single file to S3.
    
    Args:
        client: boto3 S3 client
        file_path: Local file path
        bucket: Target bucket name
        object_key: S3 object key
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        client.upload_file(
            str(file_path),
            bucket,
            object_key,
            ExtraArgs={
                'ContentType': CONTENT_TYPE,
                'CacheControl': CACHE_CONTROL,
                'ACL': 'public-read',
            }
        )
        return (True, object_key)
    except ClientError as e:
        return (False, f"{object_key}: {e}")
    except FileNotFoundError:
        return (False, f"{object_key}: File not found")


def upload_directory(
    local_dir: Path,
    bucket: str,
    prefix: str = '',
    max_workers: int = 10,
    endpoint_url: str = None,
) -> dict:
    """Upload directory of tiles to S3.
    
    Args:
        local_dir: Local directory containing tiles
        bucket: Target S3 bucket
        prefix: Optional prefix for object keys
        max_workers: Number of parallel upload threads
        endpoint_url: S3 endpoint URL
        
    Returns:
        Dictionary with upload statistics
    """
    local_dir = Path(local_dir)
    
    # Find all WebP files
    files = list(local_dir.rglob('*.webp'))
    
    if not files:
        logger.warning(f"No WebP files found in {local_dir}")
        return {'total': 0, 'success': 0, 'failed': 0}
    
    logger.info(f"Uploading {len(files)} tiles to s3://{bucket}/{prefix}")
    
    client = get_s3_client(endpoint_url)
    
    stats = {
        'total': len(files),
        'success': 0,
        'failed': 0,
        'failed_files': [],
    }
    
    # Prepare upload tasks
    tasks = []
    for file_path in files:
        # Calculate object key from relative path
        rel_path = file_path.relative_to(local_dir)
        object_key = f"{prefix.rstrip('/')}/{rel_path}" if prefix else str(rel_path)
        tasks.append((file_path, object_key))
    
    # Upload in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(upload_file, client, fp, bucket, ok): ok
            for fp, ok in tasks
        }
        
        for future in tqdm(as_completed(futures), total=len(futures), desc="Uploading"):
            success, message = future.result()
            if success:
                stats['success'] += 1
            else:
                stats['failed'] += 1
                stats['failed_files'].append(message)
                logger.warning(f"Upload failed: {message}")
    
    logger.info(
        f"Upload complete: {stats['success']}/{stats['total']} successful, "
        f"{stats['failed']} failed"
    )
    
    return stats


def upload_tiles_for_month(
    tiles_dir: Path,
    bucket: str,
    year: int,
    month: int,
    endpoint_url: str = None,
) -> dict:
    """Upload tiles for a specific month.
    
    Args:
        tiles_dir: Base tiles directory
        bucket: Target S3 bucket
        year: Data year
        month: Data month
        endpoint_url: S3 endpoint URL
        
    Returns:
        Upload statistics
    """
    month_dir = Path(tiles_dir) / str(year) / f"{month:02d}"
    
    if not month_dir.exists():
        raise FileNotFoundError(f"Tile directory not found: {month_dir}")
    
    prefix = f"tiles/{year}/{month:02d}"
    
    return upload_directory(
        month_dir,
        bucket,
        prefix=prefix,
        endpoint_url=endpoint_url
    )


def verify_uploaded_tiles(
    bucket: str,
    year: int,
    month: int,
    expected_count: int,
    endpoint_url: str = None,
) -> dict:
    """Verify tiles were uploaded correctly.
    
    Args:
        bucket: S3 bucket name
        year: Data year
        month: Data month
        expected_count: Expected number of tiles
        endpoint_url: S3 endpoint URL
        
    Returns:
        Verification results
    """
    client = get_s3_client(endpoint_url)
    prefix = f"tiles/{year}/{month:02d}/"
    
    # List all objects with prefix
    paginator = client.get_paginator('list_objects_v2')
    
    count = 0
    total_size = 0
    
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get('Contents', []):
            if obj['Key'].endswith('.webp'):
                count += 1
                total_size += obj['Size']
    
    return {
        'expected': expected_count,
        'found': count,
        'match': count == expected_count,
        'total_size_mb': total_size / 1024 / 1024,
    }


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Upload tiles to S3')
    parser.add_argument('tiles_dir', help='Local tiles directory')
    parser.add_argument('--bucket', required=True, help='S3 bucket name')
    parser.add_argument('--year', type=int, required=True)
    parser.add_argument('--month', type=int, required=True)
    parser.add_argument('--endpoint-url', help='S3 endpoint URL')
    parser.add_argument('--workers', type=int, default=10, help='Parallel upload threads')
    args = parser.parse_args()
    
    stats = upload_tiles_for_month(
        Path(args.tiles_dir),
        args.bucket,
        args.year,
        args.month,
        args.endpoint_url
    )
    
    print(f"\nUpload complete:")
    print(f"  Success: {stats['success']}")
    print(f"  Failed: {stats['failed']}")
```

### 10.5 Tile Validation

**File**: `analysis/tiles/validate_tiles.py`

```python
#!/usr/bin/env python3
"""
Validate generated tiles for coverage and integrity.
"""

import logging
from pathlib import Path
from typing import List

from PIL import Image
import mercantile

from .tile_config import (
    GERMANY_BOUNDS,
    MIN_ZOOM,
    MAX_ZOOM,
    TILE_SIZE,
    MAX_TILE_SIZE_BYTES,
)
from .generate_tiles import count_tiles

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def validate_tile_directory(
    tiles_dir: Path,
    year: int,
    month: int,
) -> dict:
    """Validate tiles in a directory.
    
    Args:
        tiles_dir: Base tiles directory
        year: Data year
        month: Data month
        
    Returns:
        Validation results
    """
    month_dir = Path(tiles_dir) / str(year) / f"{month:02d}"
    
    if not month_dir.exists():
        return {
            'valid': False,
            'error': f"Directory not found: {month_dir}",
        }
    
    results = {
        'valid': True,
        'tiles_per_zoom': {},
        'invalid_tiles': [],
        'missing_tiles': [],
        'oversized_tiles': [],
        'total_size_bytes': 0,
    }
    
    # Expected tile counts
    expected = count_tiles(GERMANY_BOUNDS, MIN_ZOOM, MAX_ZOOM)
    
    for zoom in range(MIN_ZOOM, MAX_ZOOM + 1):
        zoom_dir = month_dir / str(zoom)
        if not zoom_dir.exists():
            results['valid'] = False
            results['tiles_per_zoom'][zoom] = {'expected': expected[zoom], 'found': 0}
            continue
        
        # Count and validate tiles at this zoom
        tiles_found = list(zoom_dir.rglob('*.webp'))
        results['tiles_per_zoom'][zoom] = {
            'expected': expected[zoom],
            'found': len(tiles_found),
        }
        
        for tile_path in tiles_found:
            # Check file size
            size = tile_path.stat().st_size
            results['total_size_bytes'] += size
            
            if size > MAX_TILE_SIZE_BYTES:
                results['oversized_tiles'].append(str(tile_path))
            
            # Validate WebP integrity
            try:
                with Image.open(tile_path) as img:
                    if img.size != (TILE_SIZE, TILE_SIZE):
                        results['invalid_tiles'].append(
                            f"{tile_path}: Wrong size {img.size}"
                        )
                    if img.mode != 'RGBA':
                        results['invalid_tiles'].append(
                            f"{tile_path}: Wrong mode {img.mode}"
                        )
            except Exception as e:
                results['invalid_tiles'].append(f"{tile_path}: {e}")
    
    # Mark as invalid if any issues found
    if results['invalid_tiles'] or results['oversized_tiles']:
        results['valid'] = False
    
    # Check for significant tile count mismatch
    for zoom, counts in results['tiles_per_zoom'].items():
        # Allow some flexibility since transparent tiles may be skipped
        if counts['found'] < counts['expected'] * 0.5:
            results['valid'] = False
            logger.warning(
                f"Zoom {zoom}: Only {counts['found']}/{counts['expected']} tiles found"
            )
    
    return results


def create_preview_image(
    tiles_dir: Path,
    year: int,
    month: int,
    zoom: int = 7,
    output_path: Path = None,
) -> Path:
    """Create a composite preview image from tiles.
    
    Args:
        tiles_dir: Base tiles directory
        year: Data year
        month: Data month
        zoom: Zoom level to use for preview
        output_path: Output path for preview image
        
    Returns:
        Path to preview image
    """
    from PIL import Image
    
    month_dir = Path(tiles_dir) / str(year) / f"{month:02d}"
    zoom_dir = month_dir / str(zoom)
    
    if not zoom_dir.exists():
        raise FileNotFoundError(f"Zoom directory not found: {zoom_dir}")
    
    # Find tile range
    x_dirs = sorted([int(d.name) for d in zoom_dir.iterdir() if d.is_dir()])
    
    if not x_dirs:
        raise ValueError("No tiles found")
    
    # Find y range
    y_files = []
    for x_dir in zoom_dir.iterdir():
        if x_dir.is_dir():
            for f in x_dir.glob('*.webp'):
                y_files.append(int(f.stem))
    
    y_range = (min(y_files), max(y_files))
    x_range = (min(x_dirs), max(x_dirs))
    
    # Create composite image
    width = (x_range[1] - x_range[0] + 1) * TILE_SIZE
    height = (y_range[1] - y_range[0] + 1) * TILE_SIZE
    
    composite = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    
    for x in range(x_range[0], x_range[1] + 1):
        for y in range(y_range[0], y_range[1] + 1):
            tile_path = zoom_dir / str(x) / f"{y}.webp"
            if tile_path.exists():
                tile_img = Image.open(tile_path)
                px = (x - x_range[0]) * TILE_SIZE
                py = (y - y_range[0]) * TILE_SIZE
                composite.paste(tile_img, (px, py))
    
    # Save preview
    if output_path is None:
        output_path = month_dir / f"preview_z{zoom}.png"
    
    output_path = Path(output_path)
    composite.save(output_path)
    
    logger.info(f"Created preview: {output_path} ({width}x{height})")
    
    return output_path


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate generated tiles')
    parser.add_argument('tiles_dir', help='Tiles directory')
    parser.add_argument('--year', type=int, required=True)
    parser.add_argument('--month', type=int, required=True)
    parser.add_argument('--preview', action='store_true', help='Generate preview image')
    args = parser.parse_args()
    
    results = validate_tile_directory(Path(args.tiles_dir), args.year, args.month)
    
    print(f"\nValidation results:")
    print(f"  Valid: {results['valid']}")
    print(f"  Total size: {results['total_size_bytes'] / 1024 / 1024:.1f} MB")
    print(f"  Tiles per zoom:")
    for zoom, counts in results['tiles_per_zoom'].items():
        print(f"    z{zoom}: {counts['found']}/{counts['expected']}")
    
    if results['invalid_tiles']:
        print(f"  Invalid tiles: {len(results['invalid_tiles'])}")
    if results['oversized_tiles']:
        print(f"  Oversized tiles: {len(results['oversized_tiles'])}")
    
    if args.preview:
        preview_path = create_preview_image(
            Path(args.tiles_dir), args.year, args.month
        )
        print(f"  Preview: {preview_path}")
```

### 10.6 Test Examples

**File**: `analysis/tiles/tests/test_color_ramps.py`

```python
#!/usr/bin/env python3
"""Tests for color ramp generation."""

import pytest
import numpy as np
from analysis.tiles.color_ramps import (
    apply_colormap,
    anomaly_to_rgb,
    ANOMALY_VMIN,
    ANOMALY_VMAX,
)


class TestApplyColormap:
    """Tests for colormap application."""
    
    def test_output_shape_matches_input(self):
        """Output RGBA array has correct shape."""
        data = np.random.uniform(-3, 3, (100, 100))
        rgba = apply_colormap(data)
        
        assert rgba.shape == (100, 100, 4)
        assert rgba.dtype == np.uint8
    
    def test_cold_anomaly_is_blue(self):
        """Negative anomalies produce blue colors."""
        data = np.full((10, 10), -3.0)
        rgba = apply_colormap(data)
        
        # Blue channel should be higher than red for cold
        mean_red = rgba[:, :, 0].mean()
        mean_blue = rgba[:, :, 2].mean()
        
        assert mean_blue > mean_red
    
    def test_warm_anomaly_is_red(self):
        """Positive anomalies produce red colors."""
        data = np.full((10, 10), 3.0)
        rgba = apply_colormap(data)
        
        # Red channel should be higher than blue for warm
        mean_red = rgba[:, :, 0].mean()
        mean_blue = rgba[:, :, 2].mean()
        
        assert mean_red > mean_blue
    
    def test_zero_anomaly_is_neutral(self):
        """Zero anomaly produces near-white/gray."""
        data = np.full((10, 10), 0.0)
        rgba = apply_colormap(data)
        
        # RGB channels should be similar for neutral
        r = rgba[:, :, 0].mean()
        g = rgba[:, :, 1].mean()
        b = rgba[:, :, 2].mean()
        
        # All channels should be high (light color)
        assert r > 200
        assert g > 200
        assert b > 200
    
    def test_nan_values_are_transparent(self):
        """NaN values produce transparent pixels."""
        data = np.array([[np.nan, 1.0], [2.0, np.nan]])
        rgba = apply_colormap(data)
        
        # Alpha channel should be 0 for NaN
        assert rgba[0, 0, 3] == 0
        assert rgba[1, 1, 3] == 0
        
        # Alpha should be 255 for valid values
        assert rgba[0, 1, 3] == 255
        assert rgba[1, 0, 3] == 255
    
    def test_values_clipped_to_range(self):
        """Values outside range are clipped, not causing errors."""
        data = np.array([[-10.0, 10.0]])  # Well outside -3 to +3
        
        # Should not raise
        rgba = apply_colormap(data)
        
        # Should produce valid RGBA
        assert rgba.shape == (1, 2, 4)
        assert rgba.dtype == np.uint8


class TestAnomalyToRgb:
    """Tests for single value conversion."""
    
    def test_returns_tuple(self):
        """Returns RGB tuple."""
        result = anomaly_to_rgb(1.5)
        
        assert isinstance(result, tuple)
        assert len(result) == 3
    
    def test_values_in_range(self):
        """RGB values are in 0-255 range."""
        for value in [-3, -1.5, 0, 1.5, 3]:
            r, g, b = anomaly_to_rgb(value)
            
            assert 0 <= r <= 255
            assert 0 <= g <= 255
            assert 0 <= b <= 255
    
    def test_nan_returns_black(self):
        """NaN produces black (transparent)."""
        result = anomaly_to_rgb(np.nan)
        assert result == (0, 0, 0)
```

**File**: `analysis/tiles/tests/test_generate_tiles.py`

```python
#!/usr/bin/env python3
"""Tests for tile generation."""

import pytest
import numpy as np
import rasterio
from pathlib import Path
import tempfile

from analysis.tiles.generate_tiles import (
    get_tiles_for_bounds,
    count_tiles,
    render_tile,
    save_webp_tile,
    generate_tiles_for_geotiff,
)
from analysis.tiles.tile_config import GERMANY_BOUNDS, TILE_SIZE


@pytest.fixture
def sample_geotiff(tmp_path):
    """Create sample anomaly GeoTIFF for testing."""
    from rasterio.transform import from_bounds
    
    # Small grid covering part of Germany
    width, height = 200, 200
    data = np.random.uniform(-2, 2, (height, width)).astype(np.float32)
    
    # Add some NaN for ocean
    data[:, :50] = np.nan  # Western edge as "ocean"
    
    transform = from_bounds(
        GERMANY_BOUNDS['west'],
        GERMANY_BOUNDS['south'],
        GERMANY_BOUNDS['east'],
        GERMANY_BOUNDS['north'],
        width,
        height
    )
    
    path = tmp_path / 'sample_anomaly.tif'
    
    with rasterio.open(
        path, 'w',
        driver='GTiff',
        height=height,
        width=width,
        count=1,
        dtype=np.float32,
        crs='EPSG:4326',
        transform=transform,
    ) as dst:
        dst.write(data, 1)
    
    return path


class TestGetTilesForBounds:
    """Tests for tile coordinate generation."""
    
    def test_generates_tiles(self):
        """Generates non-empty list of tiles."""
        tiles = list(get_tiles_for_bounds(GERMANY_BOUNDS, min_zoom=6, max_zoom=6))
        assert len(tiles) > 0
    
    def test_tiles_have_correct_zoom(self):
        """All tiles have requested zoom level."""
        tiles = list(get_tiles_for_bounds(GERMANY_BOUNDS, min_zoom=7, max_zoom=7))
        
        for tile in tiles:
            assert tile.z == 7
    
    def test_more_tiles_at_higher_zoom(self):
        """Higher zoom levels have more tiles."""
        count_z6 = len(list(get_tiles_for_bounds(GERMANY_BOUNDS, 6, 6)))
        count_z8 = len(list(get_tiles_for_bounds(GERMANY_BOUNDS, 8, 8)))
        
        assert count_z8 > count_z6


class TestRenderTile:
    """Tests for single tile rendering."""
    
    def test_output_dimensions(self, sample_geotiff):
        """Rendered tile has correct dimensions."""
        import mercantile
        
        tile = mercantile.Tile(x=33, y=21, z=6)
        
        with rasterio.open(sample_geotiff) as src:
            rgba = render_tile(src, tile)
        
        assert rgba.shape == (TILE_SIZE, TILE_SIZE, 4)
    
    def test_output_dtype(self, sample_geotiff):
        """Rendered tile has uint8 dtype."""
        import mercantile
        
        tile = mercantile.Tile(x=33, y=21, z=6)
        
        with rasterio.open(sample_geotiff) as src:
            rgba = render_tile(src, tile)
        
        assert rgba.dtype == np.uint8


class TestSaveWebpTile:
    """Tests for WebP saving."""
    
    def test_creates_file(self, tmp_path):
        """Saves file to disk."""
        rgba = np.random.randint(0, 255, (256, 256, 4), dtype=np.uint8)
        path = tmp_path / 'test.webp'
        
        size = save_webp_tile(rgba, path)
        
        assert path.exists()
        assert size > 0
    
    def test_creates_parent_directories(self, tmp_path):
        """Creates parent directories if needed."""
        rgba = np.random.randint(0, 255, (256, 256, 4), dtype=np.uint8)
        path = tmp_path / 'a' / 'b' / 'c' / 'test.webp'
        
        save_webp_tile(rgba, path)
        
        assert path.exists()
    
    def test_file_is_valid_webp(self, tmp_path):
        """Saved file is valid WebP."""
        from PIL import Image
        
        rgba = np.random.randint(0, 255, (256, 256, 4), dtype=np.uint8)
        path = tmp_path / 'test.webp'
        
        save_webp_tile(rgba, path)
        
        # Should be readable by PIL
        with Image.open(path) as img:
            assert img.format == 'WEBP'
            assert img.mode == 'RGBA'


class TestGenerateTilesForGeotiff:
    """Integration tests for full tile generation."""
    
    def test_generates_tiles(self, sample_geotiff, tmp_path):
        """Generates tiles successfully."""
        stats = generate_tiles_for_geotiff(
            sample_geotiff,
            tmp_path,
            year=2024,
            month=1,
            min_zoom=6,
            max_zoom=7
        )
        
        assert stats['total_tiles'] > 0
    
    def test_creates_directory_structure(self, sample_geotiff, tmp_path):
        """Creates correct directory structure."""
        generate_tiles_for_geotiff(
            sample_geotiff,
            tmp_path,
            year=2024,
            month=1,
            min_zoom=6,
            max_zoom=6
        )
        
        # Should have year/month/z structure
        assert (tmp_path / '2024' / '01' / '6').exists()
```

### 10.7 Test Fixtures

**File**: `analysis/tiles/tests/conftest.py`

```python
#!/usr/bin/env python3
"""Pytest fixtures for tile module tests."""

import pytest
import numpy as np
import rasterio
from rasterio.transform import from_bounds
from pathlib import Path
import tempfile


@pytest.fixture
def germany_bounds():
    """Germany bounds dictionary."""
    return {
        'north': 55.1,
        'south': 47.2,
        'west': 5.8,
        'east': 15.1,
    }


@pytest.fixture
def temp_tile_dir():
    """Temporary directory for tile output."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_rgba_tile():
    """Sample RGBA array for testing."""
    return np.random.randint(0, 255, (256, 256, 4), dtype=np.uint8)


@pytest.fixture
def mock_s3_client(monkeypatch):
    """Mock boto3 S3 client."""
    
    class MockS3Client:
        def __init__(self, *args, **kwargs):
            self.uploaded = []
        
        def upload_file(self, file_path, bucket, key, **kwargs):
            self.uploaded.append({
                'file': file_path,
                'bucket': bucket,
                'key': key,
                'kwargs': kwargs,
            })
    
    mock = MockS3Client()
    
    def mock_get_client(*args, **kwargs):
        return mock
    
    monkeypatch.setattr('analysis.tiles.upload_tiles.get_s3_client', mock_get_client)
    return mock
```
