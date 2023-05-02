from __future__ import annotations

from random import choices, randint
from typing import Dict, Tuple, List, TYPE_CHECKING

import numpy as np
from engine import Engine

from game_map import GameMap
import tile_types
import entity_factories

from helpers.rng import nprng
from helpers.region_connection import connect_regions

from generators.cellular_automata import cellular_automata
from generators.room_generatorv2 import generate_rooms

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity

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

    # connect_regions(dungeon)

    # for _ in range(2):
    #     cellular_automata(dungeon, 4, wall_count)

    place_entities(dungeon, engine.game_world.current_floor)

    return dungeon