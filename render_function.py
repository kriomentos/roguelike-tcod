from __future__ import annotations
from turtle import color

from typing import TYPE_CHECKING

import color

if TYPE_CHECKING:
    from tcod import Console

def render_bar(
    console: Console, current_value: int, maximum_value: int, total_width: int
) -> None:
    bar_width = int(maximum_value - current_value * total_width) # int(float(current_value) / maximum_value * total_width)

    console.draw_rect(
        x = 84, 
        y = 2, 
        width = 1, 
        height = total_width, 
        ch = 1, 
        bg = color.bar_filled
    )

    if bar_width > 0:
        console.draw_rect(
            x = 84,
            y = 2,
            width = 1,
            height = bar_width,
            ch = 1,
            bg = color.bar_empty
        )

    console.print(
        x = 80, y = 0,
        string = f"HP: {current_value}/{maximum_value}", fg = color.bar_text
    )