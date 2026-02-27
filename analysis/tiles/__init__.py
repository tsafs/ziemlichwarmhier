"""
Tile generation module for ERA5-Land climate data visualization.

Converts processed anomaly GeoTIFFs into WebP tile pyramids (XYZ/slippy map
scheme) optimised for MapLibre GL raster sources.

Public API
----------
Configuration:
    TILE_SIZE, TILE_FORMAT, WEBP_QUALITY, MIN_ZOOM, MAX_ZOOM
    GERMANY_BOUNDS, URL_PATTERN, CACHE_CONTROL, CONTENT_TYPE
    ANOMALY_VMIN, ANOMALY_VMAX
    get_tile_url(), get_output_path()

Color:
    get_anomaly_colormap(), apply_anomaly_colormap(), get_legend_colors()

Generation:
    generate_tiles_for_geotiff()

Upload:
    upload_tiles_to_s3()

Validation:
    validate_tile_coverage(), check_tile_file_sizes()

Preview:
    create_preview_image()
"""

from __future__ import annotations

from .tile_config import (
    ANOMALY_VMAX,
    ANOMALY_VMIN,
    CACHE_CONTROL,
    CONTENT_TYPE,
    GERMANY_BOUNDS,
    MAX_TILE_SIZE_BYTES,
    MAX_ZOOM,
    MIN_ZOOM,
    TILE_FORMAT,
    TILE_SIZE,
    URL_PATTERN,
    WEBP_QUALITY,
    get_output_path,
    get_tile_url,
)
from .color_ramps import (
    apply_anomaly_colormap,
    get_anomaly_colormap,
    get_legend_colors,
)
from .generate_tiles import generate_tiles_for_geotiff
from .upload_tiles import upload_tiles_to_s3
from .validate_tiles import ValidationResult, check_tile_file_sizes, validate_tile_coverage
from .preview_tiles import create_preview_image

__all__ = [
    # tile_config
    "TILE_SIZE",
    "TILE_FORMAT",
    "WEBP_QUALITY",
    "MIN_ZOOM",
    "MAX_ZOOM",
    "GERMANY_BOUNDS",
    "URL_PATTERN",
    "CACHE_CONTROL",
    "CONTENT_TYPE",
    "ANOMALY_VMIN",
    "ANOMALY_VMAX",
    "MAX_TILE_SIZE_BYTES",
    "get_tile_url",
    "get_output_path",
    # color_ramps
    "get_anomaly_colormap",
    "apply_anomaly_colormap",
    "get_legend_colors",
    # generate_tiles
    "generate_tiles_for_geotiff",
    # upload_tiles
    "upload_tiles_to_s3",
    # validate_tiles
    "ValidationResult",
    "validate_tile_coverage",
    "check_tile_file_sizes",
    # preview_tiles
    "create_preview_image",
]
