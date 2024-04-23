'''Handle loading and initialization of game sessions'''
from __future__ import annotations

import os.path

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

path_to_background_image = os.path.abspath(os.path.join(os.path.dirname(__file__), 'menu_background.png'))
background_image = tcod.image.load(path_to_background_image)[:, :, :3]

def new_game() -> Engine:
    # return a brand new game session as Engine instance
    map_width = 80
    map_height = 40
    viewport_width = 80
    viewport_height = 40

    player = copy.deepcopy(entity_factories.player)

    engine = Engine(player = player)

    engine.game_world = GameWorld(
        engine = engine,
        viewport_width = viewport_width,
        viewport_height = viewport_height,
        map_width = map_width,
        map_height = map_height,
    )

    engine.game_world.generate_floor()
    engine.update_fov()

    engine.message_log.add_message(
        'Hello and welcome choomer, to yet another dungeon!', color.welcome_text
    )

    dagger = copy.deepcopy(entity_factories.dagger)
    leather_armor = copy.deepcopy(entity_factories.leather_armor)

    dagger.parent = player.inventory
    leather_armor.parent = player.inventory

    player.inventory.items.append(dagger)
    player.equipment.toggle_equip(dagger, add_message = False)

    player.inventory.items.append(leather_armor)
    player.equipment.toggle_equip(leather_armor, add_message = False)

    return engine

def load_game(filename: str) -> Engine:
    path_to_load = os.path.join(os.getcwd(), 'saves', filename)
    # load Engine instance from file
    with open(path_to_load, 'rb') as f:
        engine = pickle.loads(lzma.decompress(f.read()))
    assert isinstance(engine, Engine)
    
    return engine

class MainMenu(input_handlers.BaseEventHandler):
    '''handle main menu rendering and input'''

    def on_render(self, console: tcod.console.Console) -> None:
        console.draw_semigraphics(background_image, 0, 0)

        console.print(
            console.width // 2,
            console.height // 2 - 4,
            'SCUFFED ROGUELIKE',
            fg = color.menu_title,
            alignment = 2,
        )
        console.print(
            console.width // 2,
            console.height -2,
            'By Kreeo',
            fg = color.menu_title,
            alignment = 2,
        )

        menu_width = 24
        for i, text in enumerate(
            ['[N] Play a new game', '[C] Continue last game', '[Q] Quit']
        ):
            console.print(
                console.width // 2,
                console.height // 2 - 2 + i,
                text.ljust(menu_width),
                fg = color.menu_text,
                # bg = color.black,
                alignment = 2,
                bg_blend = 12,
            )

    def ev_keydown(
        self, event: tcod.event.KeyDown
    ) -> Optional[input_handlers.BaseEventHandler]:
        if event.sym in (tcod.event.KeySym.q, tcod.event.KeySym.ESCAPE):
            raise SystemExit()
        elif event.sym == tcod.event.KeySym.c:
            try:
                return input_handlers.MainGameEventHandler(load_game('save_game.sav'))
            except FileNotFoundError:
                return input_handlers.PopupMessage(self, 'No saved file to load')
            except Exception as exc:
                traceback.print_exc()
                return input_handlers.PopupMessage(self, f'Failed to load save:\n{exc}')
        elif event.sym == tcod.event.KeySym.n:
            return input_handlers.MainGameEventHandler(new_game())

        return None