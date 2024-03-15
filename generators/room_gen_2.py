from __future__ import annotations

from typing import List, Tuple
from game_map import GameMap
import tile_types

from helpers.rng import nprng
from numpy.random import Generator

from generators.room_generator import RectangularRoom

room_rng = nprng.spawn(1)[0]

def dig_room(room: RectangularRoom, dungeon: GameMap):
    # dungeon.tiles[[room.x1, room.x2], room.y1:room.y2] = tile_types.wall
    # dungeon.tiles[room.x1:room.x2, [room.y1, room.y2]] = tile_types.wall

    dungeon.tiles[room.inner] = tile_types.floor

def create_room(min_size: int, max_size: int, x: int, y: int, dungeon: GameMap, rng: Generator):
    room_w, room_h = rng.integers(min_size, max_size), rng.integers(min_size, max_size)
    
    if x < 0 or y > dungeon.width or room_w < 0 or room_h > dungeon.height:
        # out of bounds retry
        # x, y = rng.integers(0, dungeon.width - 1), rng.integers(0, dungeon.height- 1)
        create_room(min_size, max_size, x, y, dungeon, room_rng)

    room = RectangularRoom(x, y, room_w, room_h)

    return room

def generate_rooms(
    dungeon: GameMap,
    max_rooms: int,
    room_min_size: int,
    room_max_size: int,
    rng: Generator,
) -> GameMap:
    rooms: List[RectangularRoom] = []
    x, y = rng.integers(0, dungeon.width - 1), rng.integers(0, dungeon.height- 1)
    print(f'x, y: {x, y}')

    new_room = create_room(room_min_size, room_max_size, 1, 1, dungeon, room_rng)
    dig_room(new_room, dungeon)

    rooms.append(new_room)
    prev_room = new_room
    for _ in range(max_rooms):
        new_x = prev_room.x2
        new_y = prev_room.y2
        # direction = rng.choice(['n', 's', 'e', 'w'])
        # if direction == 'n':
        #     new_x = rng.integers(prev_room.x1, prev_room.x2)
        #     new_y = prev_room.y1 - new_room.height
        # elif direction == 's':
        #     new_x = rng.integers(prev_room.x1, prev_room.x2)
        #     new_y = prev_room.y1
        # elif direction == 'e':
        #     new_x = prev_room.x1
        #     new_y = rng.integers(prev_room.y1, prev_room.y2)
        # elif direction == 'w':
        #     new_x = prev_room.x1 - new_room.width
        #     new_y = rng.integers(prev_room.y1, prev_room.y2)

        print(f'newx, newy{ new_x, new_y}')
        new_room = create_room(room_min_size, room_max_size, new_x, new_y, dungeon, room_rng)

        if any(new_room.intersects(other_room) for other_room in rooms):
            # intersection skip
            continue
        
        dig_room(new_room, dungeon)

        rooms.append(new_room)
        prev_room = rooms[-1]

    return dungeon