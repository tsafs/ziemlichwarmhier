#!/usr/bin/env python3
"""
Tests for analysis/tiles/generate_tiles.py.

Covers:
  TEST-P4-005  Tile bounds calculation covers Germany
  TEST-P4-006  Generated tile has correct dimensions (256 × 256)
  TEST-P4-007  Generated WebP has alpha channel (RGBA)
  TEST-P4-008  generate_tiles_for_geotiff creates correct directory structure
  TEST-P4-009  generate_tiles_for_geotiff returns a positive tile count
"""

from __future__ import annotations

from pathlib import Path

import mercantile
import numpy as np
import pytest
from PIL import Image

from analysis.tiles.generate_tiles import (
    count_tiles,
    generate_tiles_for_geotiff,
    get_tile_bounds,
    render_tile,
    save_tile,
)
from analysis.tiles.tile_config import GERMANY_BOUNDS, TILE_SIZE


# ---------------------------------------------------------------------------
# get_tile_bounds / count_tiles
# ---------------------------------------------------------------------------


class TestGetTileBounds:
    """TEST-P4-005: tile bounds calculation covers Germany."""

    def test_returns_non_empty_list(self) -> None:
        tiles = get_tile_bounds(GERMANY_BOUNDS, zoom=6)
        assert len(tiles) > 0

    def test_all_tiles_have_correct_zoom(self) -> None:
        for z in (6, 7, 8):
            tiles = get_tile_bounds(GERMANY_BOUNDS, zoom=z)
            for t in tiles:
                assert t.z == z

    def test_higher_zoom_has_more_tiles(self) -> None:
        tiles_z6 = get_tile_bounds(GERMANY_BOUNDS, zoom=6)
        tiles_z8 = get_tile_bounds(GERMANY_BOUNDS, zoom=8)
        assert len(tiles_z8) > len(tiles_z6)

    def test_tiles_cover_germany_center(self) -> None:
        """Berlin (52.52 N, 13.40 E) must be inside at least one tile at z8."""
        tiles_z8 = get_tile_bounds(GERMANY_BOUNDS, zoom=8)
        berlin_tile = mercantile.tile(13.40, 52.52, 8)
        assert berlin_tile in tiles_z8


class TestCountTiles:
    """count_tiles() returns a dict of counts per zoom level."""

    def test_returns_dict_with_expected_keys(self) -> None:
        counts = count_tiles(GERMANY_BOUNDS, min_zoom=6, max_zoom=8)
        assert set(counts.keys()) == {6, 7, 8}

    def test_monotonically_increasing(self) -> None:
        counts = count_tiles(GERMANY_BOUNDS, min_zoom=6, max_zoom=9)
        values = [counts[z] for z in sorted(counts)]
        assert all(b >= a for a, b in zip(values, values[1:]))


# ---------------------------------------------------------------------------
# save_tile
# ---------------------------------------------------------------------------


class TestSaveTile:
    """save_tile() writes a valid WebP (RGBA) file."""

    def test_creates_file(self, tmp_path: Path) -> None:
        img = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (128, 64, 32, 255))
        out = tmp_path / "test.webp"
        size = save_tile(img, out)
        assert out.exists()
        assert size > 0

    def test_creates_nested_parent_dirs(self, tmp_path: Path) -> None:
        img = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))
        out = tmp_path / "a" / "b" / "c" / "tile.webp"
        save_tile(img, out)
        assert out.exists()

    def test_saved_file_is_readable_webp(self, tmp_path: Path) -> None:
        img = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (255, 0, 0, 200))
        out = tmp_path / "tile.webp"
        save_tile(img, out)

        with Image.open(out) as read_back:
            assert read_back.format == "WEBP"
            assert read_back.mode == "RGBA"
            assert read_back.size == (TILE_SIZE, TILE_SIZE)

    def test_quality_affects_file_size(self, tmp_path: Path) -> None:
        # Use a varied image so quality actually matters
        rng = np.random.default_rng(0)
        arr = rng.integers(0, 256, (TILE_SIZE, TILE_SIZE, 4), dtype=np.uint8)
        img = Image.fromarray(arr, mode="RGBA")

        out_hq = tmp_path / "hq.webp"
        out_lq = tmp_path / "lq.webp"
        save_tile(img, out_hq, quality=95)
        save_tile(img, out_lq, quality=10)

        assert out_hq.stat().st_size > out_lq.stat().st_size


# ---------------------------------------------------------------------------
# render_tile  (TEST-P4-006, P4-007)
# ---------------------------------------------------------------------------


