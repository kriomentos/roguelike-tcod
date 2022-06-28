from components.ai import Dummy, HostileEnemy
from components.fighter import Fighter
from entity import Actor, Entity
import color

player = Actor(
    char = "@", # string for visual representation on game map. Most ASCII symbols
    color = color.anb_white, # color of string representation format RGB(R, G, B)
    name = "Player", # name displayed when taking actions/interacting
    ai_cls = HostileEnemy, # type of AI to use, player doesn't need it but it must be specified for all Actors
    fighter = Fighter(hp = 50, defense = 3, power = 5), # base statisics for Actor
)

orc = Actor(
    char = "o",
    color = color.anb_light_green, # (63, 127, 63),
    name = "Orc",
    ai_cls = HostileEnemy,
    fighter = Fighter(hp = 10, defense = 0, power = 4),
)
troll = Actor(
    char = "T",
    color = color.anb_green, # (0, 127, 0),
    name = "Troll",
    ai_cls = HostileEnemy,
    fighter = Fighter(hp = 20, defense = 2, power = 5),
)

table = Actor(
    char = "+",
    color = color.anb_brown, # (0, 127, 0),
    name = "Table",
    ai_cls = Dummy,
    fighter = Fighter(hp = 20, defense = 0, power = 0),
)