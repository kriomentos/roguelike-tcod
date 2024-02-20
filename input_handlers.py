from __future__ import annotations

import os
from typing import Callable, Optional, Tuple, TYPE_CHECKING, Union
import tcod
from tcod import libtcodpy
import actions
from actions import (
    Action,
    BumpAction,
    PushAction,
    PickupAction,
    WaitAction
)
import color
from engine import Engine
import exceptions

if TYPE_CHECKING:
    from engine import Engine
    from entity import Item, Actor

MOVE_KEYS = {
    # Arrow keys.
    tcod.event.KeySym.UP: (0, -1),   # up
    tcod.event.KeySym.DOWN: (0, 1),  # down
    tcod.event.KeySym.LEFT: (-1, 0), # left
    tcod.event.KeySym.RIGHT: (1, 0), # right
    tcod.event.KeySym.HOME: (-1, -1),    # up-left
    tcod.event.KeySym.END: (-1, 1),  # down-left
    tcod.event.KeySym.PAGEUP: (1, -1),   # up-right
    tcod.event.KeySym.PAGEDOWN: (1, 1),  # down-right
    # Numpad keys.
    tcod.event.KeySym.KP_1: (-1, 1),
    tcod.event.KeySym.KP_2: (0, 1),
    tcod.event.KeySym.KP_3: (1, 1),
    tcod.event.KeySym.KP_4: (-1, 0),
    tcod.event.KeySym.KP_6: (1, 0),
    tcod.event.KeySym.KP_7: (-1, -1),
    tcod.event.KeySym.KP_8: (0, -1),
    tcod.event.KeySym.KP_9: (1, -1),
    # Vi keys.
    tcod.event.KeySym.h: (-1, 0),
    tcod.event.KeySym.j: (0, 1),
    tcod.event.KeySym.k: (0, -1),
    tcod.event.KeySym.l: (1, 0),
    tcod.event.KeySym.y: (-1, -1),
    tcod.event.KeySym.u: (1, -1),
    tcod.event.KeySym.b: (-1, 1),
    tcod.event.KeySym.n: (1, 1),
    # qwe ad zxc
    # tcod.event.KeySym.w: (0, -1),
    # tcod.event.KeySym.x: (0, 1),
    # tcod.event.KeySym.a: (-1, 0),
    # tcod.event.KeySym.d: (1, 0),
    # tcod.event.KeySym.q: (-1, -1),
    # tcod.event.KeySym.e: (1, -1),
    # tcod.event.KeySym.z: (-1, 1),
    # tcod.event.KeySym.c: (1, 1),
}

WAIT_KEYS = {
    tcod.event.KeySym.PERIOD,
    tcod.event.KeySym.KP_5,
    tcod.event.KeySym.CLEAR,
    tcod.event.KeySym.s,
}

CURSOR_Y_KEYS = {
    tcod.event.KeySym.UP: -1,
    tcod.event.KeySym.DOWN: 1,
    tcod.event.KeySym.PAGEUP: -10,
    tcod.event.KeySym.PAGEDOWN: 10,
}

CONFIRM_KEYS = {
    tcod.event.KeySym.RETURN,
    tcod.event.KeySym.KP_ENTER,
}

ActionHandler = Union[Action, "BaseEventHandler"]
"""An event handler return value which can trigger an action or switch active handlers.

If a handler is returned then it will become the active handler for future events.
If an action is returned it will be attempted and if it's valid then
MainGameEventHandler will become the active handler.
"""

class BaseEventHandler(tcod.event.EventDispatch[ActionHandler]):
    def handle_events(self, event: tcod.event.Event) -> BaseEventHandler:
        '''handle event and return next active event handler'''
        state = self.dispatch(event)
        if isinstance(state, BaseEventHandler):
            return state
        assert not isinstance(state, Action), f"{self!r} can not handle actions"
        return self

    def on_render(self, console: tcod.console.Console) -> None:
        raise NotImplementedError()

    def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
        raise SystemExit()

