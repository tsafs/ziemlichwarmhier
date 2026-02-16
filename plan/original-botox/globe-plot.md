# Globe Plot Specification

## Overview
Interactive 3D globe visualization serving as the primary entry point for the climate visualization website. Updates monthly with pre-calculated raster tiles.

## Visualization Type
**Rolling 12-Month Temperature Anomaly**

## Data Specification
- **Metric**: Mean temperature (average of daily mean temperatures)
- **Calculation**: Rolling 12-month average anomaly vs 1961-1990 reference period
- **Temporal Coverage**: Most recent 12 months (updates monthly)
- **Geographic Coverage**: Global (focus on Europe)
- **Spatial Resolution**: 0.25° ERA5 grid (~28km)

## Tile Specifications
- **Update Frequency**: Monthly (nightly pipeline after new month completes)
- **Zoom Levels**: z3 (continent) to z6 (country-level)
- **Format**: WebP
- **Color Scale**: Diverging blue (cooler) to red (warmer)
- **Suggested Range**: -2°C to +3°C for Europe (adjust based on data)

## User Interface
- **Default View**: Rotated to show Europe prominently
- **Interaction**: Click/tap cities to view detailed city pages
- **Title**: "How have the last 12 months compared to normal?"
- **Subtitle**: "Temperature difference vs. 1961-1990 average (updated monthly)"
- **Date Indicator**: Show which 12-month period is displayed (e.g., "Feb 2025 - Jan 2026")

## Behavior
- **No City Selected**: Globe shows global data, metrics below show global/European aggregates
- **City Selected**: Globe remains unchanged, metrics and plots below switch to selected city
- **Visual Enhancement**: Subtle fade-in animation on page load, gentle auto-rotation to Europe

## Rationale
- **Mean Temperature**: Most representative of overall climate shift, standard in climate science, balanced signal
- **Rolling 12 Months**: Avoids seasonal neutrality problem, always shows meaningful data, smooths weather noise while preserving climate signal
- **Monthly Updates**: Balances freshness with computational efficiency
- **Always-On Visualization**: Globe never changes with city selection to maintain orientation and allow comparison
