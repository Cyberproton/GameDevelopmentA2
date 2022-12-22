from ecs import Component


class State(Component):
    def __init__(self, initial_state: str = None):
        self.current = initial_state
