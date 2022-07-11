from __future__ import annotations
from abc import abstractmethod
import random
from typing import List, Optional, Tuple, TYPE_CHECKING

import numpy as np
import tcod
import color
from actions import Action, BumpAction, MeleeAction, MovementAction, WaitAction

if TYPE_CHECKING:
    from entity import Actor

class BaseAI(Action):
    entity: Actor
    @abstractmethod
    def perform(self) -> None:
        pass

    def get_path_to(self, dest_x: int, dest_y: int) -> List[Tuple[int, int]]:
        # calculates path to traget position or returns empty list if no valid path
        cost = np.array(self.entity.gamemap.tiles["walkable"], dtype = np.int8)

        for entity in self.entity.gamemap.entities:
            if entity.blocks_movement and cost[entity.x, entity.y]:
                # add to the cost of blocked position
                # lower means more entity crowding behind each other
                # higher encites them to take longer paths to surround player
                cost[entity.x, entity.y] += 10

        # create graph from the cost array (flat weight for all but active entities)
        # pass it to pathfinder
        graph = tcod.path.SimpleGraph(cost = cost, cardinal = 2, diagonal = 3)
        pathfinder = tcod.path.Pathfinder(graph)

        pathfinder.add_root((self.entity.x, self.entity.y))

        # calculate path to the destination and remove starting point
        path: List[List[int]] = pathfinder.path_to((dest_x, dest_y))[1:].tolist()

        # convert from List[List] to List[Tuple]
        return [(index[0], index[1]) for index in path]

class Dummy(BaseAI):
    def __init__(self, entity: Actor) -> None:
        super().__init__(entity)

    def perform(self) -> None:
        return

class HostileEnemy(BaseAI):
    def __init__(self, entity: Actor):
        super().__init__(entity)
        self.path:  List[Tuple[int, int]] = []

    def perform(self) -> None:
        target = self.engine.player
        dx = target.x - self.entity.x
        dy = target.y - self.entity.y

        distance = max(abs(dx), abs(dy))

        if self.engine.game_map.visible[self.entity.x, self.entity.y]:
            if distance <= 1:
                return MeleeAction(self.entity, dx, dy).perform()

            self.path = self.get_path_to(target.x, target.y)

        if self.path:
            dest_x, dest_y = self.path.pop(0)
            return MovementAction(
                self.entity, dest_x - self.entity.x, dest_y - self.entity.y
            ).perform()

        return WaitAction(self.entity).perform()

class ConfusedEnemy(BaseAI):
    # confused actor will stumble around for given number of turns, then return to normal
    # if it stumbles into antoher actor, it will attack
    def __init__(self, entity: Actor, previous_ai: Optional[BaseAI], turns_remaining: int):
        super().__init__(entity)

        self.previous_ai = previous_ai
        self.turns_remaining = turns_remaining

    def perform(self) -> None:
        # return to previous ai when the effect ends
        if self.turns_remaining <= 0:
            self.engine.message_log.add_message(
                f"The {self.entity.name} is no longer confused"
            )
            self.entity.ai = self.previous_ai
        else:
            # pick random direction
            direction_x, direction_y = random.choice(
                [
                    (-1, -1), # northwest
                    (0, -1), # north
                    (1, -1), # northeast
                    (-1, 0), # west
                    (1, 0), # east
                    (-1, 1), # southwest
                    (0, 1), # south
                    (1, 1), # southeast
                ]
            )

            self.turns_remaining -= 1

            return BumpAction(self.entity, direction_x, direction_y).perform()

class MimicHostileEnemy(BaseAI):
    def __init__(self, entity: Actor):
        super().__init__(entity)
        self.path:  List[Tuple[int, int]] = []

    def perform(self) -> None:
        # if the mimics HP is less than maximum reveal itself
        if self.entity.fighter.hp < self.entity.fighter.max_hp:
            self.entity.char = "M"
            self.entity.color = color.anb_red
            self.entity.name = "Mimic"
            # self.entity.ai = HostileEnemy

            target = self.engine.player
            dx = target.x - self.entity.x
            dy = target.y - self.entity.y

            distance = max(abs(dx), abs(dy))

            if self.engine.game_map.visible[self.entity.x, self.entity.y]:
                if distance <= 1:
                    return MeleeAction(self.entity, dx, dy).perform()

                self.path = self.get_path_to(target.x, target.y)

            if self.path:
                dest_x, dest_y = self.path.pop(0)
                return MovementAction(
                    self.entity, dest_x - self.entity.x, dest_y - self.entity.y
                ).perform()

            return WaitAction(self.entity).perform()

        else:
            return WaitAction(self.entity).perform()

        return WaitAction(self.entity).perform()

class TickingEntity(BaseAI):
    def __init__(self, entity: Actor):
        super().__init__(entity)

    def perform(self) -> None:
        target_xy = self.entity.x, self.entity.y
        print(f"Target xy: {target_xy}")
        if self.entity.fighter.hp <= 0:
            self.entity.ai = None
        else:
            for actor in set(self.engine.game_map.actors) - {self.entity}:
                if actor.distance(*target_xy) <= 3:
                    self.engine.message_log.add_message(
                        f"The {actor.name} coughs in toxic gas, taking {self.entity.fighter.power} damage"
                    )
                    actor.fighter.take_damage(self.entity.fighter.power)
            self.entity.fighter.hp -= 1