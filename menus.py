import pygame


class Menu:
    def __init__(self, width, height):
        self.width = width
        self.height = height


class StartMenu(Menu):
    def __init__(self, width, height):
        super().__init__(width, height)


class PauseMenu(Menu):
    def __init__(self, width, height):
        super().__init__(width, height)

    def draw(self):
        s = pygame.Surface((self.width, self.height))
        s.set_alpha(128)
        s.fill((0, 0, 0))
        return s
