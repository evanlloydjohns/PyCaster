import math

import pygame

FRAME_RATE = 60
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

MAP_ROW_COUNT = 10
MAP_COL_COUNT = 10


class MapBuilder:
    def __init__(self):
        pygame.init()
        pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Map Builder")

        self.builder_dim = (800, 800)
        self.clock = pygame.time.Clock()
        self.running = True

        self.map = Map(400, 0, 800, 800)
        self.tool_panel = ToolPanel(0, 0, 400, 800, self.map.save_state, self.map.load_state, self.map.reset_state, self.map.set_current_line_color)

    def inputs(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    self.map.remove_selected_line()
                if event.button == 1:
                    self.map.check_node_selections(pygame.mouse.get_pos())
                    self.tool_panel.check_button_on_click(pygame.mouse.get_pos())

    def update(self):
        self.map.check_line_selections(pygame.mouse.get_pos())
        self.tool_panel.check_button_focusing(pygame.mouse.get_pos())

    def outputs(self):
        self.draw()

    def draw(self):
        s = pygame.display.get_surface()
        s.fill((255, 0, 0), rect=(400, 0, 800, 800))
        self.map.draw()
        self.tool_panel.draw()
        pygame.display.flip()

    def run(self):
        dt = 0
        while self.running:
            dt = self.clock.tick(FRAME_RATE) / 1000
            self.inputs()
            self.update()
            self.outputs()
        pygame.quit()


class Map:
    def __init__(self, top, left, width, height):
        self.background_color = (15, 15, 15)
        self.map_color = (25, 25, 25)
        self.grid_line_color = (100, 100, 100)
        self.drawn_line_color = (255, 255, 255)
        self.rect = pygame.Rect(top, left, width, height)
        self.map_rect_offset = 50
        self.map_rect = pygame.Rect(
            top + self.map_rect_offset,
            left + self.map_rect_offset,
            width - 2 * self.map_rect_offset,
            height - 2 * self.map_rect_offset
        )

        self.nodes = []
        self.initialize_nodes()
        self.selected_node = None

        self.lines = []
        self.selected_line = None

        self.current_line_color = (255, 255, 255)

    def set_current_line_color(self, current_line_color):
        self.current_line_color = current_line_color

    def initialize_nodes(self):
        for i in range(1, MAP_ROW_COUNT):
            for j in range(1, MAP_COL_COUNT):
                # x = (i * (map_rectMAP_ROW_COUNT)) + map_rect_offset + rect.left
                # (x - map_rect_offset - rect.left) / (map_rectMAP_ROW_COUNT)
                p = self.translate_to_map((i, j))
                self.nodes.append(Node(p[0], p[1]))

    def translate_to_map(self, pos):
        x = (pos[0] * (self.map_rect.w / MAP_ROW_COUNT)) + self.map_rect_offset + self.rect.left
        y = (pos[1] * (self.map_rect.h / MAP_COL_COUNT)) + self.map_rect_offset + self.rect.top
        return x, y

    def draw(self):
        s = pygame.display.get_surface()
        pygame.draw.rect(s, self.background_color, self.rect)
        pygame.draw.rect(s, self.map_color, self.map_rect)

        for node in self.nodes:
            node.draw()

        if self.selected_node:
            pygame.draw.circle(s, (200, 0, 0), (self.selected_node.x, self.selected_node.y), self.selected_node.r + 1)

        for line in self.lines:
            line.draw()

        if self.selected_line:
            pygame.draw.line(s, (0, 0, 255), self.selected_line.p1, self.selected_line.p2, self.selected_line.width)

    def remove_selected_line(self):
        if self.selected_line:
            self.lines.remove(self.selected_line)

    def check_node_selections(self, pos):
        for node in self.nodes:
            if node.check_collision(pos):
                if self.selected_node:
                    if self.selected_node is not node:
                        line = Line((self.selected_node.x, self.selected_node.y), (node.x, node.y), self.current_line_color)
                        self.lines.append(line)
                    self.selected_node = None
                else:
                    self.selected_node = node

    def check_line_selections(self, pos):
        self.selected_line = None
        for l in self.lines:
            if self.line_point(l, pos):
                self.selected_line = l

    def line_point(self, l, p):
        p1 = l.p1
        p2 = l.p2
        x1 = p1[0]
        y1 = p1[1]
        x2 = p2[0]
        y2 = p2[1]
        px = p[0]
        py = p[1]
        d1 = math.dist((px, py), (x1, y1))
        d2 = math.dist((px, py), (x2, y2))
        l = math.dist((x1, y1), (x2, y2))
        buffer = 1
        if l - buffer <= d1 + d2 <= l + buffer:
            return True
        return False

    def translate_to_normal(self, pos):
        x = round((pos[0] - self.map_rect_offset - self.rect.left) / (self.map_rect.w / MAP_ROW_COUNT), 1)
        y = round((pos[1] - self.map_rect_offset - self.rect.top) / (self.map_rect.h / MAP_COL_COUNT), 1)
        return x, y

    def save_state(self):
        filename = "map.txt"
        with open(filename, 'w') as file:
            data = ""
            tile_set = "default"
            pycaster_scale = 10
            for line in self.lines:
                p1 = self.translate_to_normal(line.p1) * pycaster_scale
                p2 = self.translate_to_normal(line.p2) * pycaster_scale
                p1 = p1[0] * pycaster_scale, p1[1] * pycaster_scale
                p2 = p2[0] * pycaster_scale, p2[1] * pycaster_scale
                data += f"{tile_set}: {p1}; {p2}; {line.color}\n"
            # Remove trailing newline
            data = data[0:len(data) - 1]
            file.write(data)
            file.close()

    def load_state(self):
        filename = "map.txt"
        with open(filename, 'r') as file:
            self.lines.clear()
            for line in file:
                line_split = line.split(':')
                vals = line_split[1].split('; ')
                p1 = self.translate_to_map(eval(vals[0]))
                p2 = self.translate_to_map(eval(vals[1]))
                color = eval(vals[2])
                self.lines.append(Line(p1, p2, color))

    def reset_state(self):
        self.lines.clear()


class Line:
    def __init__(self, p1, p2, color):
        self.p1 = p1
        self.p2 = p2
        self.color = color
        self.width = 5

    def set_color(self, color):
        self.color = color

    def draw(self):
        s = pygame.display.get_surface()
        pygame.draw.line(s, self.color, self.p1, self.p2, self.width)


class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.r = 3
        self.color = (100, 0, 0)
        self.rect = pygame.Rect(self.x - (15 / 2), self.y - (15 / 2), 15, 15)

    def draw(self):
        s = pygame.display.get_surface()
        pygame.draw.circle(s, self.color, (self.x, self.y), self.r)

    def check_collision(self, p):
        return self.rect.collidepoint(p[0], p[1])


class ToolPanel:
    def __init__(self, top, left, width, height, save_map, load_map, reset_map, set_line_color):
        self.background_color = (25, 25, 25)
        self.text_color = (255, 255, 255)
        self.rect = pygame.Rect(top, left, width, height)

        self.buttons = []

        b_width = 350
        b_height = 35
        b_spacing = 20

        self.buttons.append(
            Button(
                rect=pygame.Rect(
                    (self.rect.w / 2) - (b_width / 2),
                    (b_height + b_spacing) * 1,
                    b_width, b_height),
                color=(50, 50, 50),
                name="Red Wall",
                action=set_line_color,
                args=(255, 0, 0),
            )
        )

        self.buttons.append(
            Button(
                rect=pygame.Rect(
                    (self.rect.w / 2) - (b_width / 2),
                    (b_height + b_spacing) * 2,
                    b_width, b_height),
                color=(50, 50, 50),
                name="Green Wall",
                action=set_line_color,
                args=(0, 255, 0),
            )
        )

        self.buttons.append(
            Button(
                rect=pygame.Rect(
                    (self.rect.w / 2) - (b_width / 2),
                    (b_height + b_spacing) * 3,
                    b_width, b_height),
                color=(50, 50, 50),
                name="Blue Wall",
                action=set_line_color,
                args=(0, 0, 255),
            )
        )

        self.buttons.append(
            Button(
                rect=pygame.Rect(
                    (self.rect.w / 2) - (b_width / 2),
                    (b_height + b_spacing) * 4,
                    b_width, b_height),
                color=(50, 50, 50),
                name="White Wall",
                action=set_line_color,
                args=(255, 255, 255),
            )
        )

        self.buttons.append(
            Button(
                rect=pygame.Rect(
                    (self.rect.w / 2) - (b_width / 2),
                    (b_height + b_spacing) * 11,
                    b_width,
                    b_height),
                color=(50, 50, 50),
                name="Save",
                action=save_map
            )
        )

        self.buttons.append(
            Button(
                rect=pygame.Rect(
                    (self.rect.w / 2) - (b_width / 2),
                    (b_height + b_spacing) * 12,
                    b_width,
                    b_height),
                color=(50, 50, 50),
                name="Load",
                action=load_map
            )
        )

        self.buttons.append(
            Button(
                rect=pygame.Rect(
                    (self.rect.w / 2) - (b_width / 2),
                    (b_height + b_spacing) * 13,
                    b_width,
                    b_height),
                color=(50, 50, 50),
                name="Reset",
                action=reset_map
            )
        )

    def draw(self):
        s = pygame.display.get_surface()
        pygame.draw.rect(s, self.background_color, self.rect)

        # Draw buttons
        font = pygame.font.SysFont('consolas.ttf', 24)
        for button in self.buttons:
            button.draw()

        pygame.display.get_surface().blit(s, (0, 0))

    def check_button_on_click(self, pos):
        for button in self.buttons:
            button.handle_click(pos)

    def check_button_focusing(self, pos):
        for button in self.buttons:
            button.check_focused(pos)


class Button:
    def __init__(self, rect, color, name, action, args=None):
        self.rect = rect
        self.color = color
        self.action = action
        self.args = args
        self.name = name

        self.font_size = 32
        self.font_name = "consolas.ttf"
        self.font_color = (240, 240, 240)

        self.focused = False

    def draw(self):
        # Draw Button
        s = pygame.display.get_surface()
        pygame.draw.rect(s, self.color, self.rect)

        # Draw name of button
        font = pygame.font.SysFont(self.font_name, self.font_size)
        text = font.render(self.name, True, self.font_color)
        t_rect = text.get_rect()
        t_pos = (
            self.rect.x + (self.rect.width - t_rect.width) / 2,
            self.rect.y + (self.rect.height - t_rect.height) / 2
        )
        s.blit(text, t_pos)

        # Draw transparent layer if focused
        if self.focused:
            overlay = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
            overlay.fill(pygame.Color(0, 0, 0, 50))
            s.blit(overlay, self.rect)

    def handle_click(self, pos):
        """
        This is probably really bad to do...
        :param pos:
        :return:
        """
        if self.rect.collidepoint(pos[0], pos[1]):
            if self.action:
                if self.args:
                    self.action(self.args)
                else:
                    self.action()

    def check_focused(self, pos):
        if self.rect.collidepoint(pos[0], pos[1]):
            self.focused = True
        else:
            self.focused = False

    def set_action(self, action):
        self.action = action


if __name__ == "__main__":
    map_builder = MapBuilder()
    map_builder.run()
