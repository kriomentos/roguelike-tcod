from __future__ import annotations

from typing import TYPE_CHECKING

from components.base_component import BaseComponent
from input_handlers import GameOverEventHandler
from render_order import RenderOrder

import color

if TYPE_CHECKING:
    from entity import Actor

class Fighter(BaseComponent):
    parent: Actor

    def __init__(self, hp: int, defense:int, power: int) -> None:
        self.max_hp = hp
        self._hp = hp
        self.defense = defense
        self.power = power

    @property
    def hp(self) -> int:
        return self._hp

    # allows us to modify value of hp ie take and do damage,
    # it makes sure we never go below 0 or above max_hp
    @hp.setter
    def hp(self, value: int) -> None:
        self._hp = max(0, min(value, self.max_hp))
        if self._hp == 0 and self.parent.ai:
            self.die()

    def die(self) -> None:
        if self.engine.player is self.parent:
            death_massage = "You died"
            death_massage_color = color.player_die
            self.engine.event_handler = GameOverEventHandler(self.engine)
        else:
            death_massage = f"{self.parent.name} is dead"
            death_massage_color = color.enemy_die

        self.parent.char = "%"
        self.parent.color = color.anb_red
        self.parent.blocks_movement = False
        self.parent.ai = None
        self.parent.name = f"Corpse of {self.parent.name}"
        self.parent.render_order = RenderOrder.CORPSE

        self.engine.message_log.add_message(death_massage, death_massage_color)

    def heal(self, amount: int) -> int:
        if self.hp == self.max_hp:
            return 0

        new_hp_value = self.hp + amount

        if new_hp_value > self.max_hp:
            new_hp_value = self.max_hp

        amount_recovered = new_hp_value - self.hp

        self.hp = new_hp_value

        return amount_recovered

    def take_damage(self, amount: int) -> None:
        self.hp -= amount

class Ticking(BaseComponent):
    parent: Actor

    def __init__(self, hp: int, power: int, radius: int) -> None:
        self.max_hp = hp
        self._hp = hp
        self.power = power
        self.radius = radius

    @property
    def hp(self) -> int:
        return self._hp

    # allows us to modify value of hp ie take and do damage,
    # it makes sure we never go below 0 or above max_hp
    @hp.setter
    def hp(self, value: int) -> None:
        self._hp = max(0, min(value, self.max_hp))
        if self._hp == 0 and self.parent.ai:
            self.die()

    def die(self) -> None:
        self.parent.char = ""
        self.parent.color = color.anb_red
        self.parent.blocks_movement = False
        self.parent.ai = None
        self.parent.name = f""
        self.parent.render_order = RenderOrder.CORPSE

    def take_damage(self, amount: int):
        pass