class ScreenConstant:
    WIDTH: int = 800
    HEIGHT: int = 600


class GameConstant:
    WIDTH_BOUNDARY = ScreenConstant.WIDTH / 2
    HEIGHT_BOUNDARY = ScreenConstant.HEIGHT / 2
    SCORE_PER_BULLET = 5
    SCORE_PER_ENEMY = 10
    SCORE_PER_HIT_BY_BULLET = -20


class AnimationConstant:
    STEP = 0.3


class PlayerConstant:
    ATTACK_RANGE = 30


class BulletConstant:
    SPEED = 3
    MAX_WALL_COLLISIONS = 3


class EnemyConstant:
    SPEED = 2
    REACH_DISTANCE = 70


class CooldownConstant:
    ENEMY_FIRE_BULLET = "enemy_fire_bullet"
    ENEMY_FIRE_BULLET_COOLDOWN = 3.0


class KeyBindings:
    pass
