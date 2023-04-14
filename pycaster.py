from random import randint

from Box2D import *

import configparser
import math
import pygame
import support

import geometry


def rand_color():
    return randint(0, 255), randint(0, 255), randint(0, 255)


# TODO: Should my positions be stored as vectors instead?
# TODO: Add saving and loading of the world state
# TODO: Check line magnitude and if large then don't calculate collisions on that ray for broad phase
# TODO: Checkout pygame gui instead of tkinter
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

        # Dictionary containing all lists of walls
        # We store each grouping of walls in a dictionary so that we can differentiate what walls belong to
        # what processes. The initial group of walls is called "Default". If we want to add more groups, we just
        # create a new group name and add them to the dictionary. This gives us the ability to potentially store
        # other types of objects in the future, and to be able to handle them differently depending on their key/tag
        # self.walls = {}

        # Dictionary containing all lists of circles
        # self.circles = {}
        self.world_objects = WorldState()

        # Setup Box2D
        self.gravity = b2Vec2(0.0, 0.0)
        self.world = b2World(gravity=self.gravity)

        self.dynamic_body = DynamicBox(
            self.world.CreateDynamicBody(
                position=(0.0, 3.0),
                fixtures=b2FixtureDef(
                    shape=b2PolygonShape(box=(0.3, 0.3)),
                    density=3.0,
                    friction=0.0
                ),
                fixedRotation=False
            )
        )

        camera_body = DynamicBox(
            self.world.CreateDynamicBody(
                position=current_position,
                fixtures=b2FixtureDef(
                    shape=b2PolygonShape(box=(0.2, 0.2)),
                    density=3.0,
                    friction=0.0
                ),
                fixedRotation=True
            )
        )
        # Set up the camera for rendering to screen
        self.camera = Camera(current_position, wall_height, width, height, camera_body)

        self.debug_stats = {
            "value": {
                "total_obj_count": self.get_world_state().get_world_object_count(),
                "camera_ray_count": len(self.camera.get_camera_rays()),
                "total_ray_count": self.camera.get_ray_count(),
                "view_angle": round(self.camera.get_rotation_delta() * (180 / math.pi))
            },
            "time": {
                "start": 0,
                "physics_step": 0,
                "update_rays": 0,
                "update_cone": 0,
                "update_camera_plane": 0,
                "update_camera": 0,
                "check_collisions": 0,
                "end": 0
            }
        }

    # Calls all necessary updates for each cycle
    def update(self, dt):
        timer = support.Timer()
        self.debug_stats["time"]["start"] = timer.tick()
        # Update physics
        self.world.Step(dt, 6, 2)
        # Get dynamic box location and add to walls dict
        self.world_objects.change_walls("dynamicBox", self.dynamic_body.get_walls())
        self.debug_stats["time"]["physics_step"] = timer.tick()
        # Updates all rays to current position
        self.camera.update_rays()
        self.debug_stats["time"]["update_rays"] = timer.tick()
        # Updates the set of rays withing to fov cone
        self.camera.update_cone()
        self.debug_stats["time"]["update_cone"] = timer.tick()
        # Updates the plane in which rays will be project onto [DEPRECIATED]
        self.camera.update_camera_plane()
        self.debug_stats["time"]["update_camera_plane"] = timer.tick()
        # Updates rays for their projection and saves them in a list [DEPRECIATED]
        self.camera.update_camera()
        self.debug_stats["time"]["update_camera"] = timer.tick()
        # Checks collisions with projected rays and walls
        self.check_collisions(self.camera.get_camera_rays())
        self.debug_stats["time"]["check_collisions"] = timer.tick()
        self.debug_stats["time"]["end"] = timer.get_total_time()

    def process_outputs(self):
        return self.camera.generate_frame()

    # Sets the object we are currently looking at to be selected
    # TODO: Investigate circles having thousands of col_points
    def set_facing_object(self):
        center_ray = self.camera.get_center_ray()
        walls = self.world_objects.get_walls_in_range(self.camera.get_position(), self.camera.get_view_radius())
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
        walls = self.world_objects.get_walls_in_range(self.camera.get_position(), self.camera.get_view_radius())
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
        # TODO: Move to process_mouse_buttons()
        self.set_facing_object()
        walls = self.world_objects.get_walls_in_range(self.camera.get_position(), self.camera.get_view_radius())
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
        # self.rotate(self.mouse_sensitivity * (mouse_pos[0] - (self.width / 2)) / 360)

    # TODO: Use the buffer swap principle for movement updates
    # TODO: remove keys param and call pygame.key.get_pressed()
    # Handles all valid key presses
    def process_keys(self):
        keys = pygame.key.get_pressed()
        # Handle moving dynamicbox
        if keys[pygame.K_LEFT]:
            self.dynamic_body.body.ApplyLinearImpulse(b2Vec2(-1.0, 0.0), self.dynamic_body.body.position, True)

        if keys[pygame.K_RIGHT]:
            self.dynamic_body.body.ApplyLinearImpulse(b2Vec2(1.0, 0.0), self.dynamic_body.body.position, True)

        if keys[pygame.K_UP]:
            self.dynamic_body.body.ApplyLinearImpulse(b2Vec2(0.0, 1.0), self.dynamic_body.body.position, True)

        if keys[pygame.K_DOWN]:
            self.dynamic_body.body.ApplyLinearImpulse(b2Vec2(0.0, -1.0), self.dynamic_body.body.position, True)
        return self.camera.process_keys(self.world_objects.get_walls_in_range(self.camera.get_position(), 20))

    # Changes the color of the currently selected wall
    def color_wall(self, color):
        # TODO: Move to process_mouse_buttons()
        self.set_facing_object()
        facing_wall = self.get_facing_object()
        if facing_wall is not None:
            facing_wall.set_color(color)

    # Checks for collisions between a set of rays and all walls/circles
    def check_collisions(self, rays):
        walls = self.world_objects.get_walls_in_range(self.camera.get_position(), self.camera.get_view_radius())
        circles = self.world_objects.get_circles()
        for ray in rays:
            for k in walls:
                for w in walls[k]:
                    p2 = geometry.intersect(w, ray)
                    if p2 is not None:
                        ray.set_color(w.get_color())
                        ray.set_p2(p2)
                        ray.set_wall(w)
                        # w.add_col_point(p2)
            for k in circles:
                for c in circles[k]:
                    p2 = geometry.circle_line_segment_intersection(c.get_p1(), c.get_r(), ray.get_p1(), ray.get_p2())
                    if p2 is not None:
                        ray.set_color(c.get_color())
                        ray.set_p2(p2)
                        # c.add_col_point(p2)

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


