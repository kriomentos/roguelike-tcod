from __future__ import annotations

from typing import Optional, Tuple, TYPE_CHECKING

import actions
import color
from components.base_component import BaseComponent
from entity import Actor
from exceptions import Impossible
from input_handlers import (
    ActionHandler,
    PushAction
)

if TYPE_CHECKING:
    from entity import Actor, Object

class Interactable(BaseComponent):
    parent: Object

    def get_action(self, user: Actor) -> Optional[ActionHandler]:
        return actions.InteractionAction(user, self.parent)

    def interact(self, action: actions.InteractionAction) -> None:
        raise NotImplementedError()
    
class BasicInteraction(Interactable):
    def __init__(self) -> None:
        super().__init__()

    def get_action(self, user: Actor) -> PushAction:
        pass

    def interact(self, action: actions.InteractionAction) -> None:
        user = action.entity
        target = action.target_xy
        targeted_object = self.engine.game_map.get_object_at_location(target[0], target[1])

        self.engine.message_log.add_message(
            f'User {user.name} interacted with {targeted_object.name}'
        )