import os
import requests
import argparse
from datetime import datetime
from bs4 import BeautifulSoup

# Directory to store the NetCDF files
OUTPUT_DIR = "./data/netcdf"

# Base URL for the DWD NetCDF data
BASE_URL = "https://opendata.dwd.de/climate_environment/CDC/grids_germany/daily/hyras_de/"

# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def download_netcdf_file(url, output_dir):
    """Download a NetCDF file from the given URL."""
    filename = url.split("/")[-1]
    output_path = os.path.join(output_dir, filename)
    
    # Skip if file already exists
    if os.path.exists(output_path):
        print(f"File already exists: {output_path}")
        return
    
    response = requests.get(url)
    if response.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"Downloaded: {url} to {output_path}")
    else:
        print(f"Failed to download: {url}")

def fetch_netcdf_files(dataset=None, start_year=None, end_year=None, resolution=None):
    """Fetch NetCDF files for the specified year range and resolution."""        
    print(f"Fetching '{dataset}' NetCDF files from year {start_year} to {end_year} with resolution '{resolution}'")
    
    base_url = f"{BASE_URL}/{dataset}/"

    # Fetch the directory listing
    response = requests.get(base_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        
        for link in soup.find_all("a"):
            href = link.get("href")
            if href and href.endswith(".nc"):
                # Extract the year from the filename (format: tasmax_hyras_1_1970_v6-0_de.nc)
                try:
                    file_parts = href.split("_")
                    if len(file_parts) >= 4:
                        file_year = int(file_parts[3])
                        file_resolution = file_parts[2]
                        
                        # Check if the file is within the requested year range and matches resolution (if specified)
                        if start_year <= file_year <= end_year and (resolution is None or file_resolution == resolution):
                            file_url = f"{base_url}{href}"
                            download_netcdf_file(file_url, OUTPUT_DIR)
                except (ValueError, IndexError) as e:
                    print(f"Error parsing filename {href}: {e}")
    else:
        print(f"Failed to fetch the list of files: {base_url}")

def main():
    # Set up command line arguments
    parser = argparse.ArgumentParser(description="Download NetCDF files from DWD")
    parser.add_argument("--dataset", required=True, type=str, help="Dataset to download (air_temperature_max, air_temperature_min, air_temperature_mean, humidity, precipitation, radiation_global)")
    parser.add_argument("--start-year", required=True, type=int, help="Start year for data download")
    parser.add_argument("--end-year", required=True, type=int, help="End year for data download")
    parser.add_argument("--resolution", required=True, type=str, help="Resolution of the data (e.g., '1' for 1km resolution)")
    
    args = parser.parse_args()
    
    # Download files based on specified year range and resolution
    fetch_netcdf_files(args.dataset, args.start_year, args.end_year, args.resolution)

if __name__ == "__main__":
    main()
