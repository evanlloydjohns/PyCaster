from random import randint

import pygame
import math

# Dimensions of the window
WIDTH = 800
HEIGHT = 800

# Number of degrees per rotation
ROTATION_AMOUNT = 4

# Amount to increment movement
MOVE_AMOUNT = 4

# Angle of the field of view cone
FOV_ANGLE = 90

# Distance to complete darkness
LIGHT_DIST = 1200

# Total number of rays
RAY_COUNT = 200

# Length/radius of Rays
GR = math.sqrt(math.pow(HEIGHT, 2) + math.pow(WIDTH, 2))

# Angle of each casted ray in radians
DEG_DIF = (360.0 / RAY_COUNT) * (math.pi / 180)

# Preset colors
colors = {
    "RED": (255, 0, 0),
    "GREEN": (0, 255, 0),
    "BLUE": (0, 0, 255),
    "BLACK": (0, 0, 0),
    "WHITE": (255, 255, 255),
    "GRAY": (100, 100, 100),
    "LIGHT_GRAY": (150, 150, 150)
}


def rand_color():
    return randint(0, 255), randint(0, 255), randint(0, 255)


class Line:
    width = 1

    def __init__(self, p1, p2, color):
        self.p1 = p1
        self.p2 = p2
        self.color = color

    def get_length(self):
        return math.sqrt(math.pow(self.p2[0] - self.p1[0], 2) + math.pow(self.p2[1] - self.p1[1], 2))

    def get_p1(self):
        return self.p1

    def set_p1(self, p1):
        self.p1 = p1

    def get_p2(self):
        return self.p2

    def set_p2(self, p2):
        self.p2 = p2

    def get_color(self):
        return self.color

    def set_color(self, color):
        self.color = color

    def get_width(self):
        return self.width

    def set_width(self, width):
        self.width = width

    def draw(self, screen):
        pygame.draw.line(screen, self.get_color(), self.get_p1(), self.get_p2(), self.get_width())


