from __future__ import annotations

from typing import List, Tuple, TYPE_CHECKING

import numpy as np
import tcod

from actions import Action, MeleeAction, MovementAction, WaitAction
from components.base_component import BaseComponent

if TYPE_CHECKING:
    from entity import Actor

class BaseAI(Action):
    entity: Actor

    def perform(self) -> None:
        raise NotImplementedError()

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