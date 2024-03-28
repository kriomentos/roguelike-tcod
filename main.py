from __future__ import annotations

from os import path

import tcod
import traceback

import color
import exceptions
import input_handlers
import setup_game

def save_game(handler: input_handlers.BaseEventHandler, filename: str) -> None:
    # if current event handler has active Engine then save it
    if isinstance(handler, input_handlers.EventHandler):
        handler.engine.save_as(filename)
        print('Game saved')

def main() -> None:
    screen_width = 80
    screen_height = 50

    path_to_tileset = path.abspath(path.join(path.dirname(__file__), './tilesets/Taffer_10x10.png'))
    tileset = tcod.tileset.load_tilesheet(
        path_to_tileset, 16, 16, tcod.tileset.CHARMAP_CP437
    )

    handler: input_handlers.BaseEventHandler = setup_game.MainMenu()

    root_console = tcod.console.Console(screen_width, screen_height, order = 'F')

    with tcod.context.new(
        columns = screen_width,
        rows = screen_height,
        tileset = tileset,
        title = 'Roguelike',
        vsync = True,
    ) as context:
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
            save_game(handler, 'save_game.sav')

        except BaseException: # save on any other unexpected exception
            traceback.print_exc()
            save_game(handler, 'save_game.sav')

if __name__ == '__main__':
    main()