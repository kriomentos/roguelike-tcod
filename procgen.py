from __future__ import annotations

from random import randrange, randint, random
from typing import TYPE_CHECKING
from scipy import signal

import numpy as np
from sqlalchemy import table
from engine import Engine

from game_map import GameMap
import tile_types
import entity_factories

if TYPE_CHECKING:
    from engine import Engine

# helper kernel for convolve2d, basically 3x3 array [[1, 1, 1], [1, 0, 1], [1, 1, 1]]
kernel = np.ones((3, 3), dtype = "int")
kernel[1, 1] = 0


def place_entities(dungeon: GameMap, maximum_monsters: int):

    for i in range(maximum_monsters):
        # select random postion for enemy
        # it is in bounds of the map minus the edges
        x = randint(1, dungeon.width - 1)
        y = randint(0, dungeon.height - 1)

        # check if the selected spot doesn't contain any entity already
        # if it does not then place one of the monsters
        # 80% chance for orc 20% for troll
        if not any(entity.x == x and entity.y == y for entity in dungeon.entities):
            if random() < 0.8:
                entity_factories.orc.spawn(dungeon, x, y)
                print("Placed orc at: ", x, y)
            else:
                entity_factories.troll.spawn(dungeon, x, y)
                print("Placed troll at: ", x, y)

def generate_dungeon(
    map_width: int,
    map_height: int,
    initial_open: int,
    max_monsters: int,
    engine: Engine,
) -> GameMap:
    # Generate a new dungeon map.
    player = engine.player
    dungeon = GameMap(engine, map_width, map_height, entities = [player])
    # helper map for convolve calculation
    wall_count = GameMap(engine, map_width, map_height)

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

    place_entities(dungeon, max_monsters)

    player.place(40, 20, dungeon)
    entity_factories.table.place(40, 21, dungeon)

    return dungeon