from ecs import Signal, Entity
from game.entity import Player, Bullet, Enemy


class EntityCollideSignal(Signal):
    def __init__(self, entity: Entity):
        self.entity = entity


class BulletCollideWithPlayerSignal(Signal):
    def __init__(self, bullet: Bullet, player: Player):
        self.bullet = bullet
        self.player = player


class PlayerAttackSignal(Signal):
    def __init__(self, player: Player):
        self.player = player


class PlayerHurtSignal(Signal):
    def __init__(self, player: Player):
        self.player = player


class EnemyAttackSignal(Signal):
    def __init__(self, enemy: Enemy):
        self.enemy = enemy


class EnemyDeathSignal(Signal):
    def __init__(self, enemy: Enemy):
        self.enemy = enemy
