# Static Metrics Specification

## Overview
4-6 key climate indicators displayed prominently below the globe, above the narrative tabs. Visually striking presentation with tilted labels, large values, and explanatory subtitles.

## Visual Design
- **Layout**: Horizontal row of metric cards (responsive: stack on mobile)
- **Style**: Slightly tilted labels (~5-10 degrees), bold large numbers, smaller subtitle text
- **Color Coding**: Use color sparingly for emphasis (red for warming, context-appropriate for others)

## Metric Options

### Tier 1: Essential Metrics (Recommended: Pick 4)

#### 1. Annual Temperature Anomaly
- **Value**: "+2.3°C warmer" (or "1.8°C cooler" if applicable)
- **Subtitle**: "2025 vs 1961-1990 average"
- **Data Source**: Most recent complete calendar year mean temperature anomaly
- **Update Frequency**: Annually (January)
- **Rationale**: Simple, immediate, most relatable metric

#### 2. Warming Rate
- **Value**: "+0.4°C per decade"
- **Subtitle**: "Trend since 1995" (or "last 30 years")
- **Data Source**: Linear regression of annual mean temperatures over past ~30 years
- **Update Frequency**: Annually
- **Rationale**: Shows acceleration, forward-looking implication

#### 3. Record-Breaking Days
- **Value**: "18 record-breaking days"
- **Subtitle**: "Jan-Jun 2026" (year-to-date) or "2025" (full year)
- **Data Source**: Count of daily temperature records (hot + cold) for specified period
- **Update Frequency**: Monthly (YTD) or Annually (full year)
- **Rationale**: Dramatic, newsworthy, easy to understand

#### 4. Climate Analog
- **Value**: "Berlin feels like 1980s Lyon"
- **Subtitle**: "Climate analog comparison"
- **Data Source**: Calculated match between current city climate and historical climate of other cities
- **Update Frequency**: Annually or static (based on last decade)
- **Calculation Method**: 
  - Compare recent climate metrics (monthly temp distributions, seasonal patterns)
  - Find best match using distance metric (Euclidean distance across monthly means)
  - Consider geographic constraints (latitude, distance)
- **Rationale**: Memorable, tangible, great conversation starter

### Tier 2: Strong Additional Metrics (Pick 1-2)

#### 5. Comfortable Days
- **Value**: "145 comfortable days"
- **Subtitle**: "15-25°C, 2025" (or "rolling 12 months")
- **Data Source**: Count of days with mean temperature in 15-25°C range
- **Update Frequency**: Annually or monthly (rolling)
- **Rationale**: Positive framing, practical relevance

#### 6. Days Outside Normal Range
- **Value**: "32 days outside normal"
- **Subtitle**: "Beyond historical 10-90% range, 2025"
- **Data Source**: Count of days outside 10th-90th percentile of 1961-1990 reference
- **Update Frequency**: Annually
- **Rationale**: Shows volatility, climate change manifestation

#### 7. Extreme Rainfall Days (if including precipitation)
- **Value**: "8 extreme rainfall days"
- **Subtitle**: "Year-to-date 2026, >25mm/day" (or ">30mm/day")
- **Data Source**: Count of days exceeding precipitation threshold
- **Update Frequency**: Monthly (YTD) or Annually
- **Rationale**: Complements temperature, practical impacts

#### 8. Snow Days Change (if including precipitation)
- **Value**: "18 fewer snow days"
- **Subtitle**: "vs 1961-1990 average"
- **Data Source**: Average annual snow days in recent period vs reference
- **Update Frequency**: Annually
- **Rationale**: Very tangible, high emotional resonance in mid-latitudes

### Tier 3: Specialized Metrics (Consider for specific audiences)

#### 9. Climate Departure Index
- **Value**: "2.1σ above normal"
- **Subtitle**: "Statistical deviation, 2025"
- **Data Source**: Standard deviations from 1961-1990 mean
- **Update Frequency**: Annually
- **Rationale**: Statistical rigor
- **Warning**: More technical, may alienate general audience

#### 10. Growing Season Length
- **Value**: "215 days above 5°C"
- **Subtitle**: "2025, +23 days vs 1961-1990"
- **Data Source**: Count of days with mean temp >5°C (or >10°C)
- **Update Frequency**: Annually
- **Rationale**: Agricultural relevance
- **Warning**: Niche audience

#### 11. Tropical Nights
- **Value**: "12 tropical nights"
- **Subtitle**: "Minimum temp >20°C, 2025"
- **Data Source**: Count of nights with minimum temperature >20°C
- **Update Frequency**: Annually
- **Rationale**: Sleep comfort, health impacts
- **Warning**: Only relevant for cities that experience these

#### 12. Hot Days / Ice Days (if not in plots)
- **Value**: "14 hot days, 8 ice days"
- **Subtitle**: "Year-to-date 2026" or "2025"
- **Data Source**: Days >30°C (hot) and days with max ≤0°C (ice)
- **Update Frequency**: Monthly (YTD) or Annually
- **Warning**: Seasonal neutrality (empty in opposite seasons)

## Behavior

### When No City Selected (Global/European View)
- Display global or European aggregate values
- Example: "Global: +1.2°C warmer (2025)"
- Encourage exploration: "Select a city for local details"

### When City Selected
- Display city-specific values
- Smooth transition/animation when switching cities
- Update all metrics simultaneously

## Data Requirements
- All metrics should be pre-calculated and stored (not computed on-demand)
- Database schema should support rapid lookup by city and time period
- Consider caching strategy for frequently accessed cities

## Recommended Final Selection (6 metrics)
1. Annual Temperature Anomaly
2. Warming Rate
3. Record-Breaking Days
4. Climate Analog
5. Comfortable Days
6. Extreme Rainfall Days (if including precipitation) OR Days Outside Normal Range (if temperature-only)