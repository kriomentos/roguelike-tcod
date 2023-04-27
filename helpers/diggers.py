from tcod import los
from typing import Tuple, Iterator
from helpers.default_rng import nprng

def tunnel_between(start: Tuple[int, int], end: Tuple[int, int]) -> Iterator[Tuple[int, int]]:
    # return L shaped tunnel between two points
    x1, y1 = start
    x2, y2 = end

    if nprng.random() < 0.5:
        # go horizontal, then vertical
        corner_x, corner_y = x2, y1
    else:
        # go vertical, then horizontal
        corner_x, corner_y = x1, y2

    for x, y in los.bresenham((x1, y1), (corner_x, corner_y)).tolist():
        yield x, y
    for x, y in los.bresenham((corner_x, corner_y), (x2, y2)).tolist():
        yield x, y