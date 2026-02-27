#!/usr/bin/env python3
"""
Tests for analysis/tiles/color_ramps.py.

Covers:
  TEST-P4-001  Cold anomaly → blue-dominant RGBA
  TEST-P4-002  Zero anomaly → neutral / near-white RGBA
  TEST-P4-003  Warm anomaly → red-dominant RGBA
  TEST-P4-004  NaN input    → transparent pixel (alpha = 0)
  get_legend_colors() interface contract
"""

from __future__ import annotations

import numpy as np
import pytest

from analysis.tiles.color_ramps import (
    ANOMALY_VMAX,
    ANOMALY_VMIN,
    apply_anomaly_colormap,
    anomaly_to_rgb,
    get_anomaly_colormap,
    get_legend_colors,
)


# ---------------------------------------------------------------------------
# get_anomaly_colormap
# ---------------------------------------------------------------------------


class TestGetAnomalyColormap:
    """Return value contract for get_anomaly_colormap()."""

    def test_returns_callable_colormap(self) -> None:
        cmap = get_anomaly_colormap()
        assert callable(cmap)

    def test_default_is_rdbu_r(self) -> None:
        cmap = get_anomaly_colormap()
        assert "rdbu" in cmap.name.lower()

    def test_custom_name_accepted(self) -> None:
        cmap = get_anomaly_colormap("coolwarm")
        assert cmap is not None


# ---------------------------------------------------------------------------
# apply_anomaly_colormap – shape / dtype
# ---------------------------------------------------------------------------


class TestApplyAnomalyColormapShape:
    """Output array has the correct shape and dtype."""

    def test_output_shape_matches_input(self) -> None:
        data = np.random.uniform(-3, 3, (100, 100))
        rgba = apply_anomaly_colormap(data)
        assert rgba.shape == (100, 100, 4)

    def test_output_dtype_is_uint8(self) -> None:
        data = np.ones((10, 10), dtype=np.float32)
        rgba = apply_anomaly_colormap(data)
        assert rgba.dtype == np.uint8

    def test_single_pixel_input(self) -> None:
        data = np.array([[1.5]])
        rgba = apply_anomaly_colormap(data)
        assert rgba.shape == (1, 1, 4)


# ---------------------------------------------------------------------------
# TEST-P4-001  Cold anomaly → blue-dominant
# ---------------------------------------------------------------------------


class TestColdAnomalyIsBlue:
    """TEST-P4-001: negative anomaly maps to blue-dominant colour."""

    def test_blue_channel_exceeds_red_at_minus_three(self) -> None:
        data = np.full((10, 10), -3.0)
        rgba = apply_anomaly_colormap(data)

        mean_red = rgba[:, :, 0].mean()
        mean_blue = rgba[:, :, 2].mean()

        assert mean_blue > mean_red, (
            f"Expected blue ({mean_blue:.1f}) > red ({mean_red:.1f}) at -3°C"
        )

    def test_alpha_is_opaque_for_valid_data(self) -> None:
        data = np.full((5, 5), -2.0)
        rgba = apply_anomaly_colormap(data)
        assert (rgba[:, :, 3] == 255).all()

    def test_anomaly_to_rgb_blue_dominant(self) -> None:
        r, g, b = anomaly_to_rgb(-3.0)
        assert b > r


# ---------------------------------------------------------------------------
# TEST-P4-002  Zero anomaly → neutral
# ---------------------------------------------------------------------------


class TestNeutralAnomalyIsWhite:
    """TEST-P4-002: zero anomaly maps to near-white / neutral colour."""

    def test_all_channels_are_bright_at_zero(self) -> None:
        data = np.full((10, 10), 0.0)
        rgba = apply_anomaly_colormap(data)

        r = rgba[:, :, 0].mean()
        g = rgba[:, :, 1].mean()
        b = rgba[:, :, 2].mean()

        # RdBu_r near 0 is close to white (all channels above 200)
        assert r > 200, f"Red channel {r:.1f} should be > 200 at 0°C"
        assert g > 200, f"Green channel {g:.1f} should be > 200 at 0°C"
        assert b > 200, f"Blue channel {b:.1f} should be > 200 at 0°C"

    def test_channels_are_similar_to_each_other(self) -> None:
        data = np.full((10, 10), 0.0)
        rgba = apply_anomaly_colormap(data)

        r = float(rgba[:, :, 0].mean())
        g = float(rgba[:, :, 1].mean())
        b = float(rgba[:, :, 2].mean())

        assert abs(r - g) < 30
        assert abs(r - b) < 30


# ---------------------------------------------------------------------------
# TEST-P4-003  Warm anomaly → red-dominant
# ---------------------------------------------------------------------------


