#!/usr/bin/env python3
"""
Export metrics to JSON format for frontend consumption.

Outputs conform to the LocationMetrics schema defined in types.py.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict

from .types import LocationMetrics, MetricsFile

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def export_metrics_json(
    metrics: LocationMetrics,
    output_path: Path,
    provider,
) -> Path:
    """Export metrics to JSON file.
    
    Args:
        metrics: LocationMetrics dictionary
        output_path: Path for output JSON file
        provider: Climate data provider for source, bounds, resolution
        
    Returns:
        Path to created JSON file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Build complete file structure
    metrics_file: MetricsFile = {
        'version': '1.0',
        'generatedAt': datetime.utcnow().isoformat() + 'Z',
        'source': provider.dataset_id,
        'coverage': {
            'bounds': dict(provider.bounds),
            'gridResolution': f'{provider.native_resolution_deg}deg',
        },
        'data': metrics,
    }
    
    # Write JSON with nice formatting
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(metrics_file, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Exported metrics to {output_path}")
    return output_path


def export_all_tile_metrics(
    tile_metrics: Dict[str, LocationMetrics],
    output_dir: Path,
    provider,
) -> Dict[str, Path]:
    """Export metrics for all tiles (grid cells).
    
    Args:
        tile_metrics: Dictionary mapping tile_id (grid_i_grid_j) to metrics
        output_dir: Directory for output files
        provider: Climate data provider for metadata
        
    Returns:
        Dictionary mapping tile_id to output path
    """
    output_dir = Path(output_dir) / 'tiles'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    paths = {}
    
    for tile_id, metrics in tile_metrics.items():
        # tile_id format: "{grid_i}_{grid_j}"
        output_path = output_dir / f"{tile_id}.json"
        paths[tile_id] = export_metrics_json(metrics, output_path, provider=provider)
    
    logger.info(f"Exported metrics for {len(paths)} tiles to {output_dir}")
    return paths


def export_germany_metrics(
    metrics: LocationMetrics,
    output_dir: Path,
    provider,
) -> Path:
    """Export country-level metrics for Germany.
    
    Args:
        metrics: Germany-aggregated LocationMetrics
        output_dir: Output directory
        provider: Climate data provider for metadata
        
    Returns:
        Path to germany.json
    """
    output_path = Path(output_dir) / 'germany.json'
    return export_metrics_json(metrics, output_path, provider=provider)


def validate_metrics_schema(data: dict) -> bool:
    """Validate that metrics dictionary conforms to schema.
    
    Args:
        data: Metrics dictionary to validate
        
    Returns:
        True if valid
        
    Raises:
        ValueError: If schema validation fails
    """
    required_keys = [
        'fiveYearAnomaly',
        'warmingRate',
        'recordDays',
        'winterWarming',
        'seasonalWarming',
        'thresholdDays',
        'snowDaysLost',
        'comfortableDays',
    ]
    
    for key in required_keys:
        if key not in data:
            raise ValueError(f"Missing required key: {key}")
    
    # Validate nested structures
    if 'value' not in data['fiveYearAnomaly']:
        raise ValueError("fiveYearAnomaly missing 'value'")
    if 'confidence' not in data['warmingRate']:
        raise ValueError("warmingRate missing 'confidence'")
    
    return True


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Export metrics to JSON')
    parser.add_argument('--output-dir', default='./data/metrics', help='Output directory')
    args = parser.parse_args()
    
    # Example: Create sample metrics
    sample_metrics: LocationMetrics = {
        'calculatedAt': datetime.utcnow().isoformat() + 'Z',
        'fiveYearAnomaly': {
            'value': 2.3,
            'periodStart': 2021,
            'periodEnd': 2025,
            'referenceStart': 1961,
            'referenceEnd': 1990,
        },
        'warmingRate': {
            'value': 0.45,
            'startYear': 1995,
            'endYear': 2025,
            'confidence': 0.85,
        },
        'recordDays': {
            'total': 18,
            'hot': 16,
            'cold': 2,
            'year': 2025,
        },
        'winterWarming': {
            'value': 2.8,
            'periodStart': 2021,
            'periodEnd': 2025,
            'referenceStart': 1961,
            'referenceEnd': 1990,
        },
        'seasonalWarming': {
            'winter': 2.8,
            'spring': 2.1,
            'summer': 1.9,
            'fall': 2.4,
            'fastestSeason': 'winter',
            'periodStart': 2021,
            'periodEnd': 2025,
            'referenceStart': 1961,
            'referenceEnd': 1990,
        },
        'thresholdDays': {
            'hotDays': 15,
            'tropicalNights': 8,
            'iceDays': 4,
            'frostDays': 52,
            'year': 2025,
        },
        'snowDaysLost': {
            'value': -18,
            'currentAverage': 12.0,
            'referenceAverage': 30.0,
            'periodStart': 2021,
            'periodEnd': 2025,
        },
        'comfortableDays': {
            'count': 95,
            'average': 93.0,
        },
    }
    
    print("Sample metrics structure created successfully")
    print(f"Keys: {list(sample_metrics.keys())}")
