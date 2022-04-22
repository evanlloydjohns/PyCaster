from random import randint

import pygame
import math

# Dimensions of the window
WIDTH = 800
HEIGHT = 800

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

# Total number of rays
RAY_COUNT = 800

# Length/radius of Rays
GR = math.sqrt(math.pow(HEIGHT, 2) + math.pow(WIDTH, 2))

# Angle of each casted ray in radians
d = (360.0 / RAY_COUNT) * (math.pi / 180)


class Line:
    width = 1

    def __init__(self, p1, p2, color):
        self.p1 = p1
        self.p2 = p2
        self.color = color

    def get_length(self):
        return math.sqrt(math.pow(self.p2[0] - self.p1[0], 2) + math.pow(self.p2[1] - self.p1[1], 2))

    def getP1(self):
        return self.p1

    def setP1(self, p1):
        self.p1 = p1

    def getP2(self):
        return self.p2

    def setP2(self, p2):
        self.p2 = p2

    def getColor(self):
        return self.color

    def setColor(self, color):
        self.color = color

    def getWidth(self):
        return self.width

    def setWidth(self, width):
        self.width = width

    def draw(self, screen):
        pygame.draw.line(screen, self.getColor(), self.getP1(), self.getP2(), self.getWidth())


class Engine:
    # index of the ray in rays that should be drawn first
    rays_cast_index_start = 0

    # index of of the ray in rays that should be drawn last
    rays_cast_index_end = 0

    # index of the ray in rays that is in the center of the user's FOV cone
    center_cone_index = 0

    # index of the ray in rays that is at a right angle to the center_cone_index
    strafe_cone_index = 0

    # Angle relative to x = 0 which rays_cast_index starts
    rays_cast_rotation_angle = 0

    # Angle of the field of view cone
    fov_angle = 90

    # Ratio between fov_angle and 360 - used for maths
    fov_angle_ratio = fov_angle / 360

    # Number of degrees per rotation
    rotation_amount = 3

    # Amount to increment movement
    move_amount = 4

    # Current Position
    current_position = WIDTH / 2, HEIGHT / 2

    # Distance to complete darkness
    light_dist = 1200

    walls = []
    rays = []

    def __init__(self):
        # Initialize walls list
        self.genWalls()

        # Initialize rays list
        p1 = self.current_position
        for i in range(RAY_COUNT):
            x = (p1[0] + (GR * math.cos(d * i)))
            y = (p1[1] + (GR * math.sin(d * i)))
            p2 = x, y
            ray = Line(p1, p2, colors["WHITE"])
            self.rays.append(ray)

        self.rays_cast_rotation_angle = 0
        self.rays_cast_index_end = int((((self.fov_angle / 360) * RAY_COUNT) + ((self.rays_cast_rotation_angle / 360) * RAY_COUNT)))
        self.rays_cast_index_start = int(((self.rays_cast_rotation_angle / 360) * RAY_COUNT))


    def genWalls(self):
        # TODO: OMG FIX THIS, SOOO UGLY
        # Consider creating a randColor()
        wall_width = 5
        c1 = (randint(0, 255), randint(0, 255), randint(0, 255))
        c2 = (randint(0, 255), randint(0, 255), randint(0, 255))
        c3 = (randint(0, 255), randint(0, 255), randint(0, 255))
        c4 = (randint(0, 255), randint(0, 255), randint(0, 255))
        w1 = Line((0, 0), (WIDTH - 1, 0), c1)
        w2 = Line((WIDTH - 1, 0), (WIDTH - 1, HEIGHT - 1), c2)
        w3 = Line((WIDTH - 1, HEIGHT - 1), (0, HEIGHT - 1), c3)
        w4 = Line((0, HEIGHT - 1), (0, 0), c4)
        w1.setWidth(wall_width)
        w2.setWidth(wall_width)
        w3.setWidth(wall_width)
        w4.setWidth(wall_width)
        self.walls.append(w1)
        self.walls.append(w2)
        self.walls.append(w3)
        self.walls.append(w4)

    # Update all rays to current mouse position
    def update(self):
        p1 = self.current_position
        for i in range(RAY_COUNT):
            x = (p1[0] + (GR * math.cos(d * i)))
            y = (p1[1] + (GR * math.sin(d * i)))
            p2 = x, y
            self.rays[i].setP1(p1)
            self.rays[i].setP2(p2)

    # Draw all rays and walls to the screen
    def draw(self, screen):
        screen.fill(colors["BLACK"])
        pygame.draw.rect(screen, colors["LIGHT_GRAY"], (0, 0, WIDTH, int(HEIGHT / 2)))
        pygame.draw.rect(screen, colors["GRAY"], (0, int(HEIGHT / 2), WIDTH, HEIGHT))
        padding = 360 / self.fov_angle

        cast_rays = []
        # TODO: probs index out of bounds on these for loops
        # Decide which rays to be rendered
        if self.rays_cast_rotation_angle + self.fov_angle < 360:
            self.rays_cast_index_end = int(((self.fov_angle / 360) * RAY_COUNT) + ((self.rays_cast_rotation_angle / 360) * RAY_COUNT))
            self.rays_cast_index_start = int((self.rays_cast_rotation_angle / 360) * RAY_COUNT)
            self.center_cone_index = int(((self.fov_angle / 2) / 360) * RAY_COUNT + ((self.rays_cast_rotation_angle / 360) * RAY_COUNT))
            self.strafe_cone_index = int(((90 / 360) * RAY_COUNT) + (((self.fov_angle / 2) + self.rays_cast_rotation_angle) / 360) * RAY_COUNT)
            for i in range(self.rays_cast_index_start, self.rays_cast_index_end + 1):
                cast_rays.append(self.rays[i])
        else:
            self.rays_cast_index_start = int((self.rays_cast_rotation_angle / 360) * RAY_COUNT)
            self.rays_cast_index_end = int(((self.fov_angle / 360) * RAY_COUNT) + (((self.rays_cast_rotation_angle - 360) / 360) * RAY_COUNT))
            self.center_cone_index = int((((self.fov_angle / 2) / 360) * RAY_COUNT) + (((self.rays_cast_rotation_angle - 360) / 360) * RAY_COUNT))
            self.strafe_cone_index = int(((90 / 360) * RAY_COUNT) + ((((self.fov_angle / 2) + self.rays_cast_rotation_angle - 360) / 360) * RAY_COUNT))
            for i in range(self.rays_cast_index_start, RAY_COUNT):
                cast_rays.append(self.rays[i])
            for i in range(self.rays_cast_index_end):
                cast_rays.append(self.rays[i])

        fov_ray = self.get_fov_ray()

        for i in range(len(cast_rays)):
            hw1 = Line((0, 0), (0, 0), colors["BLACK"])
            hw2 = Line((0, 0), (0, 0), colors["BLACK"])

            rays_start_point = self.intersect(fov_ray, cast_rays[i])
            rays_end_point = cast_rays[i].getP2()

            # r = Line(rays_start_point, rays_end_point, colors["BLACK"])

            length = cast_rays[i].get_length()
            c = cast_rays[i].getColor()
            color = self.calc_dist_color(c, length)
            new_length = (((length / GR) * HEIGHT) - HEIGHT) / 2

            hw1.setP1((i * padding, HEIGHT / 2))
            hw1.setP2((i * padding, (HEIGHT / 2) + new_length))

            hw2.setP1((i * padding, HEIGHT / 2))
            hw2.setP2((i * padding, (HEIGHT / 2) - new_length))

            # hw1.setColor(cast_rays[i].getColor())
            # hw2.setColor(cast_rays[i].getColor())
            hw1.setColor(color)
            hw2.setColor(color)

            hw1.setWidth(int(padding))
            hw2.setWidth(int(padding))

            hw2.draw(screen)
            hw1.draw(screen)

    def calc_dist_color(self, col, l):
        c = []
        for i in range(len(col)):
            c.append(col[i] - (l / self.light_dist) * col[i])
            if c[i] < 0:
                c[i] = 0
        return c

    def move(self, keys):
        if keys[pygame.K_e]:
            if self.rays_cast_rotation_angle < 360:
                self.rays_cast_rotation_angle = self.rays_cast_rotation_angle + self.rotation_amount
            if self.rays_cast_rotation_angle > 359:
                self.rays_cast_rotation_angle = 0
        if keys[pygame.K_q]:
            if self.rays_cast_rotation_angle < 1:
                self.rays_cast_rotation_angle = 360
            if self.rays_cast_rotation_angle > 0:
                self.rays_cast_rotation_angle = self.rays_cast_rotation_angle - self.rotation_amount
        if keys[pygame.K_w]:
            p1 = self.current_position
            x = (p1[0] + (self.move_amount * math.cos(d * self.center_cone_index)))
            y = (p1[1] + (self.move_amount * math.sin(d * self.center_cone_index)))
            p2 = x, y
            self.current_position = p2
            return
        if keys[pygame.K_a]:
            p1 = self.current_position
            x = (p1[0] - (self.move_amount * math.cos(d * self.strafe_cone_index)))
            y = (p1[1] - (self.move_amount * math.sin(d * self.strafe_cone_index)))
            p2 = x, y
            self.current_position = p2
            return
        if keys[pygame.K_s]:
            p1 = self.current_position
            x = (p1[0] - (self.move_amount * math.cos(d * self.center_cone_index)))
            y = (p1[1] - (self.move_amount * math.sin(d * self.center_cone_index)))
            p2 = x, y
            self.current_position = p2
            return
        if keys[pygame.K_d]:
            p1 = self.current_position
            x = (p1[0] + (self.move_amount * math.cos(d * self.strafe_cone_index)))
            y = (p1[1] + (self.move_amount * math.sin(d * self.strafe_cone_index)))
            p2 = x, y
            self.current_position = p2
            return

    def get_fov_ray(self):
        # TODO: might be issue with not checking for end index being smaller than start index
        start_ray = self.rays[self.rays_cast_index_start]
        end_ray = self.rays[self.rays_cast_index_end]
        camera_distance = 100
        x1 = start_ray.getP1()[0] + (camera_distance * math.cos(d * self.rays_cast_index_start))
        y1 = start_ray.getP1()[1] + (camera_distance * math.sin(d * self.rays_cast_index_start))
        x2 = end_ray.getP1()[0] + (camera_distance * math.cos(d * self.rays_cast_index_end))
        y2 = end_ray.getP1()[1] + (camera_distance * math.sin(d * self.rays_cast_index_end))
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
        p0 = wall.getP1()
        p1 = wall.getP2()
        p2 = ray.getP1()
        p3 = ray.getP2()

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
                    ray.setColor(wall.getColor())
                    ray.setP2(p2)

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
