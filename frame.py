import pygame

from Button import Button
from battery import Battery, Key
from dock import Dock
from drone import Drone
from drone_indicator import DroneIndicator
from image_manager import ImageManager
from door import Door
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
        self.image = ImageManager.load("images/final_image.png")
        self.white = pygame.Surface(c.WINDOW_SIZE)
        self.white.fill((255, 255, 255))
        self.age = 0
        self.buttons = [
            Button(ImageManager.load("images/player_again_button.png"), (c.WINDOW_WIDTH - 130, c.WINDOW_HEIGHT - 240), on_click=self.play_again_clicked),
            Button(ImageManager.load("images/wishlist_button.png"), (c.WINDOW_WIDTH - 180, c.WINDOW_HEIGHT - 100),
                   on_click=self.game.open_steam_page)
        ]
        pass

    def update(self, dt, events):
        self.age += dt
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.done = True
        for button in self.buttons:
            button.update(dt, events)

    def draw(self, surface, offset=(0, 0)):
        surface.blit(self.image, (0, 0))
        self.white.set_alpha(255 - 200*self.age)
        for button in self.buttons:
            button.draw(surface, *offset)
        surface.blit(self.white, (0, 0))

    def play_again_clicked(self):
        self.done = True

    def next_frame(self):
        return MainFrame(self.game)


class MainFrame(Frame):
        def load(self):
            self.player = Player(self.game, self, (-200, 610))
            self.drone = Drone(self.game, self.player, self)
            self.drone_indicator = DroneIndicator(self.game, self.drone, self.player, self)
            self.island = Island(self.game)
            self.doors = [
                Door(self.game, self.player, self.drone, (1620, 200))
            ]
            self.obstacles = [
                Obstacle(self.game, self.player, self.drone, (550, 300)),
                Obstacle(self.game, self.player, self.drone, (800, 200)),
                Obstacle(self.game, self.player, self.drone, (1050, 150)),
                Obstacle(self.game, self.player, self.drone, (1335, 230)),
                #Obstacle(self.game, self.player, self.drone, (1620, 270)),
                Obstacle(self.game, self.player, self.drone, (1900, 210)),
                Obstacle(self.game, self.player, self.drone, (2200, 110)),
                Obstacle(self.game, self.player, self.drone, (2400, -140)),
                Obstacle(self.game, self.player, self.drone, (1300, 1000)),
                Obstacle(self.game, self.player, self.drone, (300, 1100)),
                Obstacle(self.game, self.player, self.drone, (570, 1150)),
                Obstacle(self.game, self.player, self.drone, (840, 1250)),
                Obstacle(self.game, self.player, self.drone, (940, 1520)),
                Obstacle(self.game, self.player, self.drone, (840, 1790)),
                Obstacle(self.game, self.player, self.drone, (900, 2060)),
                Obstacle(self.game, self.player, self.drone, (2560, 2100)),
                Obstacle(self.game, self.player, self.drone, (2830, 1950)),
                Obstacle(self.game, self.player, self.drone, (3049, -135)),
                Obstacle(self.game, self.player, self.drone, (2923, -346)),
                Obstacle(self.game, self.player, self.drone, (1609, 2382)),
                Obstacle(self.game, self.player, self.drone, (167, -937), alternate=True),
                Obstacle(self.game, self.player, self.drone, (12, -693), alternate=True),
                Obstacle(self.game, self.player, self.drone, (210, -583), alternate=True),
                Obstacle(self.game, self.player, self.drone, (690, -1920), alternate=True),
                Obstacle(self.game, self.player, self.drone, (960, -1820), alternate=True),
                Obstacle(self.game, self.player, self.drone, (1230, -1980), alternate=True),
                Obstacle(self.game, self.player, self.drone, (1500, -1880), alternate=True),

            ]
            self.docks = [
                Dock(self.game, self.drone, (200, 670)),
                Dock(self.game, self.drone, (-70, 670)),
                Dock(self.game, self.drone, (-340, 670)),
                Dock(self.game, self.drone, (3800, 2200)),
                Dock(self.game, self.drone, (4070, 2200)),
                Dock(self.game, self.drone, (4470, 1350)),
                Dock(self.game, self.drone, (4470, 1620)),
                Dock(self.game, self.drone, (2347, -1139)),
                Dock(self.game, self.drone, (2617, -1139)),
                Dock(self.game, self.drone, (2617, -1409)),
                Dock(self.game, self.drone, (2818, 234)),
                Dock(self.game, self.drone, (0, -3278)),
                Dock(self.game, self.drone, (270, -3278)),
                Dock(self.game, self.drone, (-291, -2823)),
                Dock(self.game, self.drone, (-291, -2553)),
                Dock(self.game, self.drone, (-291, -2283)),
                Dock(self.game, self.drone, (-291, -2013)),

                Dock(self.game, self.drone, (488, -1494)),
                Dock(self.game, self.drone, (218, -1494)),
                Dock(self.game, self.drone, (-52, -1494)),

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
                Battery(self.game, self.drone, self.player, Pose((2485, 1142))),
                Battery(self.game, self.drone, self.player, Pose((3601, -1262))),
                Battery(self.game, self.drone, self.player, Pose((-648, 1530))),
                Battery(self.game, self.drone, self.player, Pose((5516, 722))),
                Battery(self.game, self.drone, self.player, Pose((1081, -2990))),
                Key(self.game, self.drone, self.player, Pose((668, -369))),
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
                Decoration(self.game, ImageManager.load("images/no_drones.png"), Pose((3120, 380)), Pose((-12, 110)),
                           radius=30),
                Decoration(self.game, ImageManager.load("images/batteries_left.png"), Pose((2233, 494)), Pose((12, 110)),
                           radius=30),

            ]
            self.particles = []
            self.objects += self.obstacles
            self.objects += self.batteries
            self.objects += self.decorations
            self.objects += self.doors
            self.background_objects += self.docks

            self.offset_pose = (self.player.calculate_ideal_camera_position() * -1 + Pose(c.WINDOW_CENTER)*(1/self.game.scale))
            self.game.scale = self.get_target_scale()
            self.offset_pose = self.get_target_offset()

            self.fadeout_surf = pygame.Surface(c.WINDOW_SIZE)
            self.since_end_sequence = 0
            self.ending = False
            self.end_sequence_duration = 1
            self.fadeout_surf.fill((255, 255, 255))

        def start_end_sequence(self):
            self.since_end_sequence = 0
            self.ending = True

        def update(self, dt, events):
            if (self.ending):
                self.since_end_sequence += dt

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.done = True

            self.island.update(dt, events)
            for object in self.background_objects:
                object.update(dt, events)

            for object in self.objects[:]:
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

            if (self.since_end_sequence > self.end_sequence_duration):
                self.done = True

        def get_target_offset(self):
            return (self.player.calculate_ideal_camera_position() * -1 + Pose(c.WINDOW_CENTER) * (
                    1 / self.game.scale))

        def get_target_scale(self):
            return 0.8/(self.player.drone_range/self.player.starting_drone_range)

        def draw(self, surface, offset=(0, 0)):
            surface.fill((99, 174, 204))

            self.objects.sort(key = lambda x: x.get_base_position().y)
            self.background_objects.sort(key=lambda x: x.get_base_position().y)

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

            fadeout_alpha = int(255 * self.since_end_sequence/self.end_sequence_duration)
            self.fadeout_surf.set_alpha(fadeout_alpha)
            if (fadeout_alpha > 0):
                surface.blit(self.fadeout_surf, (0, 0))


        def next_frame(self):
            self.drone.on_scene_unload()
            return TitleFrame(self.game)

