from drone import Drone
from image_manager import ImageManager
from primitives import *
import pygame
import constants as c

class Obstacle(GameObject):
    def __init__(self, game, player, drone, position = (500, 300)):
        super().__init__(game)
        self.surface = ImageManager.load("images/test_obstacle.png")
        self.shadow_mask = ImageManager.load("images/test_obstacle_shadow_mask.png")
        self.size = Pose((250, 250))
        self.base_point = Pose((0, -50))
        self.height = 120
        self.position = Pose(position)
        self.opacity = 256
        self.player = player
        self.drone = drone

    def draw(self, surf, offset=(0, 0), scale = 1):
        if (not self.is_on_screen(offset, scale)):
            return

        surf_to_draw = scale_surface_by(self.surface, scale)

        x = (self.position.x + offset[0])*scale - surf_to_draw.get_width()//2
        y = (self.position.y + offset[1])*scale - surf_to_draw.get_height()//2
        surf_to_draw.set_alpha(self.opacity)
        surf.blit(surf_to_draw, (x,y))

        if self.collides_with(self.drone):
            self.drone.draw_shadow_over(self, surf, offset, scale)

        if c.SHOW_DEBUG:
            pygame.draw.rect(surf, (0, 255, 0), (self.position.x*scale + offset[0]*scale - self.size.x//2*scale, self.position.y*scale + offset[1]*scale - self.size.y//2*scale, self.size.x*scale, self.size.y*scale), width=3)

    def is_on_screen(self, offset=(0, 0), scale=1):
        x = offset[0] * scale + self.position.x * scale
        y = offset[1] * scale + self.position.y * scale

        buffer = 300
        if x < -buffer or x > c.WINDOW_WIDTH + buffer or y < -buffer or y > c.WINDOW_HEIGHT + buffer:
            return False
        return True

    def draw_shadow(self, surf, offset, scale):
        return

    def update(self, dt, events):
        if self.collides_with(self.player, nudge = True):
            pass

    def directly_over(self, player):
        rect3 = pygame.Rect(
            self.position.x - self.size.x//2,
            self.position.y - self.size.y//2,
            self.size.x,
            self.size.y
        )
        if rect3.collidepoint(*player.position.get_position()):
            return True
        return False

    def collides_with(self, player, nudge = False):
        if player.get_base_position().y > self.position.y + self.size.y//2 + player.radius:
            return False
        if player.get_base_position().y < self.position.y - self.size.y//2 - player.radius:
            return False
        if player.get_base_position().x > self.position.x + self.size.x//2 + player.radius:
            return False
        if player.get_base_position().x < self.position.x - self.size.x//2 - player.radius:
            return False

        player_position = player.get_base_position().get_position()
        player_position_yscaled = player_position[0], player_position[1]*2
        radius = player.radius
        if (isinstance(player, Drone)):
            radius = player.max_radius
        rect1 = pygame.Rect(
            self.position.x - self.size.x//2 - radius,
            (self.position.y - self.size.y//2)*2,
            self.size.x + radius*2,
            self.size.y*2)
        if rect1.collidepoint(*player_position_yscaled):
            if nudge:
                if (player.get_base_position().x < self.position.x):
                    player.position.x = self.position.x - self.size.x//2 - radius - player.base_point.x
                else:
                    player.position.x = self.position.x + self.size.x // 2 + radius - player.base_point.x
            return True
        rect2 = pygame.Rect(
            self.position.x - self.size.x//2,
            (self.position.y - self.size.y//2)*2 - radius,
            self.size.x,
            (self.size.y)*2 + radius * 2)
        if rect2.collidepoint(*player_position_yscaled):
            if nudge:
                if (player.get_base_position().y < self.position.y):
                    player.position.y = self.position.y - self.size.y//2 - radius//2 - player.base_point.y
                else:
                    player.position.y = self.position.y + self.size.y//2 + radius//2 - player.base_point.y
            return True
        rect3 = pygame.Rect(
            self.position.x - self.size.x//2,
            (self.position.y - self.size.y//2)*2,
            self.size.x,
            self.size.y*2
        )
        for position in (rect3.bottomleft, rect3.bottomright, rect3.topleft, rect3.topright):
            diff = (Pose(player_position_yscaled) - Pose(position))
            if diff.magnitude() < radius:
                if nudge:
                    diff.scale_to(radius)
                    target = Pose((position[0] + diff.x, position[1] //2 + diff.y//2))
                    player.position = target - player.base_point
                return True
        return False