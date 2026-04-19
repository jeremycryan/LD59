from image_manager import ImageManager
from primitives import *
import constants as c


class Battery(GameObject):
    def __init__(self, game, drone, player, position, starting_height=0):
        super().__init__(game)
        self.radius = 50
        self.max_radius = 50
        self.height = 0
        self.drone = drone
        self.position = position
        self.battery_surf = ImageManager.load("images/battery.png")
        self.base_point = Pose((0, 25))
        self.original_base_point = self.base_point

        self.drone_pickup_radius = 70
        self.player_pickup_radius = 70
        self.player = player

        self.height_on = starting_height
        self.height = starting_height

    def update(self, dt, events):
        if (self.drone.get_base_position() - self.position).magnitude() < self.drone_pickup_radius:
            self.drone.pickup_battery(self)
            self.height_on = self.drone.height_over
        if (self.player.get_base_position() - self.position + self.original_base_point).magnitude() < self.player_pickup_radius:
            if not self.is_destroyed:
                self.destroy()
                self.player.on_pickup_battery()

    def effective_height(self):
        if self.height_on > self.height:
            return 0
        return self.height - self.height_on

    def draw_shadow(self, surf, offset=(0, 0), scale=1):
        if (self.effective_height() < 50):
            self.radius = max(0, self.max_radius - self.effective_height())
            super().draw_shadow(surf, offset, scale)
            self.base_point = Pose((0, 25))
        else:
            self.base_point = Pose((0, -50))


    def draw(self, surf, offset=(0, 0), scale = 1):
        surf_to_use = self.battery_surf

        surf_to_use = scale_surface_by(surf_to_use, scale)

        flight_offset = Pose((0, -self.height))
        x = offset[0]*scale + self.position.x*scale + flight_offset.x*scale - surf_to_use.get_width()//2
        y = offset[1]*scale + self.position.y*scale + flight_offset.y*scale - surf_to_use.get_height()//2
        surf.blit(surf_to_use, (x, y))

        if c.SHOW_DEBUG:
            pygame.draw.circle(surf, (255, 0, 0), (self.position.x*scale + offset[0]*scale, self.position.y*scale + offset[1]*scale), 5)
        pass