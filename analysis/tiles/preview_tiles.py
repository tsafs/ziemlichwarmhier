#!/usr/bin/env python3
"""
Generate a visual preview mosaic from a tile pyramid.

Stitches all tiles at a given zoom level into a single RGBA PNG/WebP image
that can be used for quick visual spot-checks without a full web-map client.

Public API
----------
create_preview_image(tile_dir, year, month, zoom, output_path)
    → PIL.Image.Image
"""

from __future__ import annotations

import logging
from pathlib import Path

from PIL import Image

from .tile_config import TILE_SIZE

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def create_preview_image(
    tile_dir: Path | str,
    year: int,
    month: int,
    zoom: int = 8,
    output_path: Path | str | None = None,
) -> Image.Image:
    """Stitch all tiles at *zoom* into a single composite image.

    Tiles are arranged according to their x/y XYZ coordinates.  Missing
    tiles (ocean-skipped transparent tiles) are left as transparent cells in
    the composite.

    The composite is saved to *output_path* if provided (PNG by default for
    lossless preview quality).  If *output_path* is ``None``, the image is
    returned without writing to disk.

    Args:
        tile_dir:    Root tile directory (contains ``{year}/{month:02d}/…``).
        year:        Data year.
        month:       Data month 1-12.
        zoom:        Zoom level to stitch.  Defaults to 8 (≈ 35 tiles for DE).
        output_path: Optional output file path.  If the suffix is ``.webp``
                     the image will be encoded as WebP; otherwise PNG is used.
                     When ``None`` the image is only returned in memory.

    Returns:
        :class:`PIL.Image.Image` (RGBA) — the stitched mosaic.

    Raises:
        FileNotFoundError: If the zoom directory does not exist.
        ValueError:        If no tiles are found at the requested zoom level.
    """
    tile_dir = Path(tile_dir)
    zoom_dir = tile_dir / str(year) / f"{month:02d}" / str(zoom)

    if not zoom_dir.exists():
        raise FileNotFoundError(f"Zoom directory not found: {zoom_dir}")

    # -----------------------------------------------------------------------
    # Discover tile coordinates
    # -----------------------------------------------------------------------
    tiles: dict[tuple[int, int], Path] = {}

    for x_dir in zoom_dir.iterdir():
        if not x_dir.is_dir():
            continue
        try:
            x = int(x_dir.name)
        except ValueError:
            continue
        for tile_file in x_dir.glob("*.webp"):
            try:
                y = int(tile_file.stem)
            except ValueError:
                continue
            tiles[(x, y)] = tile_file

    if not tiles:
        raise ValueError(f"No tiles found in {zoom_dir}")

    xs = [coord[0] for coord in tiles]
    ys = [coord[1] for coord in tiles]
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)

    cols = x_max - x_min + 1
    rows = y_max - y_min + 1
    canvas_w = cols * TILE_SIZE
    canvas_h = rows * TILE_SIZE

    logger.info(
        "Stitching %d tiles at zoom %d → %d×%d px mosaic",
        len(tiles),
        zoom,
        canvas_w,
        canvas_h,
    )

    # -----------------------------------------------------------------------
    # Build composite canvas
    # -----------------------------------------------------------------------
    composite = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))

    for (x, y), tile_path in tiles.items():
        try:
            tile_img = Image.open(tile_path).convert("RGBA")
        except Exception as exc:
            logger.warning("Skipping unreadable tile %s: %s", tile_path, exc)
            continue

        paste_x = (x - x_min) * TILE_SIZE
        paste_y = (y - y_min) * TILE_SIZE
        composite.paste(tile_img, (paste_x, paste_y))

    # -----------------------------------------------------------------------
    # Optionally persist
    # -----------------------------------------------------------------------
    if output_path is not None:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        fmt = "WEBP" if out.suffix.lower() == ".webp" else "PNG"
        composite.save(out, format=fmt)
        logger.info("Preview saved to %s (%dx%d)", out, canvas_w, canvas_h)

    return composite


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    parser = argparse.ArgumentParser(description="Generate a mosaic preview of tile pyramid.")
    parser.add_argument("tiles_dir", help="Root tile directory")
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--month", type=int, required=True)
    parser.add_argument("--zoom", type=int, default=8, help="Zoom level to stitch")
    parser.add_argument(
        "--output",
        default=None,
        help="Output file path (default: <tiles_dir>/<year>/<month>/preview_z<zoom>.png)",
    )
    args = parser.parse_args()

    output_path = args.output
    if output_path is None:
        base = Path(args.tiles_dir) / str(args.year) / f"{args.month:02d}"
        output_path = base / f"preview_z{args.zoom}.png"

    img = create_preview_image(
        Path(args.tiles_dir),
        args.year,
        args.month,
        zoom=args.zoom,
        output_path=Path(output_path),
    )
    print(f"Preview: {output_path} ({img.width}×{img.height} px)")
