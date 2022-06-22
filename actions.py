from __future__ import annotations
from select import select

from typing import TYPE_CHECKING
from xmlrpc.server import DocXMLRPCRequestHandler

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity

# default action
class Action:
    def perform(self, engine: Engine, entity: Entity) -> None:
        raise NotImplementedError()

# what to do on escape, currently exit console gracefully
class EscapeAction(Action):
    def perform(self, engine: Engine, entity: Entity) -> None:
        raise SystemExit()

class ActionWithDirection(Action):
    def __init__(self, dx: int, dy: int):
        super().__init__()

        self.dx = dx
        self.dy = dy
    
    def perform(self, engine: Engine, entity: Entity) -> None:
        raise NotImplementedError()

class MeleeAction(ActionWithDirection):
    def perform(self, engine: Engine, entity: Entity) -> None:
        dest_x = entity.x + self.dx
        dest_y = entity.y + self.dy
        # get entity we try to attack
        target = engine.game_map.get_blocking_entity_at_location(dest_x, dest_y)
        # if no entity to attack
        if not target:
            return

        print(f"You kick the {target.name}, it does nothing")

class MovementAction(ActionWithDirection):
    # perform the movement action in given direction
    def perform(self, engine: Engine, entity: Entity) -> None:
        dest_x = entity.x + self.dx
        dest_y = entity.y + self.dy

        # if the desitnaiton is out of bounds do nothing
        if not engine.game_map.in_bounds(dest_x, dest_y):
            return
        # if the destination is not walkable tile do nothing
        if not engine.game_map.tiles["walkable"][dest_x, dest_y]:
            return
        # if the destination is blocked by another enitty do nothing
        if engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
            return
        
        entity.move(self.dx, self.dy)

class BumpAction(ActionWithDirection):
    def perform(self, engine: Engine, entity: Entity) -> None:
        dest_x = entity.x + self.dx
        dest_y = entity.y + self.dy

        if engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
            return MeleeAction(self.dx, self.dy).perform(engine, entity)
        else:
            return MovementAction(self.dx, self.dy).perform(engine, entity)