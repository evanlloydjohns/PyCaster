import configparser
import math
from enum import Enum

import pygame

import geometry
import pycaster

# TODO: Saving/loading does not support circles

# TODO: We could use box2d to introduce physics. pushing and pulling walls around.

# TODO: Investigate adding a wall culling script for walls that are a subset of other walls
# TODO: Add a GUI module for implementation of a start menu and pause menu
# Collection of pre-defined colors
colors = {
    "RED": (255, 0, 0),
    "SKY": (63, 63, 63),
    "GROUND": (63, 63, 63),
    "GREEN": (0, 255, 0),
    "BLUE": (0, 0, 255),
    "BLACK": (0, 0, 0),
    "WHITE": (255, 255, 255),
    "GRAY": (100, 100, 100),
    "LIGHT_GRAY": (150, 150, 150)
}


class GameState(Enum):
    GAME = 0
    MENU = 1


def gen_walls():
    with open("board.txt", 'r') as file:
        walls = []
        for line in file:
            line_split = line.split(':')
            key = line_split[0]
            vals = line_split[1].split('; ')
            walls.append(geometry.Wall(eval(vals[0]), eval(vals[1]), eval(vals[2])))
        return walls
    # s = 100
    # d = 10
    # cord_loc = []
    # x_d = s / d
    # y_d = s / d
    # wl = [
    #     # geometry.Wall((-s/2, -s/2), (-s/2, s/2), colors["WHITE"]),
    #     # geometry.Wall((-s/2, s/2), (s/2, s/2), colors["WHITE"]),
    #     # geometry.Wall((s/2, s/2), (s/2, -s/2), colors["WHITE"]),
    #     # geometry.Wall((s/2, -s/2), (-s/2, -s/2), colors["WHITE"])
    # ]

    # for i in range(d):
    #     c = []
    #     for j in range(d):
    #         i_x = (i * x_d) - s/2
    #         j_y = (j * y_d) - s/2
    #         c.append((i_x, j_y))
    #     cord_loc.append(c)
    # for i in range(d):
    #     for j in range(d):
    #         if j % 2 == 0:
    #             if j + 1 is not d:
    #                 wl.append(geometry.Wall(cord_loc[i][j], cord_loc[i][j + 1], colors["WHITE"]))
    #             else:
    #                 pass
    #         if i % 2 == 0:
    #             if i + 1 is not d:
    #                 wl.append(geometry.Wall(cord_loc[i][j], cord_loc[i + 1][j], colors["WHITE"]))
    # return wl
    # maze = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    #         [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    #         [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    #         [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    #         [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    #         [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    #         [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    #         [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    #         [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    #         [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    #         [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    #         [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    #         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
    # return translate_map_coords(maze)


def translate_map_coords(map):
    coords = []
    for y in range(len(map)):
        for x in range(len(map[0])):
            if map[y][x] == 0:
                coords.append([(x*10, y*10), (x*10 + 10, y*10), (x*10 + 10, y*10 + 10), (x*10, y*10 + 10)])
    walls = []
    for rect in coords:
        walls.append(geometry.Wall(rect[0], rect[1], (255, 255, 255)))
        walls.append(geometry.Wall(rect[1], rect[2], (255, 255, 255)))
        walls.append(geometry.Wall(rect[2], rect[3], (255, 255, 255)))
        walls.append(geometry.Wall(rect[3], rect[0], (255, 255, 255)))
    return walls


# combines walls that can be made of a larger wall
def consolidate_walls(key):
    # Maximum distance for connected walls
    # TODO: figure out how to cut out walls that are within a collidable distance
    walls = engine.get_world_state().get_all_walls()[key]
    for i in range(len(walls)):
        w1 = walls[i]
        for j in range(i+1, len(walls)):
            w2 = walls[j]

    # if w1p2 == w2p1:
    #   t_wall = w1p1, w2p2
    #   m_p = w1p2
    #   if line_point_intersect(m_p, t_wall) if not None:
    #       wall = w1p1, w2p2
    con_walls = []
    walls = engine.get_world_state().get_all_walls()[key]
    for i in range(len(walls)):
        w1p1 = walls[i].get_p1()
        w1p2 = walls[i].get_p2()
        for j in range(i + 1, len(walls)):
            w2p1 = walls[j].get_p1()
            w2p2 = walls[i].get_p2()
            if w1p2 == w2p1:
                t_wall = geometry.Wall(w1p1, w2p2, (255, 255, 255))
                m_p = w1p2
                if geometry.line_point(t_wall, m_p):
                    con_walls.append(t_wall)
    for wall in con_walls:
        print("p1:{0} p2:{1}".format(wall.get_p1(), wall.get_p2()))
    engine.get_world_state().remove_wall_group(key)
    engine.get_world_state().add_walls(key, walls)


