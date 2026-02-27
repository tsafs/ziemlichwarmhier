#!/usr/bin/env python3
"""
Color ramp definitions for climate anomaly visualization.

Implements a diverging blue-red colormap for displaying temperature
anomalies where cold values are rendered in blue and warm values in red.

The primary colormap is matplotlib's ``RdBu_r`` (reversed Red-Blue), which
maps:
  - ``-3 °C`` → deep blue  (#313695)
  - ``  0 °C`` → near-white (#f7f7f7)
  - ``+3 °C`` → deep red   (#a50026)

Public API
----------
get_anomaly_colormap()
    Return the matplotlib colormap object.
apply_anomaly_colormap(data_array, vmin, vmax)
    Convert a 2-D float array to a uint8 RGBA image array.
get_legend_colors(n)
    Return a list of (value, hex_color) tuples for legend rendering.
"""

from __future__ import annotations

import numpy as np
from matplotlib import colormaps
from matplotlib.colors import LinearSegmentedColormap, Normalize

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Default matplotlib colormap name.  ``RdBu_r`` maps red=warm, blue=cold.
DEFAULT_COLORMAP: str = "RdBu_r"

#: Default lower bound of the anomaly colour scale (°C).
ANOMALY_VMIN: float = -3.0

#: Default upper bound of the anomaly colour scale (°C).
ANOMALY_VMAX: float = 3.0

# ---------------------------------------------------------------------------
# Public functions
# ---------------------------------------------------------------------------


def get_anomaly_colormap(name: str = DEFAULT_COLORMAP):
    """Return a matplotlib colormap suitable for anomaly visualization.

    The default ``RdBu_r`` colormap provides a perceptually balanced
    diverging palette where blue represents cold anomalies and red
    represents warm anomalies.

    Args:
        name: Matplotlib-registered colormap name.  Defaults to
              ``'RdBu_r'``.

    Returns:
        A :class:`matplotlib.colors.Colormap` instance.

    Examples:
        >>> cmap = get_anomaly_colormap()
        >>> cmap.name
        'RdBu_r'
    """
    return colormaps.get_cmap(name)


def apply_anomaly_colormap(
    data_array: np.ndarray,
    vmin: float = ANOMALY_VMIN,
    vmax: float = ANOMALY_VMAX,
    colormap_name: str = DEFAULT_COLORMAP,
) -> np.ndarray:
    """Apply the anomaly colormap to a 2-D float array.

    NaN values (representing ocean / NoData) are mapped to fully
    transparent pixels (alpha = 0).  All other pixels receive
    alpha = 255.

    Args:
        data_array:    2-D (H × W) NumPy array of anomaly values in °C.
        vmin:          Value mapped to the cold end of the colormap.
        vmax:          Value mapped to the warm end of the colormap.
        colormap_name: Matplotlib colormap name used for mapping.

    Returns:
        3-D uint8 NumPy array of shape (H, W, 4) in RGBA order.

    Examples:
        >>> data = np.array([[0.0, np.nan], [-3.0, 3.0]])
        >>> rgba = apply_anomaly_colormap(data)
        >>> rgba.shape
        (2, 2, 4)
        >>> rgba.dtype
        dtype('uint8')
        >>> rgba[0, 1, 3]  # NaN → transparent
        0
    """
    cmap = get_anomaly_colormap(colormap_name)
    norm = Normalize(vmin=vmin, vmax=vmax, clip=True)

    # Build a float copy so we can safely fill NaN positions for norm
    data_safe = np.where(np.isnan(data_array), 0.0, data_array)
    normalized = norm(data_safe)

    # Apply colormap → float RGBA in [0, 1]
    rgba_float = cmap(normalized)

    # Convert to uint8
    rgba = (rgba_float * 255).astype(np.uint8)

    # Restore transparency for NaN positions
    nodata_mask = np.isnan(data_array)
    rgba[nodata_mask, 3] = 0

    return rgba


