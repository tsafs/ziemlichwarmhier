```skill
---
name: climate-data-provider
description: Define a climate data provider protocol, implement concrete providers (ERA5-Land, HYRAS, DWD), and wire environment-driven selection with provider-swap tests. Use when adding or switching between climate data sources.
---

# Climate Data Provider Skill

## Purpose

Abstract climate data access behind a provider protocol so the application can switch between data sources (ERA5-Land, HYRAS, DWD station data) via environment configuration. Covers: protocol definition, provider implementations, dependency injection pattern, provider-swap testing, and env-driven selection.

## Prerequisites

Gather context:

```
Subagent 1: "Read analysis/hyras/. List and read all Python files."
Subagent 2: "Read analysis/stations/. List and read fetch_station_data.py and extract_daily_station_data.py."
Subagent 3: "Read analysis/utilities/download_from_s3.py and upload_to_s3.py."
Subagent 4: "Read pyproject.toml. Return: Python version, dependencies."
Subagent 5: "Search for 'ERA5' or 'era5' in the entire repo. Return all file paths and context."
```

## Concepts

| Term | Meaning |
|------|---------|
| **Protocol** | Python `Protocol` class defining the interface all providers must implement |
| **Provider** | Concrete class implementing the protocol for a specific data source |
| **Injection** | Passing the provider instance at call site, not hardcoding imports |
| **Provider swap** | Test that verifies the same pipeline works with different providers |

## Architecture

```
analysis/
├── providers/
│   ├── __init__.py
│   ├── protocol.py          # ClimateDataProvider Protocol
│   ├── era5_provider.py     # ERA5-Land implementation
│   ├── hyras_provider.py    # HYRAS implementation
│   ├── dwd_provider.py      # DWD station data implementation
│   └── factory.py           # Provider factory (env-driven selection)
├── tests/
│   ├── fixtures/
│   │   └── providers/
│   │       ├── era5_sample.nc   # Minimal NetCDF fixture
│   │       ├── hyras_sample.nc
│   │       └── dwd_sample.csv
│   └── test_providers.py        # Provider-swap tests
```

## Implementation Steps

### Step 1: Define Provider Protocol

**Location**: `analysis/providers/protocol.py`

```python
"""Climate data provider protocol — all providers must implement this interface."""

from __future__ import annotations
from typing import Protocol, runtime_checkable
from pathlib import Path
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class ClimateRecord:
    """Single daily climate observation."""
    date: date
    station_id: str
    tasmin: float | None = None  # Daily minimum temperature (°C)
    tasmax: float | None = None  # Daily maximum temperature (°C)
    tas: float | None = None     # Daily mean temperature (°C)
    precipitation: float | None = None  # Daily precipitation (mm)


@dataclass(frozen=True)
class StationMetadata:
    """Weather station metadata."""
    station_id: str
    name: str
    latitude: float
    longitude: float
    elevation: float | None = None


@runtime_checkable
class ClimateDataProvider(Protocol):
    """Protocol for climate data access.

    All providers must implement these methods to be usable in pipelines.
    """

    @property
    def name(self) -> str:
        """Human-readable provider name (e.g., 'ERA5-Land', 'HYRAS')."""
        ...

    def fetch_daily_data(
        self,
        station_id: str,
        start_date: date,
        end_date: date,
    ) -> list[ClimateRecord]:
        """Fetch daily climate records for a station/grid point.

        Args:
            station_id: Station ID or grid point identifier
            start_date: Start date (inclusive)
            end_date: End date (inclusive)

        Returns:
            List of ClimateRecord sorted by date

        Raises:
            FileNotFoundError: If data source is unavailable
            ValueError: If date range is invalid
        """
        ...

    def list_stations(self) -> list[StationMetadata]:
        """List available stations/grid points."""
        ...

    def get_station(self, station_id: str) -> StationMetadata | None:
        """Get metadata for a specific station."""
        ...
```

### Step 2: Implement Concrete Providers

**Location**: `analysis/providers/era5_provider.py`

```python
"""ERA5-Land climate data provider."""

