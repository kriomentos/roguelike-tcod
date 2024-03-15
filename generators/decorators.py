from __future__ import annotations
from game_map import GameMap
import tile_types

import numpy as np
import numpy.typing as npt

from helpers.rng import nprng
from helpers.diggers import drunken_walk

def add_features(dungeon: GameMap) -> GameMap:
    x, y = np.where(dungeon.tiles['walkable'])

    for _ in range(len(x)):
        j = nprng.integers(len(x))

        feature = nprng.choice(4)
        chance = nprng.random()

        if feature == 0:
            if chance < .10:
                dungeon.tiles[x[j], y[j]] = tile_types.loose_grass
            elif chance < .5:
                dungeon.tiles[x[j], y[j]] = tile_types.grass
            elif chance < .2:
                dungeon.tiles[x[j], y[j]] = tile_types.dense_grass
        elif feature == 1:
            if chance < .10:
                dungeon.tiles[x[j], y[j]] = tile_types.loose_rubble
            elif chance < .5:
                dungeon.tiles[x[j], y[j]] = tile_types.rubble
        elif feature == 2:
            if chance < .5:
                dungeon.tiles[x[j], y[j]] = tile_types.stalactite
            elif chance > .5:
                dungeon.tiles[x[j], y[j]] = tile_types.stalagmite
        # elif feature == 3:
        #     print(f'\n\nAdding single water spot...\n\n')
        #     add_aquifers(x[j], y[j], dungeon)

    return dungeon

def add_aquifers(x: int, y: int, dungeon: GameMap):
    chance = nprng.random()

    start = (x, y)

    spill_size = nprng.integers(1, 10)
    max_step = 100 # nprng.integers(0, 50)
    spill_step = 0
    spill_direction = nprng.integers(0, 3)

    if spill_direction == 0:
        end = (x - spill_size, y - spill_size)
    elif spill_direction == 1:
        end = (x - spill_size, y + spill_size)
    elif spill_direction == 2:
        end = (x + spill_size, y - spill_size)
    elif spill_direction == 3:
        end = (x + spill_size, y + spill_size)

    while spill_step != max_step:
        if nprng.random() < .5: # up or down
            if nprng.random() < .5:
                x += 1 # go down
            else:
                x += -1 # go up
        else: # left or right
            if nprng.random() < .5:
                y += 1 # go right
            else:
                y += -1 # go left

        spill_step += 1

        x = max(1, min(x, dungeon.width - 3))
        y = max(1, min(y, dungeon.height - 3))

        walkable_tiles = np.where(dungeon.tiles['walkable'])
        
        if x in walkable_tiles[0] and y in walkable_tiles[1]:
            dungeon.tiles[x, y] = tile_types.shallow_water

    return

def add_grass_features(dungeon: GameMap) -> GameMap:
    # Implement logic to add stalagmites and stalactites to the cave map
    x, y = np.where(dungeon.tiles['walkable'])
    
    for _ in range(len(x)):
        j = nprng.integers(len(x))
        chance = nprng.integers(0, 100)
        if chance <= 10:
            dungeon.tiles[x[j], y[j]] = tile_types.loose_grass
        elif 10 <= chance <= 15:
            dungeon.tiles[x[j], y[j]] = tile_types.grass
        elif 10 <= chance <= 11:
            dungeon.tiles[x[j], y[j]] = tile_types.dense_grass

    return dungeon

def add_water_features(dungeon: GameMap):
    # Implement logic to add water features like pools or underground streams
    pass

def add_rubble_and_details(dungeon: GameMap):
    # Implement logic to add random rock rubble, debris, or other atmospheric details
    x, y = np.where(dungeon.tiles['walkable'])
    
    for _ in range(len(x)):
        j = nprng.integers(len(x))
        chance = nprng.integers(0, 100)
        if 10 <= chance <= 15:
            dungeon.tiles[x[j], y[j]] = tile_types.loose_rubble
        elif chance <= 10:
            dungeon.tiles[x[j], y[j]] = tile_types.rubble

    return dungeon

def add_rock_features(dungeon: GameMap):
    # Implement logic to add random rock rubble, debris, or other atmospheric details
    x, y = np.where(dungeon.tiles['walkable'])
    
    for _ in range(len(x)):
        j = nprng.integers(len(x))
        chance = nprng.integers(0, 100)
        if chance <= 1:
            dungeon.tiles[x[j], y[j]] = tile_types.stalactite
        elif chance <= 5:
            dungeon.tiles[x[j], y[j]] = tile_types.stalagmite

    return dungeon