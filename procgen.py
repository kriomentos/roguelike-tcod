from __future__ import annotations
from copy import deepcopy
from tcod import los

from random import choices, randint, seed
from typing import Dict, Tuple, List, Set, Iterator, TYPE_CHECKING
from scipy import signal

import numpy as np
import components
from engine import Engine

from game_map import GameMap
import tile_types
import entity_factories

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity

int_seed = 0
base_seed = 'ragnis'
for ch in base_seed:
    int_seed <<= 8 + ord(ch)

seed(int_seed)

nprng = np.random.default_rng()

# tuples that contain information (floor number, maximum amount of entity type)
# used for generating amount of said entities based on current floor level
max_items_per_floor = [
    (1, 1),
    (4, 2),
    (6, 3),
]
max_monsters_per_floor = [
    (1, 2),
    (4, 3),
    (6, 5),
]

# dictionaires of weighted entites for spawning
# higher weight means higher chance of spawning
# dict key is the floor number where they start appearing
item_chances: Dict[int, List[Tuple[Entity, int]]] = {
    0: [(entity_factories.health_potion, 35),
        (entity_factories.power_ring, 5),
        (entity_factories.defense_ring, 5),
        (entity_factories.goblin, 50)],
    2: [(entity_factories.confusion_scroll, 10)],
    4: [(entity_factories.lightning_scroll, 25),
        (entity_factories.sword, 10),
        (entity_factories.power_ring, 5),
        (entity_factories.defense_ring, 5)],
    6: [(entity_factories.fireball_scroll, 25),
        (entity_factories.chain_mail, 10),
        (entity_factories.omni_ring, 5)],
    9: [(entity_factories.health_potion, 20),
        (entity_factories.chain_mail, 10),
        (entity_factories.confusion_scroll, 20)]
}

enemy_chances: Dict[int, List[Tuple[Entity, int]]] = {
    0: [(entity_factories.orc, 80)],
    3: [(entity_factories.troll, 15)],
    5: [(entity_factories.troll, 30)],
    7: [(entity_factories.orc, 25),
        (entity_factories.troll, 45)],
}

def get_max_value_for_floor(
    max_value: List[Tuple[int, int]], floor: int
) -> int:
    current_value = 0

    for floor_minimum, value in max_value:
        if floor_minimum > floor:
            break
        else:
            current_value = value

    return current_value

def get_entities_at_random(
    weighted_chance_by_floor: Dict[int, List[Tuple[Entity, int]]],
    number_of_entities: int,
    floor: int,
) -> List[Entity]:
    entity_weighted_chances = {}

    for key, values in weighted_chance_by_floor.items():
        if key > floor:
            break
        else:
            for value in values:
                entity = value[0]
                weighted_chance = value[1]

                entity_weighted_chances[entity] = weighted_chance

    entities = list(entity_weighted_chances.keys())
    entity_weighted_chance_values = list(entity_weighted_chances.values())

    chosen_entities = choices(
        entities, weights = entity_weighted_chance_values, k = number_of_entities
    )

    return chosen_entities

def place_entities(dungeon: GameMap, floor_number: int) -> None:
    number_of_monsters = randint(
        0, get_max_value_for_floor(max_monsters_per_floor, floor_number)
    )
    number_of_items = randint(
        0, get_max_value_for_floor(max_items_per_floor, floor_number)
    )

    # select random postion for enemy using numpy.where
    # we look only at positions that are floors,
    # this way we avoid placing the enemies in walls,
    # and we don't need more complicated checks
    x, y = np.where(dungeon.tiles['walkable'])

    monsters: List[Entity] = get_entities_at_random(
        enemy_chances, number_of_monsters, floor_number
    )
    items: List[Entity] = get_entities_at_random(
        item_chances, number_of_items, floor_number
    )

    for entity in monsters + items:
        # we generate random integer from tiles we found as viable
        # it's used later to select given index in the game_map array
        j = nprng.integers(len(x))

        # check if the selected spot doesn't contain any entity already
        # if it does not then place one of the monsters
        # 80% chance for orc 20% for troll
        if not any(entity.x == x[j] and entity.y == y[j] for entity in dungeon.entities):
            entity.spawn(dungeon, x[j], y[j])
            if entity is entity_factories.goblin:
                entity_factories.sword.spawn(dungeon, x[j] - 2, y[j])
                entity_factories.health_potion.spawn(dungeon, x[j] - 1, y[j] - 2)
            print(f'Placed {entity.name} at: ', x[j], y[j])

    j = nprng.integers(len(x))

    # insert stairs going down the level
    dungeon.tiles[x[j], y[j]] = tile_types.down_stairs
    dungeon.downstairs_location = (x[j], y[j])
    # insert stairs going up level
    # dungeon.tiles[x[j + 1], y[j + 1]] = tile_types.up_stairs
    # dungeon.upstairs_location = (x[j + 1], y[j + 1])

