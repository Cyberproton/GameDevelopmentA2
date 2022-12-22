import random

from game.constant import *
from ecs import Entity
from common import AnimationState, Position, State, AnimationRotation
from game.component import LookingDirection, BulletDirection, Velocity, Target, CooldownDict, Collision, PlayerTag, \
    Score


class Game(Entity):
    def __init__(self):
        pass


class GameEntity(Entity):
    def __init__(self, entity_type: str, components=None):
        super().__init__(entity_type, components)
        self.add_component(CooldownDict())


class TestEntity(GameEntity):
    def __init__(self):
        super().__init__("Player", None)
        # animation_state = AnimationState.load("./asset/sprite/bullet.png", "./asset/sprite/bullet.json",
        #                                       "./asset/sprite/bullet_state.json")

        # animation_state = AnimationState.load("./asset/sprite/zero.png", "./asset/sprite/zero.json",
        #                                       "./asset/sprite/zero_state.json")

        animation_state = AnimationState.load("./asset/sprite/enemy/grenade_man.png",
                                              "./asset/sprite/enemy/grenade_man.json",
                                              "./asset/sprite/enemy/grenade_man_state.json")

        animation_state.current_state = "idle"
        state = State("idle")

        position = Position()
        position.x = 20
        position.y = 20
        position.w = 32
        position.h = 32

        self.add_component(position)
        self.add_component(LookingDirection())
        self.add_component(state)
        self.add_component(animation_state)


class Player(GameEntity):
    def __init__(self, initial_state="join", initial_animation_state="join"):
        super().__init__("Player", None)
        animation_state = AnimationState.load("./asset/sprite/zero.png", "./asset/sprite/zero.json",
                                              "./asset/sprite/zero_state.json")
        animation_state.current_state = initial_animation_state
        state = State(initial_state)

        position = Position()
        position.x, position.y = (100, 100)
        position.w = 32
        position.h = 32

        self.add_component(PlayerTag())
        self.add_component(position)
        self.add_component(LookingDirection())
        self.add_component(state)
        self.add_component(animation_state)
        self.add_component(Score())


class Enemy(GameEntity):
    def __init__(self):
        super().__init__("Opponent", None)
        animation_state = AnimationState.load("./asset/sprite/enemy/gm.png",
                                              "./asset/sprite/enemy/grenade_man.json",
                                              "./asset/sprite/enemy/grenade_man_state.json")
        animation_state.current_state = "idle"
        state = State("idle")

        position = Position()
        position.x = random.uniform(-200, -100)
        choice_x = random.choice((0, 1))
        if choice_x == 1:
            position.x = random.uniform(GameConstant.WIDTH_BOUNDARY + 100, GameConstant.WIDTH_BOUNDARY + 200)
        position.y = random.uniform(-200, -100)
        choice_y = random.choice((0, 1))
        if choice_y == 1:
            position.y = random.uniform(GameConstant.HEIGHT_BOUNDARY + 100, GameConstant.HEIGHT_BOUNDARY + 200)
        position.w = 32
        position.h = 32

        velocity = Velocity()
        target = Target()

        self.get_component(CooldownDict).add_cooldown(
            CooldownConstant.ENEMY_FIRE_BULLET,
            CooldownConstant.ENEMY_FIRE_BULLET_COOLDOWN)

        self.add_component(position)
        self.add_component(LookingDirection())
        self.add_component(state)
        self.add_component(animation_state)
        self.add_component(velocity)
        self.add_component(target)


class Bullet(GameEntity):
    def __init__(self, position: tuple[float, float], direction: tuple[float, float]):
        super().__init__("bullet", None)
        animation_state = AnimationState.load("./asset/sprite/bullet.png", "./asset/sprite/bullet.json",
                                              "./asset/sprite/bullet_state.json")
        animation_state.current_state = "warm_up"
        state = State("warm_up")

        position_component = Position()
        position_component.x = position[0]
        position_component.y = position[1]
        position_component.w = 16
        position_component.h = 27

        bullet_direction = BulletDirection(direction)

        anim_rotation = AnimationRotation()
        anim_rotation.rotation = 90

        self.add_component(position_component)
        self.add_component(state)
        self.add_component(bullet_direction)
        self.add_component(animation_state)
        self.add_component(anim_rotation)
        self.add_component(Collision())
