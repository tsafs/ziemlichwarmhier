#!/usr/bin/env python3
# /home/sebastian/Projects/ziemlichwarmhier/playground/calculate_rolling_averages.py

import os
import re
import argparse
import pandas as pd
from pathlib import Path


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Calculate rolling averages for climate data.')
    parser.add_argument('--data-dir', type=str, default='data',
                        help='Directory containing the CSV files')
    parser.add_argument('--from-year', type=int, required=True,
                        help='Start year for the output data')
    parser.add_argument('--to-year', type=int, required=True,
                        help='End year for the output data')
    parser.add_argument('--rolling-window', type=int, default=7,
                        help='Rolling window size in days (before and after)')
    parser.add_argument('--output-dir', type=str, default='output',
                        help='Directory for the output files')
    return parser.parse_args()


def process_file(file_path, from_year, to_year, rolling_window, output_dir):
    """Process a single CSV file and create rolling averages."""
    print(f"Processing {file_path.name}...")
    
    # Extract city-id from filename
    match = re.match(r'([0-9]+)_([0-9]+)_(.+)\.csv', file_path.name)
    if not match:
        print(f"Skipping {file_path.name}: doesn't match expected naming pattern")
        return
    
    grid_x = match.group(1)
    grid_y = match.group(2)
    city_id = match.group(3)
    
    # Read the CSV file
    df = pd.read_csv(file_path)
    
    # Ensure the date column is in datetime format
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    else:
        print(f"Skipping {file_path.name}: no date column found")
        return
    
    # Sort by date to ensure proper sequence for rolling calculations
    df = df.sort_values('date')
    
    # Get all metrics (all columns except date)
    metrics = [col for col in df.columns if col != 'date']
    
    # Step 1: Calculate rolling averages using all available data
    result_df = df.copy()
    window_size = 2 * rolling_window + 1  # window includes current day plus days before and after
    
    for metric in metrics:
        result_df[metric] = df[metric].rolling(window=window_size, center=True, min_periods=1).mean()
        # Round to 2 decimal places
        result_df[metric] = result_df[metric].round(2)
    
    # Step 2: Now filter to only include the specified year range in the output
    result_df = result_df[(result_df['date'].dt.year >= from_year) & 
                         (result_df['date'].dt.year <= to_year)]
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Name the output file with the same pattern but indicating rolling average
    output_filename = f"avg_{rolling_window}d_{grid_x}_{grid_y}_{city_id}_{from_year}-{to_year}.csv"
    output_path = os.path.join(output_dir, output_filename)
    
    # Save the result
    result_df.to_csv(output_path, index=False)
    print(f"Created {output_path}")


def main():
    """Main function to process all CSV files."""
    args = parse_arguments()
    
    data_dir = Path(args.data_dir)
    output_dir = Path(args.output_dir)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all CSV files matching the pattern
    file_pattern = re.compile(r'.+_.+_.+\.csv$')
    csv_files = [f for f in data_dir.glob('*.csv') if file_pattern.match(f.name)]
    
    if not csv_files:
        print(f"No CSV files matching the pattern found in {data_dir}")
        return
    
    print(f"Found {len(csv_files)} files to process")
    
    # Process each file
    for file_path in csv_files:
        process_file(
            file_path, 
            args.from_year, 
            args.to_year, 
            args.rolling_window, 
            output_dir
        )
    
    print("Processing complete!")


if __name__ == "__main__":
    main()