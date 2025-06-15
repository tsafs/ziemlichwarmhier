import argparse
import xarray as xr
import pandas as pd
import numpy as np
import json
from pathlib import Path
import re
import glob

def load_cities(cities_file):
    # Expects a JSON or CSV with columns: name, lat, lon
    if cities_file.endswith('.json'):
        with open(cities_file, 'r') as f:
            return json.load(f)
    else:
        return pd.read_csv(cities_file).to_dict(orient='records')

def calculate_grid_centers(lat_arr, lon_arr):
    """
    Calculate the center points of each grid cell.
    
    Args:
        lat_arr, lon_arr: 2D arrays representing the grid of latitudes and longitudes at corners
    
    Returns:
        tuple (centers_lat, centers_lon) containing the center points
    """
    max_y, max_x = lat_arr.shape
    centers_lat = np.zeros((max_y - 1, max_x - 1))
    centers_lon = np.zeros((max_y - 1, max_x - 1))
    
    # Calculate centers of grid cells
    for y in range(max_y - 1):
        for x in range(max_x - 1):
            # For each cell, average the four corners to get the center
            centers_lat[y, x] = (lat_arr[y, x] + lat_arr[y+1, x] + 
                                lat_arr[y, x+1] + lat_arr[y+1, x+1]) / 4
            centers_lon[y, x] = (lon_arr[y, x] + lon_arr[y+1, x] + 
                                lon_arr[y, x+1] + lon_arr[y+1, x+1]) / 4
    
    return centers_lat, centers_lon

def find_nearest_grid_point(centers_lat, centers_lon, lat, lon):
    """
    Find the nearest grid cell to the given coordinates.
    
    Args:
        centers_lat, centers_lon: 2D arrays of grid cell centers
        lat, lon: Target coordinates to find the nearest cell for
    
    Returns:
        tuple (y, x) indices of the closest grid cell
    """
    # Calculate distances to each grid cell center
    dist = np.sqrt((centers_lat - lat)**2 + (centers_lon - lon)**2)
    
    # Find the indices of the minimum distance
    y, x = np.unravel_index(np.argmin(dist), dist.shape)
    
    # Return the indices of the closest grid cell
    return y, x

def get_grid_cell_bounds(lat_arr, lon_arr, grid_y, grid_x):
    """Get the corner coordinates (bounds) of a grid cell"""
    max_y, max_x = lat_arr.shape
    
    # Handle the case where the cell is at the edge of the grid
    if grid_y == max_y - 1:  # Last row
        grid_lat1 = lat_arr[grid_y, grid_x]
        # Estimate grid_lat2 by extrapolation
        if grid_y > 0:
            lat_diff = lat_arr[grid_y, grid_x] - lat_arr[grid_y - 1, grid_x]
            grid_lat2 = lat_arr[grid_y, grid_x] + lat_diff
        else:
            grid_lat2 = lat_arr[grid_y, grid_x]  # Fallback
    else:
        grid_lat1 = lat_arr[grid_y, grid_x]
        grid_lat2 = lat_arr[grid_y + 1, grid_x]
    
    if grid_x == max_x - 1:  # Last column
        grid_lon1 = lon_arr[grid_y, grid_x]
        # Estimate grid_lon2 by extrapolation
        if grid_x > 0:
            lon_diff = lon_arr[grid_y, grid_x] - lon_arr[grid_y, grid_x - 1]
            grid_lon2 = lon_arr[grid_y, grid_x] + lon_diff
        else:
            grid_lon2 = lon_arr[grid_y, grid_x]  # Fallback
    else:
        grid_lon1 = lon_arr[grid_y, grid_x]
        grid_lon2 = lon_arr[grid_y, grid_x + 1]
    
    return grid_lat1, grid_lon1, grid_lat2, grid_lon2

def extract_city_timeseries(ds, city, params, centers_lat, centers_lon):
    # Use the pre-calculated centers instead of recalculating them
    grid_y, grid_x = find_nearest_grid_point(centers_lat, centers_lon, city['lat'], city['lon'])
    result = {'city': city['name']}
    
    # Handle multiple parameters
    for param in params:
        if param in ds:
            # Extract the parameter values at the specified grid point
            param_data = ds[param].isel(y=grid_y, x=grid_x)
            
            # Store the values, ensuring they align with the time dimension
            result[param] = param_data.values
            result['time'] = param_data.time.values
    
    return result, grid_y, grid_x

def generate_city_id(city_name):
    """Generate a unique ID for a city based on its name"""
    # Convert to lowercase, remove special characters, replace spaces with underscores
    city_id = city_name.lower()
    city_id = re.sub(r'[^a-z0-9\s]', '', city_id)
    city_id = re.sub(r'\s+', '_', city_id)
    return city_id

def parse_file_patterns(file_patterns):
    """Parse file patterns with year ranges and expand them"""
    expanded_files = []
    
    for pattern in file_patterns:
        # Check if pattern contains year range like {1961-1965}
        year_range_match = re.search(r'\{(\d+)-(\d+)\}', pattern)
        if year_range_match:
            start_year = int(year_range_match.group(1))
            end_year = int(year_range_match.group(2))
            
            # Replace the range with each year and add to list
            for year in range(start_year, end_year + 1):
                year_file = pattern.replace(year_range_match.group(0), str(year))
                matching_files = glob.glob(year_file)
                expanded_files.extend(matching_files)
        else:
            # If no range pattern, use glob to find matching files
            matching_files = glob.glob(pattern)
            expanded_files.extend(matching_files)
    
    return expanded_files

