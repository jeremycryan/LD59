from image_manager import ImageManager
import constants as c
from primitives import *


class DroneIndicator:

    def __init__(self, game, drone, player, frame):
        self.game = game
        self.drone = drone
        self.player = player
        self.icon = scale_surface_by(ImageManager.load("images/drone_stopped.png"), 0.5)
        self.arrow = scale_surface_by(ImageManager.load("images/drone_arrow.png"), 0.5)
        self.frame = frame

    def update(self, dt, events):
        if self.drone.in_range_of_player_with_multiplier(1.5):
            return

    def draw(self, surf, offset=(0, 0), scale=1):
        if self.drone.is_on_screen(offset, scale=scale):
            return
        if not self.drone.has_been_found:
            return

        rel_pos = self.drone.position * scale - self.player.position * scale

        angle = math.atan2(-rel_pos.y, rel_pos.x) * 180/math.pi
        arrow = pygame.transform.rotate(self.arrow, angle)

        x = c.WINDOW_WIDTH//2 + rel_pos.x
        y = c.WINDOW_HEIGHT//2 + rel_pos.y

        margin = 70
        if x < margin:
            x = margin
        if y < margin:
            y = margin
        if x > c.WINDOW_WIDTH - margin:
            x = c.WINDOW_WIDTH - margin
        if y > c.WINDOW_HEIGHT - margin:
            y = c.WINDOW_HEIGHT - margin

        surf.blit(self.icon, (x - self.icon.get_width()//2, y - self.icon.get_height()//2))
        surf.blit(arrow, (x - arrow.get_width()//2, y - arrow.get_height()//2))
