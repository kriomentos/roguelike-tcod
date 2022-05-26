from __future__ import annotations

from random import randrange
from typing import Iterator, List, Tuple, TYPE_CHECKING
from scipy import signal

import numpy as np
import tcod

from game_map import GameMap
import tile_types


if TYPE_CHECKING:
    from entity import Entity

# helper kernel for convolve2d, basically 3x3 array [[1, 1, 1], [1, 0, 1], [1, 1, 1]]
kernel = np.ones((3, 3), dtype = "int")
kernel[1, 1] = 0

def generate_dungeon(
    map_width: int,
    map_height: int,
    initial_open: int,
    player: Entity
) -> GameMap:
    # Generate a new dungeon map.
    dungeon = GameMap(map_width, map_height, entities = [player])
    # helper map for convolve calculation
    wall_count = GameMap(map_width, map_height)

    # number of fields to "open" or replace/carve out with floors
    open_count = (dungeon.area * initial_open)

    # randomly selected tile gets replaced with floor/carved out
    while open_count > 0:
        rand_w = randrange(1, dungeon.width - 1)
        rand_h = randrange(1, dungeon.height - 1)

        if dungeon.tiles[rand_w, rand_h] == tile_types.wall:
            dungeon.tiles[rand_w, rand_h] = tile_types.floor
            open_count -= 1

    # gotta work with additional field "value" to get only weight of the tile. not the whole object (convolve works only on 2d arrays) 
    wall_count = signal.convolve2d(dungeon.tiles['value'], kernel, mode = "same")

    # we go through the map and simulate cellular automata rules using convolve values
    for x in range(1, dungeon.width - 1):
        for y in range(1, dungeon.height - 1):

            if wall_count[x, y] > 4:
                dungeon.tiles[x, y] = tile_types.floor
            elif wall_count[x, y] < 3:
                dungeon.tiles[x, y] = tile_types.wall

    return dungeon