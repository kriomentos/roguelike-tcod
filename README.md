## What is it?

This is my first attempt at making Roguelike game with help from [TCOD tutorial](http://https://www.rogueliketutorials.com/tutorials/tcod/v2/ "TCOD") by user [TStand90](https://github.com/TStand90 "TStand90 on GitHub")

Also my first proper contact with OOP in Python and in general.
There will definitely be bad code practices and a lot of experimenting.

## TODOs | IDEAS
- Joining lone rooms in cave generator
- Another generator for dungeons Rogue style 
- Field of view
- Movable & destroyable entities
- Enemies
- Stats system
- Saving and loading
- Interface
- Inventory and items
- Overworld map with points for caves/dungeons
- Graphical tiles
- Configurable settings and graphics

## Requirements
- Python 3.7+
- tcod 13.6.2
- scipy 1.8.0

## Running
First install tcod & scipy

`pip install tcod`

`pip install scipy`

Then run it in terminal from within the source folder

`python main.py`

Player character is represented as `@` character

Movement using arrow keys. Esc to exit the window 'gracefully'

## Extras

By running `python grid.py` from within Extras folder, you can generate varying size cave with cellular automata smoothing

It will ask for dimensions and percentage of 'open tiles'

Accepted dimensions are at least bigger than 5 for both rows and columns, with no upper bound (the bigger it is the more time it takes, with safely generated 1000x1000 maps. But they are barely readable at this point) 
I did manage to generate 10kx10k map, but it took 20 minutes on Ryzen 5 3600, the output file was 200MB plain text and required 1,5GB of RAM for calculations

Open tiles is a float between 0 - 1, with best results being between 0.4 - 0.5. It is not recommended to go above 0.8 as the generator is not guaranteed to finish in reasonable time and there's no failsafe to terminate it (requires manual terminating).
