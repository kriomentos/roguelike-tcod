'''
In it's current stae it doesn't
requires rewrite of Bresenham line tunnel creator
generation method, placing entities and passing arguments
'''
from __future__ import annotations
import random
from typing import Iterator, List, Tuple
from game_map import GameMap
import tile_types
import tcod


TILE_MAPPING = {
    0: '#',
    1: '.',
    2: '@'
}

class RectangularRoom:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height

    @property
    def center(self) -> Tuple[int, int]:
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)

        return center_x, center_y

    # return inside of the room, not counting the walls
    @property
    def inner(self) -> Tuple[slice, slice]:
        return slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2)

    def intersects(self, other: RectangularRoom) -> bool:
        return(
            self.x1 <= other.x2
            and self.x2 >= other.x1
            and self.y1 <= other.y2
            and self.y2 >= other.y1
        )

def tunnel_between(start: Tuple[int, int], end: Tuple[int, int]) -> Iterator[Tuple[int, int]]:
    # return L shaped tunnel between two points
    x1, y1 = start
    x2, y2 = end

    if random.random() < 0.5:
        # go horizontal, then vertical
        corner_x, corner_y = x2, y1
    else:
        # go vertical, then horizontal
        corner_x, corner_y = x1, y2

    for x, y in tcod.los.bresenham((x1, y1), (corner_x, corner_y)).tolist():
        yield x, y
    for x, y in tcod.los.bresenham((corner_x, corner_y), (x2, y2)).tolist():
        yield x, y

# def neighbour(node):
#     dirs = [[1, 0], [0, 1], [-1, 0], [0, -1]]
#     result = []
#     for dir in dirs:
#         neighbor = [node[0].center + dir[1], node[1].center + dir[1]]
#         if neighbor in rooms:
#             result.append(neighbor)
#     return result

def generate_dungeon(
    max_rooms: int,
    room_min_size: int,
    room_max_size: int,
    map_width: int,
    map_height: int,
) -> GameMap:

    dungeon = GameMap(map_width, map_height)

    rooms: List[RectangularRoom] = []

    for r in range(max_rooms):
        room_width = random.randint(room_min_size, room_max_size)
        room_height = random.randint(room_min_size, room_max_size)

        x = random.randint(0, dungeon.width - room_width - 1)
        y = random.randint(0, dungeon.height - room_height - 1)

        new_room = RectangularRoom(x, y, room_width, room_height)

        if any(new_room.intersects(other_room) for other_room in rooms):
            continue # intersects go next room
        # if not then room is valid

        # dig out the room
        dungeon.tiles[new_room.inner] = tile_types.floor

        if len(rooms) == 0:
            # spawn player in first room
            pass
        else:
            # dig out tunnels for the current room and the previous one, we don't do it for first, as it has no room previous to it
            for x, y in tunnel_between(rooms[-1].center, new_room.center):
                dungeon.tiles[x, y] = tile_types.floor

        # we add the new room to our list of rooms
        rooms.append(new_room)

        # hacked way of placing player glyph just for graphic representation
        dungeon.tiles[rooms[0].center] = tile_types.placeholder

        # print(rooms.type())
    return dungeon

def print_map(map):
    print('\n'.join(
        ((' '.join((TILE_MAPPING[cell] for cell in row))) for row in map.tiles['value'])
    ))

if __name__ == '__main__':
    player = 2
    map = generate_dungeon(
        30, # max rooms
        6, # min room size
        10, # max room size
        45, # height
        80  # width
    )
    start = (20, 25)
    # parents = breadth_first()
    print_map(map)