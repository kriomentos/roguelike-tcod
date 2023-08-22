# What is it?

This is my first attempt at making Roguelike game with help from [TCOD tutorial](http://https://www.rogueliketutorials.com/tutorials/tcod/v2/ "TCOD") by user [TStand90](https://github.com/TStand90 "TStand90 on GitHub")

Also my first proper contact with OOP in Python and in general.
There will definitely be bad code practices and a lot of experimenting.

## TODOs | IDEAS

- Joining lone rooms in cave generator
  - This does work currently, but requires work on smoothing artefacts created after the join, also it's slow
- Another generator for dungeons Rogue style
  - Rework room connecting method
  - Add generators for features
  - Add loot (basics are in, needs more work)
- Mimic enemy (make it less scuffed)

- Improve handling of non-hostile entities
  - Separate them into their own group of Objects
- Stats system (more complicated one)
- Interface (barebones for now)
- Overworld map with points for caves/dungeons
- More AI types
- Graphical tiles
- Configurable settings and graphics

- Dragon type enemy, possibly with multi-tile entity handling added
- End goal
- Rebalance monsters, items and level scaling
- Add eco-systems for enemies (goblins and orcs hate themselves etc.)
- Expand on the races already existing (more types, like shamans that heal, rangers etc.)
- Add classes (this one will require the more sophisticated stats system)

## Requirements

- Python 3.7+
- tcod 16.1+
- scipy 1.11+
- numpy 1.25+

## Running

First install tcod & scipy

`pip install tcod`

`pip install scipy`

Then run it in terminal from within the source folder

`python main.py`

Player character is represented as `@` character

**Important `NumLock` must be disabled to run the rouge correctly, with it on movement will be ignored**

Movement using arrow keys (`Home`, `End` and `Page Up`/`Down` for diagonals), Numpad or Vi.

Skip turns using `,` `Num5` `Del` or `S`, pickup items `G`, use items from inventory `I`, drop them from inventory `F`, descend down the stairs `>`, open character sheet pop-up `C`, look around the map `/`, open message log history `V`

To push entity insted of attacking use move keys while holding `Shift`

`Esc` to exit the window 'gracefully'

## Extras

By running `python maze_generator.py` from Extras, you can genereate even sided maze using recursive backtracking method.

By running `python cave_generator.py` from within Extras folder, you can generate varying size cave with cellular automata smoothing

It will ask for dimensions and percentage of 'open tiles'

Accepted dimensions are at least bigger than 5 for both rows and columns, with no upper bound (the bigger it is the more time it takes, with safely generated 1000x1000 maps. But they are barely readable at this point)

Open tiles is a % of cells that are born, between 0 - 1, with best results being between 0.4 - 0.5. It is not recommended to go above 0.8 as the generator is not guaranteed to finish in reasonable time and there's no failsafe to terminate it (requires manual terminating).
