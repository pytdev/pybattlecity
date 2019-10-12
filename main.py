import pygame
from pygame.locals import *
from field import Field
from projectile import Projectile
from tank import Tank
from util import *
from explosion import Explosion
from math import floor, ceil
from config import *


class Game:
    TANK_SPEED = 4

    def __init__(self):
        self.scene = GameObject()

        self.field = Field()
        self.field.load_from_file('data/level1.txt')

        self.scene.add_child(self.field)

        tank = self.tank = Tank(Tank.Color.YELLOW, Tank.Type.LEVEL_1)
        tank.place(*self.field.get_center_of_cell(1, 1))
        tank.activate_shield()
        self.scene.add_child(tank)

        self.projectiles = GameObject()
        self.scene.add_child(self.projectiles)

        # tank2 = Tank(Tank.Color.GREEN, Tank.Type.LEVEL_4)
        # tank2.place(*self.field.coord_by_col_and_row(2, 0))
        # self.scene.add_child(tank2)

        self.font_debug = pygame.font.Font(None, 18)

    def switch_my_tank(self):
        tank = self.tank
        tank.remove_from_parent()
        t, d, x, y = tank.tank_type, tank.direction, tank.x, tank.y
        types = list(Tank.Type)
        current_index = types.index(t)
        next_type = types[(current_index + 1) % len(types)]
        tank = Tank(Tank.Color.PLAIN, next_type)
        tank.x, tank.y = x, y
        tank.direction = d
        tank.activate_shield()
        self.scene.add_child(tank)
        self.tank = tank

    def make_explosion(self):
        expl = Explosion(*self.tank.center_point)
        self.scene.add_child(expl)

    def render(self, screen):
        self.scene.visit(screen)

        # - 1 because the scene is not literally an object
        dbg_text = f'Objects: {self.scene.total_children - 1}'
        dbg_label = self.font_debug.render(dbg_text, 1, (255, 255, 255))
        screen.blit(dbg_label, (5, 5))

        for p in self.projectiles:
            self.field.check_hit(p)

    def fire(self):
        pt = self.tank.gun_point
        projectile = Projectile(*pt, self.tank.direction, 1)
        self.projectiles.add_child(projectile)

    def move_tank(self, direction: Direction):
        tank = self.tank
        tank.moving = True
        tank.direction = direction
        vx, vy = direction.vector
        vx *= self.TANK_SPEED
        vy *= self.TANK_SPEED
        tank.x += vx
        tank.y += vy
        if self.field.intersect_rect(tank.bounding_rect):
            # undo movement
            tank.x -= vx
            tank.y -= vy

    def complete_moving(self):
        discrete_step = ATLAS().real_sprite_size // 2
        if self.tank.moving:
            vx, vy = self.tank.direction.vector
            if vx != 0:
                f = floor if vx < 0 else ceil
                tank.x = f(tank.x / discrete_step) * discrete_step
            if vy != 0:
                f = floor if vy < 0 else ceil
                tank.y = f(tank.y / discrete_step) * discrete_step

        self.tank.moving = False


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))

    game = Game()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_t:
                    game.switch_my_tank()
                elif event.key == K_ESCAPE:
                    running = False
                elif event.key == K_f:
                    game.make_explosion()
                elif event.key == K_SPACE:
                    game.fire()

        keys = pygame.key.get_pressed()

        tank = game.tank
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            game.move_tank(Direction.UP)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            game.move_tank(Direction.DOWN)
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            game.move_tank(Direction.LEFT)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            game.move_tank(Direction.RIGHT)
        else:
            game.complete_moving()

        screen.fill((128, 128, 128))

        game.render(screen)

        if DEBUG:
            pygame.draw.circle(screen, (0, 255, 255), game.tank.gun_point, 4, 1)
            # pygame.draw.rect(screen, (255, 255, 0), game.tank.bounding_rect, 1)
            # pygame.draw.circle(screen, (0, 0, 255), game.tank.center_point, 4, 1)

        pygame.display.flip()

    pygame.quit()