class Engine:

    walls = []
    rays = []

    def __init__(self):
        # Current Position
        self.current_position = WIDTH / 2, HEIGHT / 2

        # Initialize walls list
        self.gen_walls()

        # Initialize rays list
        self.gen_rays()

        # Angle relative to x = 0 which rays_cast_index starts
        self.rays_cast_rotation_angle = 0

        # index of of the ray in rays that should be drawn last
        self.rays_cast_index_end = int((((FOV_ANGLE / 360) * RAY_COUNT) + ((self.rays_cast_rotation_angle / 360) * RAY_COUNT)))

        # index of the ray in rays that should be drawn first
        self.rays_cast_index_start = int(((self.rays_cast_rotation_angle / 360) * RAY_COUNT))

        # index of the ray in rays that is in the center of the user's FOV cone
        self.center_cone_index = int(((FOV_ANGLE / 2) / 360) * RAY_COUNT + ((self.rays_cast_rotation_angle / 360) * RAY_COUNT))

        # index of the ray in rays that is at a right angle to the center_cone_index
        self.strafe_cone_index = int(((90 / 360) * RAY_COUNT) + (((FOV_ANGLE / 2) + self.rays_cast_rotation_angle) / 360) * RAY_COUNT)

    def gen_walls(self):
        wall_width = 5
        for i in range(4):
            c = rand_color()
            p1 = (i - 0)*(i - 3)*((WIDTH / 2)*(i - 2) + (WIDTH / -2)*(i - 1)),\
                 (i - 0)*(i - 1)*((HEIGHT / -2)*(i - 3) + (HEIGHT / 6)*(i - 2))
            p2 = (i - 2)*(i - 3)*((WIDTH / -6)*(i - 1) + (WIDTH / 2)*(i - 0)),\
                 (i - 0)*(i - 3)*((HEIGHT / 2)*(i - 2) + (HEIGHT / -2)*(i - 1))
            w = Line(p1, p2, c)
            w.set_width(wall_width)
            self.walls.append(w)

    def gen_rays(self):
        p1 = self.current_position
        for i in range(RAY_COUNT):
            x = (p1[0] + (GR * math.cos(DEG_DIF * i)))
            y = (p1[1] + (GR * math.sin(DEG_DIF * i)))
            p2 = x, y
            ray = Line(p1, p2, colors["WHITE"])
            self.rays.append(ray)

    # Update all rays to current mouse position
    def update(self):
        p1 = self.current_position
        for i in range(RAY_COUNT):
            x = (p1[0] + (GR * math.cos(DEG_DIF * i)))
            y = (p1[1] + (GR * math.sin(DEG_DIF * i)))
            p2 = x, y
            self.rays[i].set_p1(p1)
            self.rays[i].set_p2(p2)

    # Draw all rays and walls to the screen
    def draw(self, screen):
        screen.fill(colors["BLACK"])
        pygame.draw.rect(screen, colors["LIGHT_GRAY"], (0, 0, WIDTH, int(HEIGHT / 2)))
        pygame.draw.rect(screen, colors["GRAY"], (0, int(HEIGHT / 2), WIDTH, HEIGHT))
        padding = 360 / FOV_ANGLE
        plane_dist = 50

        cast_rays = []

        self.draw_caster(screen)
        # TODO: probs index out of bounds on these for loops
        # Decide which rays to be rendered
        if self.rays_cast_rotation_angle + FOV_ANGLE < 360:
            self.rays_cast_index_end = int(((FOV_ANGLE / 360) * RAY_COUNT) + ((self.rays_cast_rotation_angle / 360) * RAY_COUNT))
            self.rays_cast_index_start = int((self.rays_cast_rotation_angle / 360) * RAY_COUNT)
            self.center_cone_index = int(((FOV_ANGLE / 2) / 360) * RAY_COUNT + ((self.rays_cast_rotation_angle / 360) * RAY_COUNT))
            self.strafe_cone_index = int(((90 / 360) * RAY_COUNT) + (((FOV_ANGLE / 2) + self.rays_cast_rotation_angle) / 360) * RAY_COUNT)

            for i in range(self.rays_cast_index_start, self.rays_cast_index_end + 1):
                cast_rays.append(self.rays[i])
        else:
            self.rays_cast_index_start = int((self.rays_cast_rotation_angle / 360) * RAY_COUNT)
            self.rays_cast_index_end = int(((FOV_ANGLE / 360) * RAY_COUNT) + (((self.rays_cast_rotation_angle - 360) / 360) * RAY_COUNT))
            self.center_cone_index = int((((FOV_ANGLE / 2) / 360) * RAY_COUNT) + (((self.rays_cast_rotation_angle - 360) / 360) * RAY_COUNT))
            self.strafe_cone_index = int(((90 / 360) * RAY_COUNT) + ((((FOV_ANGLE / 2) + self.rays_cast_rotation_angle - 360) / 360) * RAY_COUNT))
            for i in range(self.rays_cast_index_start, RAY_COUNT):
                cast_rays.append(self.rays[i])
            for i in range(self.rays_cast_index_end):
                cast_rays.append(self.rays[i])

        # Generates the fov plane
        flp1x = self.rays[self.rays_cast_index_start].get_p1()[0] + (
                plane_dist * math.cos(DEG_DIF * self.rays_cast_index_start))
        flp1y = self.rays[self.rays_cast_index_start].get_p1()[1] + (
                plane_dist * math.sin(DEG_DIF * self.rays_cast_index_start))
        flp2x = self.rays[self.rays_cast_index_end].get_p1()[0] + (
                plane_dist * math.cos(DEG_DIF * self.rays_cast_index_end))
        flp2y = self.rays[self.rays_cast_index_end].get_p1()[1] + (
                plane_dist * math.sin(DEG_DIF * self.rays_cast_index_end))
        fov_line = Line((flp1x, flp1y), (flp2x, flp2y), colors["RED"])
        fov_line.draw(screen)
        print(fov_line.get_p1())

        # Draw a line some distance from player perpendicular to fov_ray
        # Draw evenly spaced points on the line equal to the number of rays in the cone
        # calculate angle of each new ray from current position to point on line
        # Create new ray at that angle and add ray to cast_rays

        fov_ray = self.get_fov_ray()

        for i in range(len(cast_rays)):
            hw1 = Line((0, 0), (0, 0), colors["BLACK"])
            hw2 = Line((0, 0), (0, 0), colors["BLACK"])

            rays_start_point = self.intersect(fov_ray, cast_rays[i])
            rays_end_point = cast_rays[i].get_p2()

            # r = Line(rays_start_point, rays_end_point, colors["BLACK"])

            length = cast_rays[i].get_length()
            c = cast_rays[i].get_color()
            color = self.calc_dist_color(c, length)
            new_length = (((length / GR) * HEIGHT) - HEIGHT) / 2

            hw1.set_p1((i * padding, HEIGHT / 2))
            hw1.set_p2((i * padding, (HEIGHT / 2) + new_length))

            hw2.set_p1((i * padding, HEIGHT / 2))
            hw2.set_p2((i * padding, (HEIGHT / 2) - new_length))

            # hw1.set_color(cast_rays[i].get_color())
            # hw2.set_color(cast_rays[i].get_color())
            hw1.set_color(color)
            hw2.set_color(color)

            hw1.set_width(int(padding))
            hw2.set_width(int(padding))

            # hw2.draw(screen)
            # hw1.draw(screen)

    def calc_dist_color(self, col, l):
        c = []
        for i in range(len(col)):
            c.append(col[i] - (l / LIGHT_DIST) * col[i])
            if c[i] < 0:
                c[i] = 0
        return c

    def move(self, keys):
        if keys[pygame.K_e]:
            if self.rays_cast_rotation_angle < 360:
                self.rays_cast_rotation_angle = self.rays_cast_rotation_angle + ROTATION_AMOUNT
            if self.rays_cast_rotation_angle > 359:
                self.rays_cast_rotation_angle = 0
        if keys[pygame.K_q]:
            if self.rays_cast_rotation_angle < 1:
                self.rays_cast_rotation_angle = 360
            if self.rays_cast_rotation_angle > 0:
                self.rays_cast_rotation_angle = self.rays_cast_rotation_angle - ROTATION_AMOUNT
        if keys[pygame.K_w]:
            p1 = self.current_position
            x = (p1[0] + (MOVE_AMOUNT * math.cos(DEG_DIF * self.center_cone_index)))
            y = (p1[1] + (MOVE_AMOUNT * math.sin(DEG_DIF * self.center_cone_index)))
            p2 = x, y
            self.current_position = p2
            return
        if keys[pygame.K_a]:
            p1 = self.current_position
            x = (p1[0] - (MOVE_AMOUNT * math.cos(DEG_DIF * self.strafe_cone_index)))
            y = (p1[1] - (MOVE_AMOUNT * math.sin(DEG_DIF * self.strafe_cone_index)))
            p2 = x, y
            self.current_position = p2
            return
        if keys[pygame.K_s]:
            p1 = self.current_position
            x = (p1[0] - (MOVE_AMOUNT * math.cos(DEG_DIF * self.center_cone_index)))
            y = (p1[1] - (MOVE_AMOUNT * math.sin(DEG_DIF * self.center_cone_index)))
            p2 = x, y
            self.current_position = p2
            return
        if keys[pygame.K_d]:
            p1 = self.current_position
            x = (p1[0] + (MOVE_AMOUNT * math.cos(DEG_DIF * self.strafe_cone_index)))
            y = (p1[1] + (MOVE_AMOUNT * math.sin(DEG_DIF * self.strafe_cone_index)))
            p2 = x, y
            self.current_position = p2
            return

    def get_fov_ray(self):
        # TODO: might be issue with not checking for end index being smaller than start index
        start_ray = self.rays[self.rays_cast_index_start]
        end_ray = self.rays[self.rays_cast_index_end]
        camera_distance = 100
        x1 = start_ray.get_p1()[0] + (camera_distance * math.cos(DEG_DIF * self.rays_cast_index_start))
        y1 = start_ray.get_p1()[1] + (camera_distance * math.sin(DEG_DIF * self.rays_cast_index_start))
        x2 = end_ray.get_p1()[0] + (camera_distance * math.cos(DEG_DIF * self.rays_cast_index_end))
        y2 = end_ray.get_p1()[1] + (camera_distance * math.sin(DEG_DIF * self.rays_cast_index_end))
        p1 = x1, y1
        p2 = x2, y2
        return Line(p1, p2, colors["BLUE"])

    def draw_caster(self, screen):
        screen.fill(colors["BLACK"])
        for wall in self.walls:
            wall.draw(screen)

        for ray in self.rays:
            ray.draw(screen)

    # Calculates a point of intersection between two lines, returns null if no intersection
    def intersect(self, wall, ray):
        p0 = wall.get_p1()
        p1 = wall.get_p2()
        p2 = ray.get_p1()
        p3 = ray.get_p2()

        s1 = (p1[0] - p0[0]), (p1[1] - p0[1])
        s2 = (p3[0] - p2[0]), (p3[1] - p2[1])

        den = (-s2[0] * s1[1] + s1[0] * s2[1])
        if den == 0:
            return None
        s = (-s1[1] * (p0[0] - p2[0]) + s1[0] * (p0[1] - p2[1])) / den
        t = (s2[0] * (p0[1] - p2[1]) - s2[1] * (p0[0] - p2[0])) / den

        if 0 <= s <= 1 and 0 <= t <= 1:
            return (p0[0] + (t * s1[0])), (p0[1] + (t * s1[1]))

        return None

    # Checks for collisions between all rays and walls
    def checkCollisions(self):
        for ray in self.rays:
            for wall in self.walls:
                p2 = self.intersect(wall, ray)
                if p2 is not None:
                    ray.set_color(wall.get_color())
                    ray.set_p2(p2)

    def addWall(self, wall):
        self.walls.append(wall)

    def getWalls(self):
        return self.walls

    def getRays(self):
        return self.rays


class Display:

    def __init__(self):
        pygame.init()
        self.image = pygame.Surface((WIDTH, HEIGHT))
        self.image.fill((0, 101, 103))
        self.react = self.image.get_rect()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))

    def update(self):
        pygame.display.flip()

    def getScreen(self):
        return self.screen


class Game:

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("RayCaster")
        self.display = Display()
        self.engine = Engine()
        self.running = True
        self.clock = pygame.time.Clock()
        self.run()

    def run(self):
        ps = []
        while self.running:
            # Look through all events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    ps.append(pygame.mouse.get_pos())
                    if len(ps) > 1:
                        self.engine.addWall(Line(ps[0], ps[1], (randint(0, 255), randint(0, 255), randint(0, 255))))
                        ps.clear()

            keys = pygame.key.get_pressed()
            self.engine.move(keys)

            # Update rays
            self.engine.update()
            self.engine.checkCollisions()

            # Draw new rays
            self.engine.draw(self.display.getScreen())

            # Draw updated rays
            self.display.update()

            # Tick the clock
            self.clock.tick(60)
        pygame.quit()


game = Game()
