import math


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


class Wall(Line):
    def __init__(self, p1, p2, color):
        self.color = color
        self.width = 1
        super().__init__(p1, p2)

    def get_color(self):
        return self.color

    def set_color(self, color):
        self.color = color

    # The width of the line, calculated by resolution_scale and display width
    def get_width(self):
        return self.width

    def set_width(self, width):
        self.width = width

    def get_wall(self):
        return self.color, self.p1, self.p2, self.width


class Ray(Line):
    def __init__(self, p1, p2, color, rd):
        # Rotation delta in radians, used for rays
        self.rd = rd
        self.color = color
        super().__init__(p1, p2)

    def get_rd(self):
        return self.rd

    def set_rd(self, rd):
        self.rd = rd

    def get_color(self):
        return self.color

    def set_color(self, color):
        self.color = color
