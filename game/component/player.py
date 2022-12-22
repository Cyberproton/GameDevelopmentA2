from ecs import Component


class Invincible(Component):
    pass


class Joined(Component):
    pass


class PlayerKeyBindings(Component):
    def __init__(self, key_bindings):
        self.key_bindings = key_bindings


class PlayerTag(Component):
    def __init__(self):
        self.tags = []


class Score(Component):
    def __init__(self):
        self.score = 0