class DynamicBox:
    """
    A render-able box that uses the box2d physics engine
    """
    def __init__(self, body):
        self.body = body
        self.body_width = 0
        self.body_height = 0
        self.gen_dims()

    def gen_dims(self):
        """
        Sets the body_width and body_height vars
        """
        for fixture in self.body.fixtures:
            transform = self.body.transform
            t_pos = (transform.position.x, transform.position.y)
            r_verts = self.rotate_point_list((0, 0), fixture.shape.vertices, transform.angle)
            w_verts = [(v[0] + t_pos[0], v[1] + t_pos[1]) for v in r_verts]
            s_verts = [self.convert_b2p(v) for v in w_verts]
            self.body_width = geometry.dist(s_verts[0], s_verts[1])
            self.body_height = geometry.dist(s_verts[0], s_verts[3])

    def get_walls(self):
        """
        Returns the b2Body dimensions as a set of pycaster walls
        :return: set of pycaster walls
        """
        transform = self.body.transform
        for fixture in self.body.fixtures:
            r_verts = self.rotate_point_list((0, 0), fixture.shape.vertices, transform.angle)
            w_verts = [(v[0] + transform.position.x, v[1] + transform.position.y) for v in r_verts]
            s_verts = [self.convert_b2p(v) for v in w_verts]
            walls = []
            for i in range(len(s_verts)):
                wall = geometry.Wall(s_verts[i], s_verts[(i+1) % len(s_verts)], (255, 0, 0))
                walls.append(wall)
            return walls

    def convert_b2p(self, pos):
        """
        Converts box2d coordinates to pycaster coordinates
        :param pos:
        :return:
        """
        return pos[0] * 10, pos[1] * 10

    def convert_p2b(self, pos):
        return pos[0]/10, pos[1]/10

    def rotate_point_list(self, origin, points, angle):
        """
        Rotates points around the origin from a given angle
        :param origin: center of rotation
        :param points: points to be rotated
        :param angle: angle of rotation
        :return: new set of rotated points
        """
        s = math.sin(angle)
        c = math.cos(angle)
        r_points = []
        for p in points:
            px = p[0]
            py = p[1]
            px -= origin[0]
            py -= origin[1]
            rx = px * c - py * s
            ry = px * s + py * c
            nx = rx + origin[0]
            ny = ry + origin[1]
            r_points.append((nx, ny))
        return r_points


