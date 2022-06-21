from __future__ import annotations

import copy
from turtle import clone
from typing import Tuple, TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from game_map import GameMap

T = TypeVar("T", bound = "Entity")

class Entity:
    # Generic object for entities
    def __init__(
        self, 
        x: int = 0, # integers for position in Fortran grid
        y: int = 0, 
        char: str = "?", # string character for visual representation
        color: Tuple[int, int, int] = (255, 255, 255), # RGB value for provided char
        name: str = "<Unnamed>", # name to be displayed when inspecting/interacting with entity
        blocks_movement: bool = False, # does the enitty block player movement
    ):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks_movement = blocks_movement

    # creating copy of generic entity, used by factories to spawn it on game map
    def spawn(self: T, gamemap: GameMap, x: int, y: int) -> T:
        clone = copy.deepcopy(self) # create deep copy of provided facotry entity
        clone.x = x # using factories we just copy cooridnates provided during placement
        clone.y = y
        gamemap.entities.add(clone) # add clone to the gamemap object to hold
        return clone

    def move(self, dx: int, dy: int) -> None:
        self.x += dx
        self.y += dy