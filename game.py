from random import randint

import configparser
import pygame

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


def gen_walls():
    wl = []
    s = 1000
    d = 8
    cord_loc = []
    w_d = s / d
    h_d = s / d
    wl = [
        geometry.Wall(((width / 2) + 0, (height / 2) + 0), ((width / 2) + 0, (height / 2) + s),
                      colors["WHITE"], wall_height - 50),
        geometry.Wall(((width / 2) + 0, (height / 2) + s), ((width / 2) + s, (height / 2) + s),
                      colors["WHITE"], wall_height - 50),
        geometry.Wall(((width / 2) + s, (height / 2) + s), ((width / 2) + s, (height / 2) + 0),
                      colors["WHITE"], wall_height - 50),
        geometry.Wall(((width / 2) + s, (height / 2) + 0), ((width / 2) + 0, (height / 2) + 0),
                      colors["WHITE"], wall_height - 50)
    ]

    for i in range(d):
        c = []
        for j in range(d):
            i_x = (width / 2) + i * w_d
            j_y = (height / 2) + j * h_d
            c.append((i_x, j_y))
        cord_loc.append(c)
    for i in range(d):
        for j in range(d):
            a = cord_loc[i][j]
    for i in range(d):
        for j in range(d):
            if j % 2 == 0:
                if j + 1 is not d:
                    wl.append(geometry.Wall(cord_loc[i][j], cord_loc[i][j + 1], colors["WHITE"], wall_height))
                else:
                    pass
            if i % 2 == 0:
                if i + 1 is not d:
                    wl.append(geometry.Wall(cord_loc[i][j], cord_loc[i + 1][j], colors["WHITE"], wall_height))
    print(cord_loc)
    # for i in range(4):
    #     c = rand_color()
    #     p1 = (i - 0) * (i - 3) * ((self.width / 2) * (i - 2) + (self.width / -2) * (i - 1)), \
    #          (i - 0) * (i - 1) * ((self.height / -2) * (i - 3) + (self.height / 6) * (i - 2))
    #     p2 = (i - 2) * (i - 3) * ((self.width / -6) * (i - 1) + (self.width / 2) * (i - 0)), \
    #          (i - 0) * (i - 3) * ((self.height / 2) * (i - 2) + (self.height / -2) * (i - 1))
    #     w = geometry.Wall(p1, p2, c)
    #     wl.append(w)
    return wl


def draw_frame():
    screen = display.get_screen()
    display_buffer = engine.generate_snapshot()
    screen.fill(colors["BLACK"])
    # pygame.draw.rect(screen, colors["SKY"], ((0, 0), (width, height / 2)))
    # pygame.draw.rect(screen, colors["GROUND"], ((0, height / 2), (width, height)))
    for wall in display_buffer:
        pygame.draw.line(display.get_screen(), wall[0].get_color(), wall[0].get_p1(), wall[0].get_p2(), wall[0].get_width())
        pygame.draw.line(display.get_screen(), wall[1].get_color(), wall[1].get_p1(), wall[1].get_p2(),  wall[1].get_width())


def draw_debug():
    display_buffer = engine.debug()
    for ray in display_buffer:
        pygame.draw.line(display.get_screen(), ray.get_color(), ray.get_p1(), ray.get_p2())


def rand_color():
    return randint(0, 255), randint(0, 255), randint(0, 255)


def run():
    global running
    # position list for mouse button clicks
    lc, rc, mc = [], [], []
    # Used to send mouse position when creating a wall
    lcb = False
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
                    lcb = not lcb
                    lc.append(pygame.mouse.get_pos())
                    if len(lc) > 1:
                        engine.add_walls("click", [geometry.Wall(lc[0], lc[1], rand_color(), wall_height)])
                        lc.clear()
                        engine.remove_walls("temp")
                # Start drawing a square
                if event.button == 2:
                    mc.append(pygame.mouse.get_pos())
                    if len(mc) > 1:
                        c = rand_color()
                        engine.add_walls("click", [geometry.Wall((mc[0][0], mc[0][1]), (mc[1][0], mc[0][1]), c, wall_height)])
                        engine.add_walls("click", [geometry.Wall((mc[1][0], mc[0][1]), (mc[1][0], mc[1][1]), c, wall_height)])
                        engine.add_walls("click", [geometry.Wall((mc[1][0], mc[1][1]), (mc[0][0], mc[1][1]), c, wall_height)])
                        engine.add_walls("click", [geometry.Wall((mc[0][0], mc[1][1]), (mc[0][0], mc[0][1]), c, wall_height)])
                        mc.clear()

        # If building wall, send mouse position for wall preview
        if lcb:
            engine.change_walls("temp", [geometry.Wall(lc[0], pygame.mouse.get_pos(), (0, 0, 0), wall_height)])

        # Update engine
        engine.update()

        # Generate next frame
        draw_frame()

        # Draw debug
        if is_debug:
            draw_debug()

        # Draw buffered frame
        pygame.display.flip()

        # Tick the clock
        clock.tick(60)
    pygame.quit()


# initialize the config parsers
config = configparser.ConfigParser()
config.read('settings.ini')
de_config = config['DEFAULT']

width = int(de_config['width'])
height = int(de_config['height'])
is_debug = int(de_config['isDebug'])
is_full_screen = bool(de_config['isFullScreen'])
wall_height = int(de_config['wallHeight'])

w1 = geometry.Wall((300, 0), (600, 600), (0, 0, 0), wall_height)
w2 = geometry.Wall((600, 600), (0, 600), (0, 0, 0), wall_height)
w3 = geometry.Wall((0, 600), (300, 0), (0, 0, 0), wall_height)
tri_list = [w1, w2, w3]
emp_list = []

pygame.init()
pygame.display.set_caption("RayCaster")
display = display.Display(width, height, is_full_screen)
engine = pycaster.Engine(width, height, wall_height)
engine.add_walls("default", gen_walls())
running = True
clock = pygame.time.Clock()
run()
