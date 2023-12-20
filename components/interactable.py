from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import color
from components.base_component import BaseComponent
from entity import Actor
from input_handlers import (
    ActionHandler,
    InteractionSelectionEventHandler,
    SelectInteractableEventHandler
)

if TYPE_CHECKING:
    from entity import Actor, Object

class Interactable(BaseComponent):
    parent: Object

    def get_action(self, user: Actor) -> Optional[ActionHandler]:
        return SelectInteractableEventHandler(self.engine)
    
class BasicInteraction(Interactable):
    def __init__(self) -> None:
        super().__init__()

    def get_action(self, user: Actor) -> SelectInteractableEventHandler:
        self.engine.message_log.add_message(
            'Select interaction to perform', color.needs_target
        )
        return SelectInteractableEventHandler(self.engine)