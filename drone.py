import random

from image_manager import ImageManager
from particle import DustParticle
from primitives import *
import pygame
import time
import constants as c
from sound_manager import SoundManager


class Drone(GameObject):
    def __init__(self, game, player, frame):
        super().__init__(game)
        self.player = player

        self.position = Pose((650, 750))
        self.current_velocity = Pose((0, 0))
        self.acceleration = 9000
        self.max_speed = 900
        self.base_point = Pose((0, 9))

        self.drone_surf = ImageManager.load("images/drone_flying.png")
        self.drone_surf_stationary = ImageManager.load("images/drone_stopped.png")

        self.is_flying = False
        self.flight_offset = Pose((0, 0))
        self.flight_liftoff_acceleration = 4
        self.flight_max_height = 200
        self.flight_fall_acceleration = 1200
        self.current_flight_height = 0
        self.current_fall_speed = 0
        self.angle_offset = 0
        self.target_angle = 0

        self.max_radius = 50
        self.min_radius = 30
        self.radius = 60
        self.obstacles = []
        self.height_over = 0
        self.radius_for_obstacle = self.radius

        self.carrying_battery = None
        self.carrying_battery_locked = False
        self.carrying_battery_offset = Pose((0, 50))

        player.drone = self
        self.frame = frame
        self.last_position = self.position

        self.complaint_showing = False
        self.complaint_opacity = 0
        self.complaint_target_opacity = 0
        self.complaint_scale = 0.5
        self.complaint_target_scale = 0.5
        self.since_complaint = 9999
        self.complaint_surf = scale_surface_by(ImageManager.load("images/drone_no_water.png"), 0.35)

        self.intersecting_docks = []
        self.has_been_found = False
        self.clatter = SoundManager.load("sound/drone_land.wav")
        self.clatter.set_volume(0.7)
        self.on_ground = True
        self.pickup_battery_sound = SoundManager.load("sound/drone_pickup_battery.wav")
        self.ongoing_sound = SoundManager.load("sound/drone_looping.wav")
        self.ongoing_sound.set_volume(0)
        self.ongoing_sound.play(-1)
        self.cut_out_sound = SoundManager.load("sound/drone_cut_out.wav")
        self.cut_out_sound.set_volume(2)

    def show_complaint(self):
        self.complaint_showing = True
        self.since_complaint = 0
        self.complaint_target_opacity = 255
        self.complaint_target_scale = 1

    def hide_complaint(self):
        self.complaint_showing = True
        self.complaint_target_opacity = 0
        self.complaint_target_scale = 0.5

    def update_complaint(self, dt, events):
        self.since_complaint += dt

        if self.complaint_showing and self.since_complaint > 0.4:
            self.hide_complaint()

        self.complaint_scale += (self.complaint_target_scale - self.complaint_scale)*dt*12
        if (self.complaint_showing and self.complaint_scale > 1):
            self.complaint_scale = 1
        self.complaint_opacity += (self.complaint_target_opacity - self.complaint_opacity)*dt*12
        if (self.complaint_showing and self.complaint_opacity > 255):
            self.complaint_opacity = 255

    def get_min_flight_height(self):
        return self.height_over

    def set_obstacles(self, obstacles):
        self.obstacles = obstacles

    def flight_prop(self):
        result = (self.current_flight_height - self.get_min_flight_height())/(self.flight_max_height - self.get_min_flight_height())
        if self.is_flying:
            self.ongoing_sound.set_volume(result*0.8)
        else:
            self.ongoing_sound.set_volume(max(0, result*10 - 9)*0.8)
        if result <= 0.01 and not self.on_ground and not self.is_flying:
            self.clatter.play()
            self.on_ground = True
            self.clatter_particles()
        return result

    def clatter_particles(self):
        for i in range(10):
            speed = 900
            velocity = random.random()*speed  - speed/2, random.random()*speed - speed/2
            self.frame.objects.append(DustParticle((self.get_base_position() + Pose((0, -30))).get_position(), velocity=velocity))

    def update(self, dt, events):
        self.update_complaint(dt, events)

        pressed = pygame.key.get_pressed()
        direction = [0, 0]
        if pressed[pygame.K_UP]:
            direction[1] -= 1
        if pressed[pygame.K_LEFT]:
            direction[0] -= 1
        if pressed[pygame.K_RIGHT]:
            direction[0] += 1
        if pressed[pygame.K_DOWN]:
            direction[1] += 1
        if not self.is_flying:
            direction = [0, 0]

        self.current_velocity += Pose((direction[0] * self.acceleration * dt, direction[1] * self.acceleration * dt))
        if self.current_velocity.magnitude() > self.max_speed:
            self.current_velocity.scale_to(self.max_speed)
        if direction[0] == 0:
            self.current_velocity.x *= 0.05**dt
            if abs(self.current_velocity.x) <= 20:
                self.current_velocity.x = 0
        if direction[1] == 0:
            self.current_velocity.y *= 0.05**dt
            if abs(self.current_velocity.y) <= 20:
                self.current_velocity.y = 0
        if direction[0] == 0 and direction[1] == 0:
            self.current_velocity *= 0.005**dt

        if self.is_flying:
            if (self.current_flight_height <= self.flight_max_height):
                p = self.flight_max_height - self.current_flight_height
                self.current_flight_height += p * dt * self.flight_liftoff_acceleration
                if self.current_flight_height > self.flight_max_height:
                    self.current_flight_height = self.flight_max_height
            self.current_fall_speed = 0
        else:
            if self.current_flight_height > self.get_min_flight_height():
                self.current_fall_speed += self.flight_fall_acceleration * dt
                self.current_flight_height -= self.current_fall_speed * dt
                if self.current_flight_height < self.get_min_flight_height():
                    self.current_flight_height = self.get_min_flight_height()

        self.flight_offset = Pose((0, self.current_flight_height * -1))
        self.flight_offset.y += math.sin(time.time() * 6)*5 * self.flight_prop()
        self.flight_offset.x += math.sin(time.time() * 2 + 1.3)*3 * self.flight_prop()

        if not self.in_range_of_player() and self.is_flying:
            self.cut_out_sound.play()
        self.is_flying = self.in_range_of_player()
        if (self.is_flying):
            self.on_ground = False


        self.position += self.current_velocity * dt

        target_angle_offset = direction[0] * -30
        p = target_angle_offset - self.angle_offset
        self.angle_offset += p * 5 * dt

        self.target_angle = self.angle_offset + math.sin(time.time() * 1) * 5 * self.flight_prop()
        self.target_angle += self.current_fall_speed * 0.05 * min(1, self.flight_prop() * 5)

        self.radius = (1 - self.current_flight_height/self.flight_max_height) * (self.max_radius - self.min_radius) + self.min_radius

        self.height_over = 0
        for obstacle in self.obstacles:
            if obstacle.collides_with(self):
                self.height_over = obstacle.height

        self.radius_for_obstacle = (1 - self.flight_prop()) * (self.max_radius - self.min_radius) + self.min_radius


        if self.carrying_battery and self.carrying_battery.is_destroyed:
            self.carrying_battery = None
        if self.carrying_battery:
            d = self.current_flight_height - self.carrying_battery.height
            self.carrying_battery.height += d * 8 * dt
            dp = self.position + self.carrying_battery_offset - self.carrying_battery.position
            self.carrying_battery.position += dp * 10 * dt

        if (self.over_water()):
            self.position = self.frame.island.nearest_water_pixel(self.last_position + self.base_point, self.position + self.base_point, exclude_dock=True) - self.base_point
            self.position = Pose(self.nearest_non_water_position(direction)) - self.base_point
            self.show_complaint()

        # for dock in self.intersecting_docks:
        #     if dock.directly_over(self):
        #         self.position = self.last_position

        self.intersecting_docks.clear()
        self.last_position = self.position

    def over_me(self, dock):
        self.intersecting_docks.append(dock)

    def nearest_non_water_position(self, direction):
        result = self.frame.island.nearest_non_water_pixel(self.get_base_position().get_position(), direction, exclude_dock=True)
        return result

    def over_water(self):
        result = self.frame.island.water_or_dock_at(self.get_base_position().get_position())
        return result

    def in_range_of_player(self):
        if (self.get_base_position() - self.player.get_base_position()).magnitude() <= self.player.drone_range:
            self.has_been_found = True
            self.player.on_drone_in_range()
            return True
        return False

    def in_range_of_player_with_multiplier(self, mult):
        if (self.get_base_position() - self.player.get_base_position()).magnitude() <= self.player.drone_range * mult:
            return True
        return False

    def is_on_screen(self, offset=(0, 0), scale=1):
        x = offset[0]*scale + self.position.x*scale + self.flight_offset.x*scale
        y = offset[1]*scale + self.position.y*scale + self.flight_offset.y*scale

        if x < 0 or x > c.WINDOW_WIDTH or y < 0 or y > c.WINDOW_HEIGHT:
            return False
        return True


    def draw(self, surf, offset=(0, 0), scale = 1):

        csurf = scale_surface_by(self.complaint_surf, self.complaint_scale)
        csurf.set_alpha(self.complaint_opacity)
        cx = offset[0]*scale + self.position.x*scale + self.flight_offset.x*scale - csurf.get_width()//2
        cy = offset[1]*scale + self.position.y*scale + self.flight_offset.y*scale - csurf.get_height()//2 - 80
        surf.blit(csurf, (cx, cy))

        surf_to_use = self.drone_surf
        if not self.is_flying:
            surf_to_use = self.drone_surf_stationary

        if abs(self.target_angle) > 1:
            surf_to_use = pygame.transform.rotate(surf_to_use, self.target_angle)

        surf_to_use = scale_surface_by(surf_to_use, scale)

        x = offset[0]*scale + self.position.x*scale + self.flight_offset.x*scale - surf_to_use.get_width()//2
        y = offset[1]*scale + self.position.y*scale + self.flight_offset.y*scale - surf_to_use.get_height()//2
        surf.blit(surf_to_use, (x, y))

        if c.SHOW_DEBUG:
            pygame.draw.circle(surf, (255, 0, 0), (self.position.x*scale + offset[0]*scale, self.position.y*scale + offset[1]*scale), 5)
        pass

    def draw_shadow_over(self, obstacle, surf, offset, scale):
        if (self.current_flight_height < obstacle.height):
            return

        radius_to_use = self.radius * scale
        shadow = pygame.Surface((radius_to_use*2, radius_to_use))
        shadow.fill((255, 255, 255))
        pygame.draw.ellipse(shadow, (200, 200, 200), shadow.get_rect())

        x = self.position.x*scale + self.base_point.x*scale + offset[0]*scale - shadow.get_width()//2
        y = self.position.y*scale + self.base_point.y*scale - obstacle.height*scale + offset[1]*scale - shadow.get_height()//2

        mask = scale_surface_by(obstacle.shadow_mask, scale)
        obs_x = obstacle.position.x*scale + offset[0]*scale - mask.get_width()//2
        obs_y = obstacle.position.y*scale + offset[1]*scale - mask.get_height()//2
        mx = obs_x - x
        my = obs_y - y
        shadow_mask = shadow.copy()
        shadow_mask.fill((255, 255, 255))
        shadow_mask.blit(mask, (mx, my), special_flags=pygame.BLEND_MULT)
        shadow.blit(shadow_mask, (0, 0), special_flags=pygame.BLEND_ADD)


        surf.blit(shadow, (x, y), special_flags=pygame.BLEND_MULT)

    def pickup_battery(self, battery):
        if (self.carrying_battery != None):
            return
        self.carrying_battery = battery
        self.carrying_battery_locked = False

    def on_scene_unload(self):
        self.ongoing_sound.stop()
