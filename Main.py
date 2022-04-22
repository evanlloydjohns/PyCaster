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
    "WHITE": (255, 255, 255)
}

# Total number of rays
RAY_COUNT = 250

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
    walls = []
    rays = []

    def __init__(self):
        # Initialize walls list
        self.genWalls()

        # Initialize rays list
        p1 = pygame.mouse.get_pos()
        for i in range(RAY_COUNT):
            x = (p1[0] + (GR * math.cos(d * i)))
            y = (p1[1] + (GR * math.sin(d * i)))
            p2 = x, y
            ray = Line(p1, p2, colors["WHITE"])
            self.rays.append(ray)

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
        p1 = pygame.mouse.get_pos()
        for i in range(RAY_COUNT):
            x = (p1[0] + (GR * math.cos(d * i)))
            y = (p1[1] + (GR * math.sin(d * i)))
            p2 = x, y
            self.rays[i].setP1(p1)
            self.rays[i].setP2(p2)

    # Draw all rays and walls to the screen
    def draw(self, screen):
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
