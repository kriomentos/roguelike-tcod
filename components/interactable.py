from __future__ import annotations

from typing import Optional , TYPE_CHECKING

import actions
import color
from components.base_component import BaseComponent
from exceptions import Impossible

if TYPE_CHECKING:
    from entity import Actor, Object

class Interactable(BaseComponent):
    parent: Object

    def get_action(self, user: Actor) -> Optional[actions.Action]:
        pass

    def interact(self, action: actions.InteractionAction) -> None:
        raise NotImplementedError()