#!/usr/bin/env python3
"""
Upload generated tile pyramids to Hetzner Object Storage (S3-compatible).

Handles parallel uploads, sets the correct ``Content-Type: image/webp``
and ``Cache-Control`` headers, and reports progress via tqdm.

Credentials are read from environment variables (or passed explicitly):
  - ``ACCESS_KEY``   – S3 access key
  - ``SECRET_KEY``   – S3 secret key
  - ``ENDPOINT_URL`` – S3 endpoint (e.g. ``https://fsn1.your-objectstorage.com``)
"""

from __future__ import annotations

import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from tqdm import tqdm

from .tile_config import CACHE_CONTROL, CONTENT_TYPE

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def upload_tiles_to_s3(
    local_dir: Path | str,
    year: int,
    month: int,
    bucket: str,
    endpoint_url: str,
    access_key: str,
    secret_key: str,
    prefix: str = "tiles",
    parallel: int = 8,
) -> int:
    """Upload all WebP tiles for a given month to S3-compatible storage.

    Recursively scans *local_dir/{year}/{month:02d}/* for ``*.webp`` files,
    uploads them in parallel, and sets the correct HTTP headers for each
    object.

    Args:
        local_dir:    Root tile directory (contains ``{year}/{month:02d}/…``).
        year:         Data year (used to locate the month subdirectory).
        month:        Data month 1-12 (used to locate the month subdirectory).
        bucket:       Target S3 bucket name.
        endpoint_url: Full S3 endpoint URL (e.g. ``https://fsn1.your-objectstorage.com``).
        access_key:   S3 access key ID.
        secret_key:   S3 secret access key.
        prefix:       Object-key prefix inside the bucket (default ``'tiles'``).
        parallel:     Number of parallel upload threads.

    Returns:
        Number of tiles successfully uploaded.

    Raises:
        RuntimeError: If *access_key* or *secret_key* are empty.
        FileNotFoundError: If the month subdirectory does not exist.
    """
    local_dir = Path(local_dir)
    month_dir = local_dir / str(year) / f"{month:02d}"

    if not access_key or not secret_key:
        raise RuntimeError(
            "S3 credentials are required. "
            "Pass access_key and secret_key, or set ACCESS_KEY / SECRET_KEY env vars."
        )

    if not month_dir.exists():
        raise FileNotFoundError(f"Tile directory not found: {month_dir}")

    tiles = list(month_dir.rglob("*.webp"))
    if not tiles:
        logger.warning("No WebP tiles found in %s", month_dir)
        return 0

    client = _make_s3_client(endpoint_url, access_key, secret_key)

    # Build (local_path, object_key) pairs
    tasks: list[tuple[Path, str]] = []
    for tile_path in tiles:
        rel = tile_path.relative_to(local_dir)
        object_key = f"{prefix.rstrip('/')}/{rel}" if prefix else str(rel)
        tasks.append((tile_path, object_key))

    logger.info(
        "Uploading %d tiles → s3://%s/%s/%s/%02d",
        len(tasks),
        bucket,
        prefix,
        year,
        month,
    )

    success_count = 0
    failures: list[str] = []

    with ThreadPoolExecutor(max_workers=parallel) as executor:
        future_to_key = {
            executor.submit(_upload_one, client, fp, bucket, key): key
            for fp, key in tasks
        }
        for future in tqdm(
            as_completed(future_to_key),
            total=len(future_to_key),
            desc="Uploading tiles",
            unit="tile",
        ):
            ok, message = future.result()
            if ok:
                success_count += 1
            else:
                failures.append(message)
                logger.warning("Upload failed: %s", message)

    logger.info(
        "Upload complete – %d/%d successful, %d failed",
        success_count,
        len(tasks),
        len(failures),
    )
    return success_count


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _make_s3_client(
    endpoint_url: str,
    access_key: str,
    secret_key: str,
    region: str = "eu-central-1",
):
    """Construct a boto3 S3 client for Hetzner Object Storage.

    Args:
        endpoint_url: S3-compatible endpoint.
        access_key:   S3 access key ID.
        secret_key:   S3 secret access key.
        region:       AWS region string (Hetzner uses ``eu-central-1``).

    Returns:
        Configured :class:`boto3.client` instance.
    """
    config = Config(
        retries={"max_attempts": 3, "mode": "adaptive"},
        max_pool_connections=25,
    )
    return boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        region_name=region,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=config,
    )


def _upload_one(
    client,
    file_path: Path,
    bucket: str,
    object_key: str,
) -> tuple[bool, str]:
    """Upload a single tile file; return ``(success, message)``."""
    try:
        client.upload_file(
            str(file_path),
            bucket,
            object_key,
            ExtraArgs={
                "ContentType": CONTENT_TYPE,
                "CacheControl": CACHE_CONTROL,
                "ACL": "public-read",
            },
        )
        return True, object_key
    except ClientError as exc:
        return False, f"{object_key}: {exc}"
    except FileNotFoundError:
        return False, f"{object_key}: local file missing"


# ---------------------------------------------------------------------------
# Convenience wrapper (reads credentials from environment)
# ---------------------------------------------------------------------------


def upload_tiles_from_env(
    local_dir: Path | str,
    year: int,
    month: int,
    prefix: str = "tiles",
    parallel: int = 8,
) -> int:
    """Upload tiles using credentials and endpoint from environment variables.

    Reads ``ACCESS_KEY``, ``SECRET_KEY``, ``ENDPOINT_URL`` and ``BUCKET_NAME``
    from the process environment.

    Args:
        local_dir: Root tile directory.
        year:      Data year.
        month:     Data month 1-12.
        prefix:    Object-key prefix inside the bucket.
        parallel:  Number of parallel upload threads.

    Returns:
        Number of tiles successfully uploaded.

    Raises:
        RuntimeError: If any required environment variable is missing.
    """
    missing = [
        v
        for v in ("ACCESS_KEY", "SECRET_KEY", "ENDPOINT_URL", "BUCKET_NAME")
        if not os.environ.get(v)
    ]
    if missing:
        raise RuntimeError(f"Missing required env vars: {', '.join(missing)}")

    return upload_tiles_to_s3(
        local_dir=local_dir,
        year=year,
        month=month,
        bucket=os.environ["BUCKET_NAME"],
        endpoint_url=os.environ["ENDPOINT_URL"],
        access_key=os.environ["ACCESS_KEY"],
        secret_key=os.environ["SECRET_KEY"],
        prefix=prefix,
        parallel=parallel,
    )


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    parser = argparse.ArgumentParser(description="Upload WebP tiles to S3-compatible storage.")
    parser.add_argument("tiles_dir", help="Local root tile directory")
    parser.add_argument("--bucket", default=os.environ.get("BUCKET_NAME", ""), required=False)
    parser.add_argument("--endpoint-url", default=os.environ.get("ENDPOINT_URL", ""))
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--month", type=int, required=True)
    parser.add_argument("--prefix", default="tiles")
    parser.add_argument("--parallel", type=int, default=8)
    args = parser.parse_args()

    n = upload_tiles_to_s3(
        local_dir=Path(args.tiles_dir),
        year=args.year,
        month=args.month,
        bucket=args.bucket,
        endpoint_url=args.endpoint_url,
        access_key=os.environ.get("ACCESS_KEY", ""),
        secret_key=os.environ.get("SECRET_KEY", ""),
        prefix=args.prefix,
        parallel=args.parallel,
    )
    print(f"Uploaded {n} tiles.")
