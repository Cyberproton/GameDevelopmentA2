from common import AnimationCycleCompletedSignal, State, AnimationState
from ecs import System
from game.component import Invincible, Passable, Score
from game.constant import GameConstant
from game.entity import Bullet, Player, Enemy
from game.signal import PlayerHurtSignal, EntityCollideSignal


def on_hurt_start(signal: PlayerHurtSignal):
    player = signal.player
    state = signal.player.get_component(State)
    anim_state = signal.player.get_component(AnimationState)
    state.current = "hurt"
    anim_state.current_state = "hurt"

    score = player.get_component(Score)
    score.score = max(0, score.score + GameConstant.SCORE_PER_HIT_BY_BULLET)
    player.add_component(Invincible())
    player.add_component(Passable())


def on_hurt_end(signal: AnimationCycleCompletedSignal):
    if signal.animation.name != "hurt":
        return
    state = signal.entity.get_component(State)
    state.current = "idle"
    player = signal.entity
    player.remove_component(Invincible)
    player.remove_component(Passable)


class HurtTransitionSystem(System):
    def __init__(self, world):
        super().__init__(world)
        self.world.register_handler(PlayerHurtSignal, on_hurt_start)
        self.world.register_handler(AnimationCycleCompletedSignal, on_hurt_end)


def on_bullet_run(signal: AnimationCycleCompletedSignal):
    if type(signal.entity) is not Bullet or signal.animation.name != "warm_up":
        return
    state = signal.entity.get_component(State)
    anim_state = signal.entity.get_component(AnimationState)
    state.current = "run"
    anim_state.current_state = "run"


def on_bullet_explode(signal: EntityCollideSignal):
    if type(signal.entity) is not Bullet:
        return
    state = signal.entity.get_component(State)
    anim_state = signal.entity.get_component(AnimationState)
    state.current = "explode"
    anim_state.current_state = "explode"


def on_bullet_dead(signal: AnimationCycleCompletedSignal):
    if type(signal.entity) is not Bullet or signal.animation.name != "explode":
        return
    state = signal.entity.get_component(State)
    anim_state = signal.entity.get_component(AnimationState)
    state.current = "dead"
    anim_state.current_state = "explode"


class BulletTransitionSystem(System):
    def __init__(self, world):
        super().__init__(world)
        self.world.register_handler(AnimationCycleCompletedSignal, on_bullet_run)
        self.world.register_handler(EntityCollideSignal, on_bullet_explode)
        self.world.register_handler(AnimationCycleCompletedSignal, on_bullet_dead)


def on_player_idle(signal: AnimationCycleCompletedSignal):
    if type(signal.entity) is not Player or signal.animation.name != "join":
        return
    state = signal.entity.get_component(State)
    anim_state = signal.entity.get_component(AnimationState)
    state.current = "idle"
    anim_state.current_state = "idle"


class PlayerTransitionSystem(System):
    def __init__(self, world):
        super().__init__(world)
        self.world.register_handler(AnimationCycleCompletedSignal, on_player_idle)


def on_enemy_attack_finished(signal: AnimationCycleCompletedSignal):
    if type(signal.entity) is not Enemy or signal.animation.name != "attack":
        return
    enemy = signal.entity
    state = enemy.get_component(State)
    state.current = "idle"
    anim_state = enemy.get_component(AnimationState)
    anim_state.current_state = "idle"


class EnemyTransitionSystem(System):
    def __init__(self, world):
        super().__init__(world)
        self.world.register_handler(AnimationCycleCompletedSignal, on_enemy_attack_finished)

    def process(self):
        pass




