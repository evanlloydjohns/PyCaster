import pygame


class Display:
    def __init__(self, width, height, is_full_screen):
        self.width = width
        self.height = height
        self.is_full_screen = is_full_screen
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill((0, 101, 103))
        self.screen = pygame.display.set_mode((self.width, self.height), self.is_full_screen)

    def get_screen(self):
        return self.screen
