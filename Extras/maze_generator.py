import random
import re
import numpy as np
import sys
from typing import Tuple

from tcod import heightmap_add

sys.setrecursionlimit(10000)

EMPTY = -1
WALL = 0
VISITED = 0.5
FLOOR = 1
DOOR = 2

TILE_MAPPING = {
    EMPTY: ' ',
    WALL: '#',
    VISITED: '+',
    FLOOR: '.',
    DOOR: '@'
}

class Maze:
    def __init__(self, width, height):
        if width % 2 == 0:
            width += 1
        if height % 2 == 0:
            height += 1

        self.width = width
        self.height = height
        self.__maze = np.ones((width, height), dtype = float)

    def start_end(self) -> Tuple[int, int]:
        dir = [1, 2, 3, 4]
        facing = random.choice(dir)
        if facing == 1: # TOP WALL
            point = [1, random.randrange(2, self.width - 2)]
            if self.__maze[2, point[1]] == 0:
                point[1] = random.randrange(2, self.width - 2)
        elif facing == 2: # BOTTOM WALL
            point = [self.height - 2, random.randrange(2, self.width - 2)]
        elif facing == 3: # LEFT WALL
            point = [random.randrange(2, self.width - 2), 1]
        elif facing == 4: # RIGHT WALL
            point = [random.randrange(2, self.width - 2), self.width - 2]

        return point

    def gen_map(self):
        for i in range(self.width):
            for j in range(self.height):
                if i % 2 == 1 or j % 2 == 1:
                    self.__maze[i, j] = 0
                if i == 0 or j == 0 or i == self.height - 1 or j == self.width - 1:
                    self.__maze[i, j] = 0.5

        sx = random.choice(range(2, self.width - 2, 2))
        sy = random.choice(range(2, self.height - 2, 2))

        self.generate(sx, sy)

        for i in range(self.width):
            for j in range(self.height):
                if self.__maze[i, j] == 0.5:
                    self.__maze[i, j] = 1
                if i == 0 or j == 0 or i == self.height - 1 or j == self.width - 1:
                    self.__maze[i, j] = -1

        start = self.start_end()
        end = self.start_end()

        self.__maze[start[0], start[1]] = 1
        self.__maze[end[0], end[1]] = 1

        return 0
    
    def generate(self, cx, cy):
        self.__maze[cy, cx] = 0.5

        if(self.__maze[cy - 2, cx] == 0.5 and self.__maze[cy + 2, cx] == 0.5 and self.__maze[cy, cx - 2] == 0.5 and self.__maze[cy, cx + 2] == 0.5):
            pass
        else:
            li = [1, 2, 3, 4]
            while len(li) > 0:
                dir = random.choice(li)
                li.remove(dir)

                if dir == 1: # UP
                    nx = cx
                    mx = cx
                    ny = cy - 2
                    my = cy - 1
                elif dir == 2: # DOWN
                    nx = cx
                    mx = cx
                    ny = cy + 2
                    my = cy + 1
                elif dir == 3: # LEFT
                    nx = cx - 2
                    mx = cx - 1
                    ny = cy
                    my = cy
                elif dir == 4: # RIGHT
                    nx = cx + 2
                    mx = cx + 1
                    ny = cy
                    my = cy
                else:
                    nx = cx
                    mx = cx

                if self.__maze[ny, nx] != 0.5:
                    self.__maze[my, mx] = 0.5
                    self.generate(nx, ny)

    def print_grid(self):
        print('\n'.join(
            (self.__get_row_as_string(row) for row in self.__maze)
        ))

    def __get_row_as_string(self, row):
        return ' '.join((TILE_MAPPING[cell] for cell in row))

def validate_input(prompt):
    while True:
        try:
            value = int(input(prompt)) # assert value is integer
        except ValueError:
            print("Input must be number, try again")
            continue

        if value > 2:
            return value
        else:
            print("Input must be positive and bigger than 5, try again")

if __name__ == '__main__':
    width = validate_input("Enter the # of rows: ")
    height = validate_input("Enter the # of columns: ")
    maze = Maze(width, height)
    maze.gen_map()
    maze.print_grid()