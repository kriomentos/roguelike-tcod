from typing import Tuple

import numpy as np  # type: ignore
import color

# Tile graphics structured type compatible with Console.tiles_rgb.
graphic_dt = np.dtype(
    [
        ("ch", np.int32),  # Unicode codepoint.
        ("fg", "3B"),  # 3 unsigned bytes, for RGB colors.
        ("bg", "3B"),
    ]
)

# Tile struct used for statically defined tile data.
tile_dt = np.dtype(
    [
        ("value", int),
        ("walkable", np.bool),  # True if this tile can be walked over.
        ("transparent", np.bool),   # True if this tile doesn't block FOV.
        ("dark", graphic_dt),   # Graphics for when this tile is not in FOV.
        ("light", graphic_dt),   # Graphics for when this tile is in FOV.
    ]
)

def new_tile(
    *,  # Enforce the use of keywords, so that parameter order doesn't matter.
    value: int,
    walkable: int,
    transparent: int,
    dark: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
    light: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
) -> np.ndarray:
    """Helper function for defining individual tile types """
    return np.array((value, walkable, transparent, dark, light), dtype = tile_dt)

# unexplored, unseen tiles
SHROUD = np.array((ord(" "), (color.white), (color.black)), dtype = graphic_dt)

floor = new_tile(
    value = 1,
    walkable = True,
    transparent = True,
    dark = (ord(" "), (color.light_grey), (color.dark_grey)),
    light = (ord(" "), (color.white), (color.grey)),
)
wall = new_tile(
    value = 0,
    walkable = False,
    transparent = False,
    dark = (ord("#"), (color.light_grey), (color.dark_grey)),
    light = (ord("#"), (color.white), (color.grey)),
)
down_stairs = new_tile(
    value = 2,
    walkable = True,
    transparent = True,
    dark = (ord(">"), (color.light_grey), (color.dark_grey)),
    light = (ord(">"), (color.white), (color.grey))
)