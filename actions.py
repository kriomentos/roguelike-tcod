from __future__ import annotations

from typing import Optional, Tuple, TYPE_CHECKING
import color

if TYPE_CHECKING:
    from engine import Engine
    from entity import Actor, Entity

# default action
class Action:
    def __init__(self, entity: Actor) -> None:
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

class WaitAction(Action):
    def perform(self) -> None:
        pass

class ActionWithDirection(Action):
    def __init__(self, entity: Actor, dx: int, dy: int):
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
    
    @property
    def target_actor(self) -> Optional[Actor]:
        return self.engine.game_map.get_actor_at_location(*self.dest_xy)

    def perform(self) -> None:
        raise NotImplementedError()

class MeleeAction(ActionWithDirection):
    def perform(self) -> None:
        # get entity we try to attack
        target = self.target_actor

        # if no entity to attack do nothing
        if not target:
            return

        # calculate damage 
        # attack power of entity doing the action
        # reduced by targets defense stat
        damage = self.entity.fighter.power - target.fighter.defense

        # fluff string to serve saying who does what to who
        attack_desc = f'{self.entity.name.capitalize()} attacks {target.name}'

        if self.entity is self.engine.player:
            attack_color = color.player_atk
        else:
            attack_color = color.enemy_atk

        # self explanatory
        if damage > 0:
            self.engine.message_log.add_message(
                f'{attack_desc} for {damage} hit points.', attack_color
            )  
            target.fighter.hp -= damage # reduce current HP by the damage dealt
        else:
            self.engine.message_log.add_message(
                f'{attack_desc} but does no damage.', attack_color
            ) # or not if the enemy power is too lowe

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

        if self.target_actor:
            return MeleeAction(self.entity, self.dx, self.dy).perform()
        else:
            return MovementAction(self.entity, self.dx, self.dy).perform()