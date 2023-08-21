from __future__ import annotations

from typing import List, Tuple
from game_map import GameMap
import tile_types

from numpy.random import Generator 

from helpers.diggers import tunnel_between, drunken_walk

class RectangularRoom:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height
        self.height = height
        self.width = width

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

def room_digout(room: RectangularRoom, dungeon: GameMap):
    # surrounding walls
    dungeon.tiles[[room.x1, room.x2], room.y1:room.y2 + 1] = tile_types.wall
    dungeon.tiles[room.x1:room.x2 + 1, [room.y1, room.y2]] = tile_types.wall
    # inside of the room
    dungeon.tiles[room.inner] = tile_types.floor

def create_room(min_size: int, max_size: int, dungeon: GameMap, rand_generator: Generator):
    room_w, room_h = rand_generator.integers(min_size, max_size), rand_generator.integers(min_size, max_size)
    x, y = rand_generator.integers(0, dungeon.width - room_w - 1), rand_generator.integers(0, dungeon.height - room_h - 1)

    if x < 0 or y > dungeon.width or room_w < 0 or room_h > dungeon.height:
        print(f'Out of bounds corners, retry')
        create_room(min_size, max_size, dungeon, rand_generator)

    room = RectangularRoom(x, y, room_w, room_h)

    return room

def generate_rooms(
    dungeon: GameMap,
    max_rooms: int,
    room_min_size: int,
    room_max_size: int,
    rand_generator: Generator,
) -> GameMap:
    rooms: List[RectangularRoom] = []

    new_room = create_room(room_min_size, room_max_size, dungeon, rand_generator)

    # # make sure the new room doesn't go out of bounds of the GameMap
    # if new_room.x1 < 0 or new_room.x2 > dungeon.width or new_room.y1 < 0 or new_room.y2 > dungeon.height:
    #     new_room = create_room(room_min_size, room_max_size, dungeon)

    room_digout(new_room, dungeon)

    (player_x, player_y) = new_room.center
    dungeon.engine.player.place(player_x, player_y, dungeon)

    rooms.append(new_room)

    # add new rooms adjacent to previous ones, up to max_rooms
    for _ in range(max_rooms):
        prev_room = rooms[-1]
        # direction = nprng.choice(["n", "s", "e", "w"])
        # if direction == "n":
        #     x = nprng.integers(prev_room.x1, prev_room.x2)
        #     y = prev_room.y1 - new_room.height
        # elif direction == "s":
        #     x = nprng.integers(prev_room.x1, prev_room.x2)
        #     y = prev_room.y2
        # elif direction == "e":
        #     x = prev_room.x2
        #     y = nprng.integers(prev_room.y1, prev_room.y2)
        # elif direction == "w":
        #     x = prev_room.x1 - new_room.width
        #     y = nprng.integers(prev_room.y1, prev_room.y2)

        new_room = create_room(room_min_size, room_max_size, dungeon, rand_generator)

        if any(new_room.intersects(other_room) for other_room in rooms):
            print(f'rooms intersecting')
            continue
        
        room_digout(new_room, dungeon)

        for x, y in tunnel_between(prev_room.center, new_room.center, rand_generator):
            dungeon.tiles[x, y] = tile_types.floor

        rooms.append(new_room)

    return dungeon
