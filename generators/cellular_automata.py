from __future__ import annotations

import numpy as np

from game_map import GameMap
from scipy import signal # type: ignore
from typing import Any
import tile_types

from helpers.region_connection import connect_regions

def setup_cellular_automata(dungeon: GameMap, random_gen: np.random.Generator, helper_map: GameMap) -> GameMap:    
    dungeon.tiles = np.where(random_gen.integers(0, 100, (dungeon.height, dungeon.width)).T > 49,
        tile_types.floor, tile_types.wall
    )

    dungeon.tiles[[0, -1], :] = tile_types.wall
    dungeon.tiles[:, [0, -1]] = tile_types.wall

    for _ in range(7):
        cellular_automata(dungeon, 4, helper_map)

    connect_regions(dungeon, random_gen)

    for _ in range(2):
        cellular_automata(dungeon, 6, helper_map)
        cellular_automata(dungeon, 5, helper_map)

    return dungeon

def cellular_automata(dungeon: GameMap, wall_rule: int, count: Any) -> GameMap:
    # on each pass we recalculate amount of neighbors, which gives much smoother output
    # more passes equals smoother map and less artifacts
    # we check the number of neighbors including tile itself is less/more than wall_rule
    # and let it "die" or not
    count = signal.convolve2d(dungeon.tiles['weight'], [[1, 1, 1], [1, 1, 1], [1, 1, 1]], mode = 'same')

    dungeon.tiles[count < wall_rule] = tile_types.wall
    dungeon.tiles[count > wall_rule] = tile_types.floor

    return dungeon