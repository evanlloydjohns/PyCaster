from random import randint
import configparser
import math

import pygame
import support
import geometry


def rand_color():
    return randint(0, 255), randint(0, 255), randint(0, 255)


# TODO: Investigate the addition of a radial gradient to simulate a light source from the player location

class Engine:
    def __init__(self, width, height, wall_height, current_position):
        # Get engine settings from settings.ini
        self.width = width
        self.height = height

        # Stores the state of all objects
        self.world_objects = WorldState()

        # Set up the camera for rendering to screen
        self.camera = Camera(current_position, wall_height, width, height)

        self.close_objects = self.world_objects.get_walls_in_range(self.camera.get_position(), self.camera.get_view_radius())

        self.debug_stats = {
            "value": {
                "total_obj_count": self.get_world_state().get_world_object_count(),
                "camera_ray_count": len(self.camera.get_camera_rays()),
                "total_ray_count": self.camera.get_ray_count(),
                "view_angle": round(self.camera.get_rotation_delta() * (180 / math.pi)),
                "view_angle(rads)": self.camera.get_rotation_delta()
            },
            "time": {
                "start": 0,
                "cast_rays": 0,
                "check_collisions": 0,
                "end": 0
            }
        }

    # Calls all necessary updates for each cycle
    def update(self, dt):
        timer = support.Timer()
        self.debug_stats["time"]["start"] = timer.tick()
        # Recast rays at current position
        self.camera.update_cone()
        self.debug_stats["time"]["cast_rays"] = timer.tick()
        # Checks collisions with projected rays and walls
        self.close_objects = self.world_objects.get_walls_in_range(self.camera.get_position(), self.camera.get_view_radius())
        self.check_collisions(self.camera.get_camera_rays())
        self.debug_stats["time"]["check_collisions"] = timer.tick()
        self.debug_stats["time"]["end"] = timer.get_total_time()

    def process_outputs(self):
        return self.camera.generate_frame()

    # Sets the object we are currently looking at to be selected
    def set_facing_object(self):
        center_ray = self.camera.get_center_ray()
        walls = self.close_objects
        circles = self.world_objects.get_circles()
        for k in walls:
            for w in walls[k]:
                p2 = geometry.intersect(w, center_ray)
                if p2 is not None:
                    w.set_selected(True)
                else:
                    w.set_selected(False)
        for k in circles:
            for c in circles[k]:
                p2 = geometry.circle_line_segment_intersection(c.get_p1(), c.get_r(),
                                                               center_ray.get_p1(), center_ray.get_p2())
                if p2 is not None:
                    c.set_selected(True)
                else:
                    c.set_selected(False)

    # Returns an instance of the wall currently being looked at
    def get_facing_object(self):
        walls = self.close_objects
        circles = self.world_objects.get_circles()
        for k in walls:
            for w in walls[k]:
                if w.get_selected():
                    return w
        for k in circles:
            for c in circles[k]:
                if c.get_selected():
                    return c
        return None

    # Deletes the wall we are currently looking at
    def remove_facing_object(self):
        self.set_facing_object()
        walls = self.close_objects
        circles = self.world_objects.get_circles()
        center_ray = self.camera.get_center_ray()
        for k in walls:
            for w in walls[k]:
                if geometry.intersect(w, center_ray) is not None:
                    self.world_objects.remove_wall(k, w)
                    return
        for k in circles:
            for c in circles[k]:
                if geometry.circle_line_segment_intersection(c.get_p1(), c.get_r(),
                                                             center_ray.get_p1(), center_ray.get_p2()) is not None:
                    self.world_objects.remove_circle(k, c)
                    return

    def debug(self):
        return self.camera.get_camera_rays()

    def get_debug_stats(self):
        self.debug_stats["value"]["total_obj_count"] = self.get_world_state().get_world_object_count()
        return self.debug_stats

    def process_mouse_movement(self, mouse_pos):
        self.camera.process_mouse_movement(mouse_pos)

    def process_keys(self):
        return self.camera.process_keys(self.close_objects)

    # Changes the color of the currently selected wall
    def color_wall(self, color):
        self.set_facing_object()
        facing_wall = self.get_facing_object()
        if facing_wall is not None:
            facing_wall.set_color(color)

    # Checks for collisions between a set of rays and all walls/circles
    def check_collisions(self, rays):
        walls = self.close_objects
        circles = self.world_objects.get_circles()
        for ray in rays:
            for k in walls:
                for w in walls[k]:
                    p2 = geometry.intersect(w, ray)
                    if p2 is not None:
                        ray.set_color(w.get_color())
                        ray.set_p2(p2)
            for k in circles:
                for c in circles[k]:
                    p2 = geometry.circle_line_segment_intersection(c.get_p1(), c.get_r(), ray.get_p1(), ray.get_p2())
                    if p2 is not None:
                        ray.set_color(c.get_color())
                        ray.set_p2(p2)

    def set_world_objects(self, world_objects):
        self.world_objects = world_objects

    def get_world_state(self):
        return self.world_objects

    def set_cur_position(self, current_position):
        self.camera.set_position(current_position)

    def get_cur_position(self):
        return self.camera.get_position()


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