# in future it wll take all gamemap objects (not Actors!)
# and turn some into mimics, or not
def make_mimic(dungeon: GameMap):
    target = dungeon.get_actor_at_location(40, 21)
    target.ai = components.ai.MimicHostileEnemy(
        entity = target, message = False, origin_x = target.x, origin_y = target.y
    )

def cellular_automata(dungeon: GameMap, wall_rule: int, count: GameMap):
    # on each pass we recalculate amount of neighbours, which gives much smoother output
    # more passes equals smoother map and less artifacts
    # we check the number of neighbours including tile itself is less/more than wall_rule
    # and let it "die" or not
    count = signal.convolve2d(dungeon.tiles['value'], [[1, 1, 1], [1, 1, 1], [1, 1, 1]], mode = 'same')

    for i in range(1, dungeon.width - 1):
        for j in range(1, dungeon.height - 1):
            if count[i, j] < wall_rule:
                dungeon.tiles[i, j] = tile_types.wall
            elif count[i, j] > wall_rule:
                dungeon.tiles[i, j] = tile_types.floor

    return dungeon

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

def add_entrances(
    room: RectangularRoom,
    dungeon: GameMap,
) -> Tuple[int, int]:
    # place randomly entrances for the rooms
    direction = nprng.choice(['n', 's', 'e', 'w'])
    if direction == "n":
        point_x = nprng.integers(room.x1 + 1, room.x2 - 1)
        point_y = room.y1
    elif direction == "s":
        point_x = nprng.integers(room.x1 + 1, room.x2 - 1)
        point_y = room.y2
    elif direction == "e":
        point_x = room.x1
        point_y = nprng.integers(room.y1 + 1, room.y2 - 1)
    elif direction == "w":
        point_x = room.x2
        point_y = nprng.integers(room.y1 + 1, room.y2 - 1)

    if point_x <= 0 or point_x >= dungeon.width or point_y <= 0 or point_y >= dungeon.height:
        print(f'tried to place another one x, y: {point_x, point_y}')
        add_entrances()

    return (point_x, point_y)

def connect_regions(dungeon: GameMap):
    # We can identify the different regions of the dungeon by flood-filling the floor tiles
    regions = get_regions(dungeon.tiles["walkable"])

    # If there is only one region, there is no need to connect anything
    if len(regions) < 2:
        return

    # Otherwise, we need to connect the regions
    # We can do this by finding the closest pair of points between regions and carving a tunnel between them
    closest_points = get_closest_points_between_regions(regions)
    # print(f'points: {closest_points}')
    for pair in closest_points:
        print(f'pair is a: {pair[0]} and b: {pair[1]}')
        for x, y in tunnel_between(pair[0], pair[1]):
            dungeon.tiles[x, y] = tile_types.floor

def get_regions(walkable: np.ndarray) -> List[Set[Tuple[int, int]]]:
    regions = []
    visited = set()

    for x in range(walkable.shape[0]):
        for y in range(walkable.shape[1]):
            if (x, y) in visited or not walkable[x, y]:
                continue

            new_region = set()
            queue = [(x, y)]

            while queue:
                current = queue.pop(0)

                if current in visited or not walkable[current]:
                    continue

                new_region.add(current)
                visited.add(current)

                neighbours = [(current[0] - 1, current[1]),
                              (current[0] + 1, current[1]),
                              (current[0], current[1] - 1),
                              (current[0], current[1] + 1)]

                for neighbour in neighbours:
                    if neighbour not in visited and walkable[neighbour]:
                        queue.append(neighbour)

            if new_region:
                regions.append(new_region)

    return regions

def get_closest_points_between_regions(regions: List[Set[Tuple[int, int]]]) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
    points = [(list(region)[0], min(region, key=lambda p: distance_to_region(p, regions))) for region in regions]
    return [(p1, p2) for p1, p2, _ in sorted([(p1, p2, distance(p1, p2)) for i, (p1, d1) in enumerate(points) for j, (p2, d2) in enumerate(points) if i < j], key=lambda t: t[2])]
    # return [(p1, p2) for i, (p1, d1) in enumerate(points) for j, (p2, d2) in enumerate(points) if i < j and d1 == d2]

def distance_to_region(point_1: Tuple[int, int], regions: List[Set[Tuple[int, int], Tuple[int,int]]]) -> float:
    return min(distance(point_1, q) for region in regions for q in region)

def distance(point_1: Tuple[int, int], point_2: Tuple[int, int]) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    return np.sqrt((point_1[0] - point_2[0]) ** 2 + (point_1[1] - point_2[1]) ** 2)