from __future__ import annotations
import logging
from datetime import date
from pathlib import Path

from .protocol import ClimateDataProvider, ClimateRecord, StationMetadata

logger = logging.getLogger(__name__)


class ERA5LandProvider:
    """Provides climate data from ERA5-Land reanalysis NetCDF files.

    Implements ClimateDataProvider protocol.

    Args:
        data_dir: Directory containing ERA5-Land NetCDF files
    """

    def __init__(self, data_dir: Path) -> None:
        self._data_dir = data_dir
        if not data_dir.exists():
            raise FileNotFoundError(f"ERA5-Land data directory not found: {data_dir}")

    @property
    def name(self) -> str:
        return "ERA5-Land"

    def fetch_daily_data(
        self,
        station_id: str,
        start_date: date,
        end_date: date,
    ) -> list[ClimateRecord]:
        if start_date > end_date:
            raise ValueError(f"start_date {start_date} > end_date {end_date}")

        # Implementation: open NetCDF, extract grid point, convert to records
        # ... (uses xarray/netCDF4)
        records: list[ClimateRecord] = []
        logger.info(f"Fetched {len(records)} records from ERA5-Land for {station_id}")
        return records

    def list_stations(self) -> list[StationMetadata]:
        # ERA5-Land uses grid points, not stations
        # Return a list of grid point identifiers
        return []

    def get_station(self, station_id: str) -> StationMetadata | None:
        return None
```

**Location**: `analysis/providers/dwd_provider.py`

```python
"""DWD station data provider."""

from __future__ import annotations
import csv
import logging
from datetime import date
from pathlib import Path

from .protocol import ClimateDataProvider, ClimateRecord, StationMetadata

logger = logging.getLogger(__name__)


