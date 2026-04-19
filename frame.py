import math
import time

import pygame

from battery import Battery
from dock import Dock
from drone import Drone
from drone_indicator import DroneIndicator
from image_manager import ImageManager
from images.decoration import Decoration
from island import Island
from obstacle import Obstacle
from player import Player
from primitives import Pose
import constants as c


class Frame:
    def __init__(self, game):
        self.game = game
        self.done = False

    def load(self):
        pass

    def update(self, dt, events):
        pass

    def draw(self, surface, offset=(0, 0)):
        surface.fill((128, 128, 128))

    def next_frame(self):
        return Frame(self.game)

    def name(self):
        return self.__class__.__name__


class TitleFrame(Frame):
    def load(self):
        pass

    def update(self, dt, events):

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.done = True

    def draw(self, surface, offset=(0, 0)):
        surface.fill((255, 255, 255))

    def next_frame(self):
        return TitleFrame


class MainFrame(Frame):
        def load(self):
            self.player = Player(self.game, self, (-200, 610))
            self.drone = Drone(self.game, self.player, self)
            self.drone_indicator = DroneIndicator(self.game, self.drone, self.player, self)
            self.island = Island(self.game)
            self.obstacles = [
                Obstacle(self.game, self.player, self.drone, (550, 300)),
                Obstacle(self.game, self.player, self.drone, (800, 200)),
                Obstacle(self.game, self.player, self.drone, (1050, 150)),
                Obstacle(self.game, self.player, self.drone, (1300, 1000)),
                Obstacle(self.game, self.player, self.drone, (300, 1100)),
                Obstacle(self.game, self.player, self.drone, (570, 1150)),
                Obstacle(self.game, self.player, self.drone, (840, 1250)),
                Obstacle(self.game, self.player, self.drone, (940, 1520)),
                Obstacle(self.game, self.player, self.drone, (840, 1790)),
                Obstacle(self.game, self.player, self.drone, (900, 2060)),
            ]
            self.docks = [
                Dock(self.game, self.drone, (200, 670)),
                Dock(self.game, self.drone, (-70, 670)),
                Dock(self.game, self.drone, (-340, 670)),
                Dock(self.game, self.drone, (3800, 2200)),
                Dock(self.game, self.drone, (4070, 2200)),
                Dock(self.game, self.drone, (4470, 1350)),
                Dock(self.game, self.drone, (4470, 1620)),
            ]
            self.drone.set_obstacles(self.obstacles)
            self.objects = [
                self.player,
                self.drone,
            ]
            self.background_objects = []
            self.batteries = [
                Battery(self.game, self.drone, self.player, Pose((1300, 1000)), starting_height=120),
                Battery(self.game, self.drone, self.player, Pose((4470, 1100))),
                Battery(self.game, self.drone, self.player, Pose((100, 1600))),
            ]
            self.ui_objects = [
                self.drone_indicator
            ]
            self.decorations = [
                Decoration(self.game, ImageManager.load("images/wasd_sign.png"), Pose((-450, 450)), Pose((12, 110)), radius=30),
                Decoration(self.game, ImageManager.load("images/arrows_sign.png"), Pose((670, 500)), Pose((-12, 110)),
                           radius=30),
                Decoration(self.game, ImageManager.load("images/battery_sign.png"), Pose((1150, 720)), Pose((12, 110)),
                           radius=30),
                Decoration(self.game, ImageManager.load("images/no_drones.png"), Pose((3600, 1950)), Pose((-12, 110)),
                           radius=30),

            ]
            self.objects += self.obstacles
            self.objects += self.batteries
            self.objects += self.decorations
            self.background_objects += self.docks

            self.offset_pose = (self.player.calculate_ideal_camera_position() * -1 + Pose(c.WINDOW_CENTER)*(1/self.game.scale))
            self.game.scale = self.get_target_scale()
            self.offset_pose = self.get_target_offset()

        def update(self, dt, events):

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.done = True

            self.island.update(dt, events)
            for object in self.background_objects:
                object.update(dt, events)

            for object in self.objects:
                object.update(dt, events)

            for object in self.ui_objects:
                object.update(dt, events)

            self.objects = [item for item in self.objects if not item.is_destroyed]

            target_offset = self.get_target_offset()
            diff = target_offset - self.offset_pose
            self.offset_pose += diff * dt * 3

            target_scale = self.get_target_scale()
            ds = target_scale - self.game.scale
            self.game.scale += ds * dt * 4
            if abs(target_scale - self.game.scale) < 0.001:
                self.game.scale = target_scale

        def get_target_offset(self):
            return (self.player.calculate_ideal_camera_position() * -1 + Pose(c.WINDOW_CENTER) * (
                    1 / self.game.scale))

        def get_target_scale(self):
            return 0.8/(self.player.drone_range/self.player.starting_drone_range)

        def draw(self, surface, offset=(0, 0)):
            surface.fill((99, 174, 204))

            self.objects.sort(key = lambda x: x.get_base_position().y)

            offset = self.offset_pose.get_position()

            self.island.draw(surface, offset, self.game.scale)
            for object in self.background_objects:
                object.draw_shadow(surface, offset, self.game.scale)
            for object in self.background_objects:
                object.draw(surface, offset, self.game.scale)
            for object in self.objects:
                object.draw_shadow(surface, offset, self.game.scale)
            for object in self.objects:
                object.draw(surface, offset, self.game.scale)
            for object in self.ui_objects:
                object.draw(surface, offset, self.game.scale)

        def next_frame(self):
            return TitleFrame

