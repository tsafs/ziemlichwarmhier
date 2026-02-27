FROM python:3.13-slim

WORKDIR /app

# Copy analysis modules
COPY analysis/__init__.py ./analysis/__init__.py
COPY analysis/era5/ ./analysis/era5/
COPY analysis/tiles/ ./analysis/tiles/

# Copy job source
COPY jobs/job-era5-monthly/src ./src/
COPY jobs/job-era5-monthly/entrypoint.sh /app/

# Install Python dependencies
RUN pip install --no-cache-dir \
    cdsapi \
    xarray \
    rasterio \
    rioxarray \
    geopandas \
    shapely \
    numpy \
    boto3 \
    tqdm \
    rio-tiler \
    mercantile \
    pillow \
    matplotlib \
    requests

# Create output directories
RUN mkdir -p /app/data /app/output

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

# Set PYTHONPATH so `from analysis.era5...` imports work
ENV PYTHONPATH=/app

CMD ["/app/entrypoint.sh"]