# I know this is horrible programming
def cull_redundant_walls(key):
    walls = engine.get_world_state().get_all_walls()
    redundant_walls = []
    for i in range(len(walls[key])):
        w1 = walls[key][i]
        for j in range(i + 1, len(walls[key])):
            w2 = walls[key][j]
            if w1.get_p1() == w2.get_p1() and w1.get_p2() == w2.get_p2():
                redundant_walls.append((key, w1))
            if w1.get_p1() == w2.get_p2() and w1.get_p2() == w2.get_p1():
                redundant_walls.append((key, w1))
    for r_wall in redundant_walls:
        walls[r_wall[0]].remove(r_wall[1])


def gen_circles():
    cl = []
    # cl.append(geometry.Circle((100, 100), 3, (255, 0, 0)))
    # cl.append(geometry.Circle((110, 105), 3, (0, 255, 0)))
    # cl.append(geometry.Circle((115, 110), 3, (0, 0, 255)))
    # cl.append(geometry.Circle((100, 110), 3, (255, 0, 255)))
    return cl


def load_state(filename):
    with open(filename, 'r') as file:
        engine.get_world_state().remove_all_walls()
        engine.get_world_state().remove_all_circles()
        walls = {}
        circles = {}
        for line in file:
            line_split = line.split(':')
            key = line_split[0]
            vals = line_split[1].split('; ')
            if key in walls:
                walls[key].append(geometry.Wall(eval(vals[0]), eval(vals[1]), eval(vals[2])))
            else:
                walls[key] = [geometry.Wall(eval(vals[0]), eval(vals[1]), eval(vals[2]))]
        engine.get_world_state().set_walls(walls)


# TODO: saving multiple times because key is being pressed
def save_state(filename):
    print("saving!")
    with open(filename, 'w') as file:
        data = ""
        walls = engine.get_world_state().get_walls()
        for k in walls:
            for w in walls[k]:
                data += "{0}: {1}; {2}; {3}\n".format(k, w.get_p1(), w.get_p2(), w.get_color())
        # Remove trailing newline
        data = data[0:len(data) - 1]
        file.write(data)


def draw_frame():

    screen = pygame.display.get_surface()
    frame = engine.process_outputs()
    screen.fill(colors["BLACK"])
    pygame.draw.rect(screen, colors["SKY"], ((0, 0), (width, height / 2)))
    pygame.draw.rect(screen, colors["GROUND"], ((0, height / 2), (width, height)))
    segment_width = frame.get_segment_width()
    segments = frame.get_segments()
    for segment in segments:
        pygame.draw.line(screen, segment.get_color(), segment.get_p1(), segment.get_p2(), segment_width)
    pygame.draw.line(screen, (255, 255, 255), (width / 2, height / 2 + 10), (width / 2, height / 2 - 10), 1)
    pygame.draw.line(screen, (255, 255, 255), (width / 2 + 10, height / 2), (width / 2 - 10, height / 2), 1)


