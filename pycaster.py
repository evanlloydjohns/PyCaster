from random import randint

import configparser
import math
import pygame

import geometry


def rand_color():
    return randint(0, 255), randint(0, 255), randint(0, 255)


# TODO: Add config for variable graphics modules (maybe class that handles controls depending on module)
class Engine:
    def __init__(self, width, height, wall_height, current_position):
        # initialize the config parsers
        config = configparser.ConfigParser()
        config.read('settings.ini')
        en_config = config['ENGINE']
        mo_config = config['MOVEMENT']

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
        self.rotation_units = int(mo_config['rotationUnits']) * (math.pi / 180)

        # Pixels the camera moves
        self.movement_units = float(mo_config['movementUnits'])

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
        self.sprint_scalar = float(mo_config['sprintScalar'])

        # Looking Sensitivity
        self.mouse_sensitivity = float(mo_config['mouseSensitivity'])

        # Current position of the camera
        self.current_position = current_position

        # Current height of the camera
        self.current_height = 0

        # Dictionary containing all lists of walls
        # We store each grouping of walls in a dictionary so that we can differentiate what walls belong to
        # what processes. The initial group of walls is called "Default". If we want to add more groups, we just
        # create a new group name and add them to the dictionary. This gives us the ability to potentially store
        # other types of objects in the future, and to be able to handle them differently depending on their key/tag
        self.walls = {}

        # Dictionary containing all lists of circles
        self.circles = {}

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
        self.rotation_delta = (90 * (math.pi / 180)) - (self.fov / 2)

        # Angle the fov cone starts at
        self.fov_lower = self.rotation_delta

        # Angle the fov cone ends at
        self.fov_upper = self.rotation_delta + self.fov

        # Calculate center ray of the fov cone
        p1 = self.current_position
        x = (p1[0] + (self.view_radius * math.cos(self.rotation_delta + (self.fov / 2))))
        y = (p1[1] + (self.view_radius * math.sin(self.rotation_delta + (self.fov / 2))))
        self.fov_center_ray = geometry.Ray(p1, (x, y), (255, 255, 255), 0)

        # Used for looking up the appropriate action for a key press
        self.movements = {
            pygame.K_a: self.move_left,
            pygame.K_d: self.move_right,
            pygame.K_s: self.move_backward,
            pygame.K_w: self.move_forward,
            pygame.K_q: self.rotate_left,
            pygame.K_e: self.rotate_right
        }

        # Update the fov cone
        self.update_cone()

        # Update the current location of the camera plane relative to the camera
        self.update_camera_plane()

        # Color of distance fog
        self.fog_color = (63, 63, 63)

    def get_pos(self):
        return self.current_position

    # Initializes all the rays
    def gen_rays(self):
        rad_slice = (360.0 / self.ray_count) * (math.pi / 180)
        p1 = self.current_position
        for i in range(self.ray_count):
            x = (p1[0] + (self.view_radius * math.cos(rad_slice * i)))
            y = (p1[1] + (self.view_radius * math.sin(rad_slice * i)))
            p2 = x, y
            ray = geometry.Ray(p1, p2, (255, 255, 255), (rad_slice * i))
            self.all_rays.append(ray)

    # Updates all ray origin locations to current position
    def update_rays(self):
        rad_slice = (360.0 / self.ray_count) * (math.pi / 180)
        p1 = self.current_position
        for i in range(self.ray_count):
            x = (p1[0] + (self.view_radius * math.cos(rad_slice * i)))
            y = (p1[1] + (self.view_radius * math.sin(rad_slice * i)))
            p2 = x, y
            self.all_rays[i].set_p1(p1)
            self.all_rays[i].set_p2(p2)

    # Updates what rays are included in our FoV cone
    def update_cone(self):
        self.cone_rays.clear()
        self.fov_lower = self.rotation_delta
        self.fov_upper = self.rotation_delta + self.fov

        # Account for loop-back on upper bound of fov cone
        if self.fov_upper > (360 * (math.pi / 180)):
            self.fov_upper = (self.rotation_delta + self.fov) - (360 * (math.pi / 180))

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

    # Updates the plane to which we are rendering the rays from (can't render from a single point, need to use plane)
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

    # Updates the angle each ray is cast at from the camera plane
    def update_camera(self):
        # In order to prevent a pseudo fish-eye effect, we need to account for the
        # angle which the rays are cast from. We do this by shifting the origin of
        # each ray to an even interval along the camera plane. You can think of
        # the camera plane as the window you are viewing the ray caster from.
        self.camera_rays.clear()
        for i in range(len(self.cone_rays)):
            # Theta = angle from the fov center ray that intersects the camera plane at an even interval
            theta = math.atan(((geometry.length(self.camera_plane) / len(self.cone_rays)) *
                               (i - ((len(self.cone_rays) - 1) / 2))) / self.camera_plane_distance)
            p1 = self.current_position
            x = p1[0] + (self.view_radius * math.cos(self.fov_center_ray.get_rd() + theta))
            y = p1[1] + (self.view_radius * math.sin(self.fov_center_ray.get_rd() + theta))
            p2 = x, y
            self.camera_rays.append(geometry.Ray(p1, p2, self.cone_rays[i].get_color(),
                                                 self.fov_center_ray.get_rd() + theta))

    # Calls all necessary updates for each cycle
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

    # Returns the ray at the center of the FoV cone
    def get_center_ray(self):
        return self.camera_rays[round(len(self.camera_rays) / 2)]

    # Sets the object we are currently looking at to be selected
    # TODO: Investigate circles having thousands of col_points
    def set_facing_object(self):
        center_ray = self.get_center_ray()
        for k in self.walls:
            for wall in self.walls[k]:
                p2 = geometry.intersect(wall, center_ray)
                if p2 is not None:
                    wall.set_selected(True)
                else:
                    wall.set_selected(False)
        for k in self.circles:
            for circle in self.circles[k]:
                p2 = geometry.circle_line_segment_intersection(circle.get_p1(), circle.get_r(),
                                                               center_ray.get_p1(), center_ray.get_p2())
                if p2 is not None:
                    circle.set_selected(True)
                else:
                    circle.set_selected(False)

    # Returns an instance of the wall currently being looked at
    def get_facing_object(self):
        for k in self.walls:
            for wall in self.walls[k]:
                if wall.get_selected():
                    return wall
        for k in self.circles:
            for circle in self.circles[k]:
                if circle.get_selected():
                    return circle
        return None

    # Deletes the wall we are currently looking at
    def remove_facing_object(self):
        # TODO: Move to process_mouse_buttons()
        self.set_facing_object()
        center_ray = self.get_center_ray()
        for k in self.walls:
            for wall in self.walls[k]:
                if geometry.intersect(wall, center_ray) is not None:
                    self.walls[k].remove(wall)
                    return
        for k in self.circles:
            for circle in self.circles[k]:
                if geometry.circle_line_segment_intersection(circle.get_p1(), circle.get_r(),
                                                             center_ray.get_p1(), center_ray.get_p2()) is not None:
                    self.circles[k].remove(circle)
                    return

    # Returns FrameState object, which contains all information about the
    def generate_frame(self):
        rays = self.camera_rays.copy()

        # Padding between each slice
        padding = self.width / len(rays)

        # Initialize the frame
        frame = FrameState()
        frame.set_segment_width(int(padding + 1))
        segment_count = 0
        for ray in self.camera_rays:
            ray_length = geometry.length(ray)

            # Help with the math: https://permadi.com/1996/05/ray-casting-tutorial-9/
            distance_to_projection_plane = self.camera_plane_distance
            distance_to_segment = max(ray_length * math.cos(math.fabs(ray.get_rd() - self.fov_center_ray.get_rd())), 1)
            projected_segment_height = (self.wall_height / distance_to_segment) * distance_to_projection_plane

            # Create the segment
            seg_p1 = (segment_count * padding, (self.height / 2) - projected_segment_height / 2)
            seg_p2 = (segment_count * padding, (self.height / 2) + projected_segment_height / 2)
            seg_c = self.depth_shader(ray.get_color(), ray_length, aug=self.fog_color)

            # Add segment to frame
            frame.add_segment(Segment(seg_c, seg_p1, seg_p2))
            segment_count += 1
        return frame

    def debug(self):
        return self.camera_rays

    # TODO: Investigate the addition of a radial gradient to simulate a light source from the player location
    # Behold, the epitome of list comprehension
    def depth_shader(self, col, length, aug):
        return [max(aug[i], col[i] - ((col[i] - aug[i]) * math.log(length + 1) / math.log(self.lighting_distance + 1))) for i
                in range(len(col))]

    def process_mouse_movement(self, mouse_pos):
        self.rotate(self.mouse_sensitivity * (mouse_pos[0] - (self.width / 2)) / 360)

    # TODO: Use the buffer swap principle for movement updates
    # Handles all valid key presses
    def process_keys(self, keys):
        # Handle Sprint
        if keys[pygame.K_LSHIFT]:
            self.sprint_mod = self.sprint_scalar * self.movement_units
        else:
            self.sprint_mod = 0
        # Handle closing the game
        if keys[pygame.K_ESCAPE]:
            return False
        # Handle all other keys
        for key in self.movements:
            if keys[key]:
                self.movements[key]()
        # This but list comprehension just for the heck of it
        # [self.movements[k]() if keys[k] else None for k in self.movements]
        return True

    # TODO: Investigate the use of a decorator for the player collision check
    def move_left(self):
        p1 = self.current_position
        x = (p1[0] - ((self.movement_units + self.sprint_mod) *
                      math.cos(self.rotation_delta + (self.fov / 2) + (90 * (math.pi / 180)))))
        y = (p1[1] - ((self.movement_units + self.sprint_mod) *
                      math.sin(self.rotation_delta + (self.fov / 2) + (90 * (math.pi / 180)))))
        p2 = x, y
        self.current_position = self.check_player_collision(p1, p2)

    def move_right(self):
        p1 = self.current_position
        x = (p1[0] + ((self.movement_units + self.sprint_mod) *
                      math.cos(self.rotation_delta + (self.fov / 2) + (90 * (math.pi / 180)))))
        y = (p1[1] + ((self.movement_units + self.sprint_mod) *
                      math.sin(self.rotation_delta + (self.fov / 2) + (90 * (math.pi / 180)))))
        p2 = x, y
        self.current_position = self.check_player_collision(p1, p2)

    def move_forward(self):
        p1 = self.current_position
        x = (p1[0] + ((self.movement_units + self.sprint_mod) * math.cos(self.rotation_delta + (self.fov / 2))))
        y = (p1[1] + ((self.movement_units + self.sprint_mod) * math.sin(self.rotation_delta + (self.fov / 2))))
        p2 = x, y
        self.current_position = self.check_player_collision(p1, p2)

    def move_backward(self):
        p1 = self.current_position
        x = (p1[0] - ((self.movement_units + self.sprint_mod) * math.cos(self.rotation_delta + (self.fov / 2))))
        y = (p1[1] - ((self.movement_units + self.sprint_mod) * math.sin(self.rotation_delta + (self.fov / 2))))
        p2 = x, y
        self.current_position = self.check_player_collision(p1, p2)

    def rotate_left(self):
        self.rotate(-self.rotation_units)

    def rotate_right(self):
        self.rotate(self.rotation_units)

    # Rotates the camera a certain number of degrees
    # TODO: Need to make mouse movement smooth
    def rotate(self, delta):
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

    def check_player_collision(self, cur_pos, new_pos):
        player_line = geometry.Line(cur_pos, new_pos)
        for ray in self.camera_rays:
            wall = ray.get_wall()
            if wall is not None:
                p2 = geometry.intersect(player_line, wall)
                if p2 is not None:
                    # Awful sliding along a wall, just return new_pos if you want to turn this off
                    d_cn = math.dist(cur_pos, new_pos)
                    d_cp = math.dist(cur_pos, p2)
                    x_diff = d_cn - d_cp
                    y_diff = x_diff
                    if cur_pos[0] < new_pos[0]:
                        x_diff *= -1
                    if cur_pos[1] < new_pos[1]:
                        y_diff *= -1
                    np = cur_pos[0] + x_diff, cur_pos[1] + y_diff
                    return np
        return new_pos

    # Changes the color of the currently selected wall
    def color_wall(self, color):
        # TODO: Move to process_mouse_buttons()
        self.set_facing_object()
        facing_wall = self.get_facing_object()
        if facing_wall is not None:
            facing_wall.set_color(color)

    # Checks for collisions between a set of rays and all walls/circles
    def check_collisions(self, rays):
        for ray in rays:
            for k in self.walls:
                for wall in self.walls[k]:
                    p2 = geometry.intersect(wall, ray)
                    if p2 is not None:
                        ray.set_color(wall.get_color())
                        ray.set_p2(p2)
                        ray.set_wall(wall)
                        wall.add_col_point(p2)
            for k in self.circles:
                for c in self.circles[k]:
                    p2 = geometry.circle_line_segment_intersection(c.get_p1(), c.get_r(), ray.get_p1(), ray.get_p2())
                    if p2 is not None:
                        ray.set_color(c.get_color())
                        ray.set_p2(p2)
                        c.add_col_point(p2)

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

    def change_circles(self, key, circles):
        self.circles[key] = circles

    def add_circles(self, key, circles):
        if key in self.circles:
            temp = self.circles[key]
            for circle in circles:
                temp.append(circle)
            self.circles[key] = temp
        else:
            self.circles[key] = circles

    def remove_wall_group(self, key):
        self.walls.pop(key)

    def set_cur_position(self, current_position):
        self.current_position = current_position

    def get_cur_position(self):
        return self.current_position

    def get_world_object_count(self):
        s = 0
        for k in self.walls:
            s += len(self.walls[k])
        for k in self.circles:
            s += len(self.circles[k])
        return s


# A segment represents a vertical slice of the final rendered image
class Segment:
    def __init__(self, color, p1, p2):
        self.color = color
        self.p1 = p1
        self.p2 = p2

    def get_color(self):
        return self.color

    def set_color(self, color):
        self.color = color

    def get_p1(self):
        return self.p1

    def set_p1(self, p1):
        self.p1 = p1

    def get_p2(self):
        return self.p2

    def set_p2(self, p2):
        self.p2 = p2


# Stores the state of each frame generated from the pycaster engine
class FrameState:
    def __init__(self):
        # A list of segments which make up each individual vertical line to be displayed on the screen
        self.segments = []
        # The width of each segment
        self.segment_width = 0

    def get_segments(self):
        return self.segments

    def set_segments(self, segments):
        self.segments = segments

    def add_segment(self, segment):
        self.segments.append(segment)

    def clear_segments(self):
        self.segments.clear()

    def get_segment_width(self):
        return self.segment_width

    def set_segment_width(self, segment_width):
        self.segment_width = segment_width
