from __future__ import annotations
from typing import Iterable, Iterator, TYPE_CHECKING
import numpy as np
import lzma
import pickle

import exceptions
from tcod.console import Console
from entity import Actor, Item, Object
import tile_types

import os.path

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity

class GameMap:
    def __init__(
        self,
        engine: Engine,
        width: int,
        height: int,
        entities: Iterable[Entity] = (),
        visibility = False
    ):
        self.engine = engine
        self.width, self.height = width, height
        self.entities = set(entities)
        self.tiles = np.full((width, height), fill_value = tile_types.wall, order='F') # numpy filled with wall tiles in fortran order

        self.visible = np.full(
            (width, height), fill_value = False, order = 'F'
        ) # tiles the player can see currently

        self.explored = np.full(
            (width, height), fill_value = False, order = 'F'
        ) # tiles the player has seen already

        self.visibility = visibility

        self.downstairs_location = (0, 0)
        self.upstairs_location = (0, 0)

        self.view_start_x = 0
        self.view_start_y = 0

    @property
    def gamemap(self) -> GameMap:
        return self

    @property
    def area(self):
        return self.width * self.height
    
    @property
    def objects(self) -> Iterator[Object]:
        yield from (
            entity
            for entity in self.entities
            if isinstance(entity, Object)
        )

    @property
    def actors(self) -> Iterator[Actor]:
        yield from (
            entity
            for entity in self.entities
            if isinstance(entity, Actor) and entity.is_alive
        )

    @property
    def items(self) -> Iterator[Item]:
        yield from (entity for entity in self.entities if isinstance(entity, Item))

    # check list of entities and return one being at [x, y] location
    def get_blocking_entity_at_location(self, location_x: int, location_y: int):
        for entity in self.entities:
            if (entity.blocks_movement and entity.x == location_x and entity.y == location_y):
                return entity

        return None
    
    def get_object_at_location(self, x: int, y: int):
        for object in self.objects:
            if object.x == x and object.y == y:
                return object
        
        return None

    def get_actor_at_location(self, x: int, y: int):
        for actor in self.actors:
            if actor.x == x and actor.y == y:
                return actor

        return None

    # check if given coordinates are within bounds of game map
    def in_bounds(self, x: int, y: int) -> bool:
        # Return True if x and y are inside of the bounds of this map.
        return 0 <= x < self.width and 0 <= y < self.height

    def render(self, console: Console) -> None:
        self.view_start_x = min(max(self.engine.player.x - int(self.engine.game_world.viewport_width / 2), 0), self.engine.game_world.map_width - self.engine.game_world.viewport_width)
        self.view_start_y = min(max(self.engine.player.y - int(self.engine.game_world.viewport_height / 2), 0), self.engine.game_world.map_height - self.engine.game_world.viewport_height)
        # view_end_x = min(max(self.engine.player.x + int(self.engine.game_world.viewport_width / 2), self.engine.game_world.viewport_width), self.engine.game_world.map_width)
        # view_end_y = min(max(self.engine.player.y + int(self.engine.game_world.viewport_height / 2), self.engine.game_world.viewport_height), self.engine.game_world.map_height)

        view_end_x = max(self.engine.player.x + int(self.engine.game_world.viewport_width / 2), self.engine.game_world.viewport_width)
        view_end_y = max(self.engine.player.y + int(self.engine.game_world.viewport_height / 2), self.engine.game_world.viewport_height)

        # print(
        #     f'\n=======\n'
        #     f'camera x: {self.view_start_x} camera y: {self.view_start_y}\n'
        #     f'camera view_end_x: {view_end_x} camera view_end_y: {view_end_y}\n'
        #     f'player x: {self.engine.player.x} player y: {self.engine.player.y}'
        # )

        # view_start_x:self.engine.game_world.viewport_width, view_start_y:self.engine.game_world.viewport_height used for all works
        # but creates static camera that doesn't follow player
        viewport_tiles = self.tiles[self.view_start_x:view_end_x, self.view_start_y:view_end_y]  # [o_x:view_end_x+1,o_y:view_end_y + 1]
        viewport_visible = self.visible[self.view_start_x:view_end_x, self.view_start_y:view_end_y]
        viewport_explored = self.explored[self.view_start_x:view_end_x, self.view_start_y:view_end_y]

        # prints the whole map, its called from within Engine when we render every bit to console
        # print based on condition whether tiles are visible or were explored already
        # if not, default to SHROUDed tile, which is just empty black square
        # can be toggled to show every tile or only ones seen by player
        if self.visibility == True:
            # display whole map without FOV function
            console.rgb[0 : self.width, 0 : self.height] = self.tiles['light']
        else:
            console.rgb[0:self.engine.game_world.viewport_width, 0:self.engine.game_world.viewport_height] = np.select(
                (viewport_visible, viewport_explored),
                (viewport_tiles['light'], viewport_tiles['dark']),
                tile_types.SHROUD
            )

        self.engine.update_fov()

        # sorted list of entities to render on gamemap, based on order value
        entities_for_rendering = sorted(
            self.entities, key = lambda x: x.render_order.value
        )

        for entity in entities_for_rendering:
            # don't apply FOV to entities
            if self.visibility:
                console.print(x = entity.x, y = entity.y, string = entity.char, fg = entity.color)
            else:
                # display entity only if in FOV
                if self.visible[entity.x, entity.y]:
                    console.print(
                        x = entity.x - self.view_start_x, y = entity.y - self.view_start_y, string = entity.char, fg = entity.color
                    )

