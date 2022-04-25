from random import randint

import pygame
import math

# IDEA: Grayscale unless color is majority red

WIDTH = 1920
HEIGHT = 1080
# Field of the camera's view
FOV = 130 * (math.pi / 180)
# Width of each line drawn to the screen
RES_SCALE = 5
# Number of rays in fov_cone scale based on size of window
RAY_COUNT = int((WIDTH / (FOV / (360 * (math.pi/180)))) / RES_SCALE)
# Amount the user rotates their fov
ROTATION_UNITS = 2 * (math.pi / 180)
# Amount the user moves in the world
MOVE_UNITS = 5
# Default of each ray (View Distance)
GR = math.sqrt(math.pow(HEIGHT, 2) + math.pow(WIDTH, 2))
# Distance till light = 0
LIGHT_DIST = GR
# CAMERA_PLANE_DIST = math.fabs((WIDTH / 2) / math.tan((FOV * 180/math.pi) / 2))
CAMERA_PLANE_DIST = (WIDTH/2) / (math.tan(FOV/2))

WALL_HEIGHT = 1000

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
    def __init__(self, p1, p2, color, rd):
        self.p1 = p1
        self.p2 = p2
        self.width = 1
        self.color = color
        # Rotation amount from 0 ray
        self.rd = rd

    def get_length(self):
        return math.sqrt(math.pow(self.p2[0] - self.p1[0], 2) + math.pow(self.p2[1] - self.p1[1], 2))

    def get_rd(self):
        return self.rd

    def set_rd(self, rd):
        self.rd = rd

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
    def __init__(self):
        self.current_position = WIDTH / 2, 10
        self.walls = []
        self.all_rays = []
        # All rays that are to be displayed
        self.display_rays = []
        self.camera_plane = Line((0, 0), (0, 0), colors["RED"], 0)
        self.gen_walls()
        self.gen_rays()

        # All rays that are located inside the FOV cone
        self.cone_rays = []
        # All rays inside the FOV cone adjusted for camera plane
        self.camera_rays = []
        self.rotation_delta = (90 * (math.pi / 180)) - (FOV/2)
        self.fov_lower = self.rotation_delta
        self.fov_upper = self.rotation_delta + FOV

        p1 = self.current_position
        x = (p1[0] + (GR * math.cos(self.rotation_delta + (FOV / 2))))
        y = (p1[1] + (GR * math.sin(self.rotation_delta + (FOV / 2))))
        self.fov_center_ray = Line(p1, (x, y), colors["WHITE"], 0)

        self.update_cone()
        self.update_camera_plane()

    def gen_walls(self):
        wall_width = 5
        for i in range(4):
            c = rand_color()
            p1 = (i - 0) * (i - 3) * ((WIDTH / 2) * (i - 2) + (WIDTH / -2) * (i - 1)), \
                 (i - 0) * (i - 1) * ((HEIGHT / -2) * (i - 3) + (HEIGHT / 6) * (i - 2))
            p2 = (i - 2) * (i - 3) * ((WIDTH / -6) * (i - 1) + (WIDTH / 2) * (i - 0)), \
                 (i - 0) * (i - 3) * ((HEIGHT / 2) * (i - 2) + (HEIGHT / -2) * (i - 1))
            w = Line(p1, p2, c, 0)
            w.set_width(wall_width)
            self.walls.append(w)

    def gen_rays(self):
        rad_slice = (360.0 / RAY_COUNT) * (math.pi / 180)
        p1 = self.current_position
        for i in range(RAY_COUNT):
            x = (p1[0] + (GR * math.cos(rad_slice * i)))
            y = (p1[1] + (GR * math.sin(rad_slice * i)))
            p2 = x, y
            ray = Line(p1, p2, colors["WHITE"], (rad_slice * i))
            self.all_rays.append(ray)

    def update_rays(self):
        rad_slice = (360.0 / RAY_COUNT) * (math.pi / 180)
        p1 = self.current_position
        for i in range(RAY_COUNT):
            x = (p1[0] + (GR * math.cos(rad_slice * i)))
            y = (p1[1] + (GR * math.sin(rad_slice * i)))
            p2 = x, y
            self.all_rays[i].set_p1(p1)
            self.all_rays[i].set_p2(p2)

    def update_cone(self):
        self.cone_rays.clear()
        self.fov_lower = self.rotation_delta

        self.fov_upper = self.rotation_delta + FOV
        if self.fov_upper > (360 * (math.pi/180)):
            self.fov_upper = (self.rotation_delta + FOV) - (360 * (math.pi/180))

        p1 = self.current_position
        x = p1[0] + (GR * math.cos((FOV / 2) + self.rotation_delta))
        y = p1[1] + (GR * math.sin((FOV / 2) + self.rotation_delta))
        self.fov_center_ray.set_rd((FOV / 2) + self.rotation_delta)
        self.fov_center_ray.set_p2((x, y))
        self.fov_center_ray.set_p1(self.current_position)

        if self.fov_upper > self.fov_lower:
            for i in range(RAY_COUNT):
                rd = self.all_rays[i].get_rd()
                if self.fov_lower <= rd <= self.fov_upper:
                    self.cone_rays.append(self.all_rays[i])
        if self.fov_lower > self.fov_upper:
            for i in range(RAY_COUNT):
                rd = self.all_rays[i].get_rd()
                if self.fov_lower < rd < (360 * (math.pi / 180)):
                    self.cone_rays.append(self.all_rays[i])
            for i in range(RAY_COUNT):
                rd = self.all_rays[i].get_rd()
                if rd < self.fov_lower and rd < self.fov_upper:
                    self.cone_rays.append(self.all_rays[i])

    def update_camera_plane(self):
        r1 = self.cone_rays[0]
        r2 = self.cone_rays[len(self.cone_rays) - 1]

        x1 = self.current_position[0] + (CAMERA_PLANE_DIST * math.cos(r1.get_rd()))
        y1 = self.current_position[1] + (CAMERA_PLANE_DIST * math.sin(r1.get_rd()))

        x2 = self.current_position[0] + (CAMERA_PLANE_DIST * math.cos(r2.get_rd()))
        y2 = self.current_position[1] + (CAMERA_PLANE_DIST * math.sin(r2.get_rd()))

        p1 = x1, y1
        p2 = x2, y2

        # print("----------------------------------------------------------------------------------")
        #
        # print("Angles: ", r1.get_rd() * 180 / math.pi, r2.get_rd() * 180 / math.pi)
        #
        # print("Plane Dist: ", CAMERA_PLANE_DIST)
        #
        # print("Current Pos: ", r1.get_p1()[0], r1.get_p1()[1], r2.get_p1()[0], r2.get_p1()[1])
        #
        # print("FOV____ Pos: ", x1, y1, x2, y2)

        self.camera_plane = Line(p1, p2, colors["RED"], 0)

    def update_camera(self):
        # self.camera_rays = self.cone_rays.copy()
        self.camera_rays.clear()
        camera_plane_center = self.intersect(self.camera_plane, self.fov_center_ray)
        # print("-----------------------------------")
        # print(math.degrees(self.cone_rays[0].get_rd()))
        for i in range(len(self.cone_rays)):
            # angle from the fov center ray that intersects the camera plane at an even interval (110)

            theta = math.atan(((self.camera_plane.get_length()/len(self.cone_rays)) * (i - ((len(self.cone_rays)-1)/2)))/CAMERA_PLANE_DIST)
            print(math.degrees(theta))
            # print(theta * 180/math.pi)
            p1 = self.current_position
            x = p1[0] + (GR * math.cos(self.fov_center_ray.get_rd() + theta))
            y = p1[1] + (GR * math.sin(self.fov_center_ray.get_rd() + theta))
            p2 = x, y
            self.camera_rays.append(Line(p1, p2, self.cone_rays[i].get_color(), self.fov_center_ray.get_rd() + theta))
        # print(len(self.camera_rays))

        # Project rays at even intervals on the plane and  display these rays
        # TODO: THIS IS WRONG, somehow? idk what the answer to this crap is
        # self.display_rays.clear()
        # for i in range(len(self.camera_rays)):
        #     p1 = self.intersect(self.camera_rays[i], self.camera_plane)
        #     # draw line parallel to center_cone_ray from collision point with camera plane
        #     x = p1[0] + (GR * math.cos((FOV / 2) + self.rotation_delta))
        #     y = p1[1] + (GR * math.sin((FOV / 2) + self.rotation_delta))
        #     p2 = x, y
        #     ray = Line(p1, p2, self.camera_rays[i].get_color(), self.camera_rays[i].get_rd())
        #     self.display_rays.append(ray)


    def update(self):
        # print(len(self.cone_rays), ", ", len(self.all_rays))
        self.update_rays()
        self.update_cone()
        self.update_camera_plane()
        self.update_camera()
        # self.check_collisions(self.display_rays)
        self.check_collisions(self.camera_rays)

    def draw(self, screen):
        displayed_rays = self.camera_rays.copy()
        padding = WIDTH/len(displayed_rays)
        screen.fill(colors["BLACK"])
        pygame.draw.rect(screen, (100, 100, 100), ((0, 0), (WIDTH, HEIGHT/2)))
        pygame.draw.rect(screen, (75, 75, 75), ((0, HEIGHT/2), (WIDTH, HEIGHT)))

        for i in range(len(displayed_rays)):
            hw1 = Line((0, 0), (0, 0), colors["BLACK"], 0)
            hw2 = Line((0, 0), (0, 0), colors["BLACK"], 0)

            length = displayed_rays[i].get_length()
            correct_distance = length * math.cos(math.fabs(displayed_rays[i].get_rd() - self.fov_center_ray.get_rd()))
            color = self.depth_shader(displayed_rays[i].get_color(), length)

            distance_to_projection_plane = CAMERA_PLANE_DIST
            distance_to_slice = length * math.cos(math.fabs(displayed_rays[i].get_rd() - self.fov_center_ray.get_rd()))
            # THIS LITERALLY TOOK LIKE 8 HOURS TO REALIZE I HAD THIS EQUATION WRONG
            # https://permadi.com/1996/05/ray-casting-tutorial-9/
            projected_slice_height = (WALL_HEIGHT / distance_to_slice) * distance_to_projection_plane

            hw1.set_p1((i * padding, HEIGHT / 2))
            hw1.set_p2((i * padding, (HEIGHT / 2) + projected_slice_height / 2))

            hw2.set_p1((i * padding, HEIGHT / 2))
            hw2.set_p2((i * padding, (HEIGHT / 2) - projected_slice_height / 2))

            hw1.set_color(color)
            hw2.set_color(color)

            hw1.set_width(int(padding + 1))
            hw2.set_width(int(padding + 1))

            hw1.draw(screen)
            hw2.draw(screen)

        # for ray in displayed_rays:
        #     ray.draw(screen)
        # for wall in self.walls:
        #     wall.draw(screen)
        # self.camera_plane.draw(screen)

    def depth_shader(self, col, l):
        c = []
        for i in range(len(col)):
            c.append(col[i] - (l / LIGHT_DIST) * col[i])
            if c[i] < 0:
                c[i] = 0
        return c

    def move(self, keys):
        if keys[pygame.K_e]:
            if self.rotation_delta < (360 * (math.pi/180)):
                self.rotation_delta = self.rotation_delta + ROTATION_UNITS
            if self.rotation_delta > (359 * (math.pi/180)):
                self.rotation_delta = 0
        if keys[pygame.K_q]:
            if self.rotation_delta < (1 * (math.pi/180)):
                self.rotation_delta = (360 * (math.pi/180))
            if self.rotation_delta > (0 * (math.pi/180)):
                self.rotation_delta = self.rotation_delta - ROTATION_UNITS
        if keys[pygame.K_w]:
            p1 = self.current_position
            x = (p1[0] + (MOVE_UNITS * math.cos(self.rotation_delta + (FOV / 2))))
            y = (p1[1] + (MOVE_UNITS * math.sin(self.rotation_delta + (FOV / 2))))
            p2 = x, y
            self.current_position = p2
        if keys[pygame.K_a]:
            p1 = self.current_position
            x = (p1[0] - (MOVE_UNITS * math.cos(self.rotation_delta + (FOV / 2) + (90 * (math.pi / 180)))))
            y = (p1[1] - (MOVE_UNITS * math.sin(self.rotation_delta + (FOV / 2) + (90 * (math.pi / 180)))))
            p2 = x, y
            self.current_position = p2
        if keys[pygame.K_s]:
            p1 = self.current_position
            x = (p1[0] - (MOVE_UNITS * math.cos(self.rotation_delta + (FOV / 2))))
            y = (p1[1] - (MOVE_UNITS * math.sin(self.rotation_delta + (FOV / 2))))
            p2 = x, y
            self.current_position = p2
        if keys[pygame.K_d]:
            p1 = self.current_position
            x = (p1[0] + (MOVE_UNITS * math.cos(self.rotation_delta + (FOV / 2) + (90 * (math.pi / 180)))))
            y = (p1[1] + (MOVE_UNITS * math.sin(self.rotation_delta + (FOV / 2) + (90 * (math.pi / 180)))))
            p2 = x, y
            self.current_position = p2
        if keys[pygame.K_ESCAPE]:
            return False
        return True

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

    def check_collisions(self, rays):
        for ray in rays:
            for wall in self.walls:
                p2 = self.intersect(wall, ray)
                if p2 is not None:
                    ray.set_color(wall.get_color())
                    ray.set_p2(p2)

    def add_wall(self, wall):
        self.walls.append(wall)


class Display:

    def __init__(self):
        pygame.init()
        self.image = pygame.Surface((WIDTH, HEIGHT))
        self.image.fill((0, 101, 103))
        self.react = self.image.get_rect()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)

    def update(self):
        pygame.display.flip()

    def get_screen(self):
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
            keys = pygame.key.get_pressed()
            self.running = self.engine.move(keys)
            # Look through all events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    ps.append(pygame.mouse.get_pos())
                    if len(ps) > 1:
                        self.engine.add_wall(Line(ps[0], ps[1], rand_color(), 0))
                        ps.clear()

            # Update rays
            self.engine.update()
            self.engine.draw(self.display.get_screen())

            self.display.update()

            # Tick the clock
            self.clock.tick(60)
        pygame.quit()


game = Game()
