import time

from image_manager import ImageManager
from primitives import *
import pygame

class Player(GameObject):
    def __init__(self, game, frame, position):
        super().__init__(game)
        self.frame = frame

        self.position = Pose(position)
        self.current_velocity = Pose((0, 0))
        self.base_point = Pose((0, 95))
        self.acceleration = 8000
        self.max_speed = 600
        self.radius = 65

        self.player_surf = ImageManager.load("images/player.png")
        self.player_face_surf = ImageManager.load("images/player_face.png")
        self.player_face_blink = ImageManager.load("images/player_face_blink.png")

        self.drone_range = 300
        self.target_drone_range = 300
        self.starting_drone_range = self.drone_range
        self.drone = None

        self.last_direction_input = [0,0]
        self.facing_left = False

        self.since_last_footstep = 999
        self.footstep_period = 0.5

        self.squish_intensity = 0.5
        self.last_position = self.position

        self.signal_circle = ImageManager.load("images/signal_circle.png")
        self.signal_circle.set_alpha(50)

        self.age = 0

        self.since_drone_in_range = 999

        self.complaint_showing = False
        self.complaint_opacity = 0
        self.complaint_target_opacity = 0
        self.complaint_scale = 0.5
        self.complaint_target_scale = 0.5
        self.since_complaint = 9999
        self.complaint_surf = scale_surface_by(ImageManager.load_copy("images/player_respawn_drone.png"), 0.45)

        self.intersecting_docks = []
        self.has_been_found = False

    def show_complaint(self):
        self.complaint_showing = True
        self.since_complaint = 0
        self.complaint_target_opacity = 255
        self.complaint_target_scale = 1

    def hide_complaint(self):
        self.complaint_showing = False
        self.complaint_target_opacity = 0
        self.complaint_target_scale = 0.5

    def update_complaint(self, dt, events):
        self.since_complaint += dt

        if self.complaint_showing and self.since_complaint > 99999999:
            self.hide_complaint()

        self.complaint_scale += (self.complaint_target_scale - self.complaint_scale) * dt * 12
        if (self.complaint_showing and self.complaint_scale > 1):
            self.complaint_scale = 1
        self.complaint_opacity += (self.complaint_target_opacity - self.complaint_opacity) * dt * 12
        if (self.complaint_showing and self.complaint_opacity > 255):
            self.complaint_opacity = 255

    def through_footstep(self):
        return min(self.since_last_footstep/self.footstep_period, 1)

    def step(self):
        self.since_last_footstep = 0

    def footstep_vertical_offset(self):
        if self.through_footstep() >= 1:
            return 0
        return -abs(math.sin(self.since_last_footstep/self.footstep_period * 2*math.pi))*20

    def footstep_angle_offset(self):
        if self.through_footstep() >= 1:
            return 0
        return (math.sin(self.since_last_footstep/self.footstep_period * 2*math.pi))*7

    def footstep_squish_factor(self):
        # if self.through_footstep() >= 1:
        #     return 1
        return 1 - (abs(math.sin(self.since_last_footstep/self.footstep_period * 2*math.pi + math.pi/2))*0.1 * self.squish_intensity)

    def update(self, dt, events):
        self.update_complaint(dt, events)
        self.since_last_footstep += dt
        self.age += dt
        self.since_drone_in_range += dt
        pressed = pygame.key.get_pressed()
        direction = [0, 0]
        if pressed[pygame.K_w]:
            direction[1] -= 1
        if pressed[pygame.K_a]:
            direction[0] -= 1
        if pressed[pygame.K_d]:
            direction[0] += 1
        if pressed[pygame.K_s]:
            direction[1] += 1
        self.last_direction_input = direction

        if self.since_drone_in_range > 6 and not self.complaint_showing and self.drone.has_been_found:
            self.show_complaint()

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:
                    self.on_pickup_battery()
                if event.key == pygame.K_r:
                    if (not self.over_water_or_dock()):
                        self.drone.position = self.position
                        self.drone.current_flight_height = 0
                        self.hide_complaint()
                if event.key == pygame.K_p:
                    print(f"Drone position: {self.drone.get_base_position()}")

        if (self.through_footstep() < 1):
            target_squish = 1.25
        else:
            target_squish = 0.5
        ds = target_squish - self.squish_intensity
        self.squish_intensity += ds * dt * 6


        if ((direction[0] != 0 or direction[1] != 0) and self.through_footstep() >= 1):
            self.step()

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

        self.position += self.current_velocity * dt

        dr = self.target_drone_range - self.drone_range
        self.drone_range += dr * dt * 5
        if abs(self.target_drone_range - self.drone_range) < 5:
            self.drone_range = self.target_drone_range

        if (self.over_water()):
            self.position = self.frame.island.nearest_water_pixel(self.last_position + self.base_point,
                                                                  self.position + self.base_point) - self.base_point
            self.position = Pose(self.nearest_non_water_position(direction)) - self.base_point
        self.last_position = self.position

    def on_drone_in_range(self):
        self.since_drone_in_range = 0
        self.hide_complaint()

    def draw(self, surf, offset=(0, 0), scale = 1):

        csurf = scale_surface_by(self.complaint_surf, self.complaint_scale)
        csurf.set_alpha(self.complaint_opacity)
        cx = offset[0]*scale + self.position.x*scale - csurf.get_width()//2
        cy = offset[1]*scale + self.position.y*scale - csurf.get_height()//2 - 180 + 7*math.sin(time.time()*2.5)
        surf.blit(csurf, (cx, cy))

        w = self.player_surf.get_width() * scale / self.footstep_squish_factor()
        h = self.player_surf.get_height() * scale * self.footstep_squish_factor()
        oh = self.player_surf.get_height() * scale

        player_surf = pygame.transform.scale(self.player_surf, (w, h))
        face_surf_to_use = self.player_face_surf if time.time() % 6 < 5.85 else self.player_face_blink
        player_face_surf = pygame.transform.scale(face_surf_to_use, (w, h))

        if self.last_direction_input[0] < 0:
            self.facing_left = True
        if self.last_direction_input[0] > 0:
            self.facing_left = False
        if self.facing_left:
            player_surf = pygame.transform.flip(player_surf, True, False)
            player_face_surf = pygame.transform.flip(player_face_surf, True, False)

        player_surf = pygame.transform.rotate(player_surf, self.footstep_angle_offset())
        player_face_surf = pygame.transform.rotate(player_face_surf, self.footstep_angle_offset())


        x = offset[0]*scale + self.position.x*scale - player_surf.get_width()//2
        y = offset[1]*scale + self.position.y*scale - player_surf.get_height()//2 + self.footstep_vertical_offset()*scale + (oh - h)/2
        surf.blit(player_surf, (x, y))

        to_drone = (self.drone.position - self.position) *(1/ self.drone_range)
        if (to_drone.magnitude() > 1):
            to_drone.scale_to(1)
        face_offset = to_drone*10*scale


        x = offset[0]*scale + self.position.x*scale + face_offset.x - player_face_surf.get_width() // 2
        y = offset[1]*scale + self.position.y*scale + face_offset.y - player_face_surf.get_height() // 2 + self.footstep_vertical_offset()*scale + (oh - h)/2
        surf.blit(player_face_surf, (x, y))

        pass

    def calculate_ideal_camera_position(self):
        offset = Pose((self.current_velocity.x*0.5, self.current_velocity.y*0.5))
        return self.position + offset

    def draw_shadow(self, surf, offset=(0, 0), scale=1):
        super().draw_shadow(surf, offset, scale)

        r = self.drone_range * scale
        circle_surf = pygame.transform.scale(self.signal_circle, (2*r, 2*r))
        circle_surf = pygame.transform.rotate(circle_surf, self.age*8)
        x = offset[0]*scale + self.get_base_position().x * scale - circle_surf.get_width()//2
        y = offset[1]*scale + self.get_base_position().y * scale - circle_surf.get_height()//2
        surf.blit(circle_surf, (x, y))



    def on_pickup_battery(self):
        self.target_drone_range *= 1.2

    def nearest_non_water_position(self, direction):
        result = self.frame.island.nearest_non_water_pixel(self.get_base_position().get_position(), direction)
        return result

    def over_water(self):
        result = self.frame.island.water_at(self.get_base_position().get_position())
        return result

    def over_water_or_dock(self):
        result = self.frame.island.water_or_dock_at(self.get_base_position().get_position())
        return result
