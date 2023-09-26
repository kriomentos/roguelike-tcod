from sys import maxsize
from random import randrange
from numpy import random
from time import strftime, localtime

int_seed = 6184320793840983299
base_seed = 'ragnis'
for ch in base_seed:
    int_seed <<= 8 + ord(ch)

seed = randrange(maxsize)
print(f'Seed was: {seed}')
text_to_write = f'The seed was: {seed} generated on: {strftime("%a %d-%b-%Y %H:%M:%S", localtime())}'
with open('seeds.txt', 'a') as file:
    file.write(str(seed) + '\n')

nprng = random.default_rng(seed)