class WorldState:
    def __init__(self):
        self.walls = {}
        self.circles = {}

    def load_state(self, filename):
        with open(filename, 'r') as file:
            self.walls.clear()
            self.circles.clear()
            for line in file:
                line_split = line.split(':')
                key = line_split[0]
                vals = line_split[1].split('; ')
                if key in self.walls:
                    self.walls[key].append(geometry.Wall(eval(vals[0]), eval(vals[1]), eval(vals[2])))
                else:
                    self.walls[key] = [geometry.Wall(eval(vals[0]), eval(vals[1]), eval(vals[2]))]

    def save_state(self, filename):
        print("saving!")
        with open(filename, 'w') as file:
            data = ""
            for k in self.walls:
                for w in self.walls[k]:
                    data += "{0}: {1}; {2}; {3}\n".format(k, w.get_p1(), w.get_p2(), w.get_color())
            # Remove trailing newline
            data = data[0:len(data) - 1]
            file.write(data)

    def get_circles(self):
        return self.circles

    def set_circles(self, circles):
        self.circles = circles

    def add_circles(self, key, circles):
        if key in self.circles:
            temp = self.circles[key]
            for circle in circles:
                temp.append(circle)
            self.circles[key] = temp
        else:
            self.circles[key] = circles

    def remove_circle(self, key, circle):
        self.circles[key].remove(circle)

    def change_circles(self, key, circles):
        self.circles[key] = circles

    def remove_circle_group(self, key):
        self.circles.pop(key)

    def remove_all_circles(self):
        self.circles.clear()

    def get_all_walls(self):
        return self.walls

    def get_walls_in_range(self, c, r):
        """
        Used in broad-phase collision detection, only returns walls that are from a certain distance of a point
        :param c: center of the point
        :param r: radius out from that point
        :return: walls dictionary containing collidable walls
        """
        c_walls = {}
        for k in self.walls:
            temp = []
            for wall in self.walls[k]:
                p1 = wall.get_p1()
                p2 = wall.get_p2()
                if c[0] - r < p1[0] < c[0] + r and c[1] - r < p1[1] < c[1] + r:
                    temp.append(wall)
                elif c[0] - r < p2[0] < c[0] + r and c[1] - r < p2[1] < c[1] + r:
                    temp.append(wall)
            c_walls[k] = temp
        return c_walls

    def set_walls(self, walls):
        """
        Sets the walls dict to a new walls dict
        :param walls: new walls dict
        """
        self.walls = walls

    def add_walls(self, key, walls):
        """
        Adds a list of walls to the dict
        DOES NOT REPLACE
        :param key: wall group
        :param walls: set of walls to add to the group
        """
        if key in self.walls:
            temp = self.walls[key]
            for wall in walls:
                temp.append(wall)
            self.walls[key] = temp
        else:
            self.walls[key] = walls

    def remove_wall(self, key, wall):
        """
        Removes a specific wall from the walls dict
        :param key: group of walls
        :param wall: specific wall being removed
        """
        self.walls[key].remove(wall)

    def change_walls(self, key, walls):
        """
        Updates a list of walls in the dict
        WILL REPLACE THE WALLS
        """
        self.walls[key] = walls

    def remove_wall_group(self, key):
        """
        Removes a group of walls
        :param key: wall group
        """
        self.walls.pop(key)

    def remove_all_walls(self):
        """
        Clears the entire walls dict
        """
        self.walls.clear()

    def get_world_object_count(self):
        s = 0
        for k in self.walls:
            s += len(self.walls[k])
        for k in self.circles:
            s += len(self.circles[k])
        return s


