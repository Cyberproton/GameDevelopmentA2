from ecs import Signal


class AnimationCycleCompletedSignal(Signal):
    def __init__(self, entity, animation):
        self.entity = entity
        self.animation = animation