class PopupMessage(BaseEventHandler):
    # displays a popup text window

    def __init__(self, parent_handler: BaseEventHandler, text: str):
        self.parent = parent_handler
        self.text = text

    def on_render(self, console: tcod.console.Console) -> None:
        self.parent.on_render(console)
        console.rgb["fg"] //= 8
        console.rgb["bg"] //= 8

        console.print(
            console.width // 2,
            console.height // 2,
            self.text,
            fg = color.anb_white,
            bg = color.anb_black,
            alignment = tcod.CENTER,
        )

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[BaseEventHandler]:
        # any key returns to parent handler
        return self.parent

class EventHandler(BaseEventHandler):
    def __init__(self, engine: Engine):
        self.engine = engine

    def handle_events(self, event: tcod.event.Event) -> BaseEventHandler:
        '''handle events for input handlers with an engine'''
        action_or_state = self.dispatch(event)
        if isinstance(action_or_state, BaseEventHandler):
            return action_or_state
        if self.handle_action(action_or_state):
            # valid action was performed
            if not self.engine.player.is_alive:
                # player was killed sometime during or after the action
                return GameOverEventHandler(self.engine)
            elif self.engine.player.level.requires_level_up:
                return LevelUpEventHandler(self.engine)
            return MainGameEventHandler(self.engine)
        return self

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
        # if self.engine.game_map.in_bounds(event.tile.x, event.tile.y):
        self.engine.mouse_location = event.tile.x, event.tile.y

    def on_render(self, console: tcod.console.Console) -> None:
        self.engine.render(console)

class MainGameEventHandler(EventHandler):
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionHandler]:
        action: Optional[Action] = None

        key = event.sym
        modifier = event.mod

        player = self.engine.player

        # if shift and period(>) is held traverse the stairs
        # for now only downwards but will also handle upwards
        if key == tcod.event.KeySym.PERIOD and modifier and tcod.event.Modifier.SHIFT:
            return actions.TakeStairsAction(player)

        # perform move action in a given direction
        # if modifier key is held change the behavior
        if key in MOVE_KEYS:
            dx, dy = MOVE_KEYS[key]

            # if the shift is held, perform other action
            # that is push the entity in front of the player
            if key and modifier and tcod.event.Modifier.SHIFT:
                action = PushAction(player, dx, dy)
            # or just perform bump, which will resolve into move or attack
            # depending on if there is a target blocking path
            # else:
            action = BumpAction(player, dx, dy)

        # pass the turn doing nothing, it advances other AI entities turns
        elif key in WAIT_KEYS:
            action = WaitAction(player)
        # escape action, now raises SystemExit
        elif key == tcod.event.KeySym.ESCAPE:
            raise SystemExit()
        elif key == tcod.event.KeySym.o:
            return SelectInteractableEventHandler(self.engine)
        # open message log history view
        # it also changes the event_handler so we can navigate it freely
        elif key == tcod.event.KeySym.v:
            return HistoryViewer(self.engine)
        # pick items or other pickupable things off the game_maps "floor"
        elif key == tcod.event.KeySym.g:
            action = PickupAction(player)
        # open inventory to select item to use
        elif key == tcod.event.KeySym.i:
            return InventoryActivateHandler(self.engine)
        # open inventory to select item to drop
        elif key == tcod.event.KeySym.f:
            return InventoryDropHandler(self.engine)
        # open character sheet pop-up
        elif key == tcod.event.KeySym.c:
            return CharacterScreenEventHandler(self.engine)
        # lets user "look around" to gain information on the entities in fov
        # without having to interact with them
        elif key == tcod.event.KeySym.SLASH:
            return LookHandler(self.engine)
        elif key == tcod.event.KeySym.z:
            self.engine.game_map.visibility = not self.engine.game_map.visibility
            print(f'vis: {self.engine.game_map.visibility}')
        elif key == tcod.event.KeySym.x:
            print(f"Skipping to the next level...")
            return actions.SkipStairs(player)
        elif key == tcod.event.KeySym.a:
            for entity in set(self.engine.game_map.actors) - {player}:
                entity.fighter.die()

        return action

class GameOverEventHandler(EventHandler):
    def on_quit(self) -> None:
        # handle exiting out of finished game
        if os.path.exists("save_game.sav"):
            os.remove("save_game.sav") # delete active file save
        raise exceptions.QuitWithoutSaving() # avoid saving finished game

    def ev_quit(self, event: tcod.event.Quit) -> None:
        self.on_quit()

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        if event.sym == tcod.event.KeySym.ESCAPE:
            self.on_quit()
        return None

