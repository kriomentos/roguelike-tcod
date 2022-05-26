from __future__ import annotations
from html import entities
from typing import Iterable, TYPE_CHECKING
from xml.dom.minidom import Entity
import numpy as np  # type: ignore
from tcod.console import Console

import tile_types

if TYPE_CHECKING:
    from entity import E

class GameMap:
    def __init__(self, width: int, height: int, entities: Iterable[Entity] = ()):
        self.width, self.height = width, height
        self.entities = set(entities)
        self.tiles = np.full((width, height), fill_value = tile_types.wall, order='F') # numpy filled with wall tiles in fortran order

        self.visible = np.full((width, height), fill_value = False, order = "F") # tiles the player can see currently
        self.explored = np.full((width, height), fill_value = False, order = "F") # tiles the player has seen already
    
    @property
    def area(self):
        return self.width * self.height

    def in_bounds(self, x: int, y: int) -> bool:
        # Return True if x and y are inside of the bounds of this map.
        return 0 <= x < self.width and 0 <= y < self.height

    def render(self, console: Console) -> None:
        # prints the whole map, its called from within Engine when we render every bit to console 
        console.tiles_rgb[0:self.width, 0:self.height] = np.select(
            condlist = [self.visible, self.explored],
            choicelist = [self.tiles["light"], self.tiles["dark"]],
            default = tile_types.SHROUD
        )
        for entity in self.entities:
            if self.visible[entity.x, entity.y]:
                console.print(x = entity.x, y = entity.y, string = entity.char, fg = entity.color)