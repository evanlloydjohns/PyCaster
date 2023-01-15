import configparser
import pygame

import geometry
import pycaster


# TODO: Investigate adding a wall culling script for walls that are a subset of other walls
# TODO: Add a GUI module for implementation of a start menu and pause menu
# Collection of pre-defined colors
colors = {
    "RED": (255, 0, 0),
    "SKY": (125, 175, 250),
    "GROUND": (68, 74, 68),
    "GREEN": (0, 255, 0),
    "BLUE": (0, 0, 255),
    "BLACK": (0, 0, 0),
    "WHITE": (255, 255, 255),
    "GRAY": (100, 100, 100),
    "LIGHT_GRAY": (150, 150, 150)
}


def gen_walls():
    s = 100
    d = 10
    cord_loc = []
    x_d = s / d
    y_d = s / d
    wl = [
        geometry.Wall((-s/2, -s/2), (-s/2, s/2), pycaster.rand_color()),
        geometry.Wall((-s/2, s/2), (s/2, s/2), pycaster.rand_color()),
        geometry.Wall((s/2, s/2), (s/2, -s/2), pycaster.rand_color()),
        geometry.Wall((s/2, -s/2), (-s/2, -s/2), pycaster.rand_color())
    ]

    for i in range(d):
        c = []
        for j in range(d):
            i_x = (i * x_d) - s/2
            j_y = (j * y_d) - s/2
            c.append((i_x, j_y))
        cord_loc.append(c)
    for i in range(d):
        for j in range(d):
            if j % 2 == 0:
                if j + 1 is not d:
                    wl.append(geometry.Wall(cord_loc[i][j], cord_loc[i][j + 1], pycaster.rand_color()))
                else:
                    pass
            if i % 2 == 0:
                if i + 1 is not d:
                    wl.append(geometry.Wall(cord_loc[i][j], cord_loc[i + 1][j], pycaster.rand_color()))
    return wl


def gen_circles():
    cl = []
    # cl.append(geometry.Circle((100, 100), 10, (255, 0, 0)))
    return cl


def draw_frame():
    screen = pygame.display.get_surface()
    frame = engine.generate_frame()
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
    if is_detailed_debug:
        display_buffer = engine.debug()
        for ray in display_buffer:
            pygame.draw.line(screen, ray.get_color(), ray.get_p1(), ray.get_p2())
            pygame.draw.circle(screen, (0, 0, 255), ray.get_p2(), 5, 0)
    font = pygame.font.SysFont('freesansbold.ttf', 24)
    text = font.render('fps:{0}'.format(round(clock.get_fps(), 1)), True, (0, 255, 0))
    screen.blit(text, (0, 0))
    cur_pos = engine.get_cur_position()
    text = font.render('x:{0} y:{1}'.format(round(cur_pos[0], 1), round(cur_pos[1], 1)), True, (0, 255, 0))
    screen.blit(text, (0, 20))


def process_inputs():
    global loop_i, mli_limit
    # Send engine keyboard input
    keys = pygame.key.get_pressed()
    running = engine.process_keys(keys)
    for event in pygame.event.get():
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

    return running


def update():
    # Update Engine
    engine.update()


def process_output():
    draw_frame()

    # Draw debug
    if is_debug:
        draw_debug()

    # Draw buffered frame to display
    pygame.display.flip()


def run():
    running = True
    while running:
        running = process_inputs()
        update()
        process_output()
        # Tick the clock
        clock.tick(120)
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
engine.add_walls("default", gen_walls())
engine.add_circles("default", gen_circles())

clock = pygame.time.Clock()

# Set  up mouse
pygame.mouse.set_pos(width / 2, height / 2)
if not is_detailed_debug:
    pygame.mouse.set_visible(False)

run()
