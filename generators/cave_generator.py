from random import randrange, seed
from scipy import signal #type: ignore
from scipy.ndimage import label, generate_binary_structure # type: ignore
import numpy as np

EMPTY = -1
WALL = 0
FLOOR = 1
TREE = 2

TILE_MAPPING = {
    EMPTY: ' ',
    WALL: '#',
    FLOOR: '.',
    TREE: '^'
}

# helper kernel for convolve2d, basically 2d array
# kernel = [
#     [0, 1, 0],
#     [1, 0, 1],
#     [0, 1, 0]
# ]
kernel = np.ones((3, 3), dtype="int")
kernel[1, 1] = 0

seed(1337)

class caveGen:
    def __init__(self, rows, cols, initial_open, number_of_iterations):
        self.__rows = rows
        self.__cols = cols
        self.__map = np.full((rows, cols), fill_value = WALL, order='F')
        self.__map_new = self.__map.copy()
        self.__number_of_iterations = number_of_iterations
        self.__pre_genenerate_map(initial_open)

    @property
    def __area(self):
        # Area is a derived value. It should be re-calculated if either __cols or __rows changes.
        # Don't store derived values if they are not expensive to compute.
        return self.__rows * self.__cols

    def print_grid(self):
        print("_ " * self.__rows + '\n\n' + 'Grid map\n' + '_ ' * self.__rows, end = '\n\n\n')

        # quite old way of printing out grids
        # for r in range(self.__rows):
        #   for c in range(self.__cols):
        #       print('{}'.format(self.tile_content(r, c)), end=' ')
        #   print('\n')

        # much better and 'new' approach thanks to Uncle
        print('\n'.join(
            (self.__get_row_as_string(row) for row in self.__map)
        ), end = '\n\n')

        f = open('grid_output.txt', 'w')
        f.write('\n\n')
        f.write('\n'.join(
            (self.__get_row_as_string(row) for row in self.__map)
        ))
        f.close()

    def __get_row_as_string(self, row):
        return ' '.join((TILE_MAPPING[cell] for cell in row))

    def gen_map(self, min, max):
        self.__map_new = signal.convolve2d(self.__map, kernel, mode = "same", boundary = 'wrap')

        for r in range(1, self.__rows - 1):
            for c in range(1, self.__cols - 1):
                if self.__map_new[r, c] > max:
                    self.__map[r, c] = FLOOR
                elif self.__map_new[r, c] < min:
                    self.__map[r, c] = WALL

        return self.__map

    def __pre_genenerate_map(self, initial_open):

        # fill grid with WALLS
        # for r in range(0, self.__rows):
        #     row = [WALL for _ in range(0, self.__cols)]
        #     self.__map.append(row)

        # numbers of spots to 'open'
        open_count = int(self.__area * initial_open)

        # randomly select cell and turn it into FLOOR until we run out of open spots
        while open_count > 0:
            rand_r = randrange(1, self.__rows - 1)
            rand_c = randrange(1, self.__cols - 1)

            if self.__map[rand_r, rand_c] == WALL:
                self.__map[rand_r, rand_c] = FLOOR
                open_count -= 1

        # run cellular automata given number of times, it rans two sets of rules that I personally
        # selected as "looking good" with the code I wrote for it
        # it tends to create central "hub" like big space with corridors out of it and smaller pockets near edges
        # overall it makes more open caves, running just 4, 5 makes tighter caves
        # but also more closed off little pockets
        for _ in range(self.__number_of_iterations):
            # self.gen_map(3, 4)
            self.gen_map(4, 5)

    def label_array(self):
        s = generate_binary_structure(2,2)
        labeled_array, num_features = label(self.__map, structure = s)
        print(f'Num of features in map: {num_features}')
        print(labeled_array)

def validate_input(prompt):
    while True:
        try:
            value = int(input(prompt)) # assert value is integer
        except ValueError:
            print('Input must be number, try again')
            continue

        if value > 5:
            return value
        else:
            print('Input must be positive and bigger than 5, try again')

if __name__ == '__main__':
    length = validate_input("Enter the # of rows: ")
    width = validate_input("Enter the # of columns: ")
    initial = float(input("Enter percentage of open spaces (Best results for pre gen are 0.4-0.5): "))

    # higher number of iterations >2 make for more open space caves with big rooms and wide hallways
    # smaller ones <=2 make tighter and smaller cave
    num_of_iterations = int(input("Enter number of iterations for cellular automata: "))
    cave = caveGen(length, width, initial, num_of_iterations)
    cave.print_grid()
    cave.label_array()