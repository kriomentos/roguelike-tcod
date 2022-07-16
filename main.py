import tcod
import copy
import traceback

import color
from engine import Engine
import entity_factories
import exceptions
import input_handlers
from procgen import generate_dungeon

def main() -> None:
    screen_width = 80
    screen_height = 50

    map_width = 80
    map_height = 44
    init_open = 0.5
    max_monsters = 5
    max_items = 3

    tileset = tcod.tileset.load_tilesheet(
        "dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD
    )

    player = copy.deepcopy(entity_factories.player)

    engine = Engine(player = player)

    engine.game_map = generate_dungeon(
        map_width = map_width,
        map_height = map_height,
        initial_open = init_open,
        max_monsters = max_monsters,
        max_items = max_items,
        engine = engine,
    )

    engine.update_fov()

    engine.message_log.add_message(
        "You stepped down into yet another dungeon!", color.welcome_text
    )

    handler: input_handlers.BaseEventHandler = input_handlers.MainGameEventHandler(engine)

    with tcod.context.new_terminal(
        screen_width,
        screen_height,
        tileset = tileset,
        title = "Roguelike",
        vsync = True,
    ) as context:
        root_console = tcod.Console(screen_width, screen_height, order = "F")
        try:
            while True:
                root_console.clear()
                handler.on_render(console = root_console)
                context.present(root_console)

                try:
                    for event in tcod.event.wait():
                        context.convert_event(event)
                        handler = handler.handle_events(event)
                except Exception:
                    traceback.print_exc() # print error to stderr
                    # then print it in message log
                    if isinstance(handler, input_handlers.EventHandler):
                        handler.engine.message_log.add_message(
                            traceback.format_exc(), color.error
                        )
        except exceptions.QuitWithoutSaving:
            raise
        except SystemExit: # Save and quit
            raise
        except BaseException: # save on any other unexpected exception
            raise

if __name__ == "__main__":
    main()