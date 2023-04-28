from game_map import GameMap
from typing import Any
from scipy import signal # type: ignore
import tile_types

def cellular_automata(dungeon: GameMap, wall_rule: int, count: Any) -> GameMap:
    # on each pass we recalculate amount of neighbours, which gives much smoother output
    # more passes equals smoother map and less artifacts
    # we check the number of neighbours including tile itself is less/more than wall_rule
    # and let it "die" or not
    count = signal.convolve2d(dungeon.tiles['value'], [[1, 1, 1], [1, 1, 1], [1, 1, 1]], mode = 'same')

    for i in range(1, dungeon.width - 1):
        for j in range(1, dungeon.height - 1):
            print(f'count [x,y]: {count[i, j]}')
            if count[i, j] < wall_rule:
                dungeon.tiles[i, j] = tile_types.wall
            elif count[i, j] > wall_rule:
                dungeon.tiles[i, j] = tile_types.floor

    return dungeon