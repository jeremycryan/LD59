from primitives import *
from image_manager import ImageManager
import constants as c
from drone import Drone

class Dock(GameObject):
    def __init__(self, game, drone, position = (100, 400)):
        super().__init__(game)
        self.surface = ImageManager.load("images/dock.png")
        self.shadow_mask = ImageManager.load("images/dock_mask.png")
        self.size = Pose((270, 270))
        self.position = Pose(position)
        self.drone = drone
        self.height = 0

    def update(self, dt, events):
        if self.directly_over(self.drone):
            # self.drone.show_complaint()
            self.drone.over_me(self)
            pass


    def draw(self, surf, offset=(0, 0), scale = 1):
        if not self.is_on_screen(offset, scale):
            return
        surf_to_draw = scale_surface_by(self.surface, scale)

        x = (self.position.x + offset[0])*scale - surf_to_draw.get_width()//2
        y = (self.position.y + offset[1])*scale - surf_to_draw.get_height()//2
        surf.blit(surf_to_draw, (x,y))

        if c.SHOW_DEBUG:
            pygame.draw.rect(surf, (0, 255, 0), (self.position.x*scale + offset[0]*scale - self.size.x//2*scale, self.position.y*scale + offset[1]*scale - self.size.y//2*scale, self.size.x*scale, self.size.y*scale), width=3)

    def directly_over(self, player, nudge = False):
        rect3 = pygame.Rect(
            self.position.x - self.size.x//2,
            self.position.y - self.size.y//2,
            self.size.x,
            self.size.y
        )
        if rect3.collidepoint(*player.position.get_position()):
            if nudge:
                diff = player.position - self.position
                if (abs(diff.x) > abs(diff.y)):
                    if (diff.x < 0):
                        player.position.x = self.position.x - self.size.x//2
                    else:
                        player.position.x = self.position.x + self.size.x//2
                else:
                    if diff.y < 0:
                        player.position.y = self.position.y - self.size.y//2
                    else:
                        player.position.y = self.position.y + self.size.y//2
            return True
        return False

    def draw_shadow(self, surf, offset=(0, 0), scale=1):
        return

    def collides_with(self, player, nudge = False):
        if player.position.y > self.position.y + self.size.y//2 + player.radius:
            return False
        if player.position.y < self.position.y - self.size.y//2 - player.radius:
            return False
        if player.position.x > self.position.x + self.size.x//2 + player.radius:
            return False
        if player.position.x < self.position.x - self.size.x//2 - player.radius:
            return False

        player_position = player.position.get_position()
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
                if (player.position.x < self.position.x):
                    player.position.x = self.position.x - self.size.x//2 - radius
                else:
                    player.position.x = self.position.x + self.size.x // 2 + radius
            return True
        rect2 = pygame.Rect(
            self.position.x - self.size.x//2,
            (self.position.y - self.size.y//2)*2 - radius,
            self.size.x,
            (self.size.y)*2 + radius * 2)
        if rect2.collidepoint(*player_position_yscaled):
            if nudge:
                if (player.position.y < self.position.y):
                    player.position.y = self.position.y - self.size.y//2 - radius//2
                else:
                    player.position.y = self.position.y + self.size.y//2 + radius//2
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
                    player.position = target
                return True
        return False

    def is_on_screen(self, offset=(0, 0), scale=1):
        x = offset[0] * scale + self.position.x * scale
        y = offset[1] * scale + self.position.y * scale

        buffer = 150
        if x < -buffer or x > c.WINDOW_WIDTH + buffer or y < -buffer or y > c.WINDOW_HEIGHT + buffer:
            return False
        return True