def main():
    parser = argparse.ArgumentParser(description="Extract daily temperatures for cities from NetCDF")
    parser.add_argument('--file', action='append', required=True, 
                        help='NetCDF file path(s). Can use patterns like "tasmax_hyras_5_{1961-1965}_v5-0_de.nc"')
    parser.add_argument('--cities', required=True, help='CSV or JSON file with columns: name, lat, lon')
    parser.add_argument('--param', action='append', required=True, 
                        help='Variable name(s) for climate parameters (e.g., tasmax, tasmin). Can be specified multiple times.')
    parser.add_argument('--output-dir', default='.', help='Output directory for CSV files')
    parser.add_argument('--cities-metadata', default='cities_metadata.csv', help='Output file for cities metadata')
    args = parser.parse_args()

    # Parse and expand file patterns
    input_files = parse_file_patterns(args.file)
    if not input_files:
        print("Error: No matching input files found.")
        return
    
    print(f"Processing {len(input_files)} input files...")
    
    # Create output directory if it doesn't exist
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load cities and assign IDs
    cities = load_cities(args.cities)
    for i, city in enumerate(cities):
        city['id'] = generate_city_id(city['name'])
    
    # Save cities metadata file
    cities_df = pd.DataFrame([{
        'city_id': city['id'],
        'city_name': city['name'],
        'city_lat': city['lat'],
        'city_lon': city['lon'],
        'grid_y': None,  # Will update after processing first file
        'grid_x': None,
        'grid_lat1': None,  # Grid cell lower bound for latitude
        'grid_lon1': None,  # Grid cell lower bound for longitude
        'grid_lat2': None,  # Grid cell upper bound for latitude
        'grid_lon2': None,  # Grid cell upper bound for longitude
    } for city in cities])
    
    # Initialize city data dictionaries - change to use a nested dict with dates as keys
    city_data_dict = {city['id']: {} for city in cities}
    
    # Process each input file
    params = args.param  # List of parameters to extract
    
    # Store grid bounds for each city
    grid_bounds = {}
    
    for file_path in input_files:
        print(f"Processing {file_path}...")
        try:
            ds = xr.open_dataset(file_path)
            
            # Check which parameters are in this file
            available_params = [param for param in params if param in ds]
            if not available_params:
                print(f"Warning: None of the specified parameters {params} found in {file_path}. Skipping this file.")
                continue
            
            # Get lat and lon arrays for bounds calculation
            lat_arr = ds['lat'].values
            lon_arr = ds['lon'].values
            
            # Calculate grid centers once for all cities
            centers_lat, centers_lon = calculate_grid_centers(lat_arr, lon_arr)
                
            for city in cities:
                city_data, grid_y, grid_x = extract_city_timeseries(ds, city, params, centers_lat, centers_lon)
                
                # Update the grid indices in cities metadata (from first file)
                if cities_df.loc[cities_df['city_id'] == city['id'], 'grid_y'].iloc[0] is None:
                    cities_df.loc[cities_df['city_id'] == city['id'], 'grid_y'] = grid_y
                    cities_df.loc[cities_df['city_id'] == city['id'], 'grid_x'] = grid_x
                    
                    # Calculate and store grid cell bounds
                    if city['id'] not in grid_bounds:
                        grid_lat1, grid_lon1, grid_lat2, grid_lon2 = get_grid_cell_bounds(lat_arr, lon_arr, grid_y, grid_x)
                        grid_bounds[city['id']] = {
                            'grid_lat1': grid_lat1,
                            'grid_lon1': grid_lon1,
                            'grid_lat2': grid_lat2,
                            'grid_lon2': grid_lon2
                        }
                # Add data for this city
                for i, date in enumerate(city_data["time"]):
                    date_str = pd.to_datetime(date).strftime('%Y-%m-%d')
                    
                    # Create entry for this date if it doesn't exist
                    if date_str not in city_data_dict[city['id']]:
                        city_data_dict[city['id']][date_str] = {'date': date_str}
                    
                    # Add each available parameter to the existing entry
                    for param in params:
                        if param in city_data and i < len(city_data[param]):
                            city_data_dict[city['id']][date_str][param] = city_data[param][i]
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    # Update cities DataFrame with grid bounds
    for city_id, bounds in grid_bounds.items():
        for bound_name, bound_val in bounds.items():
            cities_df.loc[cities_df['city_id'] == city_id, bound_name] = bound_val
    
    # Save cities metadata
    cities_metadata_path = output_dir / args.cities_metadata
    cities_df.to_csv(cities_metadata_path, index=False)
    print(f"Saved cities metadata: {cities_metadata_path}")
    
    # Save individual city files - convert dict of dicts to list for DataFrame
    for city in cities:
        city_id = city['id']
        grid_y = int(cities_df.loc[cities_df['city_id'] == city_id, 'grid_y'].iloc[0])
        grid_x = int(cities_df.loc[cities_df['city_id'] == city_id, 'grid_x'].iloc[0])
        
        # Convert dictionary to list for DataFrame creation
        city_data_list = list(city_data_dict[city_id].values())
        city_df = pd.DataFrame(city_data_list)
        
        if not city_df.empty:  # Only create file if we have data
            # Sort by date
            if 'date' in city_df.columns:
                city_df['date'] = pd.to_datetime(city_df['date'])
                city_df = city_df.sort_values('date')
                city_df['date'] = city_df['date'].dt.strftime('%Y-%m-%d')
            
            city_file_path = output_dir / f"{grid_y}_{grid_x}_{city_id}.csv"
            city_df.to_csv(city_file_path, index=False)
            print(f"Saved: {city_file_path}")

if __name__ == "__main__":
    main()