class TestRenderTile:
    """TEST-P4-006 / P4-007: rendered tile dimensions and mode."""

    def test_output_size_is_256x256(self, sample_geotiff_path: Path) -> None:
        from rio_tiler.io import Reader

        tile = mercantile.tile(10.0, 51.0, 7)  # Central Germany, z7
        with Reader(str(sample_geotiff_path)) as src:
            img = render_tile(src, tile.x, tile.y, tile.z)

        assert img.size == (TILE_SIZE, TILE_SIZE)

    def test_output_mode_is_rgba(self, sample_geotiff_path: Path) -> None:
        from rio_tiler.io import Reader

        tile = mercantile.tile(10.0, 51.0, 7)
        with Reader(str(sample_geotiff_path)) as src:
            img = render_tile(src, tile.x, tile.y, tile.z)

        assert img.mode == "RGBA"

    def test_tile_outside_bounds_is_transparent(self, sample_geotiff_path: Path) -> None:
        """A tile far outside Germany should produce a fully transparent image."""
        from rio_tiler.io import Reader

        # Tile somewhere in North Africa (well outside Germany GeoTIFF)
        africa_tile = mercantile.tile(15.0, 30.0, 7)

        with Reader(str(sample_geotiff_path)) as src:
            img = render_tile(src, africa_tile.x, africa_tile.y, africa_tile.z)

        arr = np.array(img)
        # All alpha values should be 0 (no land data here)
        assert arr[:, :, 3].max() == 0


# ---------------------------------------------------------------------------
# generate_tiles_for_geotiff  (TEST-P4-005 to P4-009)
# ---------------------------------------------------------------------------


class TestGenerateTilesForGeotiff:
    """Integration tests for the full tile-generation pipeline."""

    def test_returns_positive_tile_count(
        self, sample_geotiff_path: Path, tmp_tile_dir: Path
    ) -> None:
        """TEST-P4-009: at least one tile is written."""
        count = generate_tiles_for_geotiff(
            sample_geotiff_path,
            tmp_tile_dir,
            year=2024,
            month=7,
            min_zoom=6,
            max_zoom=7,
        )
        assert count > 0

    def test_creates_correct_directory_structure(
        self, sample_geotiff_path: Path, tmp_tile_dir: Path
    ) -> None:
        """TEST-P4-008: tiles are placed in {year}/{month}/{z}/{x}/{y}.webp."""
        generate_tiles_for_geotiff(
            sample_geotiff_path,
            tmp_tile_dir,
            year=2024,
            month=7,
            min_zoom=6,
            max_zoom=6,
        )
        # Year / month dir exists
        month_dir = tmp_tile_dir / "2024" / "07"
        assert month_dir.exists()

        # Zoom-level directory exists
        zoom_dir = month_dir / "6"
        assert zoom_dir.exists()

        # At least one .webp file is present somewhere under zoom dir
        tiles = list(zoom_dir.rglob("*.webp"))
        assert len(tiles) > 0

    def test_tiles_are_256x256(
        self, sample_geotiff_path: Path, tmp_tile_dir: Path
    ) -> None:
        """TEST-P4-006: every written tile is exactly 256 × 256 pixels."""
        generate_tiles_for_geotiff(
            sample_geotiff_path,
            tmp_tile_dir,
            year=2024,
            month=1,
            min_zoom=6,
            max_zoom=6,
        )
        for tile_path in (tmp_tile_dir / "2024" / "01" / "6").rglob("*.webp"):
            with Image.open(tile_path) as img:
                assert img.size == (TILE_SIZE, TILE_SIZE), (
                    f"{tile_path.name}: expected 256×256, got {img.size}"
                )

    def test_tiles_have_alpha_channel(
        self, sample_geotiff_path: Path, tmp_tile_dir: Path
    ) -> None:
        """TEST-P4-007: every written tile has RGBA mode."""
        generate_tiles_for_geotiff(
            sample_geotiff_path,
            tmp_tile_dir,
            year=2024,
            month=1,
            min_zoom=6,
            max_zoom=6,
        )
        for tile_path in (tmp_tile_dir / "2024" / "01" / "6").rglob("*.webp"):
            with Image.open(tile_path) as img:
                assert img.mode == "RGBA", (
                    f"{tile_path.name}: expected RGBA, got {img.mode}"
                )

    def test_month_zero_padding_in_path(
        self, sample_geotiff_path: Path, tmp_tile_dir: Path
    ) -> None:
        """Single-digit months are zero-padded in the directory name."""
        generate_tiles_for_geotiff(
            sample_geotiff_path,
            tmp_tile_dir,
            year=2024,
            month=3,
            min_zoom=6,
            max_zoom=6,
        )
        assert (tmp_tile_dir / "2024" / "03").exists()
        # No unpadded directory should have been created
        assert not (tmp_tile_dir / "2024" / "3").exists()

    def test_missing_geotiff_raises(self, tmp_tile_dir: Path) -> None:
        """FileNotFoundError when the source GeoTIFF does not exist."""
        with pytest.raises(FileNotFoundError):
            generate_tiles_for_geotiff(
                Path("/nonexistent/file.tif"),
                tmp_tile_dir,
                year=2024,
                month=1,
                min_zoom=6,
                max_zoom=6,
            )
