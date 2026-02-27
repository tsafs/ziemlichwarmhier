#!/usr/bin/env python3
"""
Validate generated tile pyramids for coverage and file integrity.

Checks that:
  * The expected tile directories exist.
  * Tile counts fall within the acceptable range for each zoom level.
  * Every tile file is a valid 256×256 RGBA WebP.
  * No tile exceeds the 50 KB size budget.

Public API
----------
validate_tile_coverage(tile_dir, year, month, bounds_dict, min_zoom, max_zoom)
    → ValidationResult

check_tile_file_sizes(tile_dir, max_bytes)
    → list[Path]
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

import mercantile
from PIL import Image

from .tile_config import (
    GERMANY_BOUNDS,
    MAX_TILE_SIZE_BYTES,
    MAX_ZOOM,
    MIN_ZOOM,
    TILE_SIZE,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------


@dataclass
class ValidationResult:
    """Summary of a completed tile-coverage validation run.

    Attributes:
        total_expected: Total candidate tiles across all zoom levels
                        (geographic – includes ocean tiles that may have
                        been skipped during generation).
        total_found:    Total ``.webp`` files found in the tree.
        tiles_per_zoom: Per-zoom counts ``{zoom: {"expected": N, "found": M}}``.
        errors:         Human-readable error / warning strings.
        valid:          ``True`` when no blocking errors were detected.
    """

    total_expected: int = 0
    total_found: int = 0
    tiles_per_zoom: dict[int, dict[str, int]] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    valid: bool = True

    # Convenience
    def add_error(self, msg: str) -> None:
        """Append *msg* to ``errors`` and set ``valid = False``."""
        self.errors.append(msg)
        self.valid = False


# ---------------------------------------------------------------------------
# Public functions
# ---------------------------------------------------------------------------


def validate_tile_coverage(
    tile_dir: Path | str,
    year: int,
    month: int,
    bounds_dict: dict[str, float] | None = None,
    min_zoom: int = MIN_ZOOM,
    max_zoom: int = MAX_ZOOM,
) -> ValidationResult:
    """Validate tile coverage for a month's tile pyramid.

    For each zoom level the function:

    1. Counts expected tiles (geographical) using :func:`mercantile.tiles`.
    2. Counts ``.webp`` files found on disk.
    3. Opens each WebP with Pillow and checks size (256×256) and mode (RGBA).

    A *ValidationResult* is returned regardless of outcome – the ``valid``
    field and ``errors`` list describe any problems found.

    Args:
        tile_dir:   Root tile directory (contains ``{year}/{month:02d}/…``).
        year:       Data year.
        month:      Data month 1-12.
        bounds_dict: Bounding box for expected-count calculation.
                     Defaults to :data:`GERMANY_BOUNDS`.
        min_zoom:   Lowest zoom level to check.
        max_zoom:   Highest zoom level to check (inclusive).

    Returns:
        A populated :class:`ValidationResult` instance.
    """
    if bounds_dict is None:
        bounds_dict = GERMANY_BOUNDS

    tile_dir = Path(tile_dir)
    month_dir = tile_dir / str(year) / f"{month:02d}"
    result = ValidationResult()

    if not month_dir.exists():
        result.add_error(f"Month directory not found: {month_dir}")
        return result

    west = bounds_dict["west"]
    south = bounds_dict["south"]
    east = bounds_dict["east"]
    north = bounds_dict["north"]

    for z in range(min_zoom, max_zoom + 1):
        expected = len(list(mercantile.tiles(west, south, east, north, zooms=[z])))
        result.total_expected += expected

        zoom_dir = month_dir / str(z)
        if not zoom_dir.exists():
            result.tiles_per_zoom[z] = {"expected": expected, "found": 0}
            # A missing zoom directory is a warning but not immediately fatal
            # because transparent ocean tiles are skipped during generation.
            logger.warning("Zoom %d directory missing: %s", z, zoom_dir)
            continue

        tile_files = list(zoom_dir.rglob("*.webp"))
        found = len(tile_files)
        result.tiles_per_zoom[z] = {"expected": expected, "found": found}
        result.total_found += found

        # Structural check: fewer than 50 % of expected tiles is suspicious
        if found < expected * 0.5:
            result.add_error(
                f"Zoom {z}: only {found}/{expected} tiles found (< 50 %)"
            )

        # Integrity check each file
        for tp in tile_files:
            try:
                with Image.open(tp) as img:
                    if img.size != (TILE_SIZE, TILE_SIZE):
                        result.add_error(
                            f"{tp.relative_to(tile_dir)}: wrong size {img.size}"
                        )
                    if img.mode != "RGBA":
                        result.add_error(
                            f"{tp.relative_to(tile_dir)}: wrong mode {img.mode}"
                        )
            except Exception as exc:
                result.add_error(f"{tp.relative_to(tile_dir)}: cannot open – {exc}")

    return result


def check_tile_file_sizes(
    tile_dir: Path | str,
    max_bytes: int = MAX_TILE_SIZE_BYTES,
) -> list[Path]:
    """Return a list of tile files that exceed *max_bytes*.

    Scans *tile_dir* recursively for every ``*.webp`` file and collects paths
    whose size is strictly greater than *max_bytes*.

    Args:
        tile_dir:  Root tile directory (or any subdirectory).
        max_bytes: Maximum allowable file size in bytes.  Defaults to
                   :data:`MAX_TILE_SIZE_BYTES` (50 KB).

    Returns:
        List of :class:`pathlib.Path` objects for oversized tiles (may be
        empty if all tiles are within budget).
    """
    tile_dir = Path(tile_dir)
    oversized: list[Path] = []

    for tile_path in tile_dir.rglob("*.webp"):
        if tile_path.stat().st_size > max_bytes:
            oversized.append(tile_path)
            logger.warning(
                "Oversized tile: %s (%d bytes > %d bytes)",
                tile_path,
                tile_path.stat().st_size,
                max_bytes,
            )

    return oversized


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    parser = argparse.ArgumentParser(description="Validate generated tile pyramid.")
    parser.add_argument("tiles_dir", help="Root tile directory")
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--month", type=int, required=True)
    parser.add_argument("--min-zoom", type=int, default=MIN_ZOOM)
    parser.add_argument("--max-zoom", type=int, default=MAX_ZOOM)
    args = parser.parse_args()

    vr = validate_tile_coverage(
        Path(args.tiles_dir),
        args.year,
        args.month,
        min_zoom=args.min_zoom,
        max_zoom=args.max_zoom,
    )

    print(f"\nValidation result: {'✓ PASS' if vr.valid else '✗ FAIL'}")
    print(f"  Total expected (geographic): {vr.total_expected}")
    print(f"  Total found:                 {vr.total_found}")
    print(f"  Tiles per zoom:")
    for z, counts in sorted(vr.tiles_per_zoom.items()):
        print(f"    z{z}: {counts['found']}/{counts['expected']}")
    if vr.errors:
        print(f"\n  Errors ({len(vr.errors)}):")
        for err in vr.errors[:20]:
            print(f"    • {err}")
        if len(vr.errors) > 20:
            print(f"    … and {len(vr.errors) - 20} more")

    oversized = check_tile_file_sizes(Path(args.tiles_dir))
    if oversized:
        print(f"\n  Oversized tiles ({len(oversized)}):")
        for p in oversized[:10]:
            print(f"    {p}")
