import pygame

from common import State, Position
from ecs import System
from game.component import Invincible, PlayerTag, PlayerKeyBindings, Joined, LookingDirection, Passable
from game.constant import ScreenConstant, GameConstant
from game.entity import Player
from game.signal import BulletCollideWithPlayerSignal, PlayerHurtSignal, PlayerAttackSignal
from game.system import SPEED


class PlayerCollisionSystem(System):
    def __init__(self, world):
        super().__init__(world)
        self.world.register_handler(BulletCollideWithPlayerSignal, self.on_player_collide_with_bullet)

    def on_player_collide_with_bullet(self, signal: BulletCollideWithPlayerSignal):
        if signal.player.has_component(Invincible):
            return
        self.world.dispatch_signal(PlayerHurtSignal(signal.player))


class PlayerJoinSystem(System):
    def __init__(self, world):
        super().__init__(world)

    def process(self):
        key_pressed = pygame.key.get_pressed()
        players = self.world.get_entities(Player)

        for player in players:
            if player.has_component(Joined):
                continue
            key_bindings = player.get_component(PlayerKeyBindings).key_bindings
            if not key_pressed[key_bindings["ATTACK"]]:
                continue
            player.add_component(Joined())
            state = player.get_component(State)
            state.current = "join"
            anim_state = player.get_component(State)
            anim_state.current_state = "join"
            player.remove_component(Passable)
            player.remove_component(Invincible)


class PlayerInputSystem(System):
    def __init__(self, world):
        super().__init__(world)

    def process(self):
        key_pressed = pygame.key.get_pressed()

        entities = self.world.get_entities(Player)

        for entity in entities:
            if not entity.has_component(Joined):
                continue

            state = entity.get_component(State)

            x = 0
            y = 0
            a = False

            key_bindings = entity.get_component(PlayerKeyBindings).key_bindings
            if key_pressed[key_bindings["UP"]]:
                y = -1
            if key_pressed[key_bindings["DOWN"]]:
                y = 1
            if key_pressed[key_bindings["LEFT"]]:
                x = -1
            if key_pressed[key_bindings["RIGHT"]]:
                x = 1
            if key_pressed[key_bindings["ATTACK"]]:
                a = True

            looking_direction = entity.get_component(LookingDirection)
            looking_direction.x = looking_direction.x if x == 0 else x
            looking_direction.y = looking_direction.y if y == 0 else y

            if state.current == "hurt" or state.current == "join":
                return
            if a:
                state.current = "attack"
                if looking_direction.x > 0:
                    x += 0.2
                else:
                    x -= 0.2
                self.world.dispatch_signal(PlayerAttackSignal(entity))
            elif x == 0 and y == 0:
                state.current = "idle"
            else:
                state.current = "run"

            position = entity.get_component(Position)
            position.x += SPEED * x
            position.y += SPEED * y
            if position.x < 0:
                position.x = 0
            if position.x > GameConstant.WIDTH_BOUNDARY:
                position.x = GameConstant.HEIGHT_BOUNDARY
            if position.y < 0:
                position.y = 0
            if position.y > GameConstant.WIDTH_BOUNDARY:
                position.y = GameConstant.HEIGHT_BOUNDARY
