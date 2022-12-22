from pygame.math import Vector2

from common import Position, State, AnimationState
from ecs import System
from game.component import Target, Velocity, CooldownDict, Joined, LookingDirection
from game.constant import EnemyConstant, CooldownConstant
from game.entity import Player, Enemy, Bullet


class EnemySelectTargetSystem(System):
    def process(self):
        players = self.world.entity_container.get_entities(Player)
        enemies = self.world.entity_container.get_entities(Enemy)

        # Select nearest player as target
        for enemy in enemies:
            enemy_pos = enemy.get_component(Position)
            enemy_target = enemy.get_component(Target)
            nearest_player_index = -1
            min_distance = float("inf")
            current_index = 0

            enemy_target.target = None

            for player in players:
                if not player.has_component(Joined):
                    continue

                player_pos = player.get_component(Position)
                distance = enemy_pos.distance(player_pos)
                if distance < min_distance:
                    min_distance = distance
                    nearest_player_index = current_index
                current_index += 1

            if nearest_player_index < 0:
                continue

            enemy_target.target = players[nearest_player_index]


class EnemyLookingDirection(System):
    def __init__(self, world):
        super().__init__(world)


class EnemyVelocitySystem(System):
    def process(self):
        enemies = self.world.entity_container.get_entities(Enemy)

        for enemy in enemies:
            target = enemy.get_component(Target).target
            position = enemy.get_component(Position)
            velocity = enemy.get_component(Velocity)
            looking_direction = enemy.get_component(LookingDirection)

            #looking_direction.x = 1 if velocity.x > 0 else -1
            #looking_direction.y = 1 if velocity.y > 0 else -1

            velocity.x = 0
            velocity.y = 0

            state = enemy.get_component(State)
            anim_state = enemy.get_component(AnimationState)

            if state.current == "attack":
                return

            if not target:
                continue

            target_position = target.get_component(Position)
            if target_position.distance(position) < EnemyConstant.REACH_DISTANCE:
                state.current = "idle"
                anim_state.current_state = "idle"
                continue

            state.current = "run"
            anim_state.current_state = "run"

            diff_x = target_position.x - position.x
            diff_y = target_position.y - position.y
            direction = Vector2(diff_x, diff_y).normalize()

            looking_direction.x = 1 if direction.x > 0 else -1
            looking_direction.y = 1 if direction.y > 0 else -1

            velocity.x = direction.x * velocity.speed
            velocity.y = direction.y * velocity.speed


class EnemyPositionSystem(System):
    def process(self):
        enemies = self.world.entity_container.get_entities(Enemy)

        for enemy in enemies:
            velocity = enemy.get_component(Velocity)
            position = enemy.get_component(Position)

            position.x += velocity.x
            position.y += velocity.y


class EnemyAttackSystem(System):
    def process(self):
        enemies = self.world.entity_container.get_entities(Enemy)

        for enemy in enemies:
            state = enemy.get_component(State)

            if state.current == "attack":
                continue

            cooldown_dict = enemy.get_component(CooldownDict)
            cooldown_expired = cooldown_dict.has_cooldown_expired(CooldownConstant.ENEMY_FIRE_BULLET)

            if not cooldown_expired:
                continue

            cooldown_dict.add_cooldown(CooldownConstant.ENEMY_FIRE_BULLET, CooldownConstant.ENEMY_FIRE_BULLET_COOLDOWN)

            position = enemy.get_component(Position)
            target = enemy.get_component(Target)
            target_position = target.target.get_component(Position)
            direction = (target_position - position).normalize()

            anim_state = enemy.get_component(AnimationState)
            state.current = "attack"
            anim_state.current_state = "attack"

            bullet = Bullet(position.copy(), direction)
            self.world.entity_container.add_entity(bullet)