def draw_debug():
    screen = pygame.display.get_surface()
    cur_pos = engine.get_cur_position()
    font_label = ['fps:{0}'.format(round(clock.get_fps(), 1)),
                  'x:{0} y:{1}'.format(round(cur_pos[0], 1), round(cur_pos[1], 1))]
    if is_detailed_debug:
        debug_rays = engine.debug()
        for ray in debug_rays:
            p1 = ray.get_p1()[0] + (width / 2), ray.get_p1()[1] + (height / 2)
            p2 = ray.get_p2()[0] + (width / 2), ray.get_p2()[1] + (height / 2)
            pygame.draw.line(screen, ray.get_color(), p1, p2)
            pygame.draw.circle(screen, (0, 0, 255), p2, 5, 0)
        walls = engine.get_world_state().get_all_walls()
        for k in walls:
            for wall in walls[k]:
                p1 = wall.get_p1()[0] + (width / 2), wall.get_p1()[1] + (height / 2)
                p2 = wall.get_p2()[0] + (width / 2), wall.get_p2()[1] + (height / 2)
                pygame.draw.line(screen, wall.get_color(), p1, p2)
        # Display debug stats
        engine_debug = engine.get_debug_stats()
        for k in engine_debug:
            font_label.append('')
            font_label.append(f'[{k}]')
            for i in engine_debug[k]:
                font_label.append(f'{i}: {engine_debug[k][i]}')

    font = pygame.font.SysFont('consolas.ttf', 24)
    for i in range(len(font_label)):
        text = font.render(font_label[i], True, (0, 255, 0))
        screen.blit(text, (5, i * 20 + 5))


def process_inputs():
    global state
    keys = pygame.key.get_pressed()
    if keys[pygame.K_m]:
        state = GameState.MENU
        pygame.mouse.set_visible(True)
    running = True
    if state is GameState.GAME:
        global loop_i, mli_limit
        # Send engine keyboard input
        running = engine.process_keys()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                # Handle saving and loading
                if event.key == pygame.K_o:
                    save_state("world.txt")
                if event.key == pygame.K_p:
                    load_state("board.txt")
            # Check for exit condition
            if event.type == pygame.QUIT:
                running = False
            # TODO: Investigate migrating mouse button input to engine.process_mouse_buttons()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Color wall on left click
                if event.button == 1:
                    engine.color_wall(pycaster.rand_color())
                # Remove wall on right click
                if event.button == 3:
                    engine.remove_facing_object()

            # Send engine mouse input every 2 loops
            if loop_i == mli_limit:
                # This allows for a more precise rotation delta, and smoother movement
                engine.process_mouse_movement(pygame.mouse.get_pos())
                pygame.mouse.set_pos(width / 2, height / 2)
                loop_i = 0
            else:
                loop_i += 1
    if state is GameState.MENU:
        pass

    return running


def update(dt):
    if state is GameState.GAME:
        # Update Engine
        engine.update(dt)
    if state is GameState.MENU:
        pass


def process_output():
    draw_frame()

    # Draw debug
    if is_debug:
        draw_debug()

    if state is GameState.MENU:
        s = pygame.Surface((width, height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 200))
        pygame.display.get_surface().blit(s, (0, 0))

    # Draw buffered frame to display
    pygame.display.flip()


def run():
    dt = 0
    running = True
    while running:
        # Tick the clock
        dt = clock.tick(120) / 1000
        running = process_inputs()
        update(dt)
        process_output()
    pygame.quit()


# initialize the config parsers
config = configparser.ConfigParser()
config.read('settings.ini')
de_config = config['DEFAULT']

width = de_config.getint('width')
height = de_config.getint('height')
is_debug = de_config.getboolean('isDebug')
is_detailed_debug = de_config.getboolean('isDetailedDebug')
is_full_screen = de_config.getboolean('isFullScreen')
wall_height = de_config.getint('wallHeight')

pygame.init()

# Number of main loop iterations before reading mouse movement
mli_limit = 2
# Used in differentiating one main loop cycle from the next
loop_i = 0

# If using full screen then set width and height to display resolution
if is_full_screen:
    width = pygame.display.Info().current_w
    height = pygame.display.Info().current_h
    mli_limit = 0

pygame.font.init()
pygame.display.set_caption("RayCaster")
pygame.display.set_mode((width, height), is_full_screen)

engine = pycaster.Engine(width, height, wall_height, (7, 7))
world_objects = pycaster.WorldState()
world_objects.add_walls("default", gen_walls())
world_objects.add_circles("default", gen_circles())
engine.set_world_objects(world_objects)
cull_redundant_walls("default")
consolidate_walls("default")

clock = pygame.time.Clock()

# Center mouse location
pygame.mouse.set_pos(width / 2, height / 2)

state = GameState.GAME

if not is_detailed_debug:
    pygame.mouse.set_visible(False)

run()