class HistoryViewer(EventHandler):
    # show log history on a larger window with page scrolling
    def __init__(self, engine: Engine):
        super().__init__(engine)
        self.log_length = len(engine.message_log.messages)
        self.cursor = self.log_length - 1

    def on_render(self, console: tcod.console.Console) -> None:
        super().on_render(console) # main state as the background

        log_console = tcod.console.Console(console.width - 6, console.height - 6)

        # draw frame with custom banner
        log_console.draw_frame(0, 0, log_console.width, log_console.height)
        log_console.print_box(
            0, 0, log_console.width, 1, "~Message log~", alignment = libtcodpy.CENTER
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

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[MainGameEventHandler]:
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
        elif event.sym == tcod.event.KeySym.HOME:
            self.cursor = 0 # on HOME go back to the top | first message
        elif event.sym == tcod.event.KeySym.END:
            self.cursor = self.log_length # on END go to the bottom | last message
        else: # on any other action go back to main game state
            return MainGameEventHandler(self.engine)
        return None

class AskUserEventHandler(EventHandler):
    # handle inputs for action with special input required

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionHandler]:
        # by default any key exits this handler
        if event.sym in {
            tcod.event.KeySym.LSHIFT,
            tcod.event.KeySym.RSHIFT,
            tcod.event.KeySym.LCTRL,
            tcod.event.KeySym.RCTRL,
            tcod.event.KeySym.LALT,
            tcod.event.KeySym.RALT,
        }:
            return None
        return self.on_exit()

    def ev_mousebuttondown(
        self, event: tcod.event.MouseButtonDown
    ) -> Optional[ActionHandler]:
        # any mouse click returns to main handler
        return self.on_exit()

    def on_exit(self) -> Optional[ActionHandler]:
        # called on action exit or cancel
        # returns to main handler
        return MainGameEventHandler(self.engine)

class SelectInteractableEventHandler(AskUserEventHandler):
    def __init__(self, engine: Engine):
        super().__init__(engine)
        self.player = self.engine.player
        engine.mouse_location = self.player.x, self.player.y

    def on_render(self, console: tcod.console.Console) -> None:
        super().on_render(console)
        x, y = self.engine.mouse_location
        console.rgb["bg"][x, y] = color.anb_white
        console.rgb["fg"][x, y] = color.anb_black

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionHandler]:
        key = event.sym

        if key in MOVE_KEYS:
            dx, dy = MOVE_KEYS[key]

            x, y = self.engine.mouse_location
            x += dx
            y += dy
            x = max(self.player.x- 1, min(x, self.player.x + 1))
            y = max(self.player.y - 1, min(y, self.player.y + 1))
            self.engine.mouse_location = x, y

            return None
        elif key in CONFIRM_KEYS:
            return self.on_index_selected(*self.engine.mouse_location)
        return super().ev_keydown(event)
    
    def ev_mousebuttondown(
        self, event: tcod.event.MouseButtonDown
    ) -> Optional[ActionHandler]:
        if self.engine.game_map.in_bounds(*event.tile):
            if event.button == 1:
                return self.on_index_selected(*event.tile)
        return super().ev_mousebuttondown(event)

    def on_index_selected(self, x: int, y: int) -> Optional[ActionHandler]:
        return InteractionSelectionEventHandler(self.engine, (x, y))
    

INTERACTIONS = {
    'object': ['option 1', 'option 2', 'option 3'],
    'actor': ['other 1', 'other 2', 'other 3', 'other 4'],
    'other': ['it is', 'what it', 'is', 'joever', 'orewa', 'ochinchin'],
}

