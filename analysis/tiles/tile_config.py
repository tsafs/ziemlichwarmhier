#!/usr/bin/env python3
"""
Tile generation configuration.

Defines parameters for XYZ map tile generation including zoom levels,
tile size, geographic bounds, colour-scale range and helper utilities
for deriving tile URLs and local file paths.
"""

from __future__ import annotations

from pathlib import Path

# ---------------------------------------------------------------------------
# Tile encoding
# ---------------------------------------------------------------------------

#: Output pixel size for a square map tile.
TILE_SIZE: int = 256

#: Output file format string (used in file-name construction and PIL save).
TILE_FORMAT: str = "webp"

#: WebP compression quality (0-100).  80 balances visual fidelity and size.
WEBP_QUALITY: int = 80

# ---------------------------------------------------------------------------
# Zoom levels
# ---------------------------------------------------------------------------

#: Minimum XYZ zoom level generated.  z5 ≈ 2 tiles cover all of Germany.
MIN_ZOOM: int = 5

#: Maximum XYZ zoom level generated.  z7 gives ~12 tiles and good detail.
MAX_ZOOM: int = 7

# ---------------------------------------------------------------------------
# Geographic extent – Germany
# ---------------------------------------------------------------------------

#: Bounding box for Germany used both to determine which tiles to generate
#: and for validation.  Imported by Phase-3 ERA5 pipeline as well.
GERMANY_BOUNDS: dict[str, float] = {
    "north": 55.1,
    "south": 47.2,
    "west": 5.8,
    "east": 15.1,
}

# ---------------------------------------------------------------------------
# HTTP / CDN settings
# ---------------------------------------------------------------------------

#: Template for the public tile URL.
#: Placeholders: base_url, year, month (zero-padded), z, x, y.
URL_PATTERN: str = "{base_url}/{year}/{month:02d}/{z}/{x}/{y}.webp"

#: Cache-Control header value applied to every uploaded tile.
#: Tiles for a given month are immutable after generation.
CACHE_CONTROL: str = "public, max-age=31536000, immutable"

#: MIME type for WebP tiles.
CONTENT_TYPE: str = "image/webp"

# ---------------------------------------------------------------------------
# Colour-scale range
# ---------------------------------------------------------------------------

#: Lower bound of the anomaly colour scale (°C, mapped to deep blue).
ANOMALY_VMIN: float = -3.0

#: Upper bound of the anomaly colour scale (°C, mapped to deep red).
ANOMALY_VMAX: float = 3.0

# ---------------------------------------------------------------------------
# File-size budget
# ---------------------------------------------------------------------------

#: Maximum acceptable size for a single tile file (bytes).
#: Tiles exceeding this are flagged as oversized during validation.
MAX_TILE_SIZE_BYTES: int = 50 * 1024  # 50 KB

# ---------------------------------------------------------------------------
# Expected tile counts (informational – used in validation)
# ---------------------------------------------------------------------------

#: Approximate tile counts per zoom level for Germany bounds.
#: Computed via ``mercantile.tiles()``; transparent ocean tiles are excluded
#: from the actual output so real counts will be lower.
EXPECTED_TILE_COUNTS: dict[int, int] = {
    5: 2,
    6: 4,
    7: 12,
}

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def get_tile_url(
    base_url: str,
    year: int,
    month: int,
    z: int,
    x: int,
    y: int,
) -> str:
    """Build the public URL for a specific tile.

    Args:
        base_url: Base URL of the tile server (trailing slash is stripped).
        year:     Data year (e.g. 2024).
        month:    Data month 1-12.
        z:        XYZ zoom level.
        x:        XYZ tile column.
        y:        XYZ tile row.

    Returns:
        Fully-formed tile URL string.

    Examples:
        >>> get_tile_url("https://cdn.example.com/tiles", 2024, 7, 8, 135, 85)
        'https://cdn.example.com/tiles/2024/07/8/135/85.webp'
    """
    return URL_PATTERN.format(
        base_url=base_url.rstrip("/"),
        year=year,
        month=month,
        z=z,
        x=x,
        y=y,
    )


def get_output_path(
    base_dir: str | Path,
    year: int,
    month: int,
    z: int,
    x: int,
    y: int,
) -> Path:
    """Build the local filesystem path for a tile.

    The directory structure mirrors the URL pattern:
    ``{base_dir}/{year}/{month:02d}/{z}/{x}/{y}.webp``

    Args:
        base_dir: Root directory for all generated tiles.
        year:     Data year.
        month:    Data month 1-12.
        z:        XYZ zoom level.
        x:        XYZ tile column.
        y:        XYZ tile row.

    Returns:
        :class:`pathlib.Path` object (parent directories are *not* created
        by this function – the caller is responsible for that).

    Examples:
        >>> get_output_path("/data/tiles", 2024, 7, 8, 135, 85)
        PosixPath('/data/tiles/2024/07/8/135/85.webp')
    """
    return (
        Path(base_dir)
        / str(year)
        / f"{month:02d}"
        / str(z)
        / str(x)
        / f"{y}.{TILE_FORMAT}"
    )
