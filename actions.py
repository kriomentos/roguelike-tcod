from __future__ import annotations
from abc import abstractmethod

from typing import Optional, Tuple, TYPE_CHECKING

import color
from entity import Actor
import exceptions

if TYPE_CHECKING:
    from engine import Engine
    from entity import Actor, Entity, Item, Object

# default action
class Action:
    def __init__(self, entity: Actor) -> None:
        super().__init__()
        self.entity = entity

    @property
    def engine(self) -> Engine:
        return self.entity.gamemap.engine

    def perform(self) -> None:
        '''Perform this action with the objects needed to determine its scope.
        `self.engine` is the scope this action is being performed in.
        `self.entity` is the object performing the action.
        This method must be overridden by Action subclasses.
        '''
        raise NotImplementedError()

class PickupAction(Action):
    # pick and add item to inventory, if theres room

    def __init__(self, entity: Actor):
        super().__init__(entity)

    def perform(self) -> None:
        actor_location_x = self.entity.x
        actor_location_y = self.entity.y
        inventory = self.entity.inventory

        for item in self.engine.game_map.items:
            if actor_location_x == item.x and actor_location_y == item.y:
                if len(inventory.items) >= inventory.capacity:
                    raise exceptions.Impossible('There\'s no room in your inventory')

                self.engine.game_map.entities.remove(item)
                item.parent = self.entity.inventory
                inventory.items.append(item)

                # display pickup message only for player
                if self.entity is self.engine.player:
                    self.engine.message_log.add_message(f'You picked up {item.name}')

                return

        raise exceptions.Impossible('There is nothing to pick up')

class InteractionAction(Action):
    def __init__(
        self, 
        entity: Actor, 
        object: Object, 
        target_xy: Tuple[int, int] = None
    ) -> None:
        super().__init__(entity)
        self.object = object
        self.target_xy = target_xy


    # rethink targetting to be more versatile not just actor bound
    @property
    def target(self) -> Optional[Actor]:
        return self.engine.game_map.get_actor_at_location(*self.target_xy)

    def perform(self) -> None:
        if self.object.interaction:
            self.object.interaction.interact(self)

class ItemAction(Action):
    def __init__(
        self,
        entity: Actor,
        item: Item,
        target_xy: Optional[Tuple[int, int]] = None
    ) -> None:
        super().__init__(entity)
        self.item = item
        if not target_xy:
            target_xy = entity.x, entity.y
        self.target_xy = target_xy

    @property
    def target_actor(self) -> Optional[Actor]:
        return self.engine.game_map.get_actor_at_location(*self.target_xy) # return actor at this action destination

    # invoke item ability, this action is given to provide context
    def perform(self) -> None:
        if self.item.consumable:
            self.item.consumable.activate(self)

class DropItem(ItemAction):
    def perform(self) -> None:
        if self.entity.equipment.item_is_equipped(self.item):
            self.entity.equipment.toggle_equip(self.item)

        self.entity.inventory.drop(self.item)

class EquipAction(Action):
    def __init__(self, entity: Actor, item: Item):
        super().__init__(entity)

        self.item = item

    def perform(self) -> None:
        self.entity.equipment.toggle_equip(self.item)

class WaitAction(Action):
    def perform(self) -> None:
        pass

class TakeStairsAction(Action):
    def perform(self) -> None:
        '''Takes the stairs, if they exist at entity location'''
        if (self.entity.x, self.entity.y) == self.engine.game_map.downstairs_location:
            self.engine.game_world.go_downstairs()
            self.engine.message_log.add_message(
                'You descend down the staircase', color.descend
            )        
        elif (self.entity.x, self.entity.y) == self.engine.game_map.upstairs_location:
            self.engine.game_world.go_upstairs()
            self.engine.message_log.add_message(
                'You ascend up the staircase', color.descend
            )
        else:
            raise exceptions.Impossible('There are no stairs here')

class SkipStairs(Action):
    def perform(self) -> None:
        self.engine.game_world.go_downstairs()

