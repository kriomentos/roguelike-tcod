from __future__ import annotations

from random import randrange
from typing import Iterator, List, Tuple, TYPE_CHECKING

import tcod

from game_map import GameMap
import tile_types


if TYPE_CHECKING:
    from entity import Entity

def generate_dungeon(
    map_width: int,
    map_height: int,
    initial_open: int,
    player: Entity,
) -> GameMap:
    """Generate a new dungeon map."""
    dungeon = GameMap(map_width, map_height)

    open_count = (dungeon.area * initial_open)

    while open_count > 0:
        rand_w = randrange(1, dungeon.width - 1)
        rand_h = randrange(1, dungeon.height - 1)

        if dungeon.tiles[rand_w, rand_h] == tile_types.wall:
            dungeon.tiles[rand_w, rand_h] = tile_types.floor
            open_count -= 1

    changes = 0

    #for n in range(2):
    for x in range(1, dungeon.width - 1):
        for y in range(1, dungeon.height - 1):
            wall_count = __adj_wall_count(dungeon, x, y)
            #if dungeon.tiles[x, y] == tile_types.floor:
            if wall_count > 5:
                dungeon.tiles[x, y] = tile_types.wall
            elif wall_count < 4:
                dungeon.tiles[x, y] = tile_types.floor

    return dungeon

def __adj_wall_count(dungeon, x, y):
    count = 0

    for r in (-1, 0, 1):
        for c in (-1, 0, 1):
            if dungeon.tiles[(x + r), (y + c)] != tile_types.floor and not(r == 0 and c == 0):
                count += 1

    return count