class DWDStationProvider:
    """Provides climate data from DWD weather station CSV files.

    Implements ClimateDataProvider protocol.

    Args:
        data_dir: Directory containing station CSV files
    """

    def __init__(self, data_dir: Path) -> None:
        self._data_dir = data_dir

    @property
    def name(self) -> str:
        return "DWD Stations"

    def fetch_daily_data(
        self,
        station_id: str,
        start_date: date,
        end_date: date,
    ) -> list[ClimateRecord]:
        csv_path = self._data_dir / f"{station_id}.csv"
        if not csv_path.exists():
            raise FileNotFoundError(f"Station data not found: {csv_path}")

        records = []
        with open(csv_path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row_date = date.fromisoformat(row["date"])
                if start_date <= row_date <= end_date:
                    records.append(ClimateRecord(
                        date=row_date,
                        station_id=station_id,
                        tasmin=float(row["tasmin"]) if row.get("tasmin") else None,
                        tasmax=float(row["tasmax"]) if row.get("tasmax") else None,
                        tas=float(row["tas"]) if row.get("tas") else None,
                    ))
        return sorted(records, key=lambda r: r.date)

    def list_stations(self) -> list[StationMetadata]:
        stations = []
        for csv_path in sorted(self._data_dir.glob("*.csv")):
            stations.append(StationMetadata(
                station_id=csv_path.stem,
                name=csv_path.stem,
                latitude=0.0,
                longitude=0.0,
            ))
        return stations

    def get_station(self, station_id: str) -> StationMetadata | None:
        csv_path = self._data_dir / f"{station_id}.csv"
        if csv_path.exists():
            return StationMetadata(
                station_id=station_id,
                name=station_id,
                latitude=0.0,
                longitude=0.0,
            )
        return None
```

### Step 3: Create Provider Factory

**Location**: `analysis/providers/factory.py`

```python
"""Provider factory — selects provider based on environment configuration."""

from __future__ import annotations
import os
import logging
from pathlib import Path

from .protocol import ClimateDataProvider
from .era5_provider import ERA5LandProvider
from .dwd_provider import DWDStationProvider

logger = logging.getLogger(__name__)

PROVIDER_REGISTRY: dict[str, type] = {
    "era5": ERA5LandProvider,
    "dwd": DWDStationProvider,
    # "hyras": HYRASProvider,  # Add when implemented
}


def create_provider(
    provider_name: str | None = None,
    data_dir: Path | None = None,
) -> ClimateDataProvider:
    """Create a climate data provider based on configuration.

    Args:
        provider_name: Provider name (default: from CLIMATE_DATA_PROVIDER env var)
        data_dir: Data directory (default: from CLIMATE_DATA_DIR env var)

    Returns:
        Configured ClimateDataProvider instance

    Raises:
        ValueError: If provider name is unknown
        FileNotFoundError: If data directory doesn't exist
    """
    name = provider_name or os.environ.get("CLIMATE_DATA_PROVIDER", "dwd")
    directory = data_dir or Path(os.environ.get("CLIMATE_DATA_DIR", "data"))

    if name not in PROVIDER_REGISTRY:
        raise ValueError(
            f"Unknown provider '{name}'. Available: {list(PROVIDER_REGISTRY.keys())}"
        )

    provider_class = PROVIDER_REGISTRY[name]
    provider = provider_class(data_dir=directory)

    logger.info(f"Created climate data provider: {provider.name} (dir: {directory})")
    return provider
```

### Step 4: Create Test Fixtures

**Location**: `analysis/tests/fixtures/providers/dwd_sample.csv`

```csv
date,station_id,tasmin,tasmax,tas
2024-01-01,00044,-2.3,5.1,1.4
2024-01-02,00044,-3.1,4.2,0.5
2024-06-15,00044,14.2,28.7,21.5
2024-12-31,00044,-5.1,0.8,-2.2
```

### Step 5: Write Provider-Swap Tests

**Location**: `analysis/tests/test_providers.py`

```python
"""Provider-swap tests — verify all providers satisfy the protocol contract."""

import pytest
from datetime import date
from pathlib import Path

from providers.protocol import ClimateDataProvider, ClimateRecord, StationMetadata
from providers.dwd_provider import DWDStationProvider
from providers.factory import create_provider

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "providers"


class TestDWDProvider:
    """Test DWD provider implementation."""

    @pytest.fixture
    def provider(self):
        return DWDStationProvider(data_dir=FIXTURE_DIR)

    def test_implements_protocol(self, provider):
        assert isinstance(provider, ClimateDataProvider)

    def test_name(self, provider):
        assert provider.name == "DWD Stations"

    def test_fetch_daily_data(self, provider):
        records = provider.fetch_daily_data("dwd_sample", date(2024, 1, 1), date(2024, 12, 31))
        assert len(records) == 4
        assert all(isinstance(r, ClimateRecord) for r in records)
        assert records[0].date == date(2024, 1, 1)
        assert records[0].tasmin == pytest.approx(-2.3)

    def test_fetch_date_range_filtering(self, provider):
        records = provider.fetch_daily_data("dwd_sample", date(2024, 6, 1), date(2024, 7, 1))
        assert len(records) == 1
        assert records[0].date == date(2024, 6, 15)

    def test_fetch_nonexistent_station(self, provider):
        with pytest.raises(FileNotFoundError):
            provider.fetch_daily_data("nonexistent", date(2024, 1, 1), date(2024, 1, 2))

    def test_invalid_date_range(self, provider):
        with pytest.raises(ValueError):
            provider.fetch_daily_data("dwd_sample", date(2024, 12, 31), date(2024, 1, 1))

    def test_list_stations(self, provider):
        stations = provider.list_stations()
        assert len(stations) >= 1
        assert all(isinstance(s, StationMetadata) for s in stations)


class TestProviderFactory:
    """Test provider factory env-driven selection."""

    def test_creates_dwd_provider(self):
        provider = create_provider("dwd", FIXTURE_DIR)
        assert provider.name == "DWD Stations"

    def test_unknown_provider_raises(self):
        with pytest.raises(ValueError, match="Unknown provider"):
            create_provider("nonexistent", FIXTURE_DIR)

    def test_env_driven_selection(self, monkeypatch):
        monkeypatch.setenv("CLIMATE_DATA_PROVIDER", "dwd")
        monkeypatch.setenv("CLIMATE_DATA_DIR", str(FIXTURE_DIR))
        provider = create_provider()
        assert provider.name == "DWD Stations"

    def test_default_is_dwd(self, monkeypatch):
        monkeypatch.delenv("CLIMATE_DATA_PROVIDER", raising=False)
        monkeypatch.setenv("CLIMATE_DATA_DIR", str(FIXTURE_DIR))
        provider = create_provider()
        assert provider.name == "DWD Stations"


class TestProviderSwap:
    """Verify that a pipeline produces equivalent results with different providers.

    This is the key self-correction test: if a new provider is added,
    run the same assertions against it.
    """

    @pytest.fixture(params=["dwd"])  # Add "era5", "hyras" as implemented
    def provider(self, request):
        if request.param == "dwd":
            return DWDStationProvider(data_dir=FIXTURE_DIR)
        pytest.skip(f"Provider {request.param} not yet implemented with test fixtures")

    def test_returns_sorted_records(self, provider):
        records = provider.fetch_daily_data("dwd_sample", date(2024, 1, 1), date(2024, 12, 31))
        dates = [r.date for r in records]
        assert dates == sorted(dates)

    def test_records_have_required_fields(self, provider):
        records = provider.fetch_daily_data("dwd_sample", date(2024, 1, 1), date(2024, 12, 31))
        for r in records:
            assert r.date is not None
            assert r.station_id is not None
```

### Step 6: Wire Provider into Pipeline

```python
# In any pipeline script:
from providers.factory import create_provider

def run_pipeline():
    provider = create_provider()  # Reads env vars
    records = provider.fetch_daily_data("00044", date(2024, 1, 1), date(2024, 12, 31))
    # ... process records
```

## Adding a New Provider

1. Create `analysis/providers/<name>_provider.py` implementing `ClimateDataProvider`
2. Add to `PROVIDER_REGISTRY` in `factory.py`
3. Add fixture file in `analysis/tests/fixtures/providers/`
4. Add provider name to `@pytest.fixture(params=[...])` in `TestProviderSwap`
5. Run `pytest analysis/tests/test_providers.py` — all swap tests must pass
6. Add env var docs to `.env.example`

## Run Commands

```bash
# Run provider tests
python -m pytest analysis/tests/test_providers.py -v

# Run with specific provider
CLIMATE_DATA_PROVIDER=dwd python -m pytest analysis/tests/test_providers.py -v

# Check protocol compliance
python -c "from providers.dwd_provider import DWDStationProvider; from providers.protocol import ClimateDataProvider; assert isinstance(DWDStationProvider('data'), ClimateDataProvider)"
```

## Failure Modes & Self-Correction

| Failure | Cause | Fix |
|---------|-------|-----|
| `TypeError: Protocols ... cannot be instantiated` | Using Protocol as base class instead of structural typing | Use `@runtime_checkable` and `isinstance()` check |
| `ModuleNotFoundError: providers` | Missing `__init__.py` or wrong sys.path | Add `__init__.py` to `analysis/providers/` |
| Provider swap test skipped | Fixture not created for provider | Add fixture file and unskip in params |
| `FileNotFoundError` on data_dir | Directory doesn't exist | Create dir or adjust path |
| netCDF4 import error | Not installed | `pip install netCDF4 xarray` |

## Checklist

- [ ] Protocol defined with `@runtime_checkable`
- [ ] At least one concrete provider implemented
- [ ] Provider factory with env-driven selection
- [ ] Test fixtures in `analysis/tests/fixtures/providers/`
- [ ] Protocol compliance test (`isinstance` check)
- [ ] Provider-swap parameterized tests
- [ ] Factory env-var tests
- [ ] `__init__.py` files in `analysis/providers/`
- [ ] `.env.example` updated with `CLIMATE_DATA_PROVIDER` and `CLIMATE_DATA_DIR`
- [ ] `pytest` passes with no network
```
