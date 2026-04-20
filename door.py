from obstacle import Obstacle, scale_surface_by
from image_manager import ImageManager

class Door(Obstacle):
    def __init__(self, game, player, drone, position = (500, 300), alternate=False):
        super().__init__(game, player, drone, position = position, alternate=alternate)
        self.surface = ImageManager.load("images/door.png")
        self.lighten_surf = ImageManager.load("images/door_white.png")

        self.lighten_amount = 0
        self.since_destroy = 0
        self.preparing_destroy = False
        self.destroy_duration = 1

    def on_pickup_key(self):
        self.prep_destroy()

    def prep_destroy(self):
        self.preparing_destroy = True
        self.game.shake

    def through_destroy(self):
        return min(self.since_destroy/self.destroy_duration, 1)

    def update(self, dt, events):
        super().update(dt, events)
        if (self.preparing_destroy):
            self.since_destroy += dt

        if self.through_destroy() >= 0.999:
            self.destroy()

    def draw(self, surf, offset=(0, 0), scale = 1):
        if (not self.is_on_screen(offset, scale)):
            return

        surf_scale = (1 + self.through_destroy()**0.5*1.5)*scale

        surf_to_draw = self.surface.copy()
        self.lighten_surf.set_alpha(255 * self.through_destroy()**(0.1))
        surf_to_draw.blit(self.lighten_surf, (0, 0))
        surf_to_draw = scale_surface_by(surf_to_draw, surf_scale)

        x = (self.position.x + offset[0])*scale - surf_to_draw.get_width()//2
        y = (self.position.y + offset[1])*scale - surf_to_draw.get_height()//2
        surf_to_draw.set_alpha(255 - 255*self.through_destroy())
        surf.blit(surf_to_draw, (x,y))

        if self.collides_with(self.drone) and not self.preparing_destroy:
            self.drone.draw_shadow_over(self, surf, offset, scale)
