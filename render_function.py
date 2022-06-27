from __future__ import annotations

from typing import TYPE_CHECKING

import color

if TYPE_CHECKING:
    from tcod import Console

def render_bar(
    console: Console, current_value: int, maximum_value: int, total_width: int
) -> None:
    # it ends up as 0 for current_value < 3, which makes it be empty
    # while player is still alive :)
    # i can't into basic maths
    bar_width = int(float(current_value) / maximum_value * total_width)

    # console.draw_rect(
    #     x = 84, 
    #     y = 2, 
    #     width = 1, 
    #     height = total_width, 
    #     ch = 1, 
    #     bg = color.bar_filled
    # )

    console.draw_rect(x = 0, y = 45, width = total_width, height = 1, ch = 1, bg = color.bar_empty)

    if bar_width > 0:
        console.draw_rect(
            x = 0, y = 45, width = bar_width, height = 1, ch = 1, bg = color.bar_filled
        )

    # if bar_width >= 0:
    #     console.draw_rect(
    #         x = 84,
    #         y = 2,
    #         width = 1,
    #         height = total_width - bar_width,
    #         ch = 1,
    #         bg = color.bar_empty
    #     )

    console.print(
        x = 1, y = 45,
        string = f"HP: {current_value}/{maximum_value}", fg = color.black
    )