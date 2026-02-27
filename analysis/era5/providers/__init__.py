"""Climate data provider registry and factory.

Usage
-----
    from analysis.era5.providers import get_provider

    provider = get_provider()                # reads CLIMATE_DATA_PROVIDER env var
    provider = get_provider('era5-land')     # explicit selection
"""

from __future__ import annotations

import os

from .era5_land import ERA5LandProvider
from .protocol import ClimateDataProvider

# ---------------------------------------------------------------------------
# Provider registry
# ---------------------------------------------------------------------------
# To add a new provider: implement ClimateDataProvider protocol + register here.

_PROVIDERS: dict[str, type] = {
    "era5-land": ERA5LandProvider,
}


def get_provider(provider_id: str | None = None) -> ClimateDataProvider:
    """Instantiate the configured climate data provider.

    Args:
        provider_id: Provider identifier string (e.g. ``'era5-land'``).
            If ``None``, the value of the ``CLIMATE_DATA_PROVIDER``
            environment variable is used.  If that is also unset,
            defaults to ``'era5-land'``.

    Returns:
        A freshly instantiated provider that satisfies
        :class:`~analysis.era5.providers.protocol.ClimateDataProvider`.

    Raises:
        ValueError: If ``provider_id`` is not in the registry.

    Examples:
        >>> provider = get_provider()
        >>> provider.dataset_id
        'era5-land'
        >>> get_provider('unknown')
        Traceback (most recent call last):
            ...
        ValueError: Unknown provider 'unknown'. Available: ['era5-land']
    """
    pid = provider_id or os.environ.get("CLIMATE_DATA_PROVIDER", "era5-land")
    if pid not in _PROVIDERS:
        raise ValueError(
            f"Unknown provider '{pid}'. Available: {list(_PROVIDERS)}"
        )
    return _PROVIDERS[pid]()


__all__ = ["ClimateDataProvider", "ERA5LandProvider", "get_provider"]