def get_legend_colors(n: int = 7) -> list[tuple[float, str]]:
    """Return a list of (value, hex_color) tuples for legend rendering.

    By default returns 7 evenly-spaced values spanning the full anomaly
    range: ``[-3, -2, -1, 0, +1, +2, +3]`` °C.

    Args:
        n: Number of legend steps (must be ≥ 2).

    Returns:
        List of ``(value, "#rrggbb")`` tuples ordered from cold to warm.

    Examples:
        >>> legend = get_legend_colors()
        >>> len(legend)
        7
        >>> legend[0][0]  # coldest value
        -3.0
        >>> legend[-1][0]  # warmest value
        3.0
        >>> legend[3][0]  # neutral
        0.0
    """
    if n < 2:
        raise ValueError("n must be at least 2")  # noqa: TRY003

    cmap = get_anomaly_colormap()
    norm = Normalize(vmin=ANOMALY_VMIN, vmax=ANOMALY_VMAX, clip=True)
    values = np.linspace(ANOMALY_VMIN, ANOMALY_VMAX, n)

    result: list[tuple[float, str]] = []
    for v in values:
        rgba_float = cmap(norm(float(v)))
        r, g, b = (int(c * 255) for c in rgba_float[:3])
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        result.append((float(v), hex_color))

    return result


# ---------------------------------------------------------------------------
# Internal helpers (used by generate_tiles.py)
# ---------------------------------------------------------------------------


def anomaly_to_rgb(value: float) -> tuple[int, int, int]:
    """Convert a single anomaly value to an RGB triple (0-255 each).

    NaN maps to ``(0, 0, 0)`` (fully transparent in RGBA context).

    Args:
        value: Anomaly value in °C.

    Returns:
        ``(R, G, B)`` tuple with each component in range 0-255.
    """
    if np.isnan(value):
        return (0, 0, 0)

    cmap = get_anomaly_colormap()
    norm = Normalize(vmin=ANOMALY_VMIN, vmax=ANOMALY_VMAX, clip=True)
    rgba_float = cmap(norm(float(value)))
    return tuple(int(c * 255) for c in rgba_float[:3])  # type: ignore[return-value]


def create_custom_anomaly_colormap() -> LinearSegmentedColormap:
    """Create a bespoke colormap optimised for temperature anomaly display.

    Uses a 7-stop gradient tuned to match the colours specified in the
    Phase-4 design:

    =========  =========  =========
    Value      Hex        Description
    =========  =========  =========
    −3 °C      #313695    Deep blue
    −1.5 °C    #74add1    Medium blue
    −0.3 °C    #e0f3f8    Light blue
    0 °C       #ffffbf    Near-white
    +0.3 °C    #fee090    Light yellow
    +1.5 °C    #f46d43    Orange
    +3 °C      #a50026    Deep red
    =========  =========  =========

    Returns:
        A :class:`matplotlib.colors.LinearSegmentedColormap` instance
        registered as ``'anomaly_custom'``.
    """
    stops: list[tuple[float, str]] = [
        (0.00, "#313695"),
        (0.25, "#74add1"),
        (0.45, "#e0f3f8"),
        (0.50, "#ffffbf"),
        (0.55, "#fee090"),
        (0.75, "#f46d43"),
        (1.00, "#a50026"),
    ]

    positions = [s[0] for s in stops]
    rgb_colors: list[tuple[float, float, float]] = []
    for _, hex_color in stops:
        h = hex_color.lstrip("#")
        rgb_colors.append(
            tuple(int(h[i : i + 2], 16) / 255.0 for i in (0, 2, 4))  # type: ignore[misc]
        )

    return LinearSegmentedColormap.from_list(
        "anomaly_custom", list(zip(positions, rgb_colors))
    )


# ---------------------------------------------------------------------------
# Module-level legend snapshot (for documentation / quick reference)
# ---------------------------------------------------------------------------

#: Pre-computed RGB values for each full-degree step in the anomaly range.
LEGEND_COLORS: dict[str, tuple[int, int, int]] = {
    "-3": anomaly_to_rgb(-3.0),
    "-2": anomaly_to_rgb(-2.0),
    "-1": anomaly_to_rgb(-1.0),
    "0": anomaly_to_rgb(0.0),
    "+1": anomaly_to_rgb(1.0),
    "+2": anomaly_to_rgb(2.0),
    "+3": anomaly_to_rgb(3.0),
}


if __name__ == "__main__":
    print("Anomaly legend colors (RGB):")
    for label, rgb in LEGEND_COLORS.items():
        print(f"  {label:>3}°C → {rgb}")
    print()
    print("Legend (value, hex):")
    for val, hex_color in get_legend_colors():
        print(f"  {val:+.1f}°C → {hex_color}")
