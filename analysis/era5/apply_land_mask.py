"""Apply a Germany land mask to native-resolution ERA5-Land data.

Uses Natural Earth 1:10m land polygons rasterized to the provider's
native grid.  German coastal islands (Sylt, Rügen, Helgoland, Borkum,
Fehmarn, Usedom) are explicitly verified after mask creation.
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import xarray as xr

from .config import GERMAN_ISLANDS
from .providers.protocol import ClimateDataProvider

logger = logging.getLogger(__name__)

# URL for Natural Earth 1:10m land polygons.
_NATURAL_EARTH_URL = (
    "https://naciscdn.org/naturalearth/10m/physical/ne_10m_land.zip"
)


# ---------------------------------------------------------------------------
# Polygon download
# ---------------------------------------------------------------------------


def download_land_polygons(cache_dir: Path) -> Path:
    """Download Natural Earth 1:10m land polygons (with local caching).

    Args:
        cache_dir: Directory where the archive and extracted shapefile
            are stored.

    Returns:
        Path to the extracted ``ne_10m_land.shp`` file.

    Raises:
        requests.HTTPError: If the download fails.
    """
    import requests
    import zipfile

    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)

    zip_path = cache_dir / "ne_10m_land.zip"
    shp_path = cache_dir / "ne_10m_land" / "ne_10m_land.shp"

    if shp_path.exists():
        logger.info("Using cached land polygons: %s", shp_path)
        return shp_path

    logger.info("Downloading Natural Earth 1:10m land polygons …")
    response = requests.get(_NATURAL_EARTH_URL, timeout=60)
    response.raise_for_status()

    zip_path.write_bytes(response.content)
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(cache_dir / "ne_10m_land")

    logger.info("Extracted land polygons to: %s", shp_path)
    return shp_path


# ---------------------------------------------------------------------------
# Mask creation
# ---------------------------------------------------------------------------


def create_germany_land_mask(
    output_path: Path,
    ds: xr.Dataset,
    provider: ClimateDataProvider,
    cache_dir: Path = Path("./data/cache"),
) -> np.ndarray:
    """Create a boolean land mask matching the provider's native grid.

    Rasterizes Natural Earth 1:10m land polygons clipped to the
    provider's bounds onto the same latitude / longitude grid as ``ds``.

    Args:
        output_path: Path where the mask is saved as a single-band
            ``uint8`` GeoTIFF (1 = land, 0 = ocean / outside Germany).
        ds: Reference ``xr.Dataset`` whose coordinate arrays define the
            output grid shape and extent.
        provider: Active climate data provider supplying the bounds.
        cache_dir: Directory for Natural Earth download cache.

    Returns:
        Boolean ``numpy`` array shaped ``(n_lat, n_lon)`` where
        ``True`` indicates a land cell.

    Raises:
        ValueError: If the shapefile could not be loaded.
    """
    import geopandas as gpd
    import rasterio
    from rasterio import features as rio_features
    from rasterio.transform import from_bounds as rasterio_from_bounds

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    shp_path = download_land_polygons(cache_dir)

    logger.info("Loading land polygons …")
    land = gpd.read_file(shp_path)

    bnd = provider.bounds
    buf = 0.5
    land_clipped = land.cx[
        bnd["west"] - buf : bnd["east"] + buf,
        bnd["south"] - buf : bnd["north"] + buf,
    ]

    lat_key = provider.coordinate_names["latitude"]
    lon_key = provider.coordinate_names["longitude"]
    n_lat = int(ds[lat_key].size)
    n_lon = int(ds[lon_key].size)

    transform = rasterio_from_bounds(
        bnd["west"],
        bnd["south"],
        bnd["east"],
        bnd["north"],
        n_lon,
        n_lat,
    )

    logger.info("Rasterizing to %dx%d grid …", n_lat, n_lon)
    shapes = [(geom, 1) for geom in land_clipped.geometry if geom is not None]
    mask_raw = rio_features.rasterize(
        shapes,
        out_shape=(n_lat, n_lon),
        transform=transform,
        fill=0,
        dtype=np.uint8,
    )
    mask = mask_raw.astype(bool)

    _verify_islands(mask, transform)

    with rasterio.open(
        output_path,
        "w",
        driver="GTiff",
        height=n_lat,
        width=n_lon,
        count=1,
        dtype=np.uint8,
        crs="EPSG:4326",
        transform=transform,
    ) as dst:
        dst.write(mask.astype(np.uint8), 1)

    logger.info("Saved land mask: %s", output_path)
    return mask


# ---------------------------------------------------------------------------
# Island verification
# ---------------------------------------------------------------------------


def _verify_islands(mask: np.ndarray, transform) -> None:
    """Log a warning for any German island not covered by the land mask.

    Args:
        mask: Boolean land mask array (True = land).
        transform: Rasterio affine transform for coordinate conversion.
    """
    for island in GERMAN_ISLANDS:
        col, row = ~transform * (island["lon"], island["lat"])
        row_i, col_i = int(row), int(col)
        if 0 <= row_i < mask.shape[0] and 0 <= col_i < mask.shape[1]:
            if mask[row_i, col_i]:
                logger.debug("✓ %s included in land mask", island["name"])
            else:
                logger.warning(
                    "Island '%s' at (lat=%.2f, lon=%.2f) NOT in land mask!",
                    island["name"],
                    island["lat"],
                    island["lon"],
                )
        else:
            logger.warning("Island '%s' is outside grid bounds", island["name"])


# ---------------------------------------------------------------------------
# Mask loading
# ---------------------------------------------------------------------------


def load_land_mask(mask_path: Path) -> np.ndarray:
    """Load a pre-computed land mask from a GeoTIFF file.

    Args:
        mask_path: Path to a single-band uint8 GeoTIFF (1=land, 0=ocean).

    Returns:
        Boolean ``numpy`` array (True = land).
    """
    import rasterio

    with rasterio.open(mask_path) as src:
        data = src.read(1)
    return data.astype(bool)


# ---------------------------------------------------------------------------
# Mask application
# ---------------------------------------------------------------------------


def apply_germany_land_mask(
    ds: xr.Dataset,
    provider: ClimateDataProvider,
    mask_path: Path | None = None,
    cache_dir: Path = Path("./data/cache"),
) -> xr.Dataset:
    """Apply a Germany land mask to every data variable in *ds*.

    Ocean / outside-Germany cells are set to ``NaN``.

    Args:
        ds: Input ``xr.Dataset`` with latitude / longitude coordinates
            matching the provider's native grid.
        provider: Active climate data provider.
        mask_path: Path to a pre-computed mask GeoTIFF.  If ``None`` or the
            file does not exist, a new mask is created and optionally saved
            to ``cache_dir / 'germany_land_mask.tif'``.
        cache_dir: Directory for mask caching and Natural Earth data.

    Returns:
        Copy of *ds* with ocean cells replaced by ``NaN`` and a global
        attribute ``land_mask_applied = True``.
    """
    import rasterio
    from rasterio.transform import from_bounds as rasterio_from_bounds

    cache_dir = Path(cache_dir)

    if mask_path is None:
        mask_path = cache_dir / "germany_land_mask.tif"

    mask_path = Path(mask_path)

    if mask_path.exists():
        mask = load_land_mask(mask_path)
    else:
        mask = create_germany_land_mask(mask_path, ds, provider, cache_dir)

    lat_key = provider.coordinate_names["latitude"]
    lon_key = provider.coordinate_names["longitude"]

    n_lat = int(ds[lat_key].size)
    n_lon = int(ds[lon_key].size)

    bnd = provider.bounds
    transform = rasterio_from_bounds(
        bnd["west"],
        bnd["south"],
        bnd["east"],
        bnd["north"],
        n_lon,
        n_lat,
    )

    if mask.shape != (n_lat, n_lon):
        logger.warning(
            "Mask shape %s does not match dataset grid %s; skipping mask.",
            mask.shape,
            (n_lat, n_lon),
        )
        return ds

    masked_ds = ds.copy(deep=True)
    for var in masked_ds.data_vars:
        arr = masked_ds[var].values
        # Handle time dimension: apply mask to each spatial slice
        if arr.ndim == 3:
            arr = np.where(mask[np.newaxis, :, :], arr, np.nan)
        elif arr.ndim == 2:
            arr = np.where(mask, arr, np.nan)
        masked_ds[var] = xr.DataArray(
            arr,
            dims=masked_ds[var].dims,
            coords=masked_ds[var].coords,
            attrs=masked_ds[var].attrs,
        )

    masked_ds.attrs["land_mask_applied"] = True
    return masked_ds