def generate_rooms(
    dungeon: GameMap,
    max_rooms: int,
    room_min_size: int,
    room_max_size: int,
) -> List[Tuple[int, int, int, int]]:

    rooms: List[RectangularRoom] = []

    room_width, room_height = nprng.integers(room_min_size, room_max_size), nprng.integers(room_min_size, room_max_size)

    # random position within map bounds
    x = nprng.integers(0, dungeon.width - room_width - 1)
    y = nprng.integers(0, dungeon.height - room_height - 1)

    new_room = RectangularRoom(x, y, room_width, room_height)
    # make sure the new room doesn't go out of bounds of the GameMap
    if new_room.x1 < 0 or new_room.x2 > dungeon.width or new_room.y1 < 0 or new_room.y2 > dungeon.height:
        return dungeon

    # dig out the room
    # top and bottom wall
    dungeon.tiles[x:x+room_width, y] = tile_types.wall
    dungeon.tiles[x:x+room_width +1, y+room_height] = tile_types.wall
    # left and right wall
    dungeon.tiles[x, y:y+room_height] = tile_types.wall
    dungeon.tiles[x+room_width, y:y+room_height] = tile_types.wall
    dungeon.tiles[new_room.inner] = tile_types.floor

    (player_x, player_y) = new_room.center
    dungeon.engine.player.place(player_x, player_y, dungeon)

    rooms.append(new_room)

    a, b = add_entrances(new_room, dungeon)
    dungeon.tiles[a, b] = tile_types.floor

    # add new rooms adjacent to previous ones, up to max_rooms
    for r in range(1, max_rooms):
        prev_room = rooms[-1]
        direction = nprng.choice(["n", "s", "e", "w"])
        if direction == "n":
            x = nprng.integers(prev_room.x1, prev_room.x2)
            y = prev_room.y1 - room_height
        elif direction == "s":
            x = nprng.integers(prev_room.x1, prev_room.x2)
            y = prev_room.y2
        elif direction == "e":
            x = prev_room.x2
            y = nprng.integers(prev_room.y1, prev_room.y2)
        elif direction == "w":
            x = prev_room.x1 - room_width
            y = nprng.integers(prev_room.y1, prev_room.y2)

        # Generate random room width and height
        room_width = nprng.integers(room_min_size, room_max_size)
        room_height = nprng.integers(room_min_size, room_max_size)

        new_room = RectangularRoom(x, y, room_width, room_height)
        # make sure the new room doesn't go out of bounds of the GameMap
        if new_room.x1 < 0 or new_room.x2 > dungeon.width or new_room.y1 < 0 or new_room.y2 > dungeon.height:
            continue

        if any(new_room.intersects(other_room) for other_room in rooms):
            continue

        #top and bottom wall
        dungeon.tiles[x:x+room_width, y] = tile_types.wall
        dungeon.tiles[x:x+room_width +1, y+room_height] = tile_types.wall
        # left and right wall
        dungeon.tiles[x, y:y+room_height] = tile_types.wall
        dungeon.tiles[x+room_width, y:y+room_height] = tile_types.wall
        # inside of the room
        dungeon.tiles[new_room.inner] = tile_types.floor

        a, b = add_entrances(new_room, dungeon)
        dungeon.tiles[a, b] = tile_types.floor

        for x, y in tunnel_between(prev_room.center, new_room.center):
            dungeon.tiles[x, y] = tile_types.floor

        rooms.append(new_room)

    return dungeon

def generate_dungeon(
    map_width: int,
    map_height: int,
    initial_open: int,
    convolve_steps: int,
    engine: Engine,
) -> GameMap:
    # Generate a new dungeon map.
    player = engine.player
    dungeon = GameMap(engine, map_width, map_height, entities = [player])
    # helper map to hold convolve calculation
    wall_count = GameMap(engine, map_width, map_height)

    # dang fast way of filling map randomly
    dungeon.tiles = np.where(nprng.integers(0, 100, (map_height, map_width)).T > initial_open,
        tile_types.floor, tile_types.wall
    )

    # ensures surrounding wall
    dungeon.tiles[[0, -1], :] = tile_types.wall
    dungeon.tiles[:, [0, -1]] = tile_types.wall

    # we go through the map and simulate cellular automata rules using convolve values
    for _ in range(convolve_steps):
        cellular_automata(dungeon, 4, wall_count)

    x, y = np.where(dungeon.tiles["walkable"])
    j = nprng.integers(len(x))
    player.place(x[j], y[j], dungeon)

    for _ in range(1):
        generate_rooms(dungeon, 10, 4, 10)

    connect_regions(dungeon)

    for _ in range(2):
        cellular_automata(dungeon, 4, wall_count)

    place_entities(dungeon, engine.game_world.current_floor)

    return dungeon