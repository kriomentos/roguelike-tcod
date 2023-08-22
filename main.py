from __future__ import annotations

import tcod
import traceback

import numpy as np

import color
import exceptions
import input_handlers
import setup_game

def save_game(handler: input_handlers.BaseEventHandler, filename: str) -> None:
    # if current event handler has active Engine then save it
    if isinstance(handler, input_handlers.EventHandler):
        handler.engine.save_as(filename)
        print('Game saved')

def generate_rex_file(console: tcod.console.Console):
    CP437_TO_UNICODE = np.asarray(tcod.tileset.CHARMAP_CP437)

    # Initialize a Unicode-to-CP437 array.
    # 0x20000 is the current full range of Unicode.
    # fill_value=ord("?") means that "?" will be the result of any unknown codepoint.
    UNICODE_TO_CP437 = np.full(0x20000, fill_value=ord("?"))
    # Assign the CP437 mappings.
    UNICODE_TO_CP437[CP437_TO_UNICODE] = np.arange(len(CP437_TO_UNICODE))

    # Convert from Unicode to CP437 in-place.
    console.ch[:] = UNICODE_TO_CP437[console.ch]

    # Convert console alpha into REXPaint's alpha key color.
    KEY_COLOR = (255, 0, 255)
    is_transparent = console.rgba["bg"][:, :, 3] == 0
    console.rgb["bg"][is_transparent] = KEY_COLOR

    tcod.console.save_xp("example.xp", [console])

def main() -> None:
    screen_width = 80
    screen_height = 50

    tileset = tcod.tileset.load_tilesheet(
        'tilesets/Anikki_square_10x10.png', 16, 16, tcod.tileset.CHARMAP_CP437
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
            generate_rex_file(root_console)

        except BaseException: # save on any other unexpected exception
            traceback.print_exc()
            save_game(handler, 'save_game.sav')

if __name__ == '__main__':
    main()