import math
import random

import pygame

from image_manager import ImageManager
from primitives import *
import platform


class Particle:

    def __init__(self, position=(0, 0), velocity=(0, 0), duration=1.0):
        self.position = Pose(position)
        self.velocity = Pose(velocity)
        self.is_destroyed = False
        self.duration = duration
        self.age = 0
        self.layer = 1

    def get_scale(self):
        return 1

    def get_alpha(self):
        return 255

    def get_base_position(self):
        return self.position - Pose((0, 40))

    def draw_shadow(self, surface, offset, scale):
        pass

    def update(self, dt, events):
        if self.is_destroyed:
            return
        self.position += self.velocity * dt
        if self.age > self.duration:
            self.destroy()
        self.age += dt

    def draw(self, surf, offset=(0, 0), scale=1):
        if self.is_destroyed:
            return

    def through(self):
        return min(0.999, self.age/self.duration)

    def destroy(self):
        self.is_destroyed = True


class DustParticle(Particle):
    def __init__(self, position=(0, 0), velocity = (0, 0), duration = 0.7):
        super().__init__(position, velocity, duration)
        self.surf = ImageManager.load("images/dust_particle.png")

    def get_scale(self):
        return (1 - 0.5*self.through())*0.6

    def get_alpha(self):
        return (255 - 255 * self.through())

    def get_rotation(self):
        return self.age*40

    def draw(self, surf, offset=(0, 0), scale=1):
        to_draw = pygame.transform.rotate(self.surf, self.get_rotation())
        to_draw = scale_surface_by(to_draw, scale * self.get_scale())
        to_draw.set_alpha(self.get_alpha())

        x = self.position.x*scale + offset[0]*scale - to_draw.get_width()//2
        y = self.position.y*scale + offset[1]*scale - to_draw.get_height()//2
        surf.blit(to_draw, (x, y))

    def update(self, dt, events):
        super().update(dt, events)
        self.velocity *= 0.01**dt


class BatteryCollectParticle(Particle):
    def __init__(self, position=(0, 0), velocity = (0, 0), duration = 0.7):
        super().__init__(position, velocity, duration)
        self.surf = ImageManager.load("images/collect_particle.png")
        self.age = random.random() * self.duration

    def get_scale(self):
        return (1 - 1*self.through()) * 0.7

    def get_alpha(self):
        return (255 - 255 * self.through()**3)

    def get_rotation(self):
        angle_rad = math.atan2(self.velocity.y, self.velocity.x)
        return angle_rad*180/math.pi

    def draw(self, surf, offset=(0, 0), scale=1):
        to_draw = pygame.transform.rotate(self.surf, self.get_rotation())
        to_draw = scale_surface_by(to_draw, scale * self.get_scale())
        to_draw.set_alpha(self.get_alpha())

        x = self.position.x*scale + offset[0]*scale - to_draw.get_width()//2
        y = self.position.y*scale + offset[1]*scale - to_draw.get_height()//2
        surf.blit(to_draw, (x, y))

    def update(self, dt, events):
        super().update(dt, events)
        self.velocity *= 0.01**dt