class GameWorld:
    '''Holds settings for GameMap and generates new maps when dwelling deeper down'''

    def __init__(
        self,
        *,
        engine: Engine,
        viewport_width,
        viewport_height,
        map_width: int,
        map_height: int,
        initial_open: int,
        cellulara_repeats: int,
        current_floor: int = 0,
        floors_list: dict = {},
    ):
        self.engine = engine

        self.viewport_width = viewport_width
        self.viewport_height = viewport_height

        self.map_width = map_width
        self.map_height = map_height
        self.initial_open = initial_open
        self.cellulara_repeats = cellulara_repeats

        self.current_floor = current_floor
        self.floors_list = floors_list

    def load_map(self, filename: str) -> Engine:
        with open(filename, 'rb') as f:
            engine = pickle.loads(lzma.decompress(f.read()))
        assert isinstance(engine, Engine)
        return engine

    def save_map(self, filename: str) -> None:
        save_data = lzma.compress(pickle.dumps(self.engine))
        path_to_save = os.getcwd()
        with open(os.path.join('C:/Users/Konrad/Documents/Repo/Python-bits/saves', filename), 'wb') as f:
            f.write(save_data)

    def generate_floor(self) -> None:
        from procgen import generate_dungeon

        self.engine.game_map = generate_dungeon(
            map_width = self.map_width,
            map_height = self.map_height,
            initial_open = self.initial_open,
            cellulara_repeats = self.cellulara_repeats,
            engine = self.engine,
        )

    def go_downstairs(self) -> None:
        if self.current_floor + 1 in self.floors_list:
            print(
                f'lower floor in dict\n'
                f'flr_number: {self.current_floor + 1}\n'
            )
            floor_to_descend = self.floors_list[self.current_floor + 1] # pickle.loads(lzma.decompress(self.floors_list[self.current_floor + 1]))

            self.engine.game_map = floor_to_descend
            self.engine.player.place(
                self.engine.game_map.upstairs_location[0],
                self.engine.game_map.upstairs_location[1],
                self.engine.game_map
            )
            self.engine.update_fov()

            self.current_floor += 1
        else:   
            floor_to_save = self.engine.game_map

            self.generate_floor()
            
            self.floors_list[self.current_floor] = floor_to_save # lzma.compress(pickle.dumps(floor_to_save))

            print(f'list after addition: {self.floors_list.keys()}')
            map_name = 'level_' + str(self.current_floor) + '.sav'

            self.current_floor += 1

            # self.save_map(map_name)

    def go_upstairs(self) -> None:
        if self.current_floor - 1 in self.floors_list:
            print(
                f'upper floor in dict\n'
                f'flr_number: {self.current_floor - 1}\n'
            )

            if self.current_floor + 1 not in self.floors_list:
                floor_to_save = self.engine.game_map
                self.floors_list[self.current_floor] = floor_to_save # lzma.compress(pickle.dumps(floor_to_save))

                print(
                    f'current floor wasn\'t saved, doin that now to avoid issues on next descent\n'
                    f'list after addition: {self.floors_list.keys()}')

            floor_to_ascend = self.floors_list[self.current_floor - 1] # pickle.loads(lzma.decompress(self.floors_list[self.current_floor - 1]))

            self.engine.game_map = floor_to_ascend
            self.engine.player.place(
                self.engine.game_map.downstairs_location[0],
                self.engine.game_map.downstairs_location[1],
                self.engine.game_map
            )
            self.engine.update_fov()
            self.current_floor -= 1
        else:
            print(
                f'Floor not in dict or unexpected case\n'
                f'Iterator: {self.current_floor}\n'
            )
            raise exceptions.Impossible("No upper floor to ascend to!")