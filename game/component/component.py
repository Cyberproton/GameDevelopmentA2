from typing import Optional

from pygame.math import Vector2
import time

from game.constant import BulletConstant, EnemyConstant
from ecs import Component


class Passable(Component):
    pass


class LookingDirection(Component):
    def __init__(self):
        self.x = 1
        self.y = 1


class LiveState(Component):
    def __init__(self):
        self.alive = True


class BulletDirection(Component, Vector2):
    def __init__(self, direction: tuple[float, float] = (1, 0), speed: float = BulletConstant.SPEED):
        super().__init__()
        self.x = direction[0]
        self.y = direction[1]
        self.speed = speed
        self.normalize_ip()

    def negate_ip(self):
        self.x = -self.x
        self.y = -self.y


class Collision(Component):
    def __init__(self):
        self.times = 0


class Health(Component):
    def __init__(self):
        self.health = 0


class Target(Component):
    def __init__(self):
        self.target = None


class Velocity(Component, Vector2):
    def __init__(self, direction: tuple[float, float] = (0, 0), speed: float = EnemyConstant.SPEED):
        super().__init__()
        self.x = direction[0]
        self.y = direction[1]
        self.speed = speed
        if self.x != 0 or self.y != 0:
            self.normalize_ip()
        self.x *= speed
        self.y *= speed


class Cooldown:
    def __init__(self, cooldown_type: str, duration: float, start: float):
        self.cooldown_type = cooldown_type
        self.start = start
        self.end = start + duration
        self.duration = duration

    def has_expired(self) -> bool:
        return time.time() > self.end

    def add_duration(self, duration: float):
        return Cooldown(self.cooldown_type, self.duration + duration, self.start)


class CooldownDict(Component):
    def __init__(self):
        self.cooldown = {}

    def get_cooldown(self, cooldown_type: str) -> Optional[Cooldown]:
        if cooldown_type not in self.cooldown:
            return None
        return self.cooldown[cooldown_type]

    def has_cooldown_expired(self, cooldown_type: str) -> bool:
        if cooldown_type not in self.cooldown:
            return True
        return self.cooldown[cooldown_type].has_expired()

    def add_cooldown(self, cooldown_type: str, duration: float):
        if cooldown_type in self.cooldown and not self.cooldown[cooldown_type].has_expired():
            cooldown = self.cooldown[cooldown_type].add_duration(duration)
        else:
            cooldown = Cooldown(cooldown_type, duration, time.time())
        self.cooldown[cooldown_type] = cooldown


    def remove_cooldown(self, cooldown: Cooldown):
        if cooldown.cooldown_type not in self.cooldown:
            return
        self.cooldown.pop(cooldown.cooldown_type)

    def remove_expired_cooldowns(self):
        for value in list(self.cooldown.values()):
            if value.has_expired():
                self.cooldown.pop(value.cooldown_type)




