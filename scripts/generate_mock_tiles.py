#!/usr/bin/env python3
"""
Generate synthetic mock tiles for frontend development.

Creates transparent WebP tiles at zoom levels 6-8 for Germany,
using the same RdBu_r color ramp as the real tile pipeline.
Tiles are written to frontend/public/mock-tiles/{year}/{month:02d}/{z}/{x}/{y}.webp.

Land masking uses the Germany GeoJSON boundary already in public/.

Usage:
    poetry run python scripts/generate_mock_tiles.py
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import mercantile
import numpy as np
from matplotlib.colors import Normalize
from matplotlib import colormaps
from PIL import Image, ImageDraw
from shapely.geometry import shape, box as shapely_box, MultiPolygon, Polygon

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

TILE_SIZE = 256
WEBP_QUALITY = 80
GERMANY_BOUNDS = {"north": 55.1, "south": 47.2, "west": 5.8, "east": 15.1}
ZOOM_LEVELS = [6, 7, 8]
COLORMAP_NAME = "RdBu_r"
ANOMALY_VMIN = -3.0
ANOMALY_VMAX = 3.0

# Generate tiles for ALL available dates from DATA_START (2016/01) through
# the latest available month (previous month relative to "now").
# This mirrors the range exposed by the frontend DateSelector.
DATA_START_YEAR = 2016
DATA_START_MONTH = 1


def _build_mock_dates() -> list[tuple[int, int]]:
    """Build the full list of (year, month) tuples the frontend can select."""
    from datetime import date

    today = date.today()
    # ERA5-Land has ~5-day delay → latest available = previous month
    if today.month == 1:
        end_year, end_month = today.year - 1, 12
    else:
        end_year, end_month = today.year, today.month - 1

    dates: list[tuple[int, int]] = []
    y, m = DATA_START_YEAR, DATA_START_MONTH
    while (y, m) <= (end_year, end_month):
        dates.append((y, m))
        m += 1
        if m > 12:
            m = 1
            y += 1
    return dates


MOCK_DATES = _build_mock_dates()

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "frontend" / "public" / "mock-tiles"
GEOJSON_PATH = ROOT / "frontend" / "public" / "germany_10m_admin_0_reduced.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def load_germany_geometry() -> MultiPolygon | Polygon:
    """Load Germany boundary as a shapely geometry."""
    with open(GEOJSON_PATH) as f:
        geojson = json.load(f)

    # Handle both Feature and FeatureCollection formats
    if geojson.get("type") == "FeatureCollection":
        features = geojson["features"]
    elif geojson.get("type") == "Feature":
        features = [geojson]
    else:
        # Raw geometry
        return shape(geojson)

    polys = []
    for feature in features:
        geom = shape(feature["geometry"])
        if isinstance(geom, Polygon):
            polys.append(geom)
        elif isinstance(geom, MultiPolygon):
            polys.extend(geom.geoms)
    if len(polys) == 1:
        return polys[0]
    return MultiPolygon(polys)


def tile_bounds(tile: mercantile.Tile) -> tuple[float, float, float, float]:
    """Return (west, south, east, north) for a tile."""
    b = mercantile.bounds(tile)
    return b.west, b.south, b.east, b.north


def generate_anomaly_field(
    tile: mercantile.Tile,
    year: int,
    month: int,
) -> np.ndarray:
    """Generate a synthetic anomaly field for a tile.

    Uses a smooth latitude + longitude gradient with a per-date seed
    so different months produce visibly different patterns.
    """
    west, south, east, north = tile_bounds(tile)

    # Create coordinate grids
    ys = np.linspace(north, south, TILE_SIZE)
    xs = np.linspace(west, east, TILE_SIZE)
    lon_grid, lat_grid = np.meshgrid(xs, ys)

    # Seed-based spatial variation
    seed = (year * 13 + month * 7) % 100
    freq = 0.5 + (seed % 10) * 0.1

    # Smooth synthetic anomaly: latitude-driven + gentle wave
    anomaly = (
        (lat_grid - 51.0) * 0.3  # north-south gradient
        + np.sin(lon_grid * freq) * 0.8  # east-west wave
        + np.cos(lat_grid * freq * 0.7 + seed * 0.1) * 0.6  # latitude wave
        + (month - 6) * 0.15  # seasonal bias: warm in summer, cool in winter
    )

    return np.clip(anomaly, ANOMALY_VMIN, ANOMALY_VMAX)


def render_land_mask(
    tile: mercantile.Tile,
    germany: MultiPolygon | Polygon,
) -> np.ndarray:
    """Return a boolean mask (TILE_SIZE x TILE_SIZE) where True = land."""
    west, south, east, north = tile_bounds(tile)
    tile_box = shapely_box(west, south, east, north)

    if not germany.intersects(tile_box):
        return np.zeros((TILE_SIZE, TILE_SIZE), dtype=bool)

    # Rasterize the intersection into pixels
    clipped = germany.intersection(tile_box)
    if clipped.is_empty:
        return np.zeros((TILE_SIZE, TILE_SIZE), dtype=bool)

    # Draw the polygon on a PIL image as a binary mask
    img = Image.new("L", (TILE_SIZE, TILE_SIZE), 0)
    draw = ImageDraw.Draw(img)

    def draw_polygon(poly: Polygon) -> None:
        # Transform geo coords to pixel coords
        def to_pixel(lon: float, lat: float) -> tuple[int, int]:
            px = int((lon - west) / (east - west) * TILE_SIZE)
            py = int((north - lat) / (north - south) * TILE_SIZE)
            return (
                max(0, min(TILE_SIZE - 1, px)),
                max(0, min(TILE_SIZE - 1, py)),
            )

        exterior = [to_pixel(x, y) for x, y in poly.exterior.coords]
        if len(exterior) >= 3:
            draw.polygon(exterior, fill=255)
        for interior in poly.interiors:
            hole = [to_pixel(x, y) for x, y in interior.coords]
            if len(hole) >= 3:
                draw.polygon(hole, fill=0)

    if isinstance(clipped, Polygon):
        draw_polygon(clipped)
    elif isinstance(clipped, MultiPolygon):
        for poly in clipped.geoms:
            draw_polygon(poly)
    else:
        # GeometryCollection or other — try to extract polygons
        for geom in getattr(clipped, "geoms", []):
            if isinstance(geom, Polygon):
                draw_polygon(geom)

    return np.array(img) > 128


def generate_tile(
    tile: mercantile.Tile,
    year: int,
    month: int,
    germany: MultiPolygon | Polygon,
    cmap,
    norm: Normalize,
) -> Image.Image | None:
    """Generate a single RGBA tile image. Returns None if tile is all-ocean."""
    land_mask = render_land_mask(tile, germany)
    if not land_mask.any():
        return None

    anomaly = generate_anomaly_field(tile, year, month)

    # Apply colormap
    normalized = norm(anomaly)
    rgba = (cmap(normalized) * 255).astype(np.uint8)

    # Set ocean pixels to transparent
    rgba[~land_mask, 3] = 0

    return Image.fromarray(rgba, "RGBA")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    import shutil

    print(f"Generating mock tiles for {len(MOCK_DATES)} year/month combos …")
    print(f"  Date range: {MOCK_DATES[0][0]}/{MOCK_DATES[0][1]:02d} → "
          f"{MOCK_DATES[-1][0]}/{MOCK_DATES[-1][1]:02d}")

    # Wipe previous output so stale dates don't linger
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)

    print("Loading Germany boundary …")
    germany = load_germany_geometry()

    cmap = colormaps.get_cmap(COLORMAP_NAME)
    norm = Normalize(vmin=ANOMALY_VMIN, vmax=ANOMALY_VMAX)

    # Pre-compute tiles per zoom (same for every date)
    tiles_by_zoom: dict[int, list[mercantile.Tile]] = {}
    for zoom in ZOOM_LEVELS:
        tiles_by_zoom[zoom] = list(
            mercantile.tiles(
                GERMANY_BOUNDS["west"],
                GERMANY_BOUNDS["south"],
                GERMANY_BOUNDS["east"],
                GERMANY_BOUNDS["north"],
                zooms=zoom,
            )
        )

    # Pre-compute land masks per tile (they don't change across dates)
    print("Pre-computing land masks …")
    land_masks: dict[tuple[int, int, int], np.ndarray | None] = {}
    for zoom, tiles in tiles_by_zoom.items():
        for tile in tiles:
            mask = render_land_mask(tile, germany)
            land_masks[(tile.z, tile.x, tile.y)] = mask if mask.any() else None

    tiles_per_date = sum(len(t) for t in tiles_by_zoom.values())
    total_tiles = 0
    total_saved = 0

    for idx, (year, month) in enumerate(MOCK_DATES, 1):
        date_saved = 0
        for zoom in ZOOM_LEVELS:
            for tile in tiles_by_zoom[zoom]:
                total_tiles += 1
                mask = land_masks[(tile.z, tile.x, tile.y)]
                if mask is None:
                    continue

                anomaly = generate_anomaly_field(tile, year, month)
                normalized = norm(anomaly)
                rgba = (cmap(normalized) * 255).astype(np.uint8)
                rgba[~mask, 3] = 0
                img = Image.fromarray(rgba, "RGBA")

                out_path = (
                    OUTPUT_DIR
                    / str(year)
                    / f"{month:02d}"
                    / str(tile.z)
                    / str(tile.x)
                    / f"{tile.y}.webp"
                )
                out_path.parent.mkdir(parents=True, exist_ok=True)
                img.save(str(out_path), "WEBP", quality=WEBP_QUALITY)
                total_saved += 1
                date_saved += 1

        # Progress line (overwrite previous)
        print(f"  [{idx:3d}/{len(MOCK_DATES)}] {year}/{month:02d}: "
              f"{date_saved} tiles", flush=True)

    print(f"\nDone. {total_saved}/{total_tiles} tiles saved to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
