import math

import pygame

import constants as c
import frame as f
import sys

from primitives import Pose
from sound_manager import SoundManager
from image_manager import ImageManager
import asyncio

import webbrowser

# Beepbox link for music: https://www.beepbox.co/#9n61sbk5l00e0jt2wa7g0jj07r1i0o452143T0v1u00f0q011d08w1h6E0T0v1u00f10qaq021d00w1h6E0T0v6u98f10i7q83231d4aw5h2E0T1v5u27f0q0w10x4d03A0F2B6Q4190Pf640E2b777T1v5u35f0qwx10l611d08A6F0B0Q05c0Pa660E2bi626T1v5u44f0qww10l51d03A1F0B7Q005dPd444E5b661862763677T4v3uf0f0q011z6666ji8k8k3jSBKSJJAArriiiiii07JCABrzrrrrrrr00YrkqHrsrrrrjr005zrAqzrjzrrqr1jRjrqGGrrzsrsA099ijrABJJJIAzrrtirqrqjqixzsrAjrqjiqaqqysttAJqjikikrizrHtBJJAzArzrIsRCITKSS099ijrAJS____Qg99habbCAYrDzh00E0b4x4i4N8k4x4i4g000000018j4xgh8x4y4ich8N4z00000x4P4jchcM00004ycO8P8zc000004i8h8x4y8ych514k4hgh50p28KFB-2QyR2OhjkbkbkkR2R2R2M0J8IybobJ2QySyS5dgJgJhjkbsbkbqbmb92O8KYbmbubskR2R2R5dUIwbmbkb0yM8I4bCYb4oJMIAkR2R2R2FE_rHWyddB_QR-28YELjbw2QkSQSBcAb8yRyPbjh-6noq-c8I8bqbmaiZdvzRicwnFE-aqieCOZ4hX96CVLQLFEZh0Rm4tdaCQvjYh9JvyCz_nSkAtl97CAughQ1juzYcGFKDUn0FBW2Q5d0J0J0JoIAbkbgkQ2Q2Q2R2R2PFRdvX_ajq_5cKN1q2CwmwmwmMmi5G5Eaq1q1r1qxqNgjNtd7QhRAuBkhQkQAt5d97hpjljx4MAt5d97hjihQhljli2CnF0MdJtttttttttttttttttttttttttttuhkMc5nnnnnnnnnnnnnnnnnnnnnnnnnnnm1qpkFTyeCieCieCieCieCieCieCieFBiA2ewzE8W2ewzE8W2ewzQ2ewzE8W2ewzEjalsZBeXt5PxncExtyVMLCG4tcAtcAtcAtcArFBiAPp6VBaGKcJ5TcZjaB0g

class Game:
    def __init__(self):
        pygame.init()
        SoundManager.init()
        ImageManager.init()
        self.small_screen = pygame.Surface(c.WINDOW_SIZE)
        self.screen = pygame.display.set_mode(c.SCALED_WINDOW_SIZE)
        self.clock = pygame.time.Clock()
        pygame.mixer.init()

        self.shake_amp = 0
        self.since_shake = 999
        self.reset()
        self.current_level = 0
        self.scale = 0.5

        pygame.display.set_caption(f"{c.CAPTION}")

        pygame.mixer.music.load("sound/music.wav")


        asyncio.run(self.main())


    def shake(self, amt=15):
        self.shake_amp = amt
        self.since_shake = 0

    @staticmethod
    def is_web_build():
        return sys.platform == "emscripten"

    def open_steam_page(self):
        if not self.is_web_build():
            webbrowser.open('https://store.steampowered.com/app/3284290/Moonsigil_Atlas/')
        else:
            webbrowser.open('https://store.steampowered.com/app/3284290/Moonsigil_Atlas/')

    def get_shake_offset(self):
        magnitude = math.cos(self.since_shake * 50) * self.shake_amp
        direction = Pose((1, 1))
        if abs(magnitude) < 0.25:
            magnitude = 0
        return direction * magnitude

    def reset(self):
        pass

    async def main(self):
        current_frame = f.MainFrame(self)
        current_frame.load()
        self.clock.tick(60)
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.5)

        while True:
            dt, events = self.get_events()
            if dt == 0:
                dt = 1/100000
            if dt > 0.05:
                dt = 0.05
            current_frame.update(dt, events)
            current_frame.draw(self.screen, self.get_shake_offset().get_position())
            # self.screen.blit(scaled, (0, 0))
            pygame.display.flip()
            await asyncio.sleep(0)

            if current_frame.done:
                current_frame = current_frame.next_frame()
                current_frame.load()


    def get_events(self):

        dt = self.clock.tick(c.FRAMERATE)/1000

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.scale *= 0.9
                if event.key == pygame.K_2:
                    self.scale /= 0.9

        self.since_shake += dt
        self.shake_amp -= 5*dt
        self.shake_amp *= 0.001 ** dt
        if (self.shake_amp < 0):
            self.shake_amp = 0

        return dt, events


if __name__ == "__main__":
    Game()
