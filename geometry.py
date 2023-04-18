import math


# math.dist() is not in python 3.6
def dist(p, q):
    return math.sqrt((q[0]-p[0])**2 + (q[1]-p[1])**2)


def intersect(l1, l2):
    p0 = l1.get_p1()
    p1 = l1.get_p2()
    p2 = l2.get_p1()
    p3 = l2.get_p2()

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


# Thanks to this magnificent person:
# https://stackoverflow.com/questions/30844482/what-is-most-efficient-way-to-find-the-intersection-of-a-line-and-a-circle-in-py
# Adapted to work with the current codebase
def circle_line_segment_intersection(circle_center, circle_radius, pt1, pt2, full_line=False, tangent_tol=1e-9):
    """ Find the points at which a circle intersects a line-segment.  This can happen at 0, 1, or 2 points.
    :param circle_center: The (x, y) location of the circle center
    :param circle_radius: The radius of the circle
    :param pt1: The (x, y) location of the first point of the segment
    :param pt2: The (x, y) location of the second point of the segment
    :param full_line: True to find intersections along full line - not just in the segment.  False will just return intersections within the segment.
    :param tangent_tol: Numerical tolerance at which we decide the intersections are close enough to consider it a tangent
    :return Sequence[Tuple[float, float]]: A list of length 0, 1, or 2, where each element is a point at which the circle intercepts a line segment.
    Note: We follow: http://mathworld.wolfram.com/Circle-LineIntersection.html
    """

    (p1x, p1y), (p2x, p2y), (cx, cy) = pt1, pt2, circle_center
    (x1, y1), (x2, y2) = (p1x - cx, p1y - cy), (p2x - cx, p2y - cy)
    dx, dy = (x2 - x1), (y2 - y1)
    dr = (dx ** 2 + dy ** 2)**.5
    big_d = x1 * y2 - x2 * y1
    discriminant = circle_radius ** 2 * dr ** 2 - big_d ** 2

    if dr == 0:  # Was throwing errors when setting starting loc to 0
        return None
    if discriminant < 0:  # No intersection between circle and line
        return None
    else:  # There may be 0, 1, or 2 intersections with the segment
        intersections = [
            (cx + (big_d * dy + sign * (-1 if dy < 0 else 1) * dx * discriminant**.5) / dr ** 2,
             cy + (-big_d * dx + sign * abs(dy) * discriminant**.5) / dr ** 2)
            for sign in ((1, -1) if dy < 0 else (-1, 1))]  # This makes sure the order along the segment is correct
        if not full_line:  # If only considering the segment, filter out intersections that do not fall within the segment
            fraction_along_segment = [(xi - p1x) / dx if abs(dx) > abs(dy) else (yi - p1y) / dy for xi, yi in intersections]
            intersections = [pt for pt, frac in zip(intersections, fraction_along_segment) if 0 <= frac <= 1]
        if len(intersections) == 2 and abs(discriminant) <= tangent_tol:  # If line is tangent to circle, return just one point (as both intersections have same location)
            return [intersections[0]]
        else:
            if len(intersections) < 2:
                return None
            dist1 = math.dist(intersections[0], pt1)
            dist2 = math.dist(intersections[1], pt1)
            if dist1 < dist2:
                return intersections[0]
            return intersections[1]


# Courtesy of https://stackoverflow.com/questions/3120357/get-closest-point-to-a-line
def closest_point(a, b, p):
    a_to_p = (p[0] - a[0], p[1] - a[1])
    a_to_b = (b[0] - a[0], b[1] - a[1])
    atb2 = a_to_b[0]**2 + a_to_b[1]**2
    atp_dot_atb = a_to_p[0]*a_to_b[0] + a_to_p[1]*a_to_b[1]
    t = atp_dot_atb / atb2
    return a[0] + a_to_b[0]*t, a[1] + a_to_b[1]*t


# Courtesy of https://www.jeffreythompson.org/collision-detection/line-circle.php
def line_point(l1, p):
    p1 = l1.get_p1()
    p2 = l1.get_p2()
    x1 = p1[0]
    y1 = p1[1]
    x2 = p2[0]
    y2 = p2[1]
    px = p[0]
    py = p[1]
    d1 = dist((px, py), (x1, y1))
    d2 = dist((px, py), (x2, y2))
    l = dist((x1, y1), (x2, y2))
    buffer = .1
    if l-buffer <= d1+d2 <= l+buffer:
        return True
    return False


def length(l1):
    p1 = l1.get_p1()
    p2 = l1.get_p2()
    return math.sqrt(math.pow(p2[0] - p1[0], 2) + math.pow(p2[1] - p1[1], 2))


class Line:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    def get_p1(self):
        return self.p1

    def set_p1(self, p1):
        self.p1 = p1

    def get_p2(self):
        return self.p2

    def set_p2(self, p2):
        self.p2 = p2


class Circle:
    def __init__(self, p1, r, color):
        self.p1 = p1
        self.r = r
        self.color = color
        self.width = 1
        self.selected = False
        # Used in debug and in texture mapping
        self.col_points = []

    def get_p1(self):
        return self.p1

    def set_p1(self, p1):
        self.p1 = p1

    def get_r(self):
        return self.r

    def set_r(self, r):
        self.r = r

    def get_color(self):
        return self.color

    def set_color(self, color):
        self.color = color

    # The width of the line, calculated by resolution_scale and display width
    def get_width(self):
        return self.width

    def set_width(self, width):
        self.width = width

    def get_circle(self):
        return self.color, self.p1, self.r, self.width

    def set_selected(self, selected):
        self.selected = selected

    def get_selected(self):
        return self.selected

    def clear_col_points(self):
        self.col_points.clear()

    def get_col_points(self):
        return self.col_points

    def add_col_point(self, point):
        self.col_points.append(point)


class Wall(Line):
    def __init__(self, p1, p2, color):
        self.color = color
        self.width = 1
        self.selected = False
        super().__init__(p1, p2)

    def get_color(self):
        # if self.selected:
        #     return (255, 0, 0)
        return self.color

    def set_color(self, color):
        self.color = color

    # When we are drawing to the display, we need the width of the line
    def get_width(self):
        return self.width

    def set_width(self, width):
        self.width = width

    def get_wall(self):
        return self.color, self.p1, self.p2, self.width

    def set_selected(self, selected):
        self.selected = selected

    def get_selected(self):
        return self.selected


class Ray(Line):
    def __init__(self, p1, p2, color, rd):
        # Rotation delta in radians, used for rays
        self.rd = rd
        self.color = color
        self.wall_height = 0
        self.collide = False
        self.wall = None
        super().__init__(p1, p2)

    def get_rd(self):
        return self.rd

    def set_rd(self, rd):
        self.rd = rd

    def get_color(self):
        return self.color

    def set_color(self, color):
        self.color = color

    def get_wall(self):
        return self.wall

    def set_wall(self, wall):
        self.wall = wall
