from __future__ import annotations
from random import randint

from typing import TYPE_CHECKING

from components.base_component import BaseComponent
from equipment_types import EquipmentType

if TYPE_CHECKING:
    from entity import Item

class Equippable(BaseComponent):
    parent: Item

    def __init__(
        self,
        equipment_type: EquipmentType,
        power_bonus: int = 0,
        defense_bonus: int = 0,
    ):
        self.equipment_type = equipment_type

        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus

class Dagger(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type = EquipmentType.WEAPON, power_bonus = 1)

class Sword(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type = EquipmentType.WEAPON, power_bonus = 3)

class LeatherArmor(Equippable):
    def __init__(self):
        super().__init__(equipment_type = EquipmentType.ARMOR, defense_bonus = 1)

class ChainMail(Equippable):
    def __init__(self):
        super().__init__(equipment_type = EquipmentType.ARMOR, defense_bonus = 3)

class DefenseRing(Equippable):
    def __init__(self):
        super().__init__(equipment_type = EquipmentType.RING, defense_bonus = randint(1, 4))

class PowerRing(Equippable):
    def __init__(self):
        super().__init__(equipment_type = EquipmentType.RING, power_bonus = randint(1, 4))

class OmniRing(Equippable):
    def __init__(self):
        super().__init__(equipment_type = EquipmentType.RING, power_bonus = randint(1, 4), defense_bonus = randint(1, 4))