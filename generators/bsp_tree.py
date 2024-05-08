'''BSP based room generator'''
from __future__ import annotations
from typing import Tuple, List

from helpers.rng import nprng

class Branch:
    def __init__(self, starting_size: Tuple[int, int], starting_position: Tuple[int, int]) -> None:
        self.size = starting_size
        self.position = starting_position

    @property
    def center(self) -> Tuple[int, int]:
        return self.size[0] + self.position[0] / 2, self.size[1] + self.position[1] / 2

    def split(self, remaining: int, paths: List):
        split_percent = nprng.uniform(0.3, 0.7)
        split_horizontal = self.size[1] >= self.size[0]

        print(f'size: {self.size}, position: {self.position}')
        print(f'split %: {split_percent}, horizontal?: {split_horizontal}')
        if split_horizontal:
            left_height = int(self.size[1] * split_percent)
            left_child = Branch((self.size[0], left_height), self.position)
            right_child = Branch(
                (self.size[0], self.size[1] - left_height),
                (self.position[0], self.position[1] + left_height)
            )
            print(f'split horizontal')
        else:
            left_width = int(self.size[0] * split_percent)
            left_child = Branch((left_width, self.size[1]), self.position)
            right_child = Branch(
                (self.size[0] - left_width, self.size[1]),
                (self.position[0] + left_width, self.position[1])
            )
            print(f'split vertical')

        path = {'left': left_child.center, 'right': right_child.center}

        paths.append(path)

        if remaining > 0:
            left_child.split(remaining - 1, paths)
            right_child.split(remaining - 1, paths)

        return paths

    def get_leaves(self, paths: List):
        if not paths:
            return self
        else:
           for path in paths:
               print(f'path: {path}\n')
# drawing it out, rewrite and implement as function in this file

# extends Node2D

# var root_node: Branch
# var tile_size: int =  16
# var world_size = Vector2i(60,30)

# var tilemap: TileMap
# var paths: Array = []

# func _draw():
# 	var rng = RandomNumberGenerator.new()
# 	for leaf in root_node.get_leaves():
# 		var padding = Vector4i(rng.randi_range(2,3),rng.randi_range(2,3),rng.randi_range(2,3),rng.randi_range(2,3))
# 		for x in range(leaf.size.x):
# 			for y in range(leaf.size.y):
# 				if not is_inside_padding(x,y, leaf, padding) :
# 					tilemap.set_cell(0, Vector2i(x + leaf.position.x,y + leaf.position.y), 2, Vector2i(2, 2))
# 	for path in paths:
# 		if path['left'].y == path['right'].y:
# 			for i in range(path['right'].x - path['left'].x):
# 				tilemap.set_cell(0, Vector2i(path['left'].x+i,path['left'].y), 2, Vector2i(2, 2))
# 		else:
# 			for i in range(path['right'].y - path['left'].y):
# 				tilemap.set_cell(0, Vector2i(path['left'].x,path['left'].y+i), 2, Vector2i(2, 2))
# func _ready():
# 	tilemap = get_node("TileMap")
# 	root_node  = Branch.new(Vector2i(0,0), world_size)
# 	root_node.split(2, paths)
# 	queue_redraw()
# 	pass

# func is_inside_padding(x, y, leaf, padding):
# 	return x <= padding.x or y <= padding.y or x >= leaf.size.x - padding.z or y >= leaf.size.y - padding.w
