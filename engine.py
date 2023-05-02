from __future__ import annotations

import lzma
import pickle
import color

from typing import TYPE_CHECKING

from tcod.console import Console
from tcod.map import compute_fov

import exceptions
import render_function
from message_log import MessageLog

if TYPE_CHECKING:
    from entity import Actor
    from game_map import GameMap, GameWorld

class Engine:
    game_map: GameMap
    game_world: GameWorld

    def __init__(self, player: Actor):
        self.message_log = MessageLog()
        self.mouse_location = (0, 0)
        self.player = player

    def handle_enemy_turns(self) -> None:
        for entity in set(self.game_map.actors) - {self.player}:
            if entity.ai:
                try:
                    entity.ai.perform()
                except exceptions.Impossible:
                    pass # ignore impossible action from AI

    def update_fov(self) -> None:
        self.game_map.visible[:] = compute_fov(
            self.game_map.tiles['transparent'],
            (self.player.x, self.player.y),
            radius = 8,
        )
        self.game_map.explored |= self.game_map.visible

    def render(self, console: Console) -> None:
        self.game_map.render(console)

        self.message_log.render(
            console = console, x = 21, y = 45, width = 50, height = 5
        )

        render_function.render_bar(
            console = console,
            current_value = self.player.fighter.hp,
            maximum_value = self.player.fighter.max_hp,
            total_width = 20,
            fill_color = color.anb_green,
            empty_color = color.anb_red,
            position = 44,
            bar_name = 'HP'
        )

        render_function.render_bar(
            console = console,
            current_value = self.player.level.current_xp,
            maximum_value = self.player.level.experience_to_next_level,
            total_width = 20,
            fill_color = color.anb_purple,
            empty_color = color.grey,
            position = 45,
            bar_name = 'XP'
        )

        render_function.render_dungeon_level(
            console = console,
            dungeon_level = self.game_world.current_floor,
            location = (0, 46)
        )

        render_function.render_names_at_mouse_location(
            console = console, x = 21, y = 44, engine = self
        )

    def save_as(self, filename: str) -> None:
        '''save this Engine instance as compressed file'''
        save_data = lzma.compress(pickle.dumps(self))
        with open(filename, 'wb') as f:
            f.write(save_data)