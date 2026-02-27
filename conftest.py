"""Root-level pytest configuration.

Ensures the project root is on sys.path so that ``analysis.*`` imports
resolve correctly regardless of the test discovery entry point.

This file is intentionally kept minimal — all fixture definitions live
in the per-suite conftest files (``analysis/tests/conftest.py``,
``analysis/era5/tests/conftest.py``, etc.).
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root so `analysis.*` packages are importable.
_ROOT = Path(__file__).parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
