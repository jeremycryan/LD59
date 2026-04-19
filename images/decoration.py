from image_manager import ImageManager
from primitives import *
import pygame
import constants as c


class Decoration(GameObject):

    def __init__(self, game, surface, position, base_point, radius=30):
        super().__init__(game)
        self.surface = surface
        self.base_point = base_point
        self.radius = radius
        self.position = position

    def update(self, dt, events):
        pass

    def draw(self, surf, offset=(0, 0), scale = 1):
        if (not self.is_on_screen(offset, scale)):
            return

        surf_to_draw = scale_surface_by(self.surface, scale)

        x = (self.position.x + offset[0])*scale - surf_to_draw.get_width()//2
        y = (self.position.y + offset[1])*scale - surf_to_draw.get_height()//2
        surf.blit(surf_to_draw, (x,y))

    def is_on_screen(self, offset=(0, 0), scale=1):
        x = offset[0] * scale + self.position.x * scale
        y = offset[1] * scale + self.position.y * scale

        buffer = self.radius * 3
        if x < -buffer or x > c.WINDOW_WIDTH + buffer or y < -buffer or y > c.WINDOW_HEIGHT + buffer:
            return False
        return True