class InteractionSelectionEventHandler(AskUserEventHandler):
    TITLE = "<missing title>"

    def __init__(self, engine: Engine, selected_target: Tuple[int, int]):
        super().__init__(engine)
        self.selected_target = selected_target

    def on_render(self, console: tcod.console.Console) -> None:
        super().on_render(console)
        if hasattr(self.engine.game_map.get_blocking_entity_at_location(self.selected_target[0], self.selected_target[1]), 'interaction'):
            self.interactions_list = INTERACTIONS['object']
        elif hasattr(self.engine.game_map.get_blocking_entity_at_location(self.selected_target[0], self.selected_target[1]), 'fighter'):
            self.interactions_list = INTERACTIONS['actor']
        else:
            self.interactions_list = INTERACTIONS['other']

        try:
            self.TITLE = self.engine.game_map.get_blocking_entity_at_location(self.selected_target[0], self.selected_target[1]).name
        except AttributeError:
            self.TITLE = "Non-entity type"

        height = len(self.interactions_list) + 2

        if height <= 3:
            height = 3

        if self.engine.player.x <= 30:
            x = 40
        else:
            x = 0
        
        y = 0

        width = len(self.TITLE) + 15
        
        console.draw_frame(
            x = x,
            y = y,
            width = width,
            height = height,
            title = self.TITLE,
            clear = True,
            fg = (color.white),
            bg = (color.black),
        )

        if len(self.interactions_list) > 0:
            for i, option in enumerate(self.interactions_list):
                option_key = chr(ord("a") + i)

                option_string = f'({option_key} {option})'

                console.print(x + 1, y + i + 1, option_string)
        else:
            console.print(x + 1, y + 1, 'HUH WHAT')

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionHandler]:
        key = event.sym
        index = key - tcod.event.KeySym.a

        if 0 <= index <= 26:
            if hasattr(self.selected_target, 'name'):
                print(f'Option {self.interactions_list[index]}, target at: {self.selected_target} it was {self.engine.game_map.get_blocking_entity_at_location(self.selected_target[0], self.selected_target[1]).name}')
            else:
                print(f'Option {self.interactions_list[index]}, target at: {self.selected_target}')
        
        return super().ev_keydown(event)

class CharacterScreenEventHandler(AskUserEventHandler):
    TITLE = "Character sheet"

    def on_render(self, console: tcod.console.Console) -> None:
        super().on_render(console)

        if self.engine.player.x <= 30:
            x = 40
        else:
            x = 0

        y = 0

        width = len(self.TITLE) + 8

        console.draw_frame(
            x = x,
            y = y,
            width = width,
            height = 7,
            title = self.TITLE,
            clear = True,
            fg = (color.white),
            bg = (color.black),
        )
        # current level, xp and amount to next level
        console.print(
            x = x + 1,
            y = y + 1,
            string = f"Level: {self.engine.player.level.current_level}"
        )
        console.print(
            x = x + 1,
            y = y + 2,
            string = f"Current experience: {self.engine.player.level.current_xp}"
        )
        console.print(
            x = x + 1,
            y = y + 3,
            string = f"To next level: {self.engine.player.level.experience_to_next_level}"
        )
        # power and defense
        console.print(
            x = x + 1,
            y = y + 4,
            string = f"Strength: {self.engine.player.fighter.power}"
        )
        console.print(
            x = x + 1,
            y = y + 5,
            string = f"Defense: {self.engine.player.fighter.defense}"
        )

class LevelUpEventHandler(AskUserEventHandler):
    TITLE = "Level up"

    def on_render(self, console: tcod.console.Console) -> None:
        super().on_render(console)

        if self.engine.player.x <= 30:
            x = 40
        else:
            x = 0

        console.draw_frame(
            x = x,
            y = 0,
            width = 35,
            height = 8,
            title = self.TITLE,
            clear = True,
            fg = (color.white),
            bg = (color.black),
        )

        console.print(x = x + 1, y = 1, string = "You gathered more experience")
        console.print(x = x + 1, y = 2, string = "One of your attributes increased")

        console.print(
            x = x + 1,
            y = 4,
            string = f"a) Constitution (+20 HP, from {self.engine.player.fighter.max_hp})",
        )
        console.print(
            x = x + 1,
            y = 5,
            string = f"b) Strength (+1 attack, from {self.engine.player.fighter.power}",
        )
        console.print(
            x = x + 1,
            y = 6,
            string = f"c) Defense (+1 defense, from {self.engine.player.fighter.defense}",
        )

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionHandler]:
        player = self.engine.player
        key = event.sym
        index = key - tcod.event.KeySym.a

        if 0 <= index <= 2:
            if index == 0:
                player.level.increase_max_hp()
            elif index == 1:
                player.level.increase_power()
            else:
                player.level.increase_defense()
        else:
            self.engine.message_log.add_message("Invalid entry", color.invalid)

            return None

        return super().ev_keydown(event)
    # blocks user from clicking mouse to exit menu
    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Optional[ActionHandler]:
        return None

