'''Handle loading and initalization of game seesions'''
from __future__ import annotations

import copy
import lzma
import pickle
import traceback
from typing import Optional

import tcod

import color
from engine import Engine
import entity_factories
import input_handlers
from game_map import GameWorld

background_image = tcod.image.load("menu_background.png")[:, :, :3]

def new_game() -> Engine:
    # return a brand new game session as Engine instance
    map_width = 80
    map_height = 44

    init_open = 0.5

    max_monsters = 6
    max_items = 4

    player = copy.deepcopy(entity_factories.player)

    engine = Engine(player = player)

    engine.game_world = GameWorld(
        engine = engine,
        map_width = map_width,
        map_height = map_height,
        initial_open = init_open,
        max_monsters = max_monsters,
        max_items = max_items,
    )

    engine.game_world.generate_floor()
    engine.update_fov()

    engine.message_log.add_message(
        "Hello and welcome choomer, to yet another dungeon!", color.welcome_text
    )

    return engine

def load_game(filename: str) -> Engine:
    # load Engine instance from file
    with open(filename, "rb") as f:
        engine = pickle.loads(lzma.decompress(f.read()))
    assert isinstance(engine, Engine)
    return engine

class MainMenu(input_handlers.BaseEventHandler):
    '''handle main menu rendering and input'''

    def on_render(self, console: tcod.Console) -> None:
        console.draw_semigraphics(background_image, 0, 0)

        console.print(
            console.width // 2,
            console.height // 2 - 4,
            "SCUFFED ROUGELIKE",
            fg = color.menu_title,
            alignment = tcod.CENTER,
        )
        console.print(
            console.width // 2,
            console.height -2,
            "By Kreeo",
            fg = color.menu_title,
            alignment = tcod.CENTER,
        )

        menu_width = 24
        for i, text in enumerate(
            ["[N] Play a new game", "[C] Contiune last game", "[Q] Quit"]
        ):
            console.print(
                console.width // 2,
                console.height // 2 - 2 + i,
                text.ljust(menu_width),
                fg = color.menu_text,
                # bg = color.black,
                alignment = tcod.CENTER,
                bg_blend = tcod.BKGND_ALPHA(64),
            )

    def ev_keydown(
        self, event: tcod.event.KeyDown
    ) -> Optional[input_handlers.BaseEventHandler]:
        if event.sym in (tcod.event.K_q, tcod.event.K_ESCAPE):
            raise SystemExit()
        elif event.sym == tcod.event.K_c:
            try:
                return input_handlers.MainGameEventHandler(load_game("save_game.sav"))
            except FileNotFoundError:
                return input_handlers.PopupMessage(self, "No saved file to load")
            except Exception as exc:
                traceback.print_exc()
                return input_handlers.PopupMessage(self, f"Failed to load save:\n{exc}")
        elif event.sym == tcod.event.K_n:
            return input_handlers.MainGameEventHandler(new_game())

        return None