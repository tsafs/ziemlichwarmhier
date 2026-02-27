"""Daily temperature threshold detection functions.

All functions accept ``numpy`` arrays and return boolean arrays of the
same shape.  No xarray or file I/O is involved — pure numerical logic.

Thresholds follow DWD (Deutscher Wetterdienst) standards:
  - **Heißer Tag** (hot day):      Tmax >= 30 °C
  - **Extreme heat**:              Tmax >= 35 °C
  - **Tropennacht** (tropical night): Tmin >= 20 °C
  - **Eistag** (ice day):          Tmax <= 0 °C
  - **Frosttag** (frost day):      Tmin < 0 °C
  - **Comfortable day**:           15 °C <= Tmean <= 25 °C
"""

from __future__ import annotations

import numpy as np


# ---------------------------------------------------------------------------
# Hot / heat detection
# ---------------------------------------------------------------------------


def hot_days(tmax_arr: np.ndarray, threshold: float = 30.0) -> np.ndarray:
    """Detect hot days: Tmax >= threshold.

    Args:
        tmax_arr: Array of daily maximum temperatures in °C.
            Any shape is accepted; the returned array has the same shape.
        threshold: Temperature threshold in °C (default 30.0 °C,
            DWD *Heißer Tag* definition).

    Returns:
        Boolean array — ``True`` where the hot-day criterion is met.
    """
    arr = np.asarray(tmax_arr, dtype=float)
    return arr >= threshold


def extreme_heat_days(tmax_arr: np.ndarray, threshold: float = 35.0) -> np.ndarray:
    """Detect extreme-heat days: Tmax >= threshold.

    Args:
        tmax_arr: Array of daily maximum temperatures in °C.
        threshold: Temperature threshold in °C (default 35.0 °C).

    Returns:
        Boolean array — ``True`` where the extreme-heat criterion is met.
    """
    arr = np.asarray(tmax_arr, dtype=float)
    return arr >= threshold


# ---------------------------------------------------------------------------
# Night / minimum temperature
# ---------------------------------------------------------------------------


def tropical_nights(tmin_arr: np.ndarray, threshold: float = 20.0) -> np.ndarray:
    """Detect tropical nights: Tmin >= threshold.

    Args:
        tmin_arr: Array of daily minimum temperatures in °C.
        threshold: Temperature threshold in °C (default 20.0 °C,
            DWD *Tropennacht* definition).

    Returns:
        Boolean array — ``True`` where the tropical-night criterion is met.
    """
    arr = np.asarray(tmin_arr, dtype=float)
    return arr >= threshold


# ---------------------------------------------------------------------------
# Cold / ice detection
# ---------------------------------------------------------------------------


def ice_days(tmax_arr: np.ndarray, threshold: float = 0.0) -> np.ndarray:
    """Detect ice days: Tmax <= threshold.

    Args:
        tmax_arr: Array of daily maximum temperatures in °C.
        threshold: Temperature threshold in °C (default 0.0 °C,
            DWD *Eistag* definition).

    Returns:
        Boolean array — ``True`` where the ice-day criterion is met.
    """
    arr = np.asarray(tmax_arr, dtype=float)
    return arr <= threshold


def frost_days(tmin_arr: np.ndarray, threshold: float = 0.0) -> np.ndarray:
    """Detect frost days: Tmin < threshold.

    Args:
        tmin_arr: Array of daily minimum temperatures in °C.
        threshold: Temperature threshold in °C (default 0.0 °C,
            DWD *Frosttag* definition).

    Returns:
        Boolean array — ``True`` where the frost-day criterion is met.
    """
    arr = np.asarray(tmin_arr, dtype=float)
    return arr < threshold


# ---------------------------------------------------------------------------
# Comfortable day
# ---------------------------------------------------------------------------


def comfortable_days(
    tmean_arr: np.ndarray,
    min_t: float = 15.0,
    max_t: float = 25.0,
) -> np.ndarray:
    """Detect comfortable days: min_t <= Tmean <= max_t.

    Args:
        tmean_arr: Array of daily mean temperatures in °C.
        min_t: Lower bound in °C (default 15.0 °C).
        max_t: Upper bound in °C (default 25.0 °C).

    Returns:
        Boolean array — ``True`` where both bounds are satisfied.
    """
    arr = np.asarray(tmean_arr, dtype=float)
    return (arr >= min_t) & (arr <= max_t)


# ---------------------------------------------------------------------------
# Monthly aggregation helper
# ---------------------------------------------------------------------------


def count_threshold_days(bool_arr: np.ndarray) -> int:
    """Count the number of ``True`` values in a boolean array.

    Args:
        bool_arr: Boolean array produced by one of the detection functions.

    Returns:
        Integer count of threshold-exceedance days.
    """
    return int(np.sum(bool_arr))