class ActionWithDirection(Action):
    def __init__(self, entity: Actor, dx: int, dy: int):
        super().__init__(entity)

        self.dx = dx
        self.dy = dy

    @property
    def dest_xy(self) -> Tuple[int, int]:
        '''Returns this actions destination.'''
        return self.entity.x + self.dx, self.entity.y + self.dy

    @property
    def blocking_entity(self) -> Optional[Entity]:
        '''Return the blocking entity at this actions destination.'''
        return self.engine.game_map.get_blocking_entity_at_location(*self.dest_xy)

    @property
    def target_actor(self) -> Optional[Actor]:
        return self.engine.game_map.get_actor_at_location(*self.dest_xy)

    @abstractmethod
    def perform(self) -> None:
        pass

class MeleeAction(ActionWithDirection):
    def perform(self) -> None:
        # get entity we try to attack
        target = self.target_actor

        # if no entity to attack do nothing
        if not target:
            raise exceptions.Impossible('Nothing to attack')

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

class RangedAction(ActionWithDirection):
    def perform(self) -> None:
        target = self.target_actor

        if not target:
            raise exceptions.Impossible('No target')

        damage = self.entity.fighter.power - target.fighter.defense
        attack_desc = f'{self.entity.name.capitalize()} attacks {target.name}'

        if self.entity is self.engine.player:
            attack_color = color.player_atk
        else:
            attack_color = color.enemy_atk

        if damage > 0:
            self.engine.message_log.add_message(
                f'{attack_desc} for {damage} hit points.', attack_color
            )
            target.fighter.hp -= damage
        else:
            self.engine.message_log.add_message(
                f'{attack_desc} but does no damage.', attack_color
            )

class MovementAction(ActionWithDirection):
    # perform the movement action in given direction
    def perform(self) -> None:
        dest_x, dest_y = self.dest_xy

        # if the desitnaiton is out of bounds do nothing
        if not self.engine.game_map.in_bounds(dest_x, dest_y):
            raise exceptions.Impossible('That way is blocked')
        # if the destination is not walkable tile do nothing
        if not self.engine.game_map.tiles['walkable'][dest_x, dest_y]:
            raise exceptions.Impossible('That way is blocked')
        # if the destination is blocked by another entity do nothing
        if self.engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
            raise exceptions.Impossible('That way is blocked')

        self.entity.move(self.dx, self.dy)

class PushAction(ActionWithDirection):
    def perform(self) -> None:
        target = self.target_actor

        if not target:
            raise exceptions.Impossible('Nothing to push')

        dest_x =  target.x + self.dx
        dest_y = target.y + self.dy

        push_desc = f'{self.entity.name.capitalize()} pushes {target.name}'

        # if the desitnaiton is out of bounds do nothing
        if not self.engine.game_map.in_bounds(dest_x, dest_y):
            raise exceptions.Impossible('That way is blocked')
        # if the destination is not walkable tile do nothing
        # and make target take flat damage (for now)
        if not self.engine.game_map.tiles['walkable'][dest_x, dest_y]:
            self.engine.message_log.add_message(
                f'{push_desc} into wall, {target.name} takes 1 damage', color.player_atk
            )
            target.fighter.hp -= 1
            return
        # if the destination is blocked by another enitty make the target take damage
        # but do nothing otherwise
        if self.engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
            self.engine.message_log.add_message(
                f'{push_desc} into {self.engine.game_map.get_blocking_entity_at_location(dest_x, dest_y).name}, both take 1 damage', color.player_atk
            )
            target.fighter.hp -= 1
            self.engine.game_map.get_actor_at_location(dest_x, dest_y).fighter.hp -= 1
            return

        # push the target in the direction we try to move
        target.move(self.dx + 1, self.dy + 1)

class BumpAction(ActionWithDirection):
    def perform(self) -> None:

        if self.target_actor:
            return MeleeAction(self.entity, self.dx, self.dy).perform()
        else:
            return MovementAction(self.entity, self.dx, self.dy).perform()