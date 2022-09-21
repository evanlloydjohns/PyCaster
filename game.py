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


def draw_frame():
    screen = display.get_screen()
    display_buffer = engine.generate_snapshot()
    screen.fill(colors["BLACK"])
    pygame.draw.rect(screen, colors["SKY"], ((0, 0), (width, height / 2)))
    pygame.draw.rect(screen, colors["GROUND"], ((0, height / 2), (width, height)))
    for wall in display_buffer:
        pygame.draw.line(display.get_screen(), wall[0].get_color(), wall[0].get_p1(), wall[0].get_p2(), wall[0].get_width())
        pygame.draw.line(display.get_screen(), wall[1].get_color(), wall[1].get_p1(), wall[1].get_p2(),  wall[1].get_width())


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
                        engine.add_walls("click", [geometry.Wall(lc[0], lc[1], rand_color())])
                        lc.clear()
                        engine.remove_walls("temp")
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

        # If building wall, send mouse position for wall preview
        if lcb:
            engine.change_walls("temp", [geometry.Wall(lc[0], pygame.mouse.get_pos(), (0, 0, 0))])

        # Update engine
        engine.update()

        # Generate next frame
        draw_frame()

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

w1 = geometry.Wall((300, 0), (600, 600), (0, 0, 0))
w2 = geometry.Wall((600, 600), (0, 600), (0, 0, 0))
w3 = geometry.Wall((0, 600), (300, 0), (0, 0, 0))
tri_list = [w1, w2, w3]
emp_list = []

pygame.init()
pygame.display.set_caption("RayCaster")
display = display.Display()
engine = pycaster.Engine()
running = True
clock = pygame.time.Clock()
run()
