import pygame

from ecs import World
from game.component import PlayerKeyBindings, Passable, Invincible, Joined, Score
from game.entity import Player, Enemy, TestEntity
from common import AnimationPlayer, EventQueue, Position
from game.system import PlayerInputSystem, GameSystem, PlayerAttackSystem, DeadEntitySystem, BulletMovementSystem, \
    BulletCollisionSystem, EntityCooldownSystem, \
    PlayerCollisionSystem, BulletRotationSystem, PlayerJoinSystem, EnemySpawnSystem
from game.system.enemy import EnemySelectTargetSystem, EnemyVelocitySystem, EnemyPositionSystem, EnemyAttackSystem
from game.constant import ScreenConstant, GameConstant
from game.system.transition import HurtTransitionSystem, BulletTransitionSystem, PlayerTransitionSystem, \
    EnemyTransitionSystem

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((ScreenConstant.WIDTH, ScreenConstant.HEIGHT))
canvas = pygame.Surface((GameConstant.WIDTH_BOUNDARY, GameConstant.HEIGHT_BOUNDARY))

pygame.display.set_caption("Assignment 2")
world = World()

world.add_system(PlayerInputSystem(world))

world.add_system(BulletRotationSystem(world))

world.add_system(PlayerAttackSystem(world))
world.add_system(PlayerCollisionSystem(world))
world.add_system(HurtTransitionSystem(world))
world.add_system(PlayerTransitionSystem(world))
world.add_system(PlayerJoinSystem(world))

world.add_system(DeadEntitySystem(world))
world.add_system(BulletMovementSystem(world))
world.add_system(BulletCollisionSystem(world))
world.add_system(BulletTransitionSystem(world))

world.add_system(EnemySelectTargetSystem(world))
world.add_system(EnemyVelocitySystem(world))
world.add_system(EnemyPositionSystem(world))
world.add_system(EnemyAttackSystem(world))
world.add_system(EnemyTransitionSystem(world))

world.add_system(EventQueue(world))
world.add_system(GameSystem(world))
world.add_system(EntityCooldownSystem(world))
world.add_system(AnimationPlayer(world, canvas))
world.add_system(EnemySpawnSystem(world))

player = Player()
player.add_component(PlayerKeyBindings({
    "UP": pygame.K_w,
    "DOWN": pygame.K_s,
    "LEFT": pygame.K_a,
    "RIGHT": pygame.K_d,
    "ATTACK": pygame.K_f,
}))
player.add_component(Joined())

player2 = Player("waiting", "waiting")
player2.add_component(PlayerKeyBindings({
    "UP": pygame.K_UP,
    "DOWN": pygame.K_DOWN,
    "LEFT": pygame.K_LEFT,
    "RIGHT": pygame.K_RIGHT,
    "ATTACK": pygame.K_j,
}))
player2.add_component(Passable())
player2.add_component(Invincible())

world.add_entity(player)
world.add_entity(player2)

world.add_entity(Enemy())
world.add_entity(Enemy())
world.add_entity(Enemy())

font = pygame.font.SysFont("monospace", 24)

# Game Loop
while world.get_system(GameSystem).is_running:
    canvas.fill((0, 0, 0))
    world.process()
    scaled_canvas = pygame.transform.scale(canvas, screen.get_size())
    screen.blit(scaled_canvas, (0, 0))

    label = font.render("Score P1: " + str(player.get_component(Score).score), True, (255, 255, 0))
    screen.blit(label, (10, 10))

    if player2.has_component(Joined):
        label = font.render("Score P2: " + str(player2.get_component(Score).score), True, (255, 255, 0))
        screen.blit(label, (ScreenConstant.WIDTH - 200, 10))

        player_name = font.render("P1", True, (0, 255, 255))
        screen.blit(player_name, (player.get_component(Position).x * 2 + 15, player.get_component(Position).y * 2 - 30))

        player_name = font.render("P2", True, (0, 255, 255))
        screen.blit(player_name, (player2.get_component(Position).x * 2 + 15, player2.get_component(Position).y * 2 - 30))

    pygame.display.flip()
    clock.tick(60)

