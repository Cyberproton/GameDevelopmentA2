import pygame

from game.constant import PlayerConstant, GameConstant
from common import Position, EventQueue, State
from game.component import CooldownDict, Score
from ecs import System
from game.entity import Enemy
from game.signal import PlayerAttackSignal, EnemyDeathSignal


class GameSystem(System):
    def __init__(self, world):
        super().__init__(world)
        self.is_running = True

    def process(self):
        events = self.world.get_system(EventQueue).events
        for event in events:
            if event.type == pygame.QUIT:
                self.is_running = False


class ScreenSystem(System):
    def __init__(self, world, width: int, height: int):
        super().__init__(world)
        self.width = width
        self.height = height


class EnemySpawnSystem(System):
    def __init__(self, world):
        super().__init__(world)
        self.world.register_handler(EnemyDeathSignal, self.on_enemy_death)

    def on_enemy_death(self, signal: EnemyDeathSignal):
        self.world.add_entity(Enemy())


class EntityCooldownSystem(System):
    def __init__(self, world):
        super().__init__(world)

    def process(self):
        entities = self.world.entity_container.get_entities_with_component(CooldownDict)
        for entity in entities:
            cooldown_dict = entity.get_component(CooldownDict)
            cooldown_dict.remove_expired_cooldowns()


SPEED = 3


class PlayerAttackSystem(System):
    def __init__(self, world):
        super().__init__(world)
        self.world.register_handler(PlayerAttackSignal, self.on_player_attack)

    def on_player_attack(self, player_attack_signal: PlayerAttackSignal):
        player = player_attack_signal.player
        player_position = player.get_component(Position)
        opponents = self.world.get_entities(Enemy)
        for entity in opponents:
            position = entity.get_component(Position)
            if position.distance(player_position) < PlayerConstant.ATTACK_RANGE:
                state = entity.get_component(State)
                state.current = "dead"
                self.world.dispatch_signal(EnemyDeathSignal(entity))
                player.get_component(Score).score += GameConstant.SCORE_PER_ENEMY


class DeadEntitySystem(System):
    def process(self):
        entities = self.world.entity_container.get_entities_with_component(State)
        for entity in entities:
            state = entity.get_component(State)
            if state.current == "dead":
                self.world.remove_entity(entity)


