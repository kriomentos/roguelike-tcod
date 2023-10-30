from __future__ import annotations
from game_map import GameMap
import tile_types

import numpy as np

from helpers.rng import nprng


def add_grass_features(dungeon: GameMap) -> GameMap:
    # Implement logic to add stalagmites and stalactites to the cave map
    x, y = np.where(dungeon.tiles['walkable'])
    
    for _ in range(len(x)):
        j = nprng.integers(len(x))
        select = nprng.integers(0, 100)
        if select <= 10:
            dungeon.tiles[x[j], y[j]] = tile_types.loose_grass
        elif 10 <= select <= 15:
            dungeon.tiles[x[j], y[j]] = tile_types.grass
        elif 10 <= select <= 11:
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
        select = nprng.integers(0, 100)
        if 10 <= select <= 15:
            dungeon.tiles[x[j], y[j]] = tile_types.loose_rubble
        elif select <= 10:
            dungeon.tiles[x[j], y[j]] = tile_types.rubble

    return dungeon

def add_rock_features(dungeon: GameMap):
    # Implement logic to add random rock rubble, debris, or other atmospheric details
    x, y = np.where(dungeon.tiles['walkable'])
    
    for _ in range(len(x)):
        j = nprng.integers(len(x))
        select = nprng.integers(0, 100)
        if select <= 1:
            dungeon.tiles[x[j], y[j]] = tile_types.stalactite
        elif select <= 5:
            dungeon.tiles[x[j], y[j]] = tile_types.stalagmite

    return dungeon