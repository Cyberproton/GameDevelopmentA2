from math import dist

from pygame.math import Vector2

from ecs import Component


class Position(Component, Vector2):
    def __init__(self):
        super().__init__()
        self.x = 0.0
        self.y = 0.0
        self.w = 0.0
        self.h = 0.0

    def center(self) -> tuple[float, float]:
        center_x = (self.x + self.w) / 2.0
        center_y = (self.y + self.h) / 2.0
        return center_x, center_y

    def as_tuple(self) -> tuple[float, float]:
        return self.x, self.y

    def distance(self, other) -> float:
        return dist(self.center(), other.center())

    def __add__(self, other):
        position = Position()
        position.x = self.x + other.x
        position.y = self.y + other.y
        return position

    def __sub__(self, other):
        position = Position()
        position.x = self.x - other.x
        position.y = self.y - other.y
        return position

    def copy(self):
        position = Position()
        position.x = self.x
        position.y = self.y
        position.w = self.w
        position.h = self.h
        return position


class Vector(Component):
    def __init__(self):
        self.x = 0.0
        self.y = 0.0

    def as_tuple(self) -> tuple[float, float]:
        return self.x, self.y
