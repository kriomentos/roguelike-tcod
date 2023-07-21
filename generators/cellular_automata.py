from game_map import GameMap
from scipy import signal # type: ignore
from typing import Any
import numpy as np
import tile_types

def cellular_automata(dungeon: GameMap, wall_rule: int, count: Any) -> GameMap:
    # on each pass we recalculate amount of neighbours, which gives much smoother output
    # more passes equals smoother map and less artifacts
    # we check the number of neighbours including tile itself is less/more than wall_rule
    # and let it "die" or not
    count = signal.convolve2d(dungeon.tiles['value'], [[1, 1, 1], [1, 1, 1], [1, 1, 1]], mode = 'same')

    dungeon.tiles[count < wall_rule] = tile_types.wall
    dungeon.tiles[count > wall_rule] = tile_types.floor

    return dungeon