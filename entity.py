from __future__ import annotations

import copy
from typing import Optional, Tuple, Type, TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from components.ai import BaseAI
    from components.fighter import Fighter
    from game_map import GameMap

T = TypeVar("T", bound = "Entity")

class Entity:
    # Generic object for entities
    gamemap: GameMap

    def __init__(
        self,
        gamemap: Optional[GameMap] = None,
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
        if gamemap:
            # if gamemap isn't provided now, it will be set later
            self.gamemap = gamemap
            gamemap.entities.add(self)

    # creating copy of generic entity, used by factories to spawn it on game map
    def spawn(self: T, gamemap: GameMap, x: int, y: int) -> T:
        clone = copy.deepcopy(self) # create deep copy of provided facotry entity
        clone.x = x # using factories we just copy cooridnates provided during placement
        clone.y = y
        clone.gamemap = gamemap
        gamemap.entities.add(clone) # add clone to the gamemap object to hold
        return clone

    def place(self, x: int, y: int, gamemap: Optional[GameMap] = None) -> None:
        # palce entity at new location, handles moving across gamemaps
        self.x = x
        self.y = y
        if gamemap:
            if hasattr(self, "gamemap"): # possibly uninitialized
                self.gamemap.entities.remove(self)
            self.gamemap = gamemap
            gamemap.entities.add(self)

    def move(self, dx: int, dy: int) -> None:
        self.x += dx
        self.y += dy

class Actor(Entity):
    def __init__(
        self, 
        *, 
        x: int = 0, 
        y: int = 0, 
        char: str = "?", 
        color: Tuple[int, int, int] = (255, 255, 255), 
        name: str = "<Unnamed>", 
        ai_cls: Type[BaseAI],
        fighter: Fighter,
    ):
        super().__init__(
            x = x, 
            y = y, 
            char = char, 
            color = color, 
            name = name, 
            blocks_movement = True,
        )

        self.ai: Optional[BaseAI] = ai_cls(self)
        
        self.fighter = fighter
        self.fighter.entity = self

    @property
    def is_alive(self) -> bool:
        return bool(self.ai)