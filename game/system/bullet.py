from pygame.math import Vector2

from common import State, Position, AnimationRotation
from ecs import System
from game.component import BulletDirection, Collision, Passable, Score
from game.constant import ScreenConstant, BulletConstant, PlayerConstant, GameConstant
from game.entity import Bullet, Player
from game.signal import PlayerAttackSignal, BulletCollideWithPlayerSignal, EntityCollideSignal


class BulletMovementSystem(System):
    def process(self):
        bullets = self.world.entity_container.get_entities(Bullet)

        for bullet in bullets:
            state = bullet.get_component(State)

            if state.current != "run":
                continue

            position = bullet.get_component(Position)
            bullet_direction = bullet.get_component(BulletDirection)

            position.x += bullet_direction.x * bullet_direction.speed
            position.y += bullet_direction.y * bullet_direction.speed


class BulletRotationSystem(System):
    def process(self):
        bullets = self.world.entity_container.get_entities(Bullet)

        for bullet in bullets:
            bullet_direction = bullet.get_component(BulletDirection)
            bullet_rotation = bullet.get_component(AnimationRotation)
            # angle = Vector2((1, 0)).angle_to(bullet_direction)
            angle = bullet_direction.angle_to(Vector2(1, 0))
            bullet_rotation.rotation = angle


class BulletCollisionSystem(System):
    def __init__(self, world):
        super().__init__(world)
        self.world.register_handler(PlayerAttackSignal, self.on_player_attack)

    def process(self):
        bullets = self.world.entity_container.get_entities(Bullet)
        players = self.world.entity_container.get_entities(Player)

        for bullet in bullets:
            position = bullet.get_component(Position)
            bullet_state = bullet.get_component(State)
            bullet_direction = bullet.get_component(BulletDirection)
            collision = bullet.get_component(Collision)

            # Dealing with walls
            if position.x < 0 or position.x > GameConstant.WIDTH_BOUNDARY:
                bullet_direction.x = -bullet_direction.x
                collision.times += 1
            if position.y < 0 or position.y > GameConstant.HEIGHT_BOUNDARY:
                bullet_direction.y = -bullet_direction.y
                collision.times += 1
            bullet_direction.normalize_ip()
            if collision.times >= BulletConstant.MAX_WALL_COLLISIONS:
                bullet_state.current = "dead"

            # Dealing with players
            for player in players:
                player_pos = player.get_component(Position)

                if position.distance(player_pos) < 10:
                    if not player.has_component(Passable):
                        self.world.dispatch_signal(BulletCollideWithPlayerSignal(bullet, player))
                        self.world.dispatch_signal(EntityCollideSignal(bullet))
                        break

    def on_player_attack(self, player_attack_signal: PlayerAttackSignal):
        player = player_attack_signal.player
        player_position = player.get_component(Position)
        bullets = self.world.get_entities(Bullet)

        for bullet in bullets:
            position = bullet.get_component(Position)
            direction = bullet.get_component(BulletDirection)
            if position.distance(player_position) < PlayerConstant.ATTACK_RANGE:
                diff_x = position.x - player_position.x
                diff_y = position.y - player_position.y
                direction.x = diff_x
                direction.y = diff_y
                direction.normalize_ip()
                player.get_component(Score).score += GameConstant.SCORE_PER_BULLET
