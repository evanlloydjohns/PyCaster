import configparser
import math
import pygame

import geometry


def rand_color():
    return 100, 100, 100
    # randint(0, 255), randint(0, 255), randint(0, 255)


class Engine:
    def __init__(self, width, height, wall_height):
        # initialize the config parsers
        config = configparser.ConfigParser()
        config.read('settings.ini')
        en_config = config['ENGINE']

        # Get engine settings from settings.ini
        self.width = width
        self.height = height

        # The field of view / angle of the view cone
        self.fov = int(en_config['fov']) * (math.pi / 180)

        # Scale of projected line width, 1 = projected line width of 1
        self.resolution_scale = int(en_config['resolutionScale'])

        # Total number of rays
        self.ray_count = int((self.width / (self.fov / (360 * (math.pi / 180)))) / self.resolution_scale)

        # Degrees the camera turns
        self.rotation_units = int(en_config['rotationUnits']) * (math.pi / 180)

        # Pixels the camera moves
        self.movement_units = float(en_config['movementUnits'])

        # Total length of each ray cast
        self.view_radius = int(en_config['viewDistance'])
        # math.sqrt(math.pow(self.height, 2) + math.pow(self.width, 2))

        # Maximum distance which depth is calculated
        self.lighting_distance = int(en_config['lightDistance'])

        # Distance the camera plane is from the center
        self.camera_plane_distance = (self.width / 2) / (math.tan(self.fov / 2))

        # Height scalar of each projected wall
        self.wall_height = wall_height

        # Sprint scalar applied when holding shift
        self.sprint_scalar = float(en_config['sprintScalar'])

        # Current position of the camera
        self.current_position = (0, 0)

        # Current height of the camera
        self.current_height = 0

        # Dictionary containing all lists of walls
        self.walls = {}

        # List of all rays cast from the camera
        self.all_rays = []

        # Plane from which serves as the origin point for all displayed rays
        self.camera_plane = geometry.Line((0, 0), (0, 0))

        # Current amount sprint is being applied
        self.sprint_mod = 0

        # Generate all
        self.gen_rays()

        # All rays that are located inside the fov cone
        self.cone_rays = []

        # All rays inside the fov cone, with origins adjusted for the camera plane
        self.camera_rays = []

        # Angle each ray is separated from the previous ray
        self.rotation_delta = (90 * (math.pi / 180)) - (self.fov/2)

        # Angle the fov cone starts at
        self.fov_lower = self.rotation_delta

        # Angle the fov cone ends at
        self.fov_upper = self.rotation_delta + self.fov

        # Calculate center ray of the fov cone
        p1 = self.current_position
        x = (p1[0] + (self.view_radius * math.cos(self.rotation_delta + (self.fov / 2))))
        y = (p1[1] + (self.view_radius * math.sin(self.rotation_delta + (self.fov / 2))))
        self.fov_center_ray = geometry.Ray(p1, (x, y), (255, 255, 255), 0)

        # Update the fov cone
        self.update_cone()

        # Update the current location of the camera plane relative to the camera
        self.update_camera_plane()

    def gen_rays(self):
        rad_slice = (360.0 / self.ray_count) * (math.pi / 180)
        p1 = self.current_position
        for i in range(self.ray_count):
            x = (p1[0] + (self.view_radius * math.cos(rad_slice * i)))
            y = (p1[1] + (self.view_radius * math.sin(rad_slice * i)))
            p2 = x, y
            ray = geometry.Ray(p1, p2, (255, 255, 255), (rad_slice * i))
            self.all_rays.append(ray)

    def update_rays(self):
        rad_slice = (360.0 / self.ray_count) * (math.pi / 180)
        p1 = self.current_position
        for i in range(self.ray_count):
            x = (p1[0] + (self.view_radius * math.cos(rad_slice * i)))
            y = (p1[1] + (self.view_radius * math.sin(rad_slice * i)))
            p2 = x, y
            self.all_rays[i].set_p1(p1)
            self.all_rays[i].set_p2(p2)

    def update_cone(self):
        self.cone_rays.clear()
        self.fov_lower = self.rotation_delta
        self.fov_upper = self.rotation_delta + self.fov

        # Account for loop-back on upper bound of fov cone
        if self.fov_upper > (360 * (math.pi/180)):
            self.fov_upper = (self.rotation_delta + self.fov) - (360 * (math.pi/180))

        # Update center ray of the fov cone
        p1 = self.current_position
        x = p1[0] + (self.view_radius * math.cos((self.fov / 2) + self.rotation_delta))
        y = p1[1] + (self.view_radius * math.sin((self.fov / 2) + self.rotation_delta))
        self.fov_center_ray.set_rd((self.fov / 2) + self.rotation_delta)
        self.fov_center_ray.set_p2((x, y))
        self.fov_center_ray.set_p1(self.current_position)

        if self.fov_upper > self.fov_lower:
            for i in range(self.ray_count):
                rd = self.all_rays[i].get_rd()
                if self.fov_lower <= rd <= self.fov_upper:
                    self.cone_rays.append(self.all_rays[i])
        if self.fov_lower > self.fov_upper:
            for i in range(self.ray_count):
                rd = self.all_rays[i].get_rd()
                if self.fov_lower < rd < (360 * (math.pi / 180)):
                    self.cone_rays.append(self.all_rays[i])
            for i in range(self.ray_count):
                rd = self.all_rays[i].get_rd()
                if rd < self.fov_lower and rd < self.fov_upper:
                    self.cone_rays.append(self.all_rays[i])

    def update_camera_plane(self):
        r1 = self.cone_rays[0]
        r2 = self.cone_rays[len(self.cone_rays) - 1]

        x1 = self.current_position[0] + (self.camera_plane_distance * math.cos(r1.get_rd()))
        y1 = self.current_position[1] + (self.camera_plane_distance * math.sin(r1.get_rd()))

        x2 = self.current_position[0] + (self.camera_plane_distance * math.cos(r2.get_rd()))
        y2 = self.current_position[1] + (self.camera_plane_distance * math.sin(r2.get_rd()))

        p1 = x1, y1
        p2 = x2, y2

        self.camera_plane = geometry.Line(p1, p2)

    def update_camera(self):
        # In order to prevent a pseudo fish-eye effect, we need to account for the
        # angle which the rays are cast from. We do this by shifting the origin of
        # each ray to an even interval along the camera plane. You can think of
        # the camera plane as the window you are viewing the ray caster from.
        self.camera_rays.clear()
        for i in range(len(self.cone_rays)):
            # Theta = angle from the fov center ray that intersects the camera plane at an even interval
            theta = math.atan(((geometry.length(self.camera_plane)/len(self.cone_rays)) *
                               (i - ((len(self.cone_rays)-1)/2)))/self.camera_plane_distance)
            p1 = self.current_position
            x = p1[0] + (self.view_radius * math.cos(self.fov_center_ray.get_rd() + theta))
            y = p1[1] + (self.view_radius * math.sin(self.fov_center_ray.get_rd() + theta))
            p2 = x, y
            self.camera_rays.append(geometry.Ray(p1, p2, self.cone_rays[i].get_color(),
                                                 self.fov_center_ray.get_rd() + theta))

    def update(self):
        # Updates all rays to current position
        self.update_rays()
        # Updates the set of rays withing to fov cone
        self.update_cone()
        # Updates the plane in which rays will be project onto [DEPRECIATED]
        self.update_camera_plane()
        # Updates rays for their projection and saves them in a list [DEPRECIATED]
        self.update_camera()
        # Checks collisions with projected rays and walls
        self.check_collisions(self.camera_rays)

    def get_center_ray(self):
        length = len(self.camera_rays)
        mid = round(length / 2)
        return self.camera_rays[mid]

    def get_facing_wall(self):
        length = len(self.camera_rays)
        mid = round(length / 2)
        center_ray = self.camera_rays[mid]
        for k in self.walls:
            for wall in self.walls[k]:
                p2 = geometry.intersect(wall, center_ray)
                if p2 is not None:
                    wall.set_selected(True)
                else:
                    wall.set_selected(False)

    def remove_facing_wall(self):
        length = len(self.camera_rays)
        mid = round(length / 2)
        center_ray = self.camera_rays[mid]
        for k in self.walls:
            for wall in self.walls[k]:
                if geometry.intersect(wall, center_ray) is not None:
                    self.walls[k].remove(wall)

    # Creates frame of the current scene
    def generate_snapshot(self):
        # List of all finalized slices (line on screen)
        self.get_facing_wall()

        display_buffer = []
        rays = self.camera_rays.copy()

        # Padding between each slice
        padding = self.width/len(rays)

        for i in range(len(rays)):
            # Top and bottom halves of the slice
            hw1 = geometry.Wall((0, 0), (0, 0), (0, 0, 0))
            hw2 = geometry.Wall((0, 0), (0, 0), (0, 0, 0))

            ray = rays[i]

            length = geometry.length(rays[i])
            color = self.depth_shader(rays[i].get_color(), length)

            # Weird math stuff I can't remember
            distance_to_projection_plane = self.camera_plane_distance
            distance_to_slice = length * math.cos(math.fabs(rays[i].get_rd() - self.fov_center_ray.get_rd()))
            # THIS LITERALLY TOOK LIKE 8 HOURS TO REALIZE I HAD THIS EQUATION WRONG
            # https://permadi.com/1996/05/ray-casting-tutorial-9/

            # Prevent division by zero when close to slice
            if distance_to_slice < 1:
                distance_to_slice = 1
            projected_slice_height = (self.wall_height / distance_to_slice) * distance_to_projection_plane

            hw1.set_p1((i * padding, self.height / 2))
            hw1.set_p2((i * padding, (self.height / 2) + projected_slice_height / 2))

            hw2.set_p1((i * padding, self.height / 2))
            hw2.set_p2((i * padding, (self.height / 2) - projected_slice_height / 2))

            hw1.set_color(color)
            hw2.set_color(color)

            hw1.set_width(int(padding + 1))
            hw2.set_width(int(padding + 1))

            # Add finalized walls to
            display_buffer.append((hw1, hw2))

        return display_buffer

    def debug(self):
        return self.camera_rays

    def depth_shader(self, col, length):
        d = 0
        c = [col[0] - ((col[0] - d) * math.log(length + 1) / math.log(self.lighting_distance + 1)),
             col[1] - ((col[1] - d) * math.log(length + 1) / math.log(self.lighting_distance + 1)),
             col[2] - ((col[2] - d) * math.log(length + 1) / math.log(self.lighting_distance + 1))]
        for i in range(len(col)):
            if c[i] < 0:
                c[i] = 0
        return c

    def move(self, keys):
        if keys[pygame.K_LSHIFT]:
            self.sprint_mod = self.sprint_scalar * self.movement_units
        else:
            self.sprint_mod = 0
        if keys[pygame.K_UP]:
            self.current_height += 0.03
        if keys[pygame.K_DOWN]:
            self.current_height -= 0.03
        if keys[pygame.K_e]:
            if self.rotation_delta < (360 * (math.pi/180)):
                self.rotation_delta = self.rotation_delta + self.rotation_units
            if self.rotation_delta > (359 * (math.pi/180)):
                self.rotation_delta = 0
        if keys[pygame.K_q]:
            if self.rotation_delta < (1 * (math.pi/180)):
                self.rotation_delta = (360 * (math.pi/180))
            if self.rotation_delta > (0 * (math.pi/180)):
                self.rotation_delta = self.rotation_delta - self.rotation_units
        if keys[pygame.K_w]:
            p1 = self.current_position
            x = (p1[0] + ((self.movement_units + self.sprint_mod) * math.cos(self.rotation_delta + (self.fov / 2))))
            y = (p1[1] + ((self.movement_units + self.sprint_mod) * math.sin(self.rotation_delta + (self.fov / 2))))
            p2 = x, y
            self.current_position = p2
        if keys[pygame.K_a]:
            p1 = self.current_position
            x = (p1[0] - ((self.movement_units + self.sprint_mod) * math.cos(self.rotation_delta + (self.fov / 2) +
                                                                             (90 * (math.pi / 180)))))
            y = (p1[1] - ((self.movement_units + self.sprint_mod) * math.sin(self.rotation_delta + (self.fov / 2) +
                                                                             (90 * (math.pi / 180)))))
            p2 = x, y
            self.current_position = p2
        if keys[pygame.K_s]:
            p1 = self.current_position
            x = (p1[0] - ((self.movement_units + self.sprint_mod) * math.cos(self.rotation_delta + (self.fov / 2))))
            y = (p1[1] - ((self.movement_units + self.sprint_mod) * math.sin(self.rotation_delta + (self.fov / 2))))
            p2 = x, y
            self.current_position = p2
        if keys[pygame.K_d]:
            p1 = self.current_position
            x = (p1[0] + ((self.movement_units + self.sprint_mod) * math.cos(self.rotation_delta + (self.fov / 2) +
                                                                             (90 * (math.pi / 180)))))
            y = (p1[1] + ((self.movement_units + self.sprint_mod) * math.sin(self.rotation_delta + (self.fov / 2) +
                                                                             (90 * (math.pi / 180)))))
            p2 = x, y
            self.current_position = p2
        if keys[pygame.K_ESCAPE]:
            return False
        return True

    def color_wall(self):
        for k in self.walls:
            for wall in self.walls[k]:
                if wall.get_selected():
                    wall.set_color((255, 0, 0))

    def rotate(self, delta):
        delta = delta / 360
        if delta > 0:
            if self.rotation_delta < (360 * (math.pi / 180)):
                self.rotation_delta = self.rotation_delta + delta
            if self.rotation_delta > (359 * (math.pi / 180)):
                self.rotation_delta = 0
        if delta < 0:
            if self.rotation_delta < (1 * (math.pi / 180)):
                self.rotation_delta = (360 * (math.pi / 180))
            if self.rotation_delta > (0 * (math.pi / 180)):
                self.rotation_delta = self.rotation_delta + delta

    def check_collisions(self, rays):
        for ray in rays:
            for k in self.walls:
                # TODO: work on adding col point stuff

                for wall in self.walls[k]:
                    p2 = geometry.intersect(wall, ray)
                    if p2 is not None:
                        ray.set_color(wall.get_color())
                        ray.set_p2(p2)
                        wall.add_col_point(p2)

    # Updates a list of walls in the dict. WILL REPLACE THE WALLS
    def change_walls(self, key, walls):
        self.walls[key] = walls

    # Adds a list of walls to the dict. DOES NOT REPLACE
    def add_walls(self, key, walls):
        if key in self.walls:
            temp = self.walls[key]
            for wall in walls:
                temp.append(wall)
            self.walls[key] = temp
        else:
            self.walls[key] = walls

    def remove_wall_group(self, key):
        self.walls.pop(key)

    def set_cur_position(self, current_position):
        self.current_position = current_position

    def get_cur_position(self):
        return self.current_position
