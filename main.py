import tcod

import copy

from engine import Engine
from input_handlers import EventHandler
import entity_factories
from procgen import generate_dungeon

def main() -> None:
    screen_width = 80
    screen_height = 50

    map_width = 80
    map_height = 45
    init_open = 0.5
    max_monsters = 3

    tileset = tcod.tileset.load_tilesheet(
        "dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD
    )

    event_handler = EventHandler()

    player = copy.deepcopy(entity_factories.player)

    game_map = generate_dungeon(
        map_width = map_width,
        map_height = map_height,
        initial_open = init_open,
        max_monsters = max_monsters,
        player = player
    )

    engine = Engine(event_handler = event_handler, game_map = game_map, player = player)

    with tcod.context.new_terminal(
        screen_width,
        screen_height,
        tileset = tileset,
        title = "Roguelike",
        vsync = True,
    ) as context:
        root_console = tcod.Console(screen_width, screen_height, order = "F")

        while True:
            engine.render(console = root_console, context = context)

            events = tcod.event.wait()

            engine.handle_events(events)

if __name__ == "__main__":
    main()