from __future__ import annotations

from typing import List, Tuple
from game_map import GameMap
import tile_types

from helpers.rng import nprng
from numpy.random import Generator

from generators.room_generator import RectangularRoom

room_rng = nprng.spawn(1)[0]

def dig_room(room: RectangularRoom, dungeon: GameMap) -> None:
    # dungeon.tiles[[room.x1, room.x2], room.y1:room.y2] = tile_types.wall
    # dungeon.tiles[room.x1:room.x2, [room.y1, room.y2]] = tile_types.wall

    dungeon.tiles[room.inner] = tile_types.floor

def create_room(x: int, y: int, x2: int, y2: int, dungeon: GameMap, rng: Generator) -> RectangularRoom:
    
    if x < 0 or y > dungeon.width or x2 < 0 or y2 > dungeon.height:
        # out of bounds retry
        print(f'out of bounds room placement attempt... skipping')
        x, y = rng.integers(0, dungeon.width - 1), rng.integers(0, dungeon.height- 1)
        room_w, room_h = rng.integers(2, 10), rng.integers(2, 10) 
        create_room(x, y, dungeon, room_rng, room_w, room_h)

    room = RectangularRoom(x, y, x2, y2)

    return room

def place_rooms(starting_room: RectangularRoom, room_min_size: int, room_max_size: int, rooms: List[RectangularRoom], dungeon: GameMap, rng: Generator) -> GameMap:
    new_x = starting_room.x2 + 1
    new_y = starting_room.y2 + 1
    room_w, room_h = rng.integers(room_min_size, room_max_size), rng.integers(room_min_size, room_max_size) 

    direction = rng.choice(['n', 's', 'e', 'w'])
    print(f'\ndirection: {direction}')
    if direction == 'n':
        new_x = max(starting_room.x1 - 1, min(rng.integers(starting_room.x1 - room_w, starting_room.x2 + room_w + 1), starting_room.x2 - 1))
        new_y = starting_room.y1 - room_h - 1
        print(f'prev_room.x1 and height: {starting_room.x1, room_h}')
    elif direction == 's':
        new_x = max(starting_room.x1 - 1, min(rng.integers(starting_room.x1 - room_w, starting_room.x2 + room_w + 1), starting_room.x2 - 1))
        new_y = starting_room.y2 + 1
    elif direction == 'e':
        new_x = starting_room.x2 + 1
        new_y = max(starting_room.y1 - 1, min(rng.integers(starting_room.y1 - room_h, starting_room.y2 + room_h + 1), starting_room.y2 - 1))
    elif direction == 'w':
        new_x = starting_room.x1 - room_w - 1
        new_y = max(starting_room.y1 - 1, min(rng.integers(starting_room.y1 - room_h, starting_room.y2 + room_h + 1), starting_room.y2 - 1))

    if dungeon.in_bounds(new_x, new_y):
        new_room = create_room(new_x, new_y, room_w, room_h, dungeon, room_rng)
        print(f'newx, newy{new_x, new_y} x2, y2: {new_room.x2, new_room.y2}')

        if any(new_room.intersects(other_room) for other_room in rooms):
            # intersection skip
            print(f'room intersecting with exsisting one... skipping placement')
        else:
            print(f'no collision... digging')
            dig_room(new_room, dungeon)

            rooms.append(new_room)
            starting_room = rooms[-1]
    else:
        print(f'not in bounds... skipping to next')

    return dungeon

def generate_rooms(
    dungeon: GameMap,
    max_rooms: int,
    room_min_size: int,
    room_max_size: int,
    rng: Generator,
) -> GameMap:
    rooms: List[RectangularRoom] = []
    x, y = rng.integers(0, dungeon.width - 1), rng.integers(0, dungeon.height- 1)
    room_w, room_h = rng.integers(room_min_size, room_max_size), rng.integers(room_min_size, room_max_size) 

    first_room = create_room(x, y, room_w, room_h, dungeon, room_rng)
    dig_room(first_room, dungeon)

    print(f'first room x, y: {x, y} , x2, y2: {first_room.x2, first_room.y2}')

    rooms.append(first_room)

    for _ in range(max_rooms):
        place_rooms(first_room, room_min_size, room_max_size, rooms, dungeon, rng)

    return dungeon