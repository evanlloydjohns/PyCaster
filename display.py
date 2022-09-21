import configparser
import pygame


class Display:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('settings.ini')
        de_config = config['DEFAULT']
        di_config = config['DISPLAY']

        self.width = int(de_config['width'])
        self.height = int(de_config['height'])
        self.isFullscreen = bool(di_config['isFullscreen'])

        pygame.init()
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill((0, 101, 103))
        self.react = self.image.get_rect()
        self.screen = pygame.display.set_mode((self.width, self.height))

    def get_screen(self):
        return self.screen
