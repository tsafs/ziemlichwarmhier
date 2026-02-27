"""Calculate temperature anomalies relative to the 1961-1990 reference period.

Anomaly = current monthly mean − corresponding climatological monthly mean.
Output is written as both a GeoTIFF (for tile rendering) and a NetCDF (for
further processing).
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import xarray as xr

from .config import ANOMALY_COLORMAP, REFERENCE_PERIOD
from .providers.protocol import ClimateDataProvider
from .types import AnomalyMetadata

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Climatology helpers
# ---------------------------------------------------------------------------


def load_climatology(climatology_path: Path, month: int) -> xr.DataArray:
    """Load the climatological monthly mean for a single calendar month.

    Args:
        climatology_path: Path to a climatology NetCDF produced by
            :func:`~analysis.era5.fetch_era5_data.fetch_reference_climatology`.
            Expected to contain a ``t2m`` variable with either a ``month``
            dimension (values 1–12) or a single time step.
        month: Calendar month (1–12).

    Returns:
        ``xr.DataArray`` with spatial dimensions ``(latitude, longitude)``.
    """
    ds = xr.open_dataset(climatology_path)
    if "month" in ds.dims:
        return ds["t2m"].sel(month=month)
    # Single-month file — return as-is
    return ds["t2m"].isel(time=0) if "time" in ds.dims else ds["t2m"]


# ---------------------------------------------------------------------------
# Anomaly calculation
# ---------------------------------------------------------------------------


def calculate_monthly_anomaly(
    ds: xr.Dataset,
    reference_ds: xr.Dataset,
    year: int,
    month: int,
    variable: str = "t2m",
) -> xr.Dataset:
    """Calculate the anomaly for one month against a reference climatology.

    Both datasets must be in the same units (Kelvin *or* Celsius — whatever
    was used consistently; the difference is unit-agnostic).

    Args:
        ds: Current-period dataset containing one month of data.  Must
            include a variable named ``variable`` with spatial dimensions
            ``latitude`` and ``longitude``.
        reference_ds: Climatology dataset.  May have a ``month`` dimension
            (values 1–12) or simply a single spatial slice for the same month.
        year: Calendar year of ``ds`` (used for metadata only).
        month: Calendar month of ``ds`` (1–12).
        variable: Variable name to process (default ``'t2m'``).

    Returns:
        ``xr.Dataset`` with a single variable ``'anomaly'`` and matching
        spatial coordinates.  Global attributes include year, month, and
        reference-period information.
    """
    # Extract current spatial field (squeeze out any size-1 time dimension)
    current = ds[variable]
    if "time" in current.dims:
        current = current.isel(time=0)

    # Extract reference field for this calendar month
    if "month" in reference_ds.dims:
        reference = reference_ds.sel(month=month)
    elif "time" in reference_ds.dims:
        reference = reference_ds.isel(time=0)
    else:
        reference = reference_ds

    if isinstance(reference, xr.Dataset):
        reference = reference[variable]

    # Align grids if they differ (e.g. climatology built on a slightly
    # different lat/lon than the current month's download).
    if reference.shape != current.shape:
        logger.info("Regridding reference climatology to match current grid …")
        reference = reference.interp(
            latitude=current["latitude"],
            longitude=current["longitude"],
            method="linear",
        )

    anomaly_values = current.values - reference.values

    logger.info(
        "Anomaly %d-%02d: min=%.2f, max=%.2f, mean=%.2f°C",
        year,
        month,
        float(np.nanmin(anomaly_values)),
        float(np.nanmax(anomaly_values)),
        float(np.nanmean(anomaly_values)),
    )

    anomaly_da = xr.DataArray(
        anomaly_values,
        dims=["latitude", "longitude"],
        coords={
            "latitude": current["latitude"].values,
            "longitude": current["longitude"].values,
        },
        attrs={
            "units": "°C",
            "long_name": (
                f"Temperature anomaly vs {REFERENCE_PERIOD[0]}–{REFERENCE_PERIOD[1]}"
            ),
        },
    )

    out_ds = xr.Dataset(
        {"anomaly": anomaly_da},
        attrs={
            "year": year,
            "month": month,
            "reference_start": REFERENCE_PERIOD[0],
            "reference_end": REFERENCE_PERIOD[1],
        },
    )
    return out_ds


# ---------------------------------------------------------------------------
# GeoTIFF export
# ---------------------------------------------------------------------------


def export_anomaly_geotiff(
    anomaly_ds: xr.Dataset,
    output_path: Path,
    provider: ClimateDataProvider | None = None,
    bounds: dict | None = None,
) -> Path:
    """Write an anomaly dataset to a GeoTIFF file.

    Args:
        anomaly_ds: Dataset produced by :func:`calculate_monthly_anomaly`,
            containing an ``'anomaly'`` variable with ``latitude`` and
            ``longitude`` coordinates.
        output_path: Destination file path (will be created with parent dirs).
        provider: If given, ``provider.bounds`` is used to set the
            geotransform.  Mutually exclusive with ``bounds``.
        bounds: Explicit ``{'north', 'south', 'east', 'west'}`` dict.
            Used when no provider is supplied.

    Returns:
        Path to the written GeoTIFF.

    Raises:
        ValueError: If neither ``provider`` nor ``bounds`` are supplied and
            the coordinates cannot be inferred automatically.
        ImportError: If ``rasterio`` is not installed.
    """
    import rasterio
    from rasterio.transform import from_bounds as rasterio_from_bounds

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data = anomaly_ds["anomaly"].values.astype(np.float32)
    n_lat, n_lon = data.shape

    # Resolve geographic extent
    if provider is not None:
        bnd = provider.bounds
    elif bounds is not None:
        bnd = bounds
    else:
        # Fall back to coordinate min/max
        lats = anomaly_ds["latitude"].values
        lons = anomaly_ds["longitude"].values
        bnd = {
            "north": float(lats.max()),
            "south": float(lats.min()),
            "west": float(lons.min()),
            "east": float(lons.max()),
        }

    transform = rasterio_from_bounds(
        bnd["west"],
        bnd["south"],
        bnd["east"],
        bnd["north"],
        n_lon,
        n_lat,
    )

    year = anomaly_ds.attrs.get("year", 0)
    month = anomaly_ds.attrs.get("month", 0)
    ref_start = anomaly_ds.attrs.get("reference_start", REFERENCE_PERIOD[0])
    ref_end = anomaly_ds.attrs.get("reference_end", REFERENCE_PERIOD[1])

    with rasterio.open(
        output_path,
        "w",
        driver="GTiff",
        height=n_lat,
        width=n_lon,
        count=1,
        dtype=np.float32,
        crs="EPSG:4326",
        transform=transform,
        nodata=np.nan,
    ) as dst:
        dst.write(data, 1)
        dst.update_tags(
            year=str(year),
            month=str(month),
            reference_period=f"{ref_start}-{ref_end}",
            units="°C",
            colormap_vmin=str(ANOMALY_COLORMAP["vmin"]),
            colormap_vmax=str(ANOMALY_COLORMAP["vmax"]),
        )

    logger.info("Saved anomaly GeoTIFF: %s", output_path)
    return output_path


# ---------------------------------------------------------------------------
# Combined pipeline step
# ---------------------------------------------------------------------------


def calculate_monthly_anomaly_from_files(
    provider: ClimateDataProvider,
    current_path: Path,
    year: int,
    month: int,
    output_dir: Path,
    climatology_path: Path | None = None,
    variable: str = "t2m",
) -> Path:
    """Full anomaly pipeline step: load → compute → export GeoTIFF + NetCDF.

    Args:
        provider: Active climate data provider.
        current_path: Path to the masked (or raw) current-month NetCDF.
        year: Year of the current month.
        month: Calendar month (1–12).
        output_dir: Directory for output files.
        climatology_path: Path to pre-computed climatology.  If ``None``,
            looks for ``../reference/climatology_{variable}_1961_1990.nc``
            relative to ``output_dir``.
        variable: Variable name (default ``'t2m'``).

    Returns:
        Path to the anomaly GeoTIFF.

    Raises:
        FileNotFoundError: If the climatology file cannot be located.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if climatology_path is None:
        climatology_path = (
            output_dir.parent
            / "reference"
            / f"climatology_{variable}_{REFERENCE_PERIOD[0]}_{REFERENCE_PERIOD[1]}.nc"
        )

    if not Path(climatology_path).exists():
        raise FileNotFoundError(
            f"Climatology not found: {climatology_path}.  "
            "Run fetch_reference_climatology() first."
        )

    ref_start = REFERENCE_PERIOD[0]
    ref_end = REFERENCE_PERIOD[1]

    ds_current = xr.open_dataset(current_path)
    ds_clim = xr.open_dataset(climatology_path)

    anomaly_ds = calculate_monthly_anomaly(ds_current, ds_clim, year, month, variable)

    tiff_path = output_dir / f"anomaly_{year}{month:02d}.tif"
    export_anomaly_geotiff(anomaly_ds, tiff_path, provider=provider)

    nc_path = output_dir / f"anomaly_{year}{month:02d}.nc"
    anomaly_ds.to_netcdf(nc_path)
    logger.info("Saved anomaly NetCDF: %s", nc_path)

    return tiff_path
