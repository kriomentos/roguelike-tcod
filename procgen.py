from __future__ import annotations

from random import randrange, randint, random
from typing import TYPE_CHECKING
from scipy import signal

import numpy as np
from engine import Engine

from game_map import GameMap
import tile_types
import entity_factories

if TYPE_CHECKING:
    from engine import Engine

# helper kernel for convolve2d, basically 3x3 array [[1, 1, 1], [1, 0, 1], [1, 1, 1]]
kernel = np.ones((3, 3), dtype = "int")
kernel[1, 1] = 0

def place_entities(dungeon: GameMap, maximum_monsters: int, maximum_items: int):
    number_of_monsters = randint(1, maximum_monsters)
    number_of_items = randint(1, maximum_items)

    for i in range(number_of_monsters):
        # select random postion for enemy using numpy.where
        # we look only at positions that are floors,
        # this way we avoid placing the enemies in walls,
        # and we don't need more complicated checks
        x, y = np.where(dungeon.tiles["walkable"])
        # we generate random integer from tiles we found as viable
        # it's used later to select given index in the game_map array
        j = np.random.randint(len(x))

        # check if the selected spot doesn't contain any entity already
        # if it does not then place one of the monsters
        # 80% chance for orc 20% for troll
        if not any(entity.x == x[j] and entity.y == y[j] for entity in dungeon.entities):
            if random() < 0.8:
                entity_factories.orc.spawn(dungeon, x[j], y[j])
                print("Placed orc at: ", x[j], y[j])
            else:
                entity_factories.troll.spawn(dungeon, x[j], y[j])
                print("Placed troll at: ", x[j], y[j])

    for i in range(number_of_items):
        x, y = np.where(dungeon.tiles["walkable"])
        j = np.random.randint(len(y))

        if not any(entity.x == x[j] and entity.y == y[j] for entity in dungeon.entities):
            entity_factories.health_potion.spawn(dungeon, x[j], y[j])
            print("Placed potion at: ", x[j], y[j])

def cellular_automata(dungeon: GameMap, min: int, max: int, count: GameMap):
    # on each pass we recalculate amount of neighbours, which gives much smoother output
    # more passes equals smoother map and less artifacts
    count = signal.convolve2d(dungeon.tiles['value'], kernel, mode = "same", boundary = 'wrap')
    for i in range(1, dungeon.width - 1):
        for j in range(1, dungeon.height - 1):
            # if in the cell neighbourhood is at least MAX floors
            # then it "dies" and turns into floor
            if count[i, j] > max:
                dungeon.tiles[i, j] = tile_types.floor
            # same rule applies to floor cells, if they have less than MIN floors
            # in neighbourhood, turn them into wall
            elif count[i, j] < min:
                dungeon.tiles[i, j] = tile_types.wall

    return dungeon

def generate_dungeon(
    map_width: int,
    map_height: int,
    initial_open: int,
    max_monsters: int,
    max_items: int,
    engine: Engine,
) -> GameMap:
    # Generate a new dungeon map.
    player = engine.player
    dungeon = GameMap(engine, map_width, map_height, entities = [player])
    # helper map to hold convolve calculation
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

    # we go through
    # the map and simulate cellular automata rules using convolve values
    # we do two passes with alternate ruleset to achieve both open spaces and tight corridors
    for x in range(1):
        cellular_automata(dungeon, 3, 4, wall_count)
        cellular_automata(dungeon, 4, 5, wall_count)

    place_entities(dungeon, max_monsters, max_items)

    player.place(40, 20, dungeon)
    entity_factories.table.spawn(dungeon, 40, 21)

    return dungeon