class Camera:
    def __init__(self, position, wall_height, width, height):
        # initialize the config parsers
        config = configparser.ConfigParser()
        config.read('settings.ini')
        en_config = config['ENGINE']
        mo_config = config['MOVEMENT']

        self.width = width
        self.height = height

        # Height scalar of each projected wall
        self.wall_height = wall_height

        # The field of view / angle of the view cone
        self.fov = int(en_config['fov']) * (math.pi / 180)

        # Distance the camera plane is from the center
        self.camera_plane_distance = (self.width / 2) / (math.tan(self.fov / 2))
        print(self.camera_plane_distance)
        self.camera_plane_distance = 10

        # Scale of projected line width, 1 = projected line width of 1
        self.resolution_scale = int(en_config['resolutionScale'])

        # Angle each ray is separated from the previous ray
        self.rotation_delta = (90 * (math.pi / 180)) - (self.fov / 2)

        # Degrees the camera turns
        self.rotation_units = int(mo_config['rotationUnits']) * (math.pi / 180)

        # Pixels the camera moves
        self.movement_units = float(mo_config['movementUnits'])

        # Sprint scalar applied when holding shift
        self.sprint_scalar = float(mo_config['sprintScalar'])

        # Looking Sensitivity
        self.mouse_sensitivity = float(mo_config['mouseSensitivity'])

        # Total length of each ray cast
        self.view_radius = int(en_config['viewDistance'])
        # math.sqrt(math.pow(self.height, 2) + math.pow(self.width, 2))

        # Maximum distance which depth is calculated
        self.lighting_distance = int(en_config['lightDistance'])

        # Total number of rays
        self.ray_count = int((self.width / (self.fov / (360 * (math.pi / 180)))) / self.resolution_scale)
        # self.ray_count = 100

        # Current amount sprint is being applied
        self.sprint_mod = 0

        # Current position
        self.position = position

        # List of all rays cast from the camera
        self.all_rays = []

        # All rays that are located inside the fov cone
        self.cone_rays = []

        # Angle the fov cone starts at
        self.fov_lower = self.rotation_delta

        # Angle the fov cone ends at
        self.fov_upper = self.rotation_delta + self.fov

        # Color of distance fog
        self.fog_color = (0, 0, 0)

        # Used for looking up the appropriate action for a key press
        self.movements = {
            pygame.K_a: self.move_left,
            pygame.K_d: self.move_right,
            pygame.K_s: self.move_backward,
            pygame.K_w: self.move_forward,
            pygame.K_q: self.rotate_left,
            pygame.K_e: self.rotate_right
        }

        # Calculate center ray of the fov cone
        angle = self.rotation_delta + (self.fov / 2)
        p1 = self.position
        p2 = self.cast_ray(p1, angle, self.view_radius)
        self.fov_center_ray = geometry.Ray(p1, p2, (255, 255, 255), 0)

        # Update the fov cone
        self.gen_cone()

    def cast_ray(self, origin, angle, distance):
        x = origin[0] + distance * math.cos(angle)
        y = origin[1] + distance * math.sin(angle)
        return x, y

    def gen_cone(self):
        p1 = self.position
        for i in range(self.ray_count):
            angle = self.rotation_delta - self.fov / 2 + i * (self.fov / (self.ray_count - 1))
            p2 = self.cast_ray(p1, angle, self.view_radius)
            self.cone_rays.append(geometry.Ray(p1, p2, (255, 255, 255), angle))

    # Updates what rays are included in our FoV cone
    def update_cone(self):
        camera_plane_p1 = self.cast_ray(self.position, self.rotation_delta - self.fov / 2, self.camera_plane_distance)
        camera_plane_p2_angle = self.rotation_delta - self.fov / 2 + (self.ray_count - 1) * (self.fov / (self.ray_count - 1))
        camera_plane_p2 = self.cast_ray(self.position, camera_plane_p2_angle, self.camera_plane_distance)

        camera_plane_length = geometry.length(geometry.Line(camera_plane_p1, camera_plane_p2))
        p1 = self.position
        for i in range(self.ray_count):
            # Theta = angle from the fov center ray that intersects the camera plane at an even interval
            theta = math.atan(((camera_plane_length / self.ray_count) * (i - ((self.ray_count - 1) / 2))) / self.camera_plane_distance)
            # We use theta because without, we get a very odd distortion
            # angle = self.rotation_delta - self.fov / 2 + i * (self.fov / (self.ray_count - 1))
            angle = self.rotation_delta + theta
            p2 = self.cast_ray(p1, angle, self.view_radius)

            self.cone_rays[i].set_p1(p1)
            self.cone_rays[i].set_p2(p2)
            self.cone_rays[i].set_rd(angle)

    # Returns FrameState object, which contains all information about the
    def generate_frame(self):
        rays = self.cone_rays.copy()

        # Padding between each slice
        padding = self.width / len(rays)

        # Initialize the frame
        frame = FrameState()
        frame.set_segment_width(int(padding + 1))
        segment_count = 0

        # Draw walls
        for ray in self.cone_rays:
            # Help with the math: https://permadi.com/1996/05/ray-casting-tutorial-9/
            ray_length = geometry.length(ray)
            ray_relative_angle = self.rotation_delta - ray.get_rd()
            ray_distance = ray_length * math.cos(ray_relative_angle)

            actual_slice_height = self.wall_height
            distance_to_slice = ray_distance
            distance_to_projection_plane = self.camera_plane_distance
            projected_slice_height = (actual_slice_height / distance_to_slice) * distance_to_projection_plane

            # Create the segment
            seg_p1 = (segment_count * padding, (self.height / 2) - projected_slice_height / 2)
            seg_p2 = (segment_count * padding, (self.height / 2) + projected_slice_height / 2)
            seg_c = self.depth_shader(ray.get_color(), ray_length, aug=self.fog_color)

            # Add segment to frame
            frame.add_segment(Segment(seg_c, seg_p1, seg_p2))
            segment_count += 1
        return frame

    # Behold, the epitome of list comprehension
    def depth_shader(self, col, length, aug):
        return [
            max(aug[i], col[i] - ((col[i] - aug[i]) * math.log(length + 1) / math.log(self.lighting_distance + 1)))
            for i in range(len(col))]

    # Handles all valid key presses
    def process_keys(self, movement_collidable_walls):
        keys = pygame.key.get_pressed()
        # Handle Sprint
        if keys[pygame.K_LSHIFT]:
            self.sprint_mod = self.sprint_scalar * self.movement_units
        else:
            self.sprint_mod = 0
        if keys[pygame.K_w]:
            self.move_forward(movement_collidable_walls)
        if keys[pygame.K_s]:
            self.move_backward(movement_collidable_walls)
        if keys[pygame.K_a]:
            self.move_left(movement_collidable_walls)
        if keys[pygame.K_d]:
            self.move_right(movement_collidable_walls)
        if keys[pygame.K_q]:
            self.rotate_left()
        if keys[pygame.K_e]:
            self.rotate_right()
        # This but list comprehension just for the heck of it
        # [self.movements[k]() if keys[k] else None for k in self.movements]
        return True

    def get_view_radius(self):
        return self.view_radius

    def get_rotation_delta(self):
        return self.rotation_delta

    def get_ray_count(self):
        return self.ray_count

    def get_camera_rays(self):
        return self.cone_rays

    # Returns the ray at the center of the FoV cone
    def get_center_ray(self):
        return self.cone_rays[round(len(self.cone_rays) / 2)]

    def get_position(self):
        return self.position

    def set_position(self, position):
        self.position = position

    def move_left(self, walls):
        dx = (self.movement_units + self.sprint_mod) * math.cos(self.rotation_delta - math.pi / 2)
        dy = (self.movement_units + self.sprint_mod) * math.sin(self.rotation_delta - math.pi / 2)
        self.position = (self.position[0] + dx, self.position[1] + dy)
        # self.position = self.check_movement_collisions(p1, p2, walls)

    def move_right(self, walls):
        dx = (self.movement_units + self.sprint_mod) * math.cos(self.rotation_delta + math.pi / 2)
        dy = (self.movement_units + self.sprint_mod) * math.sin(self.rotation_delta + math.pi / 2)
        self.position = (self.position[0] + dx, self.position[1] + dy)
        # self.position = self.check_movement_collisions(p1, p2, walls)

    def move_forward(self, walls):
        dx = (self.movement_units + self.sprint_mod) * math.cos(self.rotation_delta)
        dy = (self.movement_units + self.sprint_mod) * math.sin(self.rotation_delta)
        self.position = (self.position[0] + dx, self.position[1] + dy)
        # self.position = self.check_movement_collisions(p1, p2, walls)

    def move_backward(self, walls):
        dx = (self.movement_units + self.sprint_mod) * math.cos(self.rotation_delta)
        dy = (self.movement_units + self.sprint_mod) * math.sin(self.rotation_delta)
        self.position = (self.position[0] - dx, self.position[1] - dy)
        # self.position = self.check_movement_collisions(p1, p2, walls)

    def rotate_left(self):
        self.rotate(-self.rotation_units)

    def rotate_right(self):
        self.rotate(self.rotation_units)

    def process_mouse_movement(self, mouse_pos):
        self.rotate(self.mouse_sensitivity * (mouse_pos[0] - (self.width / 2)) / 360)
        # self.rotate(self.mouse_sensitivity * (mouse_pos[0] - (self.width / 2)) / 360)

    # Rotates the camera a certain number of degrees
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

    def check_movement_collisions(self, cur_pos, new_pos, walls):
        """
        Checks if a wall passes through the movement from one pos to another
        :param cur_pos: current position
        :param new_pos: new position
        :param walls: set of walls to check
        :return: returns point along wall if collision, else new_pos
        """
        player_line = geometry.Line(cur_pos, new_pos)
        for k in walls:
            for wall in walls[k]:
                if wall is not None:
                    p2 = geometry.intersect(player_line, wall)
                    if p2 is not None:
                        # Awful sliding along a wall, just return new_pos if you want to turn this off
                        d_cn = geometry.dist(cur_pos, new_pos)
                        d_cp = geometry.dist(cur_pos, p2)
                        x_diff = d_cn - d_cp
                        y_diff = x_diff
                        if cur_pos[0] < new_pos[0]:
                            x_diff *= -1
                        if cur_pos[1] < new_pos[1]:
                            y_diff *= -1
                        np = cur_pos[0] + x_diff, cur_pos[1] + y_diff
                        return np
        return new_pos
