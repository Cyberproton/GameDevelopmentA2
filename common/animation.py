import json
from typing import Optional

import pygame
from pygame.math import Vector2

import signal
from game.component import LookingDirection
from ecs import Component, System
from common import Sprite, Position, SpriteSheet, State
from game.constant import AnimationConstant


class Animation:
    def __init__(self, name: str, sprites: list[Sprite], step: float = 0.3, offset: Vector2 = Vector2(), flip=False, scale=1):
        self.name = name
        self.sprites = sprites
        self.index = 0
        self.max_index = len(sprites) - 1
        self.total_frames = len(sprites)
        self.step = step
        self.offset = offset
        self.flip = flip
        self.scale = scale

    def get_current_sprite(self) -> Optional[Sprite]:
        return self.sprites[int(self.index)]

    def is_last_sprite(self):
        return int(self.index) >= self.max_index

    def reset(self):
        self.index = 0


class AnimationRotation(Component):
    def __init__(self):
        self.rotation = 0


class AnimationState(Component):
    def __init__(self):
        self.states: dict[str, Animation] = {}
        self.current_state = None

    def get_current_animation(self) -> Optional[Animation]:
        if not self.current_state or self.current_state not in self.states:
            return None
        return self.states[self.current_state]

    def get_animation(self, state: str) -> Optional[Animation]:
        return self.states[state]

    @staticmethod
    def load(spritesheet_path, spritesheet_metadata_path, state_metadata_path):
        spritesheet = SpriteSheet(spritesheet_path, spritesheet_metadata_path)
        with open(state_metadata_path) as meta_file:
            metadata = json.load(meta_file)
        meta_file.close()

        animation_states = {}
        states = metadata["states"]

        for item in states.items():
            sprites = []
            step = AnimationConstant.STEP
            state, sprite_names = item
            offset = Vector2()
            flip = False
            scale = 1

            if type(sprite_names) == str:
                sprites.extend(spritesheet.parse_sprites(sprite_names))
            elif type(sprite_names) == dict:
                sprites.extend(spritesheet.parse_sprites(sprite_names["path"]))
                if "step" in sprite_names:
                    step = sprite_names["step"]
                if "offset" in sprite_names:
                    offset_dat = sprite_names["offset"]
                    if "x" in offset_dat:
                        offset.x = offset_dat["x"]
                    if "y" in offset_dat:
                        offset.y = offset_dat["y"]
                if "flip" in sprite_names:
                    flip = sprite_names["flip"]
                if "scale" in sprite_names:
                    scale = sprite_names["scale"]
            else:
                for sprite_name in sprite_names:
                    sprites.extend(spritesheet.parse_sprites(sprite_name))
            animation_states[state] = Animation(state, sprites, step, offset, flip, scale)

        res = AnimationState()
        res.states = animation_states

        return res


class AnimationPlayer(System):
    def __init__(self, world, window):
        super().__init__(world)
        self.window = window

    def process(self):
        entities = self.world.entity_container.get_entities_with_component(AnimationState)
        entities.sort(key=lambda e: e.get_component(Position).y)
        for entity in entities:
            animation_state = entity.get_component(AnimationState)
            state = entity.get_component(State)

            # If new state, reset the previous animation
            prev_animation = animation_state.get_current_animation()
            if state.current is not animation_state.current_state and prev_animation:
                prev_animation.reset()

            animation_state.current_state = state.current
            if not state.current:
                continue

            next_animation = animation_state.get_current_animation()
            current_sprite = None
            if next_animation:
                current_sprite = next_animation.get_current_sprite()
                step = current_sprite.step
                if step <= 0:
                    step = next_animation.step
                next_animation.index = (next_animation.index + step) % next_animation.total_frames

            position = entity.get_component(Position)
            looking_direction = entity.get_component(LookingDirection)
            animation_rotation = entity.get_component(AnimationRotation)
            offset = Vector2()
            scale = 1
            if next_animation:
                offset = next_animation.offset
                scale = next_animation.scale

            if current_sprite is not None:
                surface = next_animation.get_current_sprite().surface
                pos_x = position.x + offset.x + next_animation.get_current_sprite().offset_x
                pos_y = position.y + offset.y + next_animation.get_current_sprite().offset_y

                if next_animation.flip:
                    surface = pygame.transform.flip(surface, True, False)
                if scale != 1:
                    surface = pygame.transform.scale(surface, (surface.get_size()[0] * scale, surface.get_size()[1] * scale))

                if looking_direction and looking_direction.x == -1:
                    surface = pygame.transform.flip(surface, True, False)
                elif animation_rotation and animation_rotation.rotation != 0:
                    surface = pygame.transform.rotate(surface, animation_rotation.rotation)
                self.window.blit(surface, (pos_x, pos_y))

            if next_animation and next_animation.is_last_sprite():
                self.world.dispatch_signal(signal.AnimationCycleCompletedSignal(entity, next_animation))
                next_animation.reset()
