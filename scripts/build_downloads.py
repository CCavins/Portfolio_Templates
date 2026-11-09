#!/usr/bin/env python3
"""Kept for older instructions. The build now lives in scripts/build.py."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build import main  # noqa: E402

if __name__ == "__main__":
    main()
