"""Load level maps from text files in src/maps_data.

Each level file contains rows of space-separated integers (0/1). This module
exposes LEVEL_ONE .. LEVEL_SEVEN as lists of lists of ints for backward
compatibility with the rest of the codebase.
"""
from pathlib import Path
from typing import List


_ROOT = Path(__file__).parent
_DATA_DIR = _ROOT / "maps_data"


def _load_level(path: Path) -> List[List[int]]:
    with path.open("r", encoding="utf-8") as f:
        rows = []
        for line in f:
            line = line.strip()
            if not line:
                continue
            # split on whitespace and convert to int
            parts = line.split()
            rows.append([int(p) for p in parts])
    return rows


def _make_maps():
    maps = {}
    for i in range(1, 9):
        fname = f"map_{['0','1','2','3','4','5','6','7'][i-1]}.txt"
        p = _DATA_DIR / fname
        if p.exists():
            maps[i] = _load_level(p)
        else:
            # fallback: empty grid
            maps[i] = []
    return maps


_maps = _make_maps()

MAP_ZERO = _maps[1]
MAP_ONE = _maps[2]
MAP_TWO = _maps[3]
MAP_THREE = _maps[4]
MAP_FOUR = _maps[5]
MAP_FIVE = _maps[6]
MAP_SIX = _maps[7]
MAP_SEVEN = _maps[8]

__all__ = [
    "MAP_ZERO",
    "MAP_ONE",
    "MAP_TWO",
    "MAP_THREE",
    "MAP_FOUR",
    "MAP_FIVE",
    "MAP_SIX",
    "MAP_SEVEN",
]