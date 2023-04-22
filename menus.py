import pygame

from instances import GameState


class Interface:
    def __init__(self, width, height, set_state, set_running):
        """
        Template for creating menus
        :param width: Width of the Menu
        :param height: Height of the Menu
        :param set_state: Method for switching to another state
        :param set_running: Method for closing the game
        """
        self.width = width
        self.height = height
        self.set_state = set_state
        self.set_running = set_running

    def process_inputs(self, events):
        pass

    def update(self):
        pass

    def process_outputs(self):
        pass


class GameHUDInterface(Interface):
    """
    This is used for the heads-up display. It currently doesn't support
    the debug display, which is something that needs to be done in
    the future.
    """

    def __init__(self, width, height, set_state, set_running):
        super().__init__(width, height, set_state, set_running)

    def process_inputs(self, events):
        pass

    def update(self):
        pass

    def process_outputs(self):
        self.draw()

    def draw(self):
        s = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Draw Reticle
        pygame.draw.line(s, (255, 255, 255), (self.width / 2, self.height / 2 + 10), (self.width / 2, self.height / 2 - 10), 1)
        pygame.draw.line(s, (255, 255, 255), (self.width / 2 + 10, self.height / 2), (self.width / 2 - 10, self.height / 2), 1)

        pygame.display.get_surface().blit(s, (0, 0))


class StartMenuInterface(Interface):
    """
    The start menu that is displayed when the engine first starts
    """

    def __init__(self, width, height, set_state, set_running):
        super().__init__(width, height, set_state, set_running)

        self.menu_name = "PyCaster"

        self.buttons = []
        self.initialize_buttons()

    def initialize_buttons(self):
        def start_action():
            self.set_state(GameState.GAME)

        b_width = 300
        b_height = 50

        start_button = Button(
            rect=pygame.Rect(
                (self.width / 2) - (b_width / 2),
                (self.height * (3/4)),
                b_width,
                b_height),
            color=(225, 225, 225),
            action=start_action,
            name="Start"
        )
        self.buttons.append(start_button)

    def process_inputs(self, events):
        for event in events:
            for button in self.buttons:
                button.handle_event(event)
            if event.type == pygame.QUIT:
                self.set_running(False)

    def process_outputs(self):
        self.draw()

    def draw(self):
        font = pygame.font.SysFont('consolas.ttf', 120)
        s = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Draw title of menu
        text = font.render(self.menu_name, True, (255, 255, 255))
        t_rect = text.get_rect()
        t_pos = ((self.width / 2) - (t_rect.width / 2), 175)
        s.blit(text, t_pos)

        # Draw buttons
        for button in self.buttons:
            button.draw(s)

        pygame.display.get_surface().blit(s, (0, 0))


class PauseMenuInterface(Interface):
    """
    The pause menu that is displayed whenever the user presses escape
    """
    def __init__(self, width, height, set_state, set_running, reset_map):
        super().__init__(width, height, set_state, set_running)

        self.reset_map = reset_map

        self.menu_name = "Paused"

        self.buttons = []
        self.initialize_buttons()

    def initialize_buttons(self):

        def resume_action():
            self.set_state(GameState.GAME)

        def quit_action():
            self.set_running(False)

        def reset_action():
            self.reset_map("map.txt")

        b_width = 300
        b_height = 50
        b_spacing = 20

        resume_button = Button(
            rect=pygame.Rect(
                (self.width / 2) - (b_width / 2),
                (self.height / 2) + (b_height + b_spacing) * 0,
                b_width,
                b_height),
            color=(175, 175, 175),
            action=resume_action,
            name="Resume"
        )
        self.buttons.append(resume_button)

        reset_button = Button(
            rect=pygame.Rect(
                (self.width / 2) - (b_width / 2),
                (self.height / 2) + (b_height + b_spacing) * 1,
                b_width,
                b_height),
            color=(175, 175, 175),
            action=reset_action,
            name="Reset"
            )
        self.buttons.append(reset_button)

        quit_button = Button(
            rect=pygame.Rect(
                (self.width / 2) - (b_width / 2),
                (self.height / 2) + (b_height + b_spacing) * 2,
                b_width,
                b_height),
            color=(175, 175, 175),
            action=quit_action,
            name="Quit"
        )
        self.buttons.append(quit_button)

    def process_inputs(self, events):
        for event in events:
            for button in self.buttons:
                button.handle_event(event)
            if event.type == pygame.QUIT:
                self.set_running(False)

    def process_outputs(self):
        self.draw()

    def draw(self):
        font = pygame.font.SysFont('consolas.ttf', 80)
        s = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 200))

        # Draw title of menu
        text = font.render(self.menu_name, True, (150, 150, 150))
        t_rect = text.get_rect()
        t_pos = ((self.width / 2) - (t_rect.width / 2), 175)
        s.blit(text, t_pos)

        # Draw buttons
        font = pygame.font.SysFont('consolas.ttf', 24)
        for button in self.buttons:
            button.draw(s)

        # Draw keybindings
        font_label = [
            "Forward: W",
            "Backward: S",
            "Left: A",
            "Right: D",
            "Save: O",
            "Load: P"

        ]

        for i in range(len(font_label)):
            text = font.render(font_label[i], True, (150, 150, 150))
            s.blit(text, (5, i * 20 + 5))

        pygame.display.get_surface().blit(s, (0, 0))


class Button:
    def __init__(self, rect, color, action, name):
        self.rect = rect
        self.color = color
        self.action = action
        self.name = name

        self.font_size = 48
        self.font_name = "consolas.ttf"
        self.font_color = (100, 100, 100)

    def draw(self, surf):
        # Draw Button
        pygame.draw.rect(surf, self.color, self.rect)

        # Draw name of button
        font = pygame.font.SysFont(self.font_name, self.font_size)
        text = font.render(self.name, True, self.font_color)
        t_rect = text.get_rect()
        t_pos = (
            self.rect.x + (self.rect.width - t_rect.width) / 2,
            self.rect.y + (self.rect.height - t_rect.height) / 2
        )
        surf.blit(text, t_pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                if self.action:
                    self.action()

    def set_action(self, action):
        self.action = action
