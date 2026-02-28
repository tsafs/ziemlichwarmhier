#!/usr/bin/env python3
"""
Aggregate grid-level metrics to city and country level.

Provides functions to map city coordinates to nearest grid cells
and aggregate metrics spatially.
"""

import logging
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import xarray as xr

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_city_list(csv_path: Path) -> pd.DataFrame:
    """Load city list from CSV.
    
    Expected columns: name, latitude, longitude, population
    
    Args:
        csv_path: Path to city CSV file
        
    Returns:
        DataFrame with city information
    """
    df = pd.read_csv(csv_path)
    
    # Ensure required columns
    required = ['name', 'latitude', 'longitude']
    for col in required:
        if col not in df.columns:
            # Try common alternatives
            alternatives = {
                'name': ['city', 'city_name', 'NAME'],
                'latitude': ['lat', 'LAT'],
                'longitude': ['lon', 'lng', 'LON'],
            }
            for alt in alternatives.get(col, []):
                if alt in df.columns:
                    df = df.rename(columns={alt: col})
                    break
    
    logger.info(f"Loaded {len(df)} cities from {csv_path}")
    return df


def find_nearest_grid_cell(
    lat: float,
    lon: float,
    grid_lats: np.ndarray,
    grid_lons: np.ndarray,
) -> Tuple[int, int]:
    """Find nearest grid cell for a coordinate.
    
    Args:
        lat, lon: Target coordinates
        grid_lats: Array of grid latitudes
        grid_lons: Array of grid longitudes
        
    Returns:
        Tuple of (lat_index, lon_index)
    """
    lat_idx = np.argmin(np.abs(grid_lats - lat))
    lon_idx = np.argmin(np.abs(grid_lons - lon))
    return int(lat_idx), int(lon_idx)


def aggregate_to_cities(
    grid_data: xr.DataArray,
    cities: pd.DataFrame,
) -> Dict[str, float]:
    """Aggregate grid data to city locations.
    
    Uses nearest-neighbor interpolation.
    
    Args:
        grid_data: DataArray with dims (latitude, longitude)
        cities: DataFrame with city coordinates
        
    Returns:
        Dictionary mapping city name to value
    """
    grid_lats = grid_data['latitude'].values
    grid_lons = grid_data['longitude'].values
    data = grid_data.values
    
    results = {}
    
    for _, city in cities.iterrows():
        lat_idx, lon_idx = find_nearest_grid_cell(
            city['latitude'], city['longitude'],
            grid_lats, grid_lons
        )
        
        value = float(data[lat_idx, lon_idx])
        
        if not np.isnan(value):
            results[city['name']] = round(value, 2)
        else:
            logger.warning(f"No data for city {city['name']}")
    
    return results


def aggregate_to_country(
    grid_data: xr.DataArray,
    weights: xr.DataArray = None,
) -> float:
    """Aggregate grid data to country-level single value.
    
    Args:
        grid_data: DataArray with dims (latitude, longitude)
        weights: Optional area weights for proper averaging
        
    Returns:
        Weighted mean value
    """
    data = grid_data.values
    
    if weights is not None:
        # Weighted average
        weight_data = weights.values
        valid_mask = ~np.isnan(data) & ~np.isnan(weight_data)
        weighted_mean = np.average(data[valid_mask], weights=weight_data[valid_mask])
    else:
        # Simple mean
        weighted_mean = np.nanmean(data)
    
    return float(round(weighted_mean, 2))


def create_area_weights(
    lats: np.ndarray,
    lons: np.ndarray,
) -> xr.DataArray:
    """Create area weights based on latitude (cos weighting).
    
    Grid cells at higher latitudes represent smaller areas.
    
    Args:
        lats: Latitude array
        lons: Longitude array
        
    Returns:
        DataArray with area weights
    """
    # Cosine of latitude for area correction
    weights = np.cos(np.radians(lats))
    
    # Broadcast to 2D
    weights_2d = np.broadcast_to(weights[:, np.newaxis], (len(lats), len(lons)))
    
    return xr.DataArray(
        weights_2d.copy(),
        dims=['latitude', 'longitude'],
        coords={'latitude': lats, 'longitude': lons},
    )


def correlate_cities_to_grid(
    cities: pd.DataFrame,
    grid_lats: np.ndarray,
    grid_lons: np.ndarray,
) -> pd.DataFrame:
    """Map all cities to their nearest grid cells.
    
    Adds 'grid_lat_idx', 'grid_lon_idx', 'grid_lat', 'grid_lon' columns.
    
    Args:
        cities: DataFrame with city coordinates
        grid_lats: Array of grid latitudes
        grid_lons: Array of grid longitudes
        
    Returns:
        DataFrame with grid mapping columns added
    """
    cities = cities.copy()
    
    lat_idxs = []
    lon_idxs = []
    grid_lats_mapped = []
    grid_lons_mapped = []
    
    for _, city in cities.iterrows():
        lat_idx, lon_idx = find_nearest_grid_cell(
            city['latitude'], city['longitude'],
            grid_lats, grid_lons
        )
        lat_idxs.append(lat_idx)
        lon_idxs.append(lon_idx)
        grid_lats_mapped.append(grid_lats[lat_idx])
        grid_lons_mapped.append(grid_lons[lon_idx])
    
    cities['grid_lat_idx'] = lat_idxs
    cities['grid_lon_idx'] = lon_idxs
    cities['grid_lat'] = grid_lats_mapped
    cities['grid_lon'] = grid_lons_mapped
    
    return cities


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Aggregate metrics to cities')
    parser.add_argument('grid_file', help='NetCDF with grid data')
    parser.add_argument('--cities', default='frontend/public/german_cities_p5000.csv',
                        help='Path to city CSV')
    parser.add_argument('--variable', default='anomaly', help='Variable to aggregate')
    args = parser.parse_args()
    
    ds = xr.open_dataset(args.grid_file)
    cities = load_city_list(Path(args.cities))
    
    results = aggregate_to_cities(ds[args.variable], cities)
    
    print(f"\nCity values ({args.variable}):")
    for city, value in sorted(results.items())[:10]:
        print(f"  {city}: {value}")
