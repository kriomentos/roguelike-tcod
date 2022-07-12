from components import consumable
from components.ai import Dummy, HostileEnemy, MimicHostileEnemy, TickingEntity
from components.fighter import Fighter, Ticking
from components.inventory import Inventory
from entity import Actor, Item
import color

player = Actor(
    char = "@", # string for visual representation on game map. Most ASCII symbols
    color = color.anb_white, # color of string representation format RGB(R, G, B)
    name = "Player", # name displayed when taking actions/interacting
    ai_cls = HostileEnemy, # type of AI to use, player doesn't need it but it must be specified for all Actors
    fighter = Fighter(hp = 50, defense = 3, power = 5), # base statisics for Actor
    inventory = Inventory(capacity = 26), # attach Inventory to actor with set size, size determiens how many items actor can carry
)
# AI HOSTILE ACTORS
orc = Actor(
    char = "o",
    color = color.anb_light_green, # (63, 127, 63),
    name = "Orc",
    ai_cls = HostileEnemy,
    fighter = Fighter(hp = 10, defense = 0, power = 4),
    inventory = Inventory(capacity = 0),
)
troll = Actor(
    char = "T",
    color = color.anb_green, # (0, 127, 0),
    name = "Troll",
    ai_cls = HostileEnemy,
    fighter = Fighter(hp = 20, defense = 2, power = 5),
    inventory = Inventory(capacity = 0),
)
# mimic_table = Actor(
#     char = "+",
#     color = color.anb_brown,
#     name = "Table",
#     ai_cls = MimicHostileEnemy,
#     fighter = Fighter(hp = 15, defense = 2, power = 4),
#     inventory = Inventory(capacity = 0),
# )
# NON AI DESTROYABLE ACTORS
table = Actor(
    char = "+",
    color = color.anb_brown,
    name = "Table",
    ai_cls = Dummy,
    fighter = Fighter(hp = 20, defense = 0, power = 0),
    inventory = Inventory(capacity = 0),
)
# ITEMS
health_potion = Item(
    char = "!",
    color = color.anb_light_brown,
    name = "Health potion",
    consumable = consumable.HealingConsumable(amount = 4),
)
lightning_scroll = Item(
    char = "~",
    color = color.anb_light_blue,
    name = "Lightning scroll",
    consumable = consumable.LightningDamageConsumable(damage = 15, maximum_range = 5),
)
confusion_scroll = Item(
    char = "~",
    color = color.anb_purple,
    name = "Confusion scroll",
    consumable = consumable.ConfusionConsumable(number_of_turns = 10),
)
fireball_scroll = Item(
    char = "~",
    color = color.anb_red,
    name = "Fireball scroll",
    consumable = consumable.FireballDamageConsumable(damage = 12, radius = 3),
)
gascloud_scroll = Item(
    char = "~",
    color = color.anb_green,
    name = "Gas cloud scroll",
    consumable = consumable.GasDamageConsumable(damage = 12, radius = 3, turns_active = 3),
)
gas_cloud = Actor(
    char = "8",
    color = color.anb_green,
    name = "",
    ai_cls = TickingEntity,
    fighter = Ticking(hp = 3, power = 3, radius = 3),
    inventory = Inventory(capacity = 0),
)