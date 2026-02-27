#!/usr/bin/env python3
"""
Tests for analysis/tiles/upload_tiles.py.

Covers:
  TEST-P4-009  Upload sets correct Content-Type header (image/webp)
  TEST-P4-010  Upload handles missing credentials gracefully
  Additional:  upload count matches file count, missing directory raises
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

from analysis.tiles.upload_tiles import (
    _make_s3_client,
    _upload_one,
    upload_tiles_to_s3,
)
from analysis.tiles.tile_config import CACHE_CONTROL, CONTENT_TYPE


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_fake_tile_tree(root: Path, year: int, month: int, count: int) -> list[Path]:
    """Create *count* dummy .webp files in ``root/{year}/{month:02d}/6/135/``."""
    zoom_x_dir = root / str(year) / f"{month:02d}" / "6" / "135"
    zoom_x_dir.mkdir(parents=True, exist_ok=True)

    paths: list[Path] = []
    for i in range(count):
        p = zoom_x_dir / f"{85 + i}.webp"
        p.write_bytes(b"RIFF\x00\x00\x00\x00WEBP")  # minimal plausible content
        paths.append(p)

    return paths


# ---------------------------------------------------------------------------
# _make_s3_client
# ---------------------------------------------------------------------------


class TestMakeS3Client:
    """_make_s3_client creates a boto3 client without network calls."""

    def test_returns_client_object(self, mock_s3_client: MagicMock) -> None:
        # boto3.client is already patched by the fixture; just ensure
        # _make_s3_client calls through successfully.
        client = _make_s3_client(
            endpoint_url="https://fsn1.your-objectstorage.com",
            access_key="key",
            secret_key="secret",
        )
        assert client is not None


# ---------------------------------------------------------------------------
# _upload_one
# ---------------------------------------------------------------------------


class TestUploadOne:
    """_upload_one delegates to client.upload_file with correct headers."""

    def test_success_returns_true(self, tmp_path: Path) -> None:
        tile = tmp_path / "test.webp"
        tile.write_bytes(b"fake")

        mock_client = MagicMock()
        mock_client.upload_file = MagicMock(return_value=None)

        ok, msg = _upload_one(mock_client, tile, "my-bucket", "tiles/2024/07/6/135/85.webp")

        assert ok is True
        assert "tiles/2024/07/6/135/85.webp" in msg

    def test_passes_content_type_header(self, tmp_path: Path) -> None:
        """TEST-P4-009: Content-Type must be image/webp."""
        tile = tmp_path / "test.webp"
        tile.write_bytes(b"fake")

        mock_client = MagicMock()
        mock_client.upload_file = MagicMock(return_value=None)

        _upload_one(mock_client, tile, "bucket", "key.webp")

        # ExtraArgs is passed as a keyword argument to upload_file
        extra_args = mock_client.upload_file.call_args.kwargs["ExtraArgs"]
        assert extra_args["ContentType"] == CONTENT_TYPE

    def test_passes_cache_control_header(self, tmp_path: Path) -> None:
        tile = tmp_path / "tile.webp"
        tile.write_bytes(b"fake")

        mock_client = MagicMock()

        _upload_one(mock_client, tile, "bucket", "key.webp")

        extra_args = mock_client.upload_file.call_args.kwargs["ExtraArgs"]
        assert extra_args["CacheControl"] == CACHE_CONTROL

    def test_missing_file_returns_false(self, tmp_path: Path) -> None:
        from botocore.exceptions import ClientError

        mock_client = MagicMock()
        mock_client.upload_file.side_effect = FileNotFoundError("missing")

        ok, msg = _upload_one(
            mock_client,
            tmp_path / "nonexistent.webp",
            "bucket",
            "key.webp",
        )
        assert ok is False
        assert "missing" in msg.lower() or "key.webp" in msg


# ---------------------------------------------------------------------------
# upload_tiles_to_s3
# ---------------------------------------------------------------------------


class TestUploadTilesToS3:
    """Integration tests for upload_tiles_to_s3()."""

    def test_upload_count_matches_file_count(
        self, tmp_path: Path, mock_s3_client: MagicMock
    ) -> None:
        """Number of returned successes equals tiles created."""
        n_tiles = 5
        _create_fake_tile_tree(tmp_path, year=2024, month=7, count=n_tiles)

        uploaded = upload_tiles_to_s3(
            local_dir=tmp_path,
            year=2024,
            month=7,
            bucket="climate-tiles-test",
            endpoint_url="https://fsn1.your-objectstorage.com",
            access_key="key",
            secret_key="secret",
        )

        assert uploaded == n_tiles

    def test_upload_file_called_per_tile(
        self, tmp_path: Path, mock_s3_client: MagicMock
    ) -> None:
        """boto3 upload_file is called exactly once per tile."""
        n_tiles = 3
        _create_fake_tile_tree(tmp_path, year=2024, month=8, count=n_tiles)

        upload_tiles_to_s3(
            local_dir=tmp_path,
            year=2024,
            month=8,
            bucket="climate-tiles-test",
            endpoint_url="https://fsn1.your-objectstorage.com",
            access_key="key",
            secret_key="secret",
        )

        assert mock_s3_client.upload_file.call_count == n_tiles

    def test_upload_sets_content_type_webp(
        self, tmp_path: Path, mock_s3_client: MagicMock
    ) -> None:
        """TEST-P4-009: every upload_file call receives ContentType=image/webp."""
        _create_fake_tile_tree(tmp_path, year=2024, month=6, count=2)

        upload_tiles_to_s3(
            local_dir=tmp_path,
            year=2024,
            month=6,
            bucket="climate-tiles-test",
            endpoint_url="https://fsn1.your-objectstorage.com",
            access_key="key",
            secret_key="secret",
        )

        for upload_call in mock_s3_client.upload_file.call_args_list:
            extra_args = upload_call.kwargs["ExtraArgs"]
            assert extra_args["ContentType"] == "image/webp"

    def test_missing_credentials_raises_runtime_error(
        self, tmp_path: Path
    ) -> None:
        """TEST-P4-010: empty credentials raise RuntimeError before any upload."""
        _create_fake_tile_tree(tmp_path, year=2024, month=1, count=1)

        with pytest.raises(RuntimeError, match="credentials"):
            upload_tiles_to_s3(
                local_dir=tmp_path,
                year=2024,
                month=1,
                bucket="bucket",
                endpoint_url="https://fsn1.your-objectstorage.com",
                access_key="",   # empty
                secret_key="",   # empty
            )

    def test_missing_month_directory_raises(self, tmp_path: Path) -> None:
        """FileNotFoundError when month subdirectory does not exist."""
        with pytest.raises(FileNotFoundError):
            upload_tiles_to_s3(
                local_dir=tmp_path,
                year=2099,
                month=12,
                bucket="bucket",
                endpoint_url="https://example.com",
                access_key="key",
                secret_key="secret",
            )

    def test_empty_directory_returns_zero(
        self, tmp_path: Path, mock_s3_client: MagicMock
    ) -> None:
        """Returns 0 and makes no uploads when month dir has no .webp files."""
        month_dir = tmp_path / "2024" / "01"
        month_dir.mkdir(parents=True, exist_ok=True)

        # No .webp files
        result = upload_tiles_to_s3(
            local_dir=tmp_path,
            year=2024,
            month=1,
            bucket="bucket",
            endpoint_url="https://example.com",
            access_key="key",
            secret_key="secret",
        )

        assert result == 0
        mock_s3_client.upload_file.assert_not_called()

    def test_prefix_is_prepended_to_object_key(
        self, tmp_path: Path, mock_s3_client: MagicMock
    ) -> None:
        """Object keys start with the configured prefix."""
        _create_fake_tile_tree(tmp_path, year=2024, month=5, count=1)

        upload_tiles_to_s3(
            local_dir=tmp_path,
            year=2024,
            month=5,
            bucket="bucket",
            endpoint_url="https://example.com",
            access_key="key",
            secret_key="secret",
            prefix="custom-prefix",
        )

        called_key = mock_s3_client.upload_file.call_args[0][2]
        assert called_key.startswith("custom-prefix/")
