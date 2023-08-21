from __future__ import annotations

from typing import List, Set, Tuple
import numpy as np

from game_map import GameMap
import tile_types

from helpers.diggers import tunnel_between

from numpy.random import Generator

def connect_regions(dungeon: GameMap, rand_generator: Generator):
    # We can identify the different regions of the dungeon by flood-filling the floor tiles
    regions = get_regions(dungeon.tiles["walkable"])

    # If there is only one region, there is no need to connect anything
    if len(regions) < 2:
        return

    # Otherwise, we need to connect the regions
    # We can do this by finding the closest pair of points between regions and carving a tunnel between them
    closest_points = get_closest_points_between_regions(regions)
    for pair in closest_points:
        print(f'pair is a: {pair[0]} and b: {pair[1]}')
        for x, y in tunnel_between(pair[0], pair[1], rand_generator):
            dungeon.tiles[x, y] = tile_types.floor
        closest_points.pop(0)
    # center_point = (40, 20)
    # points = get_center_points(regions)
    # for _ in points:
    #     print(f'going from: {points[0]} to: {center_point}')
    #     for x, y in tunnel_between(points[0], center_point):
    #         dungeon.tiles[x, y] = tile_types.placeholder
    #     points.pop(0)

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

def distance_to_region(point_1: Tuple[int, int], regions: List[Set[Tuple[int, int]]]) -> float:
    return min(distance(point_1, q) for region in regions for q in region)

def distance(point_1: Tuple[int, int], point_2: Tuple[int, int]) -> float:
    return (point_1[0] - point_2[0]) ** 2 + (point_1[1] - point_2[1]) ** 2