class TestWarmAnomalyIsRed:
    """TEST-P4-003: positive anomaly maps to red-dominant colour."""

    def test_red_channel_exceeds_blue_at_plus_three(self) -> None:
        data = np.full((10, 10), 3.0)
        rgba = apply_anomaly_colormap(data)

        mean_red = rgba[:, :, 0].mean()
        mean_blue = rgba[:, :, 2].mean()

        assert mean_red > mean_blue, (
            f"Expected red ({mean_red:.1f}) > blue ({mean_blue:.1f}) at +3°C"
        )

    def test_anomaly_to_rgb_red_dominant(self) -> None:
        r, g, b = anomaly_to_rgb(3.0)
        assert r > b


# ---------------------------------------------------------------------------
# TEST-P4-004  NaN input → transparent pixel
# ---------------------------------------------------------------------------


class TestNaNIsTransparent:
    """TEST-P4-004: NaN values produce alpha = 0 (transparent)."""

    def test_nan_pixel_has_alpha_zero(self) -> None:
        data = np.array([[np.nan, 1.0], [2.0, np.nan]])
        rgba = apply_anomaly_colormap(data)

        assert rgba[0, 0, 3] == 0, "Top-left NaN should be transparent"
        assert rgba[1, 1, 3] == 0, "Bottom-right NaN should be transparent"

    def test_valid_pixels_have_alpha_255(self) -> None:
        data = np.array([[np.nan, 1.0], [2.0, np.nan]])
        rgba = apply_anomaly_colormap(data)

        assert rgba[0, 1, 3] == 255, "Top-right valid pixel should be opaque"
        assert rgba[1, 0, 3] == 255, "Bottom-left valid pixel should be opaque"

    def test_all_nan_array_fully_transparent(self) -> None:
        data = np.full((8, 8), np.nan)
        rgba = apply_anomaly_colormap(data)
        assert (rgba[:, :, 3] == 0).all()

    def test_anomaly_to_rgb_nan_returns_black(self) -> None:
        result = anomaly_to_rgb(float("nan"))
        assert result == (0, 0, 0)


# ---------------------------------------------------------------------------
# Out-of-range values
# ---------------------------------------------------------------------------


class TestOutOfRangeClipping:
    """Values outside [VMIN, VMAX] are clipped without error."""

    def test_extreme_negative_does_not_raise(self) -> None:
        data = np.array([[-100.0]])
        rgba = apply_anomaly_colormap(data)
        assert rgba.shape == (1, 1, 4)

    def test_extreme_positive_does_not_raise(self) -> None:
        data = np.array([[100.0]])
        rgba = apply_anomaly_colormap(data)
        assert rgba.shape == (1, 1, 4)

    def test_clipped_values_match_boundary_colours(self) -> None:
        cold_boundary = apply_anomaly_colormap(np.array([[ANOMALY_VMIN]]))
        cold_extreme = apply_anomaly_colormap(np.array([[ANOMALY_VMIN - 10]]))
        np.testing.assert_array_equal(cold_boundary, cold_extreme)


# ---------------------------------------------------------------------------
# get_legend_colors
# ---------------------------------------------------------------------------


class TestGetLegendColors:
    """Contract for get_legend_colors()."""

    def test_default_returns_seven_tuples(self) -> None:
        legend = get_legend_colors()
        assert len(legend) == 7

    def test_each_entry_is_value_hex_tuple(self) -> None:
        for value, hex_color in get_legend_colors():
            assert isinstance(value, float)
            assert isinstance(hex_color, str)
            assert hex_color.startswith("#")
            assert len(hex_color) == 7

    def test_first_value_is_anomaly_vmin(self) -> None:
        legend = get_legend_colors()
        assert legend[0][0] == ANOMALY_VMIN

    def test_last_value_is_anomaly_vmax(self) -> None:
        legend = get_legend_colors()
        assert legend[-1][0] == ANOMALY_VMAX

    def test_neutral_value_is_zero(self) -> None:
        legend = get_legend_colors(n=7)  # n=7 gives symmetric halves
        middle_val = legend[3][0]
        assert abs(middle_val) < 1e-9, f"Middle value {middle_val} should be 0"

    def test_cold_hex_is_darker_blue_than_neutral(self) -> None:
        legend = get_legend_colors(n=7)
        cold_hex = legend[0][1]
        neutral_hex = legend[3][1]

        # Extract blue channel
        cold_b = int(cold_hex[5:7], 16)
        neutral_b = int(neutral_hex[5:7], 16)

        assert cold_b > neutral_b, "Cold colour should have higher blue than neutral"

    def test_warm_hex_is_more_red_than_neutral(self) -> None:
        legend = get_legend_colors(n=7)
        warm_hex = legend[-1][1]
        neutral_hex = legend[3][1]

        warm_r = int(warm_hex[1:3], 16)
        neutral_r = int(neutral_hex[1:3], 16)

        assert warm_r > neutral_r, "Warm colour should have higher red than neutral"

    def test_custom_n(self) -> None:
        for n in (2, 5, 11):
            legend = get_legend_colors(n=n)
            assert len(legend) == n

    def test_n_less_than_two_raises(self) -> None:
        with pytest.raises(ValueError):
            get_legend_colors(n=1)
