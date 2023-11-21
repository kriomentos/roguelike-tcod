from enum import auto, Enum

class RenderOrder(Enum):
    CORPSE = auto()
    ITEM = auto()
    OBJECT = auto()
    ACTOR = auto()