from __future__ import annotations
import string

from typing import Tuple, TYPE_CHECKING

import color

if TYPE_CHECKING:
    from tcod import Console
    from engine import Engine
    from game_map import GameMap

def get_name_at_location(x: int, y: int, game_map: GameMap) -> str:
    if not game_map.in_bounds(x, y) or not game_map.visible[x, y]:
        return 'Out of bounds'

    names = ', '.join(
        entity.name for entity in game_map.entities if entity.x == x and entity.y == y
    )

    return names.capitalize()

def render_bar(
    console: Console,
    current_value: int,
    maximum_value: int,
    total_width: int,
    fill_color: tuple,
    empty_color: tuple,
    position: int,
    bar_name: string,
) -> None:
    # it ends up as 0 for current_value < 3, which makes it be empty
    bar_width = int(float(current_value) / maximum_value * total_width)

    console.draw_rect(
        x = 0,
        y = position,
        width = total_width,
        height = 1,
        ch = 1,
        bg = empty_color
    )

    if bar_width > 0:
        console.draw_rect(
            x = 0, y = position, width = bar_width, height = 1, ch = 1, bg = fill_color
        )

    console.print(
        x = 1,
        y = position,
        string = f'{bar_name}: {current_value}/{maximum_value}',
        fg = color.black
    )

def render_dungeon_level(
    console: Console, dungeon_level: int, location: Tuple[int, int]
) -> None:
    x, y = location

    console.print(x = x, y = y, string = f'Dungeon level: {dungeon_level}')

def render_names_at_mouse_location(
    console: Console, x: int, y: int, engine: Engine
) -> None:
    # grabs current moust position over grid
    mouse_x, mouse_y = engine.mouse_location
    # gets information about given coordinate hovered
    name_at_mouse_location = get_name_at_location(
        x = mouse_x, y = mouse_y, game_map = engine.game_map
    )

    console.print(x = x, y = y, string = name_at_mouse_location)