class Camera:
    def __init__(self, position, wall_height, width, height, body):
        # initialize the config parsers
        config = configparser.ConfigParser()
        config.read('settings.ini')
        en_config = config['ENGINE']
        mo_config = config['MOVEMENT']

        self.width = width
        self.height = height
        self.camera_box = body

        # Height scalar of each projected wall
        self.wall_height = wall_height

        # The field of view / angle of the view cone
        self.fov = int(en_config['fov']) * (math.pi / 180)

        # Distance the camera plane is from the center
        self.camera_plane_distance = (self.width / 2) / (math.tan(self.fov / 2))

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

        # Current amount sprint is being applied
        self.sprint_mod = 0

        # Current position
        self.position = position

        # List of all rays cast from the camera
        self.all_rays = []

        # Plane from which serves as the origin point for all displayed rays
        self.camera_plane = geometry.Line((0, 0), (0, 0))

        # Generate all
        self.gen_rays()

        # All rays that are located inside the fov cone
        self.cone_rays = []

        # All rays inside the fov cone, with origins adjusted for the camera plane
        self.camera_rays = []

        # Angle the fov cone starts at
        self.fov_lower = self.rotation_delta

        # Angle the fov cone ends at
        self.fov_upper = self.rotation_delta + self.fov

        # Color of distance fog
        self.fog_color = (63, 63, 63)

        # Used for looking up the appropriate action for a key press
        # TODO: Need to be passing in a set of walls to the move funcs
        self.movements = {
            pygame.K_a: self.move_left,
            pygame.K_d: self.move_right,
            pygame.K_s: self.move_backward,
            pygame.K_w: self.move_forward,
            pygame.K_q: self.rotate_left,
            pygame.K_e: self.rotate_right
        }

        # Calculate center ray of the fov cone
        p1 = self.position
        x = (p1[0] + (self.view_radius * math.cos(self.rotation_delta + (self.fov / 2))))
        y = (p1[1] + (self.view_radius * math.sin(self.rotation_delta + (self.fov / 2))))
        self.fov_center_ray = geometry.Ray(p1, (x, y), (255, 255, 255), 0)

        # Update the fov cone
        self.update_cone()

        # Update the current location of the camera plane relative to the camera
        self.update_camera_plane()

    # Initializes all the rays
    def gen_rays(self):
        rad_slice = (360.0 / self.ray_count) * (math.pi / 180)
        p1 = self.position
        for i in range(self.ray_count):
            x = (p1[0] + (self.view_radius * math.cos(rad_slice * i)))
            y = (p1[1] + (self.view_radius * math.sin(rad_slice * i)))
            p2 = x, y
            ray = geometry.Ray(p1, p2, (255, 255, 255), (rad_slice * i))
            self.all_rays.append(ray)

    # Updates all ray origin locations to current position
    def update_rays(self):
        rad_slice = (360.0 / self.ray_count) * (math.pi / 180)
        p1 = self.position
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
        p1 = self.position
        x = p1[0] + (self.view_radius * math.cos((self.fov / 2) + self.rotation_delta))
        y = p1[1] + (self.view_radius * math.sin((self.fov / 2) + self.rotation_delta))
        self.fov_center_ray.set_rd((self.fov / 2) + self.rotation_delta)
        self.fov_center_ray.set_p2((x, y))
        self.fov_center_ray.set_p1(self.position)

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
        pos = self.position
        r1 = self.cone_rays[0]
        r2 = self.cone_rays[len(self.cone_rays) - 1]

        x1 = pos[0] + (self.camera_plane_distance * math.cos(r1.get_rd()))
        y1 = pos[1] + (self.camera_plane_distance * math.sin(r1.get_rd()))

        x2 = pos[0] + (self.camera_plane_distance * math.cos(r2.get_rd()))
        y2 = pos[1] + (self.camera_plane_distance * math.sin(r2.get_rd()))

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
            p1 = self.position
            x = p1[0] + (self.view_radius * math.cos(self.fov_center_ray.get_rd() + theta))
            y = p1[1] + (self.view_radius * math.sin(self.fov_center_ray.get_rd() + theta))
            p2 = x, y
            self.camera_rays.append(geometry.Ray(p1, p2, self.cone_rays[i].get_color(),
                                                 self.fov_center_ray.get_rd() + theta))

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
            distance_to_segment = max(ray_length * math.cos(math.fabs(ray.get_rd() - self.fov_center_ray.get_rd())),
                                      1)
            projected_segment_height = (self.wall_height / distance_to_segment) * distance_to_projection_plane

            # Create the segment
            seg_p1 = (segment_count * padding, (self.height / 2) - projected_segment_height / 2)
            seg_p2 = (segment_count * padding, (self.height / 2) + projected_segment_height / 2)
            seg_c = self.depth_shader(ray.get_color(), ray_length, aug=self.fog_color)

            # Add segment to frame
            frame.add_segment(Segment(seg_c, seg_p1, seg_p2))
            segment_count += 1
        return frame

    # TODO: Investigate the addition of a radial gradient to simulate a light source from the player location
    # Behold, the epitome of list comprehension
    def depth_shader(self, col, length, aug):
        return [
            max(aug[i], col[i] - ((col[i] - aug[i]) * math.log(length + 1) / math.log(self.lighting_distance + 1)))
            for i in range(len(col))]

    # TODO: Use the buffer swap principle for movement updates
    # TODO: remove keys param and call pygame.key.get_pressed()
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
        self.camera_box.body.position = self.camera_box.convert_p2b(self.position)
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
        return self.camera_rays

    # Returns the ray at the center of the FoV cone
    def get_center_ray(self):
        return self.camera_rays[round(len(self.camera_rays) / 2)]

    def get_position(self):
        return self.position

    def set_position(self, position):
        self.position = position

    # TODO: Investigate the use of a decorator for the player collision check
    def move_left(self, walls):
        p1 = self.position
        x = (p1[0] - ((self.movement_units + self.sprint_mod) *
                      math.cos(self.rotation_delta + (self.fov / 2) + (90 * (math.pi / 180)))))
        y = (p1[1] - ((self.movement_units + self.sprint_mod) *
                      math.sin(self.rotation_delta + (self.fov / 2) + (90 * (math.pi / 180)))))
        p2 = x, y
        self.position = self.check_movement_collisions(p1, p2, walls)

    def move_right(self, walls):
        p1 = self.position
        x = (p1[0] + ((self.movement_units + self.sprint_mod) *
                      math.cos(self.rotation_delta + (self.fov / 2) + (90 * (math.pi / 180)))))
        y = (p1[1] + ((self.movement_units + self.sprint_mod) *
                      math.sin(self.rotation_delta + (self.fov / 2) + (90 * (math.pi / 180)))))
        p2 = x, y
        self.position = self.check_movement_collisions(p1, p2, walls)

    def move_forward(self, walls):
        p1 = self.position
        x = (p1[0] + ((self.movement_units + self.sprint_mod) * math.cos(self.rotation_delta + (self.fov / 2))))
        y = (p1[1] + ((self.movement_units + self.sprint_mod) * math.sin(self.rotation_delta + (self.fov / 2))))
        p2 = x, y
        self.position = self.check_movement_collisions(p1, p2, walls)

    def move_backward(self, walls):
        p1 = self.position
        x = (p1[0] - ((self.movement_units + self.sprint_mod) * math.cos(self.rotation_delta + (self.fov / 2))))
        y = (p1[1] - ((self.movement_units + self.sprint_mod) * math.sin(self.rotation_delta + (self.fov / 2))))
        p2 = x, y
        self.position = self.check_movement_collisions(p1, p2, walls)

    def rotate_left(self):
        self.rotate(-self.rotation_units)

    def rotate_right(self):
        self.rotate(self.rotation_units)

    def process_mouse_movement(self, mouse_pos):
        self.rotate(self.mouse_sensitivity * (mouse_pos[0] - (self.width / 2)) / 360)
        # self.rotate(self.mouse_sensitivity * (mouse_pos[0] - (self.width / 2)) / 360)

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
