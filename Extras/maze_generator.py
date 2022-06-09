import cProfile
import random
import numpy as np
import sys

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
        self.__maze = np.zeros((width, height), dtype = float)

    def start_end(self):
        dir = [1, 2, 3, 4]
        facing = random.choice(dir)
        if facing == 1: # TOP WALL
            point = [1, random.randrange(2, self.width - 1)]
            if self.__maze[2, point[1]] == 0 or self.__maze[1, point[1]] == 2:
                point = self.start_end()
        elif facing == 2: # BOTTOM WALL
            point = [self.height, random.randrange(2, self.width - 1)]
            if self.__maze[self.height - 1, point[1]] == 0 or self.__maze[self.height, point[1]] == 2:
                point = self.start_end()
        elif facing == 3: # LEFT WALL
            point = [random.randrange(2, self.width - 1), 1]
            if self.__maze[point[0], 2] == 0 or self.__maze[point[0], 1] == 2:
                point = self.start_end()
        elif facing == 4: # RIGHT WALL
            point = [random.randrange(2, self.width - 1), self.width]
            if self.__maze[point[0], self.width - 1] == 0 or self.__maze[point[0], self.width] == 2:
                point = self.start_end()

        return point

    def gen_map(self):
        self.__maze[1::2,1::2] = 1
        self.__maze = np.pad(self.__maze, pad_width = 1, mode = 'constant', constant_values = 0.5)

        sx = random.choice(range(2, self.width - 2, 2))
        sy = random.choice(range(2, self.height - 2, 2))

        self.generate(sx, sy)

        # numpy fancy indexing, select all indices of value 0.5 and change thme to -1
        self.__maze[self.__maze == 0.5] = -1

        for i in range(0, 35):
            sx = random.choice(range(2, self.width - 2, 2))
            sy = random.choice(range(2, self.height - 2, 2))
            if self.__maze[sx, sy] == -1:
                self.__maze[sx, sy] = 1

        start = self.start_end()
        self.__maze[start[0], start[1]] = 2
        end = self.start_end()
        self.__maze[end[0], end[1]] = 2

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

# def run():
#     maze = Maze(100, 100)
#     maze.gen_map()

if __name__ == '__main__':
    # cProfile.run('run()')
    # width = validate_input("Enter the # of rows: ")
    # height = validate_input("Enter the # of columns: ")
    maze = Maze(20, 20)
    maze.gen_map()
    maze.print_grid()