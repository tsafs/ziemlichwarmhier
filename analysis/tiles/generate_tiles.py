#!/usr/bin/env python3
"""
Generate WebP map tiles from GeoTIFF anomaly data.

Converts processed ERA5-Land anomaly GeoTIFFs into XYZ tile pyramids
suitable for web-map display with MapLibre GL raster sources.

Implementation note (ALT-P4-003 accepted)
------------------------------------------
This module uses **rio-tiler** (``from rio_tiler.io import Reader``) for tile
extraction.  rio-tiler reads actual float data values from the GeoTIFF and
handles CRS reprojection internally, so adjacent tiles always show consistent
colours — no explicit cross-tile blending logic is required.

Tile naming convention
-----------------------
``{output_dir}/{year}/{month:02d}/{z}/{x}/{y}.webp``
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterator

import mercantile
import numpy as np
from PIL import Image
from tqdm import tqdm

from .color_ramps import apply_anomaly_colormap
from .tile_config import (
    ANOMALY_VMAX,
    ANOMALY_VMIN,
    GERMANY_BOUNDS,
    MAX_TILE_SIZE_BYTES,
    MAX_ZOOM,
    MIN_ZOOM,
    TILE_SIZE,
    WEBP_QUALITY,
    get_output_path,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def generate_tiles_for_geotiff(
    geotiff_path: Path | str,
    output_dir: Path | str,
    year: int,
    month: int,
    min_zoom: int = MIN_ZOOM,
    max_zoom: int = MAX_ZOOM,
    vmin: float = ANOMALY_VMIN,
    vmax: float = ANOMALY_VMAX,
) -> int:
    """Generate the complete XYZ tile pyramid for one anomaly GeoTIFF.

    Iterates over all tiles that intersect ``GERMANY_BOUNDS`` from
    *min_zoom* to *max_zoom* (inclusive), renders each tile with the
    diverging anomaly colormap, and writes ``{year}/{month:02d}/{z}/{x}/{y}.webp``
    under *output_dir*.  Fully transparent tiles (100 % ocean / NoData) are
    silently skipped.

    Args:
        geotiff_path: Path to the input GeoTIFF (EPSG:4326 expected,
                      single band, float32 anomaly values in °C).
        output_dir:   Root directory for the output tile tree.
        year:         Calendar year encoded in the directory path.
        month:        Calendar month (1-12) encoded in the directory path.
        min_zoom:     Lowest zoom level to generate.
        max_zoom:     Highest zoom level to generate (inclusive).
        vmin:         Anomaly value mapped to the cold end of the colormap.
        vmax:         Anomaly value mapped to the warm end of the colormap.

    Returns:
        Number of tiles written to disk (transparent tiles excluded).

    Raises:
        FileNotFoundError: If *geotiff_path* does not exist.
    """
    from rio_tiler.io import Reader  # deferred to keep import optional at module level

    geotiff_path = Path(geotiff_path)
    output_dir = Path(output_dir)

    if not geotiff_path.exists():
        raise FileNotFoundError(f"GeoTIFF not found: {geotiff_path}")

    tile_count = 0
    total_bytes = 0
    oversized = 0

    bounds = GERMANY_BOUNDS
    west, south, east, north = (
        bounds["west"],
        bounds["south"],
        bounds["east"],
        bounds["north"],
    )

    logger.info("Generating tiles for %s (zoom %d–%d)", geotiff_path.name, min_zoom, max_zoom)

    # Collect all tiles up-front to drive the progress bar
    all_tiles: list[mercantile.Tile] = []
    for z in range(min_zoom, max_zoom + 1):
        all_tiles.extend(mercantile.tiles(west, south, east, north, zooms=[z]))

    logger.info("Total candidate tiles: %d", len(all_tiles))

    with Reader(str(geotiff_path)) as src:
        for tile in tqdm(all_tiles, desc="Generating tiles", unit="tile"):
            img = render_tile(src, tile.x, tile.y, tile.z, vmin, vmax)

            # Skip fully transparent tiles (all ocean / outside data extent)
            if _is_fully_transparent(img):
                continue

            out_path = get_output_path(output_dir, year, month, tile.z, tile.x, tile.y)
            file_size = save_tile(img, out_path, quality=WEBP_QUALITY)

            tile_count += 1
            total_bytes += file_size

            if file_size > MAX_TILE_SIZE_BYTES:
                oversized += 1
                logger.warning(
                    "Oversized tile (%d bytes > %d KB): %s",
                    file_size,
                    MAX_TILE_SIZE_BYTES // 1024,
                    out_path,
                )

    logger.info(
        "Done – %d tiles written, %.1f MB total, %d oversized",
        tile_count,
        total_bytes / 1_048_576,
        oversized,
    )
    return tile_count


def render_tile(
    src,
    x: int,
    y: int,
    z: int,
    vmin: float = ANOMALY_VMIN,
    vmax: float = ANOMALY_VMAX,
) -> Image.Image:
    """Read and colourize a single XYZ tile from an open rio-tiler Reader.

    rio-tiler handles CRS reprojection and resampling to 256×256.  The
    returned ``ImageData`` carries a mask channel (255 = valid, 0 = NoData)
    which is converted to RGBA alpha before colormap application.

    Args:
        src:  An open ``rio_tiler.io.Reader`` context.
        x:    XYZ tile column.
        y:    XYZ tile row.
        z:    XYZ zoom level.
        vmin: Colormap lower bound (°C).
        vmax: Colormap upper bound (°C).

    Returns:
        A 256×256 RGBA :class:`PIL.Image.Image` with alpha=0 for ocean /
        NoData pixels and alpha=255 for land.
    """
    try:
        img_data = src.tile(x, y, z)
        data = img_data.data[0].astype(np.float32)  # shape (256, 256)
        mask = img_data.mask  # shape (256, 256), 255=valid, 0=nodata

        # Convert rio-tiler mask to NaN so apply_anomaly_colormap handles it
        data[mask == 0] = np.nan

    except Exception as exc:
        logger.debug("Tile (%d/%d/%d) outside dataset extent: %s", z, x, y, exc)
        data = np.full((TILE_SIZE, TILE_SIZE), np.nan, dtype=np.float32)

    rgba_array = apply_anomaly_colormap(data, vmin=vmin, vmax=vmax)
    return Image.fromarray(rgba_array, mode="RGBA")


def save_tile(
    image: Image.Image,
    output_path: Path | str,
    quality: int = WEBP_QUALITY,
) -> int:
    """Write a PIL Image to disk as a WebP file.

    Creates all parent directories if they do not exist.

    Args:
        image:       RGBA :class:`PIL.Image.Image` to encode.
        output_path: Destination file path (should end in ``.webp``).
        quality:     WebP compression quality (0-100).

    Returns:
        Size of the written file in bytes.
    """
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    image.save(out, format="WEBP", quality=quality, method=6)
    return out.stat().st_size


# ---------------------------------------------------------------------------
# Tile coordinate helpers
# ---------------------------------------------------------------------------


def get_tile_bounds(bounds_dict: dict[str, float], zoom: int) -> list[mercantile.Tile]:
    """Return all XYZ tiles that intersect *bounds_dict* at *zoom*.

    Thin wrapper around :func:`mercantile.tiles` that accepts the project's
    standard ``{north, south, west, east}`` bounds dictionary.

    Args:
        bounds_dict: Geographic bounding box with keys ``north``, ``south``,
                     ``west``, ``east``.
        zoom:        XYZ zoom level.

    Returns:
        Sorted list of :class:`mercantile.Tile` named-tuples ``(x, y, z)``.
    """
    return sorted(
        mercantile.tiles(
            bounds_dict["west"],
            bounds_dict["south"],
            bounds_dict["east"],
            bounds_dict["north"],
            zooms=[zoom],
        )
    )


def count_tiles(
    bounds: dict[str, float],
    min_zoom: int = MIN_ZOOM,
    max_zoom: int = MAX_ZOOM,
) -> dict[int, int]:
    """Count candidate tiles per zoom level for *bounds*.

    Note: this counts *geographic* tiles (including ocean) – the actual
    number of tiles written will be lower because transparent tiles are
    skipped during generation.

    Args:
        bounds:   Bounding box dict with ``north / south / west / east`` keys.
        min_zoom: Lowest zoom level.
        max_zoom: Highest zoom level (inclusive).

    Returns:
        ``{zoom_level: tile_count}`` mapping.
    """
    return {
        z: len(get_tile_bounds(bounds, z)) for z in range(min_zoom, max_zoom + 1)
    }


def generate_single_tile(
    geotiff_path: Path | str,
    z: int,
    x: int,
    y: int,
    output_path: Path | str | None = None,
    vmin: float = ANOMALY_VMIN,
    vmax: float = ANOMALY_VMAX,
) -> Image.Image:
    """Generate a single tile for testing or debugging.

    Args:
        geotiff_path: Input GeoTIFF path.
        z, x, y:     Tile coordinates.
        output_path:  Optional path to save the WebP tile.
        vmin, vmax:   Colormap range.

    Returns:
        Rendered :class:`PIL.Image.Image` (RGBA).
    """
    from rio_tiler.io import Reader

    with Reader(str(geotiff_path)) as src:
        img = render_tile(src, x, y, z, vmin, vmax)

    if output_path is not None:
        save_tile(img, Path(output_path))
        logger.info("Saved single tile to %s", output_path)

    return img


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _is_fully_transparent(image: Image.Image) -> bool:
    """Return True if every pixel in *image* has alpha = 0."""
    arr = np.array(image)
    return bool(arr[:, :, 3].max() == 0)


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    parser = argparse.ArgumentParser(description="Generate map tiles from a GeoTIFF anomaly file.")
    parser.add_argument("geotiff", help="Input GeoTIFF path")
    parser.add_argument("--output-dir", default="./data/tiles", help="Output root directory")
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--month", type=int, required=True)
    parser.add_argument("--min-zoom", type=int, default=MIN_ZOOM)
    parser.add_argument("--max-zoom", type=int, default=MAX_ZOOM)
    parser.add_argument("--vmin", type=float, default=ANOMALY_VMIN)
    parser.add_argument("--vmax", type=float, default=ANOMALY_VMAX)
    args = parser.parse_args()

    n = generate_tiles_for_geotiff(
        Path(args.geotiff),
        Path(args.output_dir),
        year=args.year,
        month=args.month,
        min_zoom=args.min_zoom,
        max_zoom=args.max_zoom,
        vmin=args.vmin,
        vmax=args.vmax,
    )
    print(f"Generated {n} tiles.")
