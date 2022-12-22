from random import randint

import configparser
import pygame
import math

import display
import geometry
import pycaster


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


def rand_color():
    return randint(0, 255), randint(0, 255), randint(0, 255)


def gen_walls():
    s = 100
    d = 10
    cord_loc = []
    w_d = s / d
    h_d = s / d
    wl = [
        geometry.Wall((-s/2, -s/2), (-s/2, s/2), rand_color()),
        geometry.Wall((-s/2, s/2), (s/2, s/2), rand_color()),
        geometry.Wall((s/2, s/2), (s/2, -s/2), rand_color()),
        geometry.Wall((s/2, -s/2), (-s/2, -s/2), rand_color())
    ]

    for i in range(d):
        c = []
        for j in range(d):
            i_x = i * w_d - s/2
            j_y = j * h_d - s/2
            c.append((i_x, j_y))
        cord_loc.append(c)
    for i in range(d):
        for j in range(d):
            if j % 2 == 0:
                if j + 1 is not d:
                    wl.append(geometry.Wall(cord_loc[i][j], cord_loc[i][j + 1], rand_color()))
                else:
                    pass
            if i % 2 == 0:
                if i + 1 is not d:
                    wl.append(geometry.Wall(cord_loc[i][j], cord_loc[i + 1][j], rand_color()))
    return wl


def draw_frame():
    screen = display.get_screen()
    display_buffer = engine.generate_snapshot()
    screen.fill(colors["BLACK"])
    pygame.draw.rect(screen, colors["SKY"], ((0, 0), (width, height / 2)))
    pygame.draw.rect(screen, colors["GROUND"], ((0, height / 2), (width, height)))
    for wall in display_buffer:
        pygame.draw.line(display.get_screen(), wall[0].get_color(), wall[0].get_p1(), wall[0].get_p2(), wall[0].get_width())
        pygame.draw.line(display.get_screen(), wall[1].get_color(), wall[1].get_p1(), wall[1].get_p2(),  wall[1].get_width())
    pygame.draw.circle(screen, (255, 255, 255), (width/2, height/2), 5, 1)


def draw_debug(fps):
    font = pygame.font.SysFont('freesansbold.ttf', 32)
    frames = font.render('fps:{0}'.format(int(fps)), True, (0, 255, 0))
    pos = engine.get_pos()
    coords = font.render('x:{0} y:{1}'.format(int(pos[0]), int(pos[1])), True, (0, 255, 0))
    display_buffer = engine.debug()
    if is_detailed_debug:
        for ray in display_buffer:
            pygame.draw.line(display.get_screen(), ray.get_color(), ray.get_p1(), ray.get_p2())
            pygame.draw.circle(display.get_screen(), (0, 0, 255), ray.get_p2(), 5, 0)
    display.get_screen().blit(frames, (0, 0))
    display.get_screen().blit(coords, (0, 20))


def run():
    global running
    # position list for mouse button clicks
    lc, rc, mc = [], [], []
    screen_center = (width / 2, height / 2)
    # Used to send mouse position when creating a wall
    lcb = False
    # Set  up mouse
    pygame.mouse.set_pos(width / 2, height / 2)
    pygame.mouse.set_visible(False)
    while running:
        keys = pygame.key.get_pressed()
        # Pass key inputs on to camera movement method
        running = engine.move(keys)
        # Look through all events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Start drawing a wall
                if event.button == 1:
                    engine.color_wall()
                    # lcb = not lcb
                    # lc.append(pygame.mouse.get_pos())
                    # if len(lc) > 1:
                    #     engine.add_walls("click", [geometry.Wall(lc[0], lc[1], rand_color())])
                    #     lc.clear()
                    #     engine.remove_walls("temp")
                # Start drawing a square
                if event.button == 2:
                    mc.append(pygame.mouse.get_pos())
                    if len(mc) > 1:
                        c = rand_color()
                        engine.add_walls("click", [geometry.Wall((mc[0][0], mc[0][1]), (mc[1][0], mc[0][1]), c)])
                        engine.add_walls("click", [geometry.Wall((mc[1][0], mc[0][1]), (mc[1][0], mc[1][1]), c)])
                        engine.add_walls("click", [geometry.Wall((mc[1][0], mc[1][1]), (mc[0][0], mc[1][1]), c)])
                        engine.add_walls("click", [geometry.Wall((mc[0][0], mc[1][1]), (mc[0][0], mc[0][1]), c)])
                        mc.clear()
                if event.button == 3:
                    engine.remove_facing_wall()

        # Get mouse movement
        mouse_curr = pygame.mouse.get_pos()
        pygame.mouse.set_pos(width / 2, height / 2)
        engine.rotate(mouse_curr[0] - screen_center[0])

        # If building wall, send mouse position for wall preview
        if lcb:
            engine.change_walls("temp", [geometry.Wall(lc[0], pygame.mouse.get_pos(), (0, 0, 0))])

        # Update engine
        engine.update()

        # Generate next frame
        draw_frame()

        # Draw debug
        if is_debug:
            draw_debug(clock.get_fps())

        # Draw buffered frame
        pygame.display.flip()

        # Tick the clock
        # clock.tick(120)

    pygame.quit()


# initialize the config parsers
config = configparser.ConfigParser()
config.read('settings.ini')
de_config = config['DEFAULT']

width = int(de_config['width'])
height = int(de_config['height'])
is_debug = int(de_config['isDebug'])
is_detailed_debug = int(de_config['isDetailedDebug'])
is_full_screen = bool(de_config['isFullScreen'])
wall_height = int(de_config['wallHeight'])

w1 = geometry.Wall((300, 0), (600, 600), (0, 0, 0))
w2 = geometry.Wall((600, 600), (0, 600), (0, 0, 0))
w3 = geometry.Wall((0, 600), (300, 0), (0, 0, 0))
tri_list = [w1, w2, w3]
emp_list = []

pygame.init()
pygame.font.init()
pygame.display.set_caption("RayCaster")
display = display.Display(width, height, is_full_screen)
engine = pycaster.Engine(width, height, wall_height)
engine.add_walls("default", gen_walls())
running = True
clock = pygame.time.Clock()
run()
