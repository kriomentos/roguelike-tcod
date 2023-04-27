from sys import maxsize
from random import randrange
from numpy import random

int_seed = 3968362232835277574
base_seed = 'ragnis'
for ch in base_seed:
    int_seed <<= 8 + ord(ch)

seed = randrange(maxsize)

nprng = random.default_rng(int_seed)

print(f'Seed: was: {seed}')