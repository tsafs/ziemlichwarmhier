#!/usr/bin/env python3
"""
Calculate decadal aggregate metrics for narrative plotting.

Produces per-decade summaries consumed by Phase 9 narrative plots.
Each decade is summarized as a single JSON file: {grid_i}_{grid_j}_decadal.json
"""

import json
import logging
from pathlib import Path
from typing import Dict, List

import numpy as np
import xarray as xr

from .config import DECADES, REFERENCE_PERIOD, SEASONS, THRESHOLDS

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def calculate_decadal_mean_temp(
    ds: xr.Dataset,
    variable: str,
    decade: tuple,
) -> float:
    """Calculate mean temperature for a decade.
    
    Args:
        ds: Dataset with temperature data
        variable: Temperature variable name
        decade: Tuple of (start_year, end_year)
        
    Returns:
        Mean temperature for the decade
    """
    start, end = decade
    mask = (ds['time'].dt.year >= start) & (ds['time'].dt.year <= end)
    decade_data = ds[variable].where(mask, drop=True)
    
    if len(decade_data['time']) == 0:
        return float('nan')
    
    return float(decade_data.mean().values)


def calculate_decadal_hot_days(
    ds: xr.Dataset,
    tmax_var: str,
    decade: tuple,
) -> float:
    """Calculate average annual hot days per decade.
    
    Args:
        ds: Dataset with Tmax data
        tmax_var: Daily maximum temperature variable
        decade: Tuple of (start_year, end_year)
        
    Returns:
        Average annual hot day count for the decade
    """
    start, end = decade
    mask = (ds['time'].dt.year >= start) & (ds['time'].dt.year <= end)
    decade_tmax = ds[tmax_var].where(mask, drop=True)
    
    if len(decade_tmax['time']) == 0:
        return float('nan')
    
    # Spatial mean
    spatial_dims = [d for d in decade_tmax.dims if d not in ['time']]
    if spatial_dims:
        tmax_mean = decade_tmax.mean(dim=spatial_dims)
    else:
        tmax_mean = decade_tmax
    
    hot_days_per_year = (tmax_mean >= THRESHOLDS['hot_day']).resample(time='YE').sum()
    
    return float(hot_days_per_year.mean().values)


def calculate_decadal_aggregates(
    ds: xr.Dataset,
    temp_var: str = 't2m',
    tmax_var: str = 'tmax',
) -> List[Dict]:
    """Calculate aggregate metrics for all decades.
    
    Args:
        ds: Dataset with temperature data
        temp_var: Mean temperature variable
        tmax_var: Maximum temperature variable (for hot days)
        
    Returns:
        List of decade aggregate dictionaries
    """
    aggregates = []
    
    # Reference mean for anomaly calculation
    ref_mask = (
        (ds['time'].dt.year >= REFERENCE_PERIOD['start_year']) &
        (ds['time'].dt.year <= REFERENCE_PERIOD['end_year'])
    )
    ref_data = ds[temp_var].where(ref_mask, drop=True)
    
    if len(ref_data['time']) == 0:
        logger.warning("No reference period data for anomaly calculation")
        reference_mean = float('nan')
    else:
        reference_mean = float(ref_data.mean().values)
    
    for start, end in DECADES:
        decade_mean = calculate_decadal_mean_temp(ds, temp_var, (start, end))
        
        # Anomaly vs reference
        if not np.isnan(decade_mean) and not np.isnan(reference_mean):
            anomaly = round(decade_mean - reference_mean, 2)
        else:
            anomaly = None
        
        # Hot days (if tmax available)
        hot_days = None
        if tmax_var in ds:
            hot_days_raw = calculate_decadal_hot_days(ds, tmax_var, (start, end))
            if not np.isnan(hot_days_raw):
                hot_days = round(hot_days_raw, 1)
        
        decade_label = f"{start}s" if end - start == 9 else f"{start}-{end}"
        
        aggregate = {
            'decade': decade_label,
            'startYear': start,
            'endYear': end,
            'meanTemp': round(decade_mean, 2) if not np.isnan(decade_mean) else None,
            'anomaly': anomaly,
            'hotDays': hot_days,
        }
        
        aggregates.append(aggregate)
        logger.info(f"Decade {decade_label}: mean={aggregate['meanTemp']}, anomaly={anomaly}")
    
    return aggregates


def export_decadal_aggregates(
    aggregates: List[Dict],
    output_path: Path,
) -> Path:
    """Export decadal aggregates to JSON.
    
    Args:
        aggregates: List of decade aggregate dictionaries
        output_path: Path for output file (e.g., {grid_i}_{grid_j}_decadal.json)
        
    Returns:
        Path to created JSON file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(aggregates, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Exported decadal aggregates to {output_path}")
    return output_path


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Calculate decadal aggregates')
    parser.add_argument('input_file', help='Input NetCDF file')
    parser.add_argument('--output-dir', default='./data/metrics/decadal')
    parser.add_argument('--variable', default='t2m')
    parser.add_argument('--grid-i', type=int, default=0)
    parser.add_argument('--grid-j', type=int, default=0)
    args = parser.parse_args()
    
    ds = xr.open_dataset(args.input_file)
    aggregates = calculate_decadal_aggregates(ds, args.variable)
    
    output_path = Path(args.output_dir) / f"{args.grid_i}_{args.grid_j}_decadal.json"
    export_decadal_aggregates(aggregates, output_path)
    
    print(f"\nDecadal Aggregates ({len(aggregates)} decades):")
    for agg in aggregates:
        print(f"  {agg['decade']}: mean={agg['meanTemp']}, anomaly={agg['anomaly']}")
