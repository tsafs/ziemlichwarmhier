# Climate Temperature Anomaly Visualization Project

## Overview
Interactive web application displaying temperature anomalies for Europe using ERA5 climate data (0.25° resolution). Features both 2D map and 3D globe visualization, optimized for mobile devices.

## Data Scope
- **Time Range**: Last 10 years (2016-2026)
- **Temporal Resolution**: Monthly averages
- **Variable**: Average maximum temperature anomalies
- **Geographic Coverage**: Europe
- **Grid Resolution**: 0.25° (~28km)
- **Total Maps**: 120 months = 120 unique anomaly maps

## Architecture: Pre-generated Raster Tiles

### Tile Specifications
- **Zoom Levels**: z3 (continent) to z6 (country-level)
- **Tiles per Map**: ~5,500 tiles
- **Format**: WebP (optimized for size)
- **Total Storage**: ~12-15 GB
- **Tile URL Pattern**: `https://climate-tiles.s3.fr-par.scw.cloud/tiles/{year}/{month}/{z}/{x}/{y}.webp`

### Storage & Hosting
- **Platform**: Scaleway Object Storage (fr-par region)
- **Bucket**: climate-tiles (public read access)
- **CDN**: Optional Cloudflare free tier for caching
- **Cost**: ~€0.15-0.20/month

### Tile Generation Pipeline
- **Tooling**: Python + GDAL + rasterio + scipy
- **Process**:
  1. Load ERA5 gridded data for month
  2. Calculate anomalies vs reference period
  3. Interpolate between grid points (bicubic/bilinear)
  4. Apply color ramp (blue=cold anomaly, red=hot anomaly)
  5. Generate tiles at z3-z6 using gdal2tiles or custom tiler
  6. Upload to Scaleway Object Storage
- **Execution**: Nightly pipeline for new months (~45 min on 8 cores for full regeneration)
- **Initial Generation Time**: ~5.5 hours single-threaded, ~45 min parallelized

### Client Application
- **Framework**: deck.gl (with TileLayer and BitmapLayer)
- **Features**:
  - 2D map view (default for mobile)
  - 3D globe view (optional, for capable devices)
  - Month/year selector
  - Device capability detection (GPU/screen size)
  - Progressive tile loading
- **Performance**:
  - Network: 2-5 MB per session (tiles load progressively)
  - Rendering: GPU-accelerated, smooth on modern mobile devices
  - Battery: Minimal GPU usage (just texture display, no computation)

### Technology Stack
- **Tile Generation**: Python, GDAL, rasterio, scipy, numpy, boto3
- **Storage**: Scaleway Object Storage (S3-compatible)
- **Frontend**: deck.gl, React (optional), vanilla JS
- **Deployment**: Static hosting (Vercel, Netlify, or Scaleway Object Storage)

## Development Estimate
- **Tile Generation Pipeline**: 2-3 weeks
- **deck.gl Map/Globe Viewer**: 2-3 weeks
- **UI Controls & Device Detection**: 1 week
- **Testing & Optimization**: 1 week
- **Total**: 6-8 weeks

## Future Enhancements
- Add additional variables (mean temp, min temp) - scales linearly
- Extend time range (each additional year = +12 maps, ~1.5 GB)
- Client-side rendering fallback for custom date ranges
- Animation through time series
- Compare multiple months side-by-side
