import os
import requests
import zipfile
from io import BytesIO

# Directory to store the unzipped files
OUTPUT_DIR = "./data"

# Base URL for the DWD data
BASE_URL = "https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/daily/kl/historical/"

# Metadata file URL
METADATA_URL = f"{BASE_URL}KL_Tageswerte_Beschreibung_Stationen.txt"

# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def download_and_extract_zip(url, output_dir):
    """Download and extract a zip file from the given URL."""
    response = requests.get(url)
    if response.status_code == 200:
        zip_name = url.split("/")[-1].replace(".zip", "")
        zip_output_dir = os.path.join(output_dir, zip_name)
        os.makedirs(zip_output_dir, exist_ok=True)
        with zipfile.ZipFile(BytesIO(response.content)) as z:
            z.extractall(zip_output_dir)
            print(f"Extracted: {url} into {zip_output_dir}")
    else:
        print(f"Failed to download: {url}")

def fetch_metadata(url, output_dir):
    """Download the metadata file."""
    response = requests.get(url)
    if response.status_code == 200:
        metadata_path = os.path.join(output_dir, "KL_Tageswerte_Beschreibung_Stationen.txt")
        with open(metadata_path, "wb") as f:
            f.write(response.content)
        print(f"Metadata downloaded: {metadata_path}")
    else:
        print(f"Failed to download metadata: {url}")

def main():
    # Fetch metadata file
    fetch_metadata(METADATA_URL, OUTPUT_DIR)

    # Fetch all zip files
    response = requests.get(BASE_URL)
    if response.status_code == 200:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")
        for link in soup.find_all("a"):
            href = link.get("href")
            if href and href.endswith(".zip"):
                zip_url = f"{BASE_URL}{href}"
                download_and_extract_zip(zip_url, OUTPUT_DIR)
    else:
        print(f"Failed to fetch the list of zip files: {BASE_URL}")

if __name__ == "__main__":
    main()