from random import randrange

EMPTY = -1
WALL = 0
FLOOR = 1
TREE = 2

TILE_MAPPING = {
	EMPTY: ' ',
	WALL: '#',
	FLOOR: '-',
	TREE: '^'
}

class caveGen:
	def __init__(self, rows, cols, initial_open=0.40):
		self.__rows = rows
		self.__cols = cols
		self.__map = []
		self.__pre_genenerate_map(initial_open)

	@property
	def __area(self):
		# Area is a derived value. It should be re-calculated if either __cols or __rows changes.
        # Don't store derived values if they are not expensive to compute.
		return self.__rows * self.__cols

	def print_grid(self):
		print("_ "*self.__rows + '\n\n' + 'Grid map\n' + '_ '*self.__rows, end='\n\n\n')

		# for r in range(self.__rows):
		# 	for c in range(self.__cols):
		# 		print('{}'.format(self.tile_content(r, c)), end=' ')
		# 	print('\n')

		#much better and 'new' approach thanks to Uncle
		print('\n'.join(
			(self.__get_row_as_string(row) for row in self.__map)
		))

	def gen_map(self):
		for r in range(1, self.__rows - 1):
			for c in range(1, self.__cols - 1):
				wall_count = self.__adj_wall_count(r, c) #count walls surrounding given cell
				#5|4 celluar automata test. if theres more than 5 walls around given cell change it to WALL | less than 4 change to FLOOR
				if self.__map[r][c] == FLOOR:
					if wall_count > 5:
						self.__map[r][c] = WALL
				elif wall_count < 4:
					self.__map[r][c] = FLOOR

		return self.__map

	def __adj_wall_count(self, sr, sc):
		count = 0

		for r in (-1, 0, 1):
			for c in (-1, 0, 1):
				if self.__map[(sr + r)][(sc + c)] != FLOOR and not(r == 0 and c == 0):
					count += 1

		return count

	def __get_row_as_string(self, row):
		return ' '.join((TILE_MAPPING[cell] for cell in row))

	def __pre_genenerate_map(self, initial_open):
		for r in range(0, self.__rows):
			#fill grid with WALLS
			row = [WALL for _ in range(0, self.__cols)]
			self.__map.append(row)
		#numbers of spots to "open"
		open_count = int(self.__area * initial_open)

		#randomly select cell and turn it into FLOOR until we run out of open spots
		while open_count > 0:
			rand_r = randrange(1, self.__rows - 1)
			rand_c = randrange(1, self.__cols - 1)

			if self.__map[rand_r][rand_c] == WALL:
				self.__map[rand_r][rand_c] = FLOOR
				open_count -= 1

		# open_count2 = int((self.__area / 2) * initial_open)
		# print(open_count2)
		# while open_count2 > 0:
		# 	rand_r = randrange(1, self.__rows - 1)
		# 	rand_c = randrange(1, self.__cols - 1)

		# 	if self.__map[rand_r][rand_c] == FLOOR:
		# 		self.__map[rand_r][rand_c] = TREE
		# 	open_count2 -= 1		

def validate_input(prompt):
	while True:
		try:
			value = int(input(prompt)) # assert value is integer
		except ValueError:
			print("Input must be number, try again")
			continue

		if value > 5:
			return value
		else:
			print("Input must be positive and bigger than 5, try again")

if __name__ == '__main__':
	length = validate_input("Enter the # of rows: ")
	width = validate_input("Enter the # of columns: ")
	#initial = float(input("Enter percentage of open spaces (Best results for pre gen are 0.4-0.5): "))
	cave = caveGen(length, width, 0.41)
	cave.print_grid()
	print("\n")
	cave.gen_map()
	cave.print_grid()