from __future__ import annotations

import copy
import math
from typing import Optional, Tuple, Type, TypeVar, TYPE_CHECKING, Union

from render_order import RenderOrder

if TYPE_CHECKING:
    from components.ai import BaseAI
    from components.consumable import Consumable
    from components.equipment import Equipment
    from components.equippable import Equippable
    from components.fighter import Fighter
    from components.inventory import Inventory
    from components.level import Level
    from game_map import GameMap

T = TypeVar("T", bound = "Entity")

class Entity:
    # Generic object for entities
    parent: Union[GameMap, Inventory]

    def __init__(
        self,
        parent: Optional[GameMap] = None,
        x: int = 0, # integers for position in Fortran grid
        y: int = 0,
        char: str = "?", # string character for visual representation
        color: Tuple[int, int, int] = (255, 255, 255), # RGB value for provided char
        name: str = "<Unnamed>", # name to be displayed when inspecting/interacting with entity
        blocks_movement: bool = False, # does the enitty block player movement
        render_order: RenderOrder = RenderOrder.CORPSE
    ):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks_movement = blocks_movement
        self.render_order = render_order
        if parent:
            # if parent isn't provided now, it will be set later
            self.parent = parent
            parent.entities.add(self)

    @property
    def gamemap(self) -> GameMap:
        return self.parent.gamemap

    # creating copy of generic entity, used by factories to spawn it on game map
    def spawn(self: T, gamemap: GameMap, x: int, y: int) -> T:
        clone = copy.deepcopy(self) # create deep copy of provided facotry entity
        clone.x = x # using factories we just copy cooridnates provided during placement
        clone.y = y
        clone.parent = gamemap
        gamemap.entities.add(clone) # add clone to the gamemap object to hold
        return clone

    def place(self, x: int, y: int, gamemap: Optional[GameMap] = None) -> None:
        # palce entity at new location, handles moving across gamemaps
        self.x = x
        self.y = y
        self.parent = gamemap
        gamemap.entities.add(self)
        # if gamemap:
        #     if hasattr(self, "parent"): # possibly uninitialized
        #         if self.parent is self.gamemap:
        #             pass
        #             # self.gamemap.entities.remove(self)
        #     self.parent = gamemap
        #     gamemap.entities.add(self)

    def distance(self, x: int, y: int) -> float:
        # returns distance between this entity and givens x and y
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

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
        equipment: Equipment,
        fighter: Fighter,
        inventory: Inventory, # possibly can be an Optional[Inventory] = None? This way I could avoid defining it for every actor
        level: Level,
    ):
        super().__init__(
            x = x,
            y = y,
            char = char,
            color = color,
            name = name,
            blocks_movement = True,
            render_order = RenderOrder.ACTOR,
        )

        self.ai: Optional[BaseAI] = ai_cls(self)

        self.equipment: Equipment = equipment
        self.equipment.parent = self

        self.fighter = fighter
        self.fighter.parent = self

        self.inventory = inventory
        self.inventory.parent = self

        self.level = level
        self.level.parent = self

    @property
    def is_alive(self) -> bool:
        return bool(self.ai)

class Item(Entity):
    def __init__(
        self,
        *,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: Tuple[int, int, int] = (255, 255, 255),
        name: str = "<Unnamed>",
        consumable: Optional[Consumable] = None,
        equippable: Optional[Equippable] = None,
    ):
        super().__init__(
            x = x,
            y = y,
            char = char,
            color = color,
            name = name,
            blocks_movement = False,
            render_order = RenderOrder.ITEM,
        )

        self.consumable = consumable

        if self.consumable:
            self.consumable.parent = self

        self.equippable = equippable

        if self.equippable:
            self.equippable.parent = self