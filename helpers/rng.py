from sys import maxsize
from random import randrange
from numpy import random

int_seed = 6184320793840983299
base_seed = 'ragnis'
for ch in base_seed:
    int_seed <<= 8 + ord(ch)

seed = randrange(maxsize)
print(f'Seed was: {seed}')

nprng = random.default_rng(seed)