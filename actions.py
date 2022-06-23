from __future__ import annotations
from select import select

from typing import Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity

# default action
class Action:
    def __init__(self, entity: Entity) -> None:
        super().__init__()
        self.entity = entity

    @property
    def engine(self) -> Engine:
        return self.entity.gamemap.engine

    def perform(self) -> None:
        """Perform this action with the objects needed to determine its scope.
        `self.engine` is the scope this action is being performed in.
        `self.entity` is the object performing the action.
        This method must be overridden by Action subclasses.
        """
        raise NotImplementedError()

# what to do on escape, currently exit console gracefully
class EscapeAction(Action):
    def perform(self) -> None:
        raise SystemExit()

class ActionWithDirection(Action):
    def __init__(self, entity: Entity, dx: int, dy: int):
        super().__init__(entity)

        self.dx = dx
        self.dy = dy

    @property
    def dest_xy(self) -> Tuple[int, int]:
        """Returns this actions destination."""
        return self.entity.x + self.dx, self.entity.y + self.dy

    @property
    def blocking_entity(self) -> Optional[Entity]:
        """Return the blocking entity at this actions destination.."""
        return self.engine.game_map.get_blocking_entity_at_location(*self.dest_xy)
    
    def perform(self) -> None:
        raise NotImplementedError()

class MeleeAction(ActionWithDirection):
    def perform(self) -> None:
        # get entity we try to attack
        target = self.blocking_entity
        # if no entity to attack
        if not target:
            return

        print(f"You kick the {target.name}, it does nothing")

class MovementAction(ActionWithDirection):
    # perform the movement action in given direction
    def perform(self) -> None:
        dest_x, dest_y = self.dest_xy

        # if the desitnaiton is out of bounds do nothing
        if not self.engine.game_map.in_bounds(dest_x, dest_y):
            return
        # if the destination is not walkable tile do nothing
        if not self.engine.game_map.tiles["walkable"][dest_x, dest_y]:
            return
        # if the destination is blocked by another enitty do nothing
        if self.engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
            return
        
        self.entity.move(self.dx, self.dy)

class BumpAction(ActionWithDirection):
    def perform(self) -> None:

        if self.blocking_entity:
            return MeleeAction(self.entity, self.dx, self.dy).perform()
        else:
            return MovementAction(self.entity, self.dx, self.dy).perform()