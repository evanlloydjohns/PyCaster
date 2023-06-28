import configparser
import pygame

import geometry
import menus
import pycaster
from instances import GameState

# Clean up game.py. We could have all menus and an 'engine controller' inherit from a class that has a
# process_inputs(), update(), and process_outputs() method. This way, we could set the state of the game,
# and just call that state's three methods.
# IDEA: You could use Mazetric from 376 to generate a maze

# Collection of pre-defined colors
colors = {
    "RED": (255, 0, 0),
    "SKY": (0, 0, 0),
    "GROUND": (0, 0, 0),
    "GREEN": (0, 255, 0),
    "BLUE": (0, 0, 255),
    "BLACK": (0, 0, 0),
    "WHITE": (255, 255, 255),
    "GRAY": (100, 100, 100),
    "LIGHT_GRAY": (150, 150, 150)
}


def set_state(new_state):
    """
    Sets the current game state. Usually passed to menu interfaces
    so they can swap the game state.
    :param new_state: new game state
    """
    global current_state
    current_state = new_state
    pygame.mouse.set_pos(width / 2, height / 2)
    if not is_detailed_debug:
        pygame.mouse.set_visible(False)


def set_running(new_running):
    """
    Allows menu interfaces to end the game
    :param new_running: new running state
    :return:
    """
    global running
    running = new_running


def gen_walls():
    """
    Generates the walls list for the WorldState used in the pycaster.
    Loads the walls from map.txt
    :return:
    """
    with open("map.txt", 'r') as file:
        walls = []
        for line in file:
            line_split = line.split(':')
            key = line_split[0]
            vals = line_split[1].split('; ')
            walls.append(geometry.Wall(eval(vals[0]), eval(vals[1]), eval(vals[2])))
        return walls


def consolidate_walls(key):
    """
    Combines all walls that can be turned into a larger wall
    Only works with walls in a grid. Also might not work...
    :param key: The key of the walls dictionary in the pycaster's WorldState
    :return:
    """
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
    engine.get_world_state().remove_wall_group(key)
    engine.get_world_state().add_walls(key, walls)


def cull_redundant_walls(key):
    """
    Removes walls that are on top of one another
    :param key: The key of the walls dictionary in the pycaster's WorldState
    :return:
    """
    # I know this is horrible programming
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
    return cl


# TODO: We should really be doing this in WorldState
def load_state(filename):
    """
    Loads and sets the pycaster's WorldState from a file
    :param filename: file containing the WorldState
    :return:
    """
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


def save_state(filename):
    print("saving!")
    engine.get_world_state().save_state(filename)


def draw_frame():
    """
    Gets a frame from the pycaster and draws it
    :return:
    """
    screen = pygame.display.get_surface()
    frame = engine.process_outputs()
    screen.fill(colors["BLACK"])
    pygame.draw.rect(screen, colors["SKY"], ((0, 0), (width, height / 2)))
    pygame.draw.rect(screen, colors["GROUND"], ((0, height / 2), (width, height)))
    segment_width = frame.get_segment_width()
    segments = frame.get_segments()
    for segment in segments:
        pygame.draw.line(screen, segment.get_color(), segment.get_p1(), segment.get_p2(), segment_width)


def get_debug_dict():
    return {
        'fps': clock.get_fps(),
        'cur_pos': engine.get_cur_position(),
        'is_detailed_debug': is_detailed_debug,
        'debug_rays': engine.debug(),
        'debug_walls': engine.get_world_state().get_all_walls(),
        'engine_debug': engine.get_debug_stats()
    }


def process_inputs():
    """
    Processes all inputs given the current game state
    :return:
    """
    global current_state
    global running
    events = pygame.event.get()

    if current_state is GameState.GAME:
        global loop_i, mli_limit
        # Send engine keyboard input
        running = engine.process_keys()
        game_hud.process_inputs(events)
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    current_state = GameState.PAUSE_MENU
                    pygame.mouse.set_visible(True)
                # Handle saving and loading
                if event.key == pygame.K_o:
                    save_state("map.txt")
                if event.key == pygame.K_p:
                    load_state("map.txt")
            # Check for exit condition
            if event.type == pygame.QUIT:
                running = False
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

    if current_state is GameState.PAUSE_MENU:
        pause_menu.process_inputs(events)

    if current_state is GameState.START_MENU:
        start_menu.process_inputs(events)

    return running


def update(dt):
    """
    Calls appropriate update methods given the current game state
    :param dt:
    :return:
    """
    if current_state is GameState.GAME:
        # Update Engine
        engine.update(dt)
        game_hud.update()

    if current_state is GameState.PAUSE_MENU:
        pause_menu.update()

    if current_state is GameState.START_MENU:
        engine.update(dt)
        start_menu.update()


def process_output():
    """
    Processes all outputs given the current game state
    :return:
    """
    if current_state is GameState.GAME:
        draw_frame()
        game_hud.process_outputs()
        # if is_debug:
        #     draw_debug()

    if current_state is GameState.PAUSE_MENU:
        draw_frame()
        pause_menu.process_outputs()

    if current_state is GameState.START_MENU:
        draw_frame()
        start_menu.process_outputs()

    # Draw buffered frame to display
    pygame.display.flip()


def run():
    """
    Main game loop
    :return:
    """
    global running
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

# Initialize menus
pause_menu = menus.PauseMenuInterface(width, height, set_state, set_running, load_state)
start_menu = menus.StartMenuInterface(width, height, set_state, set_running)
game_hud = menus.GameHUDInterface(width, height, set_state, set_running, get_debug_dict)

current_state = GameState.START_MENU

running = True

run()
