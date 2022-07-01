from __future__ import annotations

from typing import Optional, TYPE_CHECKING
import tcod
from actions import (
    Action,
    BumpAction,
    EscapeAction,
    PushAction,
    WaitAction
)
import color
import exceptions

if TYPE_CHECKING:
    from engine import Engine

MOVE_KEYS = {
    # Arrow keys.
    tcod.event.K_UP: (0, -1),   # up
    tcod.event.K_DOWN: (0, 1),  # down
    tcod.event.K_LEFT: (-1, 0), # left
    tcod.event.K_RIGHT: (1, 0), # right
    tcod.event.K_HOME: (-1, -1),    # up-left
    tcod.event.K_END: (-1, 1),  # down-left
    tcod.event.K_PAGEUP: (1, -1),   # up-rigth
    tcod.event.K_PAGEDOWN: (1, 1),  # down-right
    # Numpad keys.
    tcod.event.K_KP_1: (-1, 1),
    tcod.event.K_KP_2: (0, 1),
    tcod.event.K_KP_3: (1, 1),
    tcod.event.K_KP_4: (-1, 0),
    tcod.event.K_KP_6: (1, 0),
    tcod.event.K_KP_7: (-1, -1),
    tcod.event.K_KP_8: (0, -1),
    tcod.event.K_KP_9: (1, -1),
    # Vi keys.
    tcod.event.K_h: (-1, 0),
    tcod.event.K_j: (0, 1),
    tcod.event.K_k: (0, -1),
    tcod.event.K_l: (1, 0),
    tcod.event.K_y: (-1, -1),
    tcod.event.K_u: (1, -1),
    tcod.event.K_b: (-1, 1),
    tcod.event.K_n: (1, 1),
    # qwe ad zxc
    tcod.event.K_w: (0, -1),
    tcod.event.K_x: (0, 1),
    tcod.event.K_a: (-1, 0),
    tcod.event.K_d: (1, 0),
    tcod.event.K_q: (-1, -1),
    tcod.event.K_e: (1, -1),
    tcod.event.K_z: (-1, 1),
    tcod.event.K_c: (1, 1),
}

WAIT_KEYS = {
    tcod.event.K_PERIOD,
    tcod.event.K_KP_5,
    tcod.event.K_CLEAR,
    tcod.event.K_s,
}

CURSOR_Y_KEYS = {
    tcod.event.K_UP: -1,
    tcod.event.K_DOWN: 1,
    tcod.event.K_PAGEUP: -10,
    tcod.event.K_PAGEDOWN: 10,
}

class EventHandler(tcod.event.EventDispatch[Action]):
    def __init__(self, engine: Engine):
        self.engine = engine

    def handle_events(self, event: tcod.event.Event) -> None:
        self.handle_action(self.dispatch(event))

    def handle_action(self, action: Optional[Action]) -> bool:

        if action is None:
            return False

        try:
            action.perform()
        except exceptions.Impossible as exc:
            self.engine.message_log.add_message(exc.args[0], color.impossible)
            return False

        self.engine.handle_enemy_turns()

        self.engine.update_fov()
        return True

    def ev_mousemotion(self, event: tcod.event.MouseMotion) -> None:
        if self.engine.game_map.in_bounds(event.tile.x, event.tile.y):
            self.engine.mouse_location = event.tile.x, event.tile.y

    def ev_quit(self, evemt: tcod.event.Quit) -> Optional[Action]:
        raise SystemExit()

    def on_render(self, console: tcod.Console) -> None:
        self.engine.render(console)

class MainGameEventHandler(EventHandler):
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        action: Optional[Action] = None

        key = event.sym

        player = self.engine.player

        if key in MOVE_KEYS:
            dx, dy = MOVE_KEYS[key]

            if event.mod and tcod.event.Modifier.SHIFT:
                print("mod action")
                action = PushAction(player, dx, dy)
            else:
                action = BumpAction(player, dx, dy)
        elif key in WAIT_KEYS:
            action = WaitAction(player)
        elif key == tcod.event.K_ESCAPE:
            action = EscapeAction(player)
        elif key == tcod.event.K_v:
            self.engine.event_handler = HistoryViewer(self.engine)

        return action

class GameOverEventHandler(EventHandler):
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        if event.sym == tcod.event.K_ESCAPE:
            raise SystemExit()

class HistoryViewer(EventHandler):
    # show log history on a larger window with page scrolling
    def __init__(self, engine: Engine):
        super().__init__(engine)
        self.log_length = len(engine.message_log.messages)
        self.cursor = self.log_length - 1

    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console) # main state as the background

        log_console = tcod.Console(console.width - 6, console.height - 6)

        # draw frame with custom banner
        log_console.draw_frame(0, 0, log_console.width, log_console.height)
        log_console.print_box(
            0, 0, log_console.width, 1, "~Message log~", alignment = tcod.CENTER
        )

        # render message log using cursor parameter
        self.engine.message_log.render_messages(
            log_console,
            1,
            1,
            log_console.width - 2,
            log_console.height - 2,
            self.engine.message_log.messages[: self.cursor + 1],
        )
        log_console.blit(console, 3, 3)

    def ev_keydown(self, event: tcod.event.KeyDown) -> None:
        if event.sym in CURSOR_Y_KEYS:
            adjust = CURSOR_Y_KEYS[event.sym]
            if adjust < 0 and self.cursor == 0:
                # move only from the top to bottom when on edge
                self.cursor = self.log_length - 1
            elif adjust > 0 and self.cursor == self.log_length - 1:
                # same with bottom to top
                self.cursor = 0
            else:
                # otherwise move while staying clamped to the bounds of log
                self.cursor = max(0, min(self.cursor + adjust, self.log_length - 1))
        elif event.sym == tcod.event.K_HOME:
            self.cursor = 0 # on HOME go back to the top | first message
        elif event.sym == tcod.event.K_END:
            self.cursor = self.log_length # on END go to the bottom | last message
        else: # on any other action go back to main game state
            self.engine.event_handler = MainGameEventHandler(self.engine)
