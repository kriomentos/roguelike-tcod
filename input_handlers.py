from __future__ import annotations

from typing import Optional, TYPE_CHECKING
import tcod
import actions
from actions import (
    Action,
    BumpAction,
    PushAction,
    PickupAction,
    WaitAction
)
import color
import exceptions

if TYPE_CHECKING:
    from engine import Engine
    from entity import Item

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

CONFIRM_KEYS = {
    tcod.event.K_RETURN,
    tcod.event.K_KP_ENTER,
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
        # perform move action in a given direction
        # if modifier key is held change the behavior
        if key in MOVE_KEYS:
            dx, dy = MOVE_KEYS[key]

            # if the shift is held, perform other action
            # that is push the enity in front of the player
            if event.mod and tcod.event.Modifier.SHIFT:
                action = PushAction(player, dx, dy)
            # or just perform bump, which will resolve into move or attack
            # depending on if there is a target blocking path
            else:
                action = BumpAction(player, dx, dy)
        # pass the turn doing nothing, it advances other AI entites turns
        elif key in WAIT_KEYS:
            action = WaitAction(player)
        # escape action, now raises SystemExit
        elif key == tcod.event.K_ESCAPE:
            raise SystemExit()
        # open message log history view
        # it also changes the event_handler so we can navigate it freeely
        elif key == tcod.event.K_v:
            self.engine.event_handler = HistoryViewer(self.engine)
        # pick items or other pickupable things off the game_maps "floor"
        elif key == tcod.event.K_g:
            action = PickupAction(player)
        # open inventory to select item to use
        elif key == tcod.event.K_i:
            self.engine.event_handler = InventoryActivateHandler(self.engine)
        # open inventory to select item to drop
        elif key == tcod.event.K_f:
            self.engine.event_handler = InventoryDropHandler(self.engine)
        elif key == tcod.event.K_SLASH:
            self.engine.event_handler = LookHandler(self.engine)

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

class AskUserEventHandler(EventHandler):
    # handle inputs for action with special input required

    def handle_action(self, action: Optional[Action]) -> bool:
        # go back to Main handler when valid action was performed
        if super().handle_action(action):
            self.engine.event_handler = MainGameEventHandler(self.engine)
            return True
        return False

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        # by default any key exits this handler
        if event.sym in {
            tcod.event.K_LSHIFT,
            tcod.event.K_RSHIFT,
            tcod.event.K_LCTRL,
            tcod.event.K_RCTRL,
            tcod.event.K_LALT,
            tcod.event.K_RALT,
        }:
            return None
        return self.on_exit()

    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Optional[Action]:
        # any mouse click returns to main handler
        return self.on_exit()

    def on_exit(self) -> Optional[Action]:
        # called on action exit or cancel
        # returns to main handler
        self.engine.event_handler = MainGameEventHandler(self.engine)
        return None

class InventoryEventHandler(AskUserEventHandler):
    # this handler lets user select item
    # rest of the action depends on subclass

    TITLE = "<missing title>"

    def on_render(self, console: tcod.Console) -> None:
        # render inventory menu, with items in inventory and letter to select them
        # moves to different position based on where the player is located,
        # so player can see where he is
        super().on_render(console)
        number_of_items_in_inventory = len(self.engine.player.inventory.items)

        height = number_of_items_in_inventory + 2

        if height <= 3:
            height = 3

        if self.engine.player.x <= 30:
            x = 40
        else:
            x = 0

        y = 0

        width = len(self.TITLE) + 4

        console.draw_frame(
            x = x,
            y = y,
            width = width,
            height = height,
            title = self.TITLE,
            clear = True,
            fg = color.anb_white,
            bg = color.anb_black,
        )

        if number_of_items_in_inventory > 0:
            for i, item in enumerate(self.engine.player.inventory.items):
                item_key = chr(ord("a") + i)
                console.print(x + 1, y + i + 1, f"({item_key} {item.name})")
        else:
            console.print(x + 1, y + 1, "(EMPTY)")

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        player = self.engine.player
        key = event.sym
        index = key - tcod.event.K_a

        if 0 <= index <= 26:
            try:
                selected_tem = player.inventory.items[index]
            except IndexError:
                self.engine.message_log.add_message("Invalid entry", color.inavlid)
                return None
            return self.on_item_selected(selected_tem)
        return super().ev_keydown(event)

    def on_item_selected(self, item: Item) -> Optional[Action]:
        raise NotImplementedError()

class InventoryActivateHandler(InventoryEventHandler):
    # handle using item in inventory

    TITLE = "Select an item to use"

    def on_item_selected(self, item: Item) -> Optional[Action]:
        return item.consumable.get_action(self.engine.player)

class InventoryDropHandler(InventoryEventHandler):
    # drop this item

    TITLE = "Select an item to drop"

    def on_item_selected(self, item: Item) -> Optional[Action]:
        return actions.DropItem(self.engine.player, item)

class SelectIndexHandler(AskUserEventHandler):
    # handles user selecting index on map

    def __init__(self, engine: Engine):
        # set the cursor to player when handler is constructed
        super().__init__(engine)
        player = self.engine.player
        engine.mouse_location = player.x, player.y

    def on_render(self, console: tcod.Console) -> None:
        # highlights tile under cursor
        super().on_render(console)
        x, y = self.engine.mouse_location
        console.tiles_rgb["bg"][x, y] = color.anb_white
        console.tiles_rgb["fg"][x, y] = color.anb_black

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        # handle key movement or confirmation keys

        key = event.sym
        if key in MOVE_KEYS:
            modifier = 1
            if event.mod and tcod.event.Modifier.SHIFT:
                modifier *= 5
            if event.mod and tcod.event.Modifier.CTRL:
                modifier *= 10
            if event.mod and tcod.event.Modifier.ALT:
                modifier *= 20

            x, y = self.engine.mouse_location
            dx, dy = MOVE_KEYS[key]
            x += dx * modifier
            y += dy * modifier
            # clamp cursor to map size
            x = max(0, min(x, self.engine.game_map.width - 1))
            y = max(0, min(y, self.engine.game_map.height - 1))
            self.engine.mouse_location = x, y
            return None
        elif key in CONFIRM_KEYS:
            return self.on_index_selected(*self.engine.mouse_location)
        return super().ev_keydown(event)

    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Optional[Action]:
        # left click confimrs
        if self.engine.game_map.in_bounds(*event.tile):
            if event.button == 1:
                return self.on_index_selected(*event.tile)
        return super().ev_mousebuttondown(event)

    def on_index_selected(self, x: int, y: int) -> Optional[Action]:
        raise NotImplementedError()

class LookHandler(SelectIndexHandler):
    # lets player look around using keyboard
    def on_index_selected(self, x: int, y: int) -> None:
        # go back to main handler
        self.engine.event_handler = MainGameEventHandler(self.engine)