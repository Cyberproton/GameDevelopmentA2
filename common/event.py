import pygame.event

from ecs import System


class EventQueue(System):
    def __init__(self, world):
        super().__init__(world)
        self.events = []

    def process(self):
        self.events = pygame.event.get()
