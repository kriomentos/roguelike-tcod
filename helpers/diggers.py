from tcod import los
from game_map import GameMap

from typing import Tuple, Iterator
from helpers.rng import nprng

def tunnel_between(start: Tuple[int, int], end: Tuple[int, int]) -> Iterator[Tuple[int, int]]:
    # return L shaped tunnel between two points
    x1, y1 = start
    target_x, target_y = end

    if nprng.random() < 0.5:
        # go horizontal, then vertical
        corner_x, corner_y = target_x, y1
    else:
        # go vertical, then horizontal
        corner_x, corner_y = x1, target_y

    for x, y in los.bresenham((x1, y1), (corner_x, corner_y))[1:-1].tolist():
        yield x, y
    for x, y in los.bresenham((corner_x, corner_y), (target_x, target_y))[1:-1].tolist():
        yield x, y

def drunken_walk(start: Tuple[int, int], end: Tuple[int, int], dungeon: GameMap) -> Iterator[Tuple[int, int]]:
    x, y = start
    target_x, target_y = end

    while (x, y) != end:
        if x < target_x:
            x += nprng.choice([0, 1])
        elif x > target_x:
            x += nprng.choice([0, 1])
        if y < target_y:
            y += nprng.choice([0, 1])
        elif y > target_y:
            y += nprng.choice([0, 1])

        x = max(1, min(x, dungeon.width - 1))
        y = max(1, min(y, dungeon.height - 1))

        yield x, y