import re
from numpy import power
from components.base_component import BaseComponent

class Fighter(BaseComponent):
    def __init__(self, hp: int, defense:int, power: int) -> None:
        self.max_hp = hp
        self._hp = hp
        self.defense = defense
        self.power = power

    @property
    def hp(self) -> int:
        return self._hp
    # allows us to modify value of hp, it makes sure we never go below 0 and above max_hp
    @hp.setter
    def hp(self, value: int) -> None:
        self._hp = max(0, min(value, self.max_hp))