class InventoryEventHandler(AskUserEventHandler):
    # this handler lets user select item
    # rest of the action depends on subclass

    TITLE = "<missing title>"

    def on_render(self, console: tcod.console.Console) -> None:
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

                is_equipped = self.engine.player.equipment.item_is_equipped(item)

                item_string = f"({item_key} {item.name})"

                if is_equipped:
                    item_string = f"{item_string} (E)"

                console.print(x + 1, y + i + 1, item_string)
        else:
            console.print(x + 1, y + 1, "(EMPTY)")

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionHandler]:
        player = self.engine.player
        key = event.sym
        index = key - tcod.event.KeySym.a

        if 0 <= index <= 26:
            try:
                selected_item = player.inventory.items[index]
            except IndexError:
                self.engine.message_log.add_message("Invalid entry", color.invalid)
                return None
            return self.on_item_selected(selected_item)
        return super().ev_keydown(event)

    def on_item_selected(self, item: Item) -> Optional[ActionHandler]:
        raise NotImplementedError()

class InventoryActivateHandler(InventoryEventHandler):
    # handle using item in inventory

    TITLE = "Select an item to use"

    def on_item_selected(self, item: Item) -> Optional[ActionHandler]:
        if item.consumable:
            return item.consumable.get_action(self.engine.player)
        elif item.equippable:
            return actions.EquipAction(self.engine.player, item)
        else:
            return None

class InventoryDropHandler(InventoryEventHandler):
    # drop this item

    TITLE = "Select an item to drop"

    def on_item_selected(self, item: Item) -> Optional[ActionHandler]:
        return actions.DropItem(self.engine.player, item)

class SelectIndexHandler(AskUserEventHandler):
    # handles user selecting index on map

    def __init__(self, engine: Engine):
        # set the cursor to player when handler is constructed
        super().__init__(engine)
        player = self.engine.player
        engine.mouse_location = player.x, player.y

    def on_render(self, console: tcod.console.Console) -> None:
        # highlights tile under cursor
        super().on_render(console)
        x, y = self.engine.mouse_location
        # x = x - self.engine.game_map.view_start_x
        # y = y - self.engine.game_map.view_start_y
        console.rgb["bg"][x, y] = color.anb_white
        console.rgb["fg"][x, y] = color.anb_black

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionHandler]:
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

    def ev_mousebuttondown(
        self, event: tcod.event.MouseButtonDown
    ) -> Optional[ActionHandler]:
        # left click confirms
        if self.engine.game_map.in_bounds(*event.tile):
            if event.button == 1:
                return self.on_index_selected(*event.tile)
        return super().ev_mousebuttondown(event)

    def on_index_selected(self, x: int, y: int) -> Optional[ActionHandler]:
        raise NotImplementedError()

class LookHandler(SelectIndexHandler):
    # lets player look around using keyboard
    def on_index_selected(self, x: int, y: int) -> MainGameEventHandler:
        # go back to main handler
        return MainGameEventHandler(self.engine)

class SingleRangedAttackHandler(SelectIndexHandler):
    # handles targeting single enemy
    def __init__(self, engine: Engine, callback: Callable[[Tuple[int, int]], Optional[Action]]):
        super().__init__(engine)

        self.callback = callback

    def on_index_selected(self, x: int, y: int) -> Optional[Action]:
        return self.callback((x, y))

class AreaRangedAttackHandler(SelectIndexHandler):
    # handles targeting area within given radius, any entity in area will be affected

    def __init__(
        self,
        engine: Engine,
        radius: int,
        callback: Callable[[Tuple[int, int]], Optional[Action]],
    ):
        super().__init__(engine)

        self.radius = radius
        self.callback = callback

    def on_render(self, console: tcod.console.Console) -> None:
        # highlight the tile under the cursor
        super().on_render(console)

        x, y = self.engine.mouse_location
        console.draw_frame(
            x = x - self.radius - 1,
            y = y - self.radius - 1,
            width = self.radius ** 2,
            height = self.radius ** 2,
            fg = color.anb_red,
            clear = False,
        )

    def on_index_selected(self, x: int, y: int) -> Optional[Action]:
        return self.callback((x, y))