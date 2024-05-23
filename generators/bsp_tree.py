'''BSP based room generator'''
from __future__ import annotations
from typing import Tuple, List

from helpers.rng import nprng

class Branch:
    def __init__(self, starting_size: Tuple[int, int], starting_position: Tuple[int, int]) -> None:
        self.size = starting_size
        self.position = starting_position
        self.left_child: Branch = None # type: ignore
        self.right_child: Branch = None # type: ignore

    @property
    def center(self) -> Tuple[int, int]:
        return self.size[0] + int(self.position[0] / 2), self.size[1] + int(self.position[1] / 2)

    def split(self, remaining: int, paths: List) -> List:
        split_percent = nprng.uniform(0.3, 0.7)
        split_horizontal = self.size[1] >= self.size[0]

        print(f'split %: {split_percent}, horizontal?: {split_horizontal}')
        if split_horizontal:
            left_height = int(self.size[1] * split_percent)
            self.left_child = Branch((self.size[0], left_height), self.position)
            self.right_child = Branch(
                (self.size[0], self.size[1] - left_height),
                (self.position[0], self.position[1] + left_height)
            )
            print(f'left leaf: {self.left_child.size, self.left_child.position}, right leaf: {self.right_child.size, self.right_child.position}\n')
        else:
            left_width = int(self.size[0] * split_percent)
            self.left_child = Branch((left_width, self.size[1]), self.position)
            self.right_child = Branch(
                (self.size[0] - left_width, self.size[1]),
                (self.position[0] + left_width, self.position[1])
            )
            print(f'left leaf: {self.left_child.size, self.left_child.position}, right leaf: {self.right_child.size, self.right_child.position}\n')

        path = {'left': self.left_child, 'right': self.right_child}

        paths.append(path)

        if remaining > 0:
            self.left_child.split(remaining - 1, paths)
            self.right_child.split(remaining - 1, paths)

        return paths

def get_leaves(branch: Branch) -> list[Branch]: #, paths: List[dict[str, Branch]]
    if branch is None:
        return []
    if branch is not None:
        branches = [branch.left_child, branch.right_child]
        branches.extend(get_leaves(branch.left_child))
        branches.extend(get_leaves(branch.right_child))

    only_branches = [x for x in branches if x != None]

    return only_branches

def branches_overlap(branch1: Branch, branch2: Branch) -> bool:
    x1_min, y1_min = branch1.position
    x1_max, y1_max = x1_min + branch1.size[0], y1_min + branch1.size[1]
    
    x2_min, y2_min = branch2.position
    x2_max, y2_max = x2_min + branch2.size[0], y2_min + branch2.size[1]
    
    overlap = not (x1_max <= x2_min or x1_min >= x2_max or y1_max <= y2_min or y1_min >= y2_max)
    return overlap

# drawing it out, rewrite and implement as function in this file
# 	for path in paths:
# 		if path['left'].y == path['right'].y:
# 			for i in range(path['right'].x - path['left'].x):
# 				tilemap.set_cell(0, Vector2i(path['left'].x+i,path['left'].y), 2, Vector2i(2, 2))
# 		else:
# 			for i in range(path['right'].y - path['left'].y):
# 				tilemap.set_cell(0, Vector2i(path['left'].x,path['left'].y+i), 2, Vector2i(2, 2))