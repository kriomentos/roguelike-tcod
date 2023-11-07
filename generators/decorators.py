from __future__ import annotations
from game_map import GameMap
import tile_types

import numpy as np

from helpers.rng import nprng

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

    return dungeon

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