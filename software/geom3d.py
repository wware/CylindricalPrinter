#!/usr/bin/env python

import config
logger = config.get_logger('GEOM3D')

# Floating point madness
WIGGLE_ROOM = 1.0e-6


def sign(x):
    return x > 0.0


class Vector(object):

    def __init__(self, x, y=None, z=None):
        if y is None:
            self.x, self.y, self.z = x
        else:
            self.x, self.y, self.z = x, y, z

    def serialize(self):
        import cPickle
        return cPickle.dumps((self.x, self.y, self.z))

    @classmethod
    def unserialize(self, str):
        import cPickle
        x, y, z = cPickle.loads(str)
        return Vector(x, y, z)

    def __repr__(self):
        return "<{0},{1},{2}>".format(self.x, self.y, self.z)

    def dot(self, v):
        return self.x * v.x + self.y * v.y + self.z * v.z

    def __eq__(self, v):
        """
        This is necessary because floating-point arithmetic is imperfect.
        """
        return abs(self.diff(v)) < WIGGLE_ROOM

    def __abs__(self):
        return (self.dot(self)) ** .5

    def scale(self, k):
        return Vector(k * self.x, k * self.y, k * self.z)

    def unit_length(self):
        return self.scale(1.0 / abs(self))

    def cross(self, v):
        ux, uy, uz = self.x, self.y, self.z
        vx, vy, vz = v.x, v.y, v.z
        return Vector(uy * vz - uz * vy,
                      uz * vx - ux * vz,
                      ux * vy - uy * vx)

    def add(self, v):
        return Vector(self.x + v.x, self.y + v.y, self.z + v.z)

    def diff(self, v):
        return Vector(self.x - v.x, self.y - v.y, self.z - v.z)


zeroVector = Vector((0., 0., 0.))


class BBox:
    def __init__(self, v1=None, v2=None):
        if v1 is not None:
            assert v2 is not None
            assert v1.x <= v2.x
            assert v1.y <= v2.y
            assert v1.z <= v2.z
            self._min, self._max = v1, v2

            def contains_x(x, x1=v1.x-WIGGLE_ROOM, x2=v2.x+WIGGLE_ROOM):
                return x1 < x < x2

            def contains_y(y, y1=v1.y-WIGGLE_ROOM, y2=v2.y+WIGGLE_ROOM):
                return y1 < y < y2

            def contains_z(z, z1=v1.z-WIGGLE_ROOM, z2=v2.z+WIGGLE_ROOM):
                return z1 < z < z2

            def contains_yz(y, z, y1=v1.y-WIGGLE_ROOM, y2=v2.y+WIGGLE_ROOM,
                            z1=v1.z-WIGGLE_ROOM, z2=v2.z+WIGGLE_ROOM):
                return y1 < y < y2 and z1 < z < z2

            def z_overlap(za, zb, z1=v1.z-WIGGLE_ROOM, z2=v2.z+WIGGLE_ROOM,
                          WIGGLE_ROOM=WIGGLE_ROOM):
                za, zb = min(za, zb) - WIGGLE_ROOM, max(za, zb) + WIGGLE_ROOM
                return z1 < za < z2 or z1 < zb < z2 or \
                    za < z1 < zb or za < z2 < zb

            def center(c=v1.add(v2).scale(0.5)):
                return c
        else:
            self._min = self._max = None

            def contains_x(x):
                return False

            def contains_y(y):
                return False

            def contains_z(z):
                return False

            def contains_yz(y, z):
                return False

            def z_overlap(za, zb):
                return False

            def center():
                return None
        self.contains_x = contains_x
        self.contains_y = contains_y
        self.contains_z = contains_z
        self.contains_yz = contains_yz
        self.z_overlap = z_overlap
        self.center = center

    def __contains__(self, vector):
        return self.contains_x(vector.x) and \
            self.contains_y(vector.y) and \
            self.contains_z(vector.z)

    def __repr__(self):
        return '<BBox {0} {1}>'.format(self._min, self._max)

    def copy(self):
        return BBox(self._min, self._max)

    def size(self):
        return self._max.diff(self._min)

    def set_size(self, u):
        v = u.diff(self.size()).scale(0.5)
        assert v.x >= 0
        assert v.y >= 0
        assert v.z >= 0
        self._min = self._min.diff(v)
        self._max = self._max.add(v)

    def expand(self, other):
        if self._min is None:
            return other
        elif other._min is None:
            return self
        return BBox(Vector(min(self._min.x, other._min.x),
                           min(self._min.y, other._min.y),
                           min(self._min.z, other._min.z)),
                    Vector(max(self._max.x, other._max.x),
                           max(self._max.y, other._max.y),
                           max(self._max.z, other._max.z)))

    def _iterator(self, xmin, xmax, xsteps):
        assert xmax >= xmin
        dx = (1.0 * xmax - xmin) / (xsteps - 1)
        x = 1.0 * xmin
        for i in range(xsteps):
            yield x
            x += dx

    def getXiterator(self, xsteps):
        return self._iterator(self._min.x, self._max.x, xsteps)

    def getYiterator(self, ysteps):
        return self._iterator(self._min.y, self._max.y, ysteps)

    def getZiterator(self, zsteps):
        return self._iterator(self._min.z, self._max.z, zsteps)


class Triangle:

    def __init__(self, vertex1, vertex2, vertex3, normal=None):
        u = vertex2.diff(vertex1)
        v = vertex3.diff(vertex2)
        w = u.cross(v)
        if abs(w) == 0:
            # zero-area triangle???
            vertex1 = vertex2 = vertex3 = normal = Vector(0, 0, 0)
        else:
            expected_normal = w.unit_length()
            if normal is None or normal == Vector(0, 0, 0) or \
                    normal.dot(expected_normal) < 0:
                # Replace normal with right-hand-rule-generated unit vector
                normal = expected_normal
        self.vertices = (vertex1, vertex2, vertex3)
        self.normal = normal

        minx = min(vertex1.x, vertex2.x, vertex3.x)
        miny = min(vertex1.y, vertex2.y, vertex3.y)
        minz = min(vertex1.z, vertex2.z, vertex3.z)
        maxx = max(vertex1.x, vertex2.x, vertex3.x)
        maxy = max(vertex1.y, vertex2.y, vertex3.y)
        maxz = max(vertex1.z, vertex2.z, vertex3.z)

        self._bbox = bbox = \
            BBox(Vector(minx, miny, minz), Vector(maxx, maxy, maxz))

        # this number is the same for any point in the triangle
        self.k = k = normal.dot(vertex1)

        def interior(p,
                     k=k,
                     sign=sign,
                     vertex1=vertex1,
                     vertex2=vertex2,
                     vertex3=vertex3,
                     normal=normal,
                     diff1=vertex2.diff(vertex1),
                     diff2=vertex3.diff(vertex2),
                     diff3=vertex1.diff(vertex3)):
            in_plane = abs(normal.dot(p) - k) < WIGGLE_ROOM
            xs = [
                normal.dot(diff1.cross(p.diff(vertex1))),
                normal.dot(diff2.cross(p.diff(vertex2))),
                normal.dot(diff3.cross(p.diff(vertex3)))
            ]
            negatives = reduce(lambda x, y: x and y,
                               map(lambda x: x >= -WIGGLE_ROOM, xs))
            positives = reduce(lambda x, y: x and y,
                               map(lambda x: x <= WIGGLE_ROOM, xs))
            return (in_plane and (negatives or positives))
        self.__contains__ = interior

        def bbox_contains_yz(y, z, f=bbox.contains_yz):
            return f(y, z)
        self.bbox_contains_yz = bbox_contains_yz

    def __repr__(self):
        vecs = (self.normal,) + self.vertices
        return '<n:{0}\n    {1}\n    {2}\n    {3}>'.format(*vecs)

    def __eq__(self, other):
        return self.normal == other.normal and self.vertices == other.vertices

    def scale(self, factor):
        vertices = tuple(map(lambda v, f=factor: v.scale(f),
                             self.vertices))
        return Triangle(vertices[0], vertices[1], vertices[2], self.normal)

    def serialize(self):
        str = ':'.join([v.serialize() for v in self.vertices])
        return str + ':' + self.normal.serialize()

    @classmethod
    def unserialize(self, str):
        v1, v2, v3, n = str.split(':')
        return Triangle(
            Vector.unserialize(v1),
            Vector.unserialize(v2),
            Vector.unserialize(v3),
            Vector.unserialize(n)
        )

    def intersect(self, y, z):
        """
        For given values of y and z, figure out where this triangle intersects
        a line parallel to the x axis at those y and z values, and return the
        x-coordinate of the intersection and the sign of the normal vector in
        the x direction. If the triangle doesn't intersect that line, or if the
        normal vector is perpendicular to the x axis, return None.
        """
        normal = self.normal
        nx = normal.x
        if nx == 0.0:
            return None

        # find intersection
        point = Vector((self.k - normal.y * y - normal.z * z) / nx, y, z)
        if point not in self._bbox:
            return None

        if point in self:
            return (point, normal)
        else:
            return None


class BinaryTree:
    # http://stackoverflow.com/questions/5444394/
    class Node:
        def __init__(self, val):
            self.l_child = None
            self.r_child = None
            self.data = val

    def __init__(self, extractor):
        self.root = None
        self.extractor = extractor

    def binary_insert(self, data):
        def helper(node, root, extractor=self.extractor):
            if root is None:
                self.root = node
            else:
                x = extractor(node.data)
                xt = extractor(root.data)
                if abs(x - xt) < 0.0001:
                    # already got this point
                    return
                elif xt > x:
                    if root.l_child is None:
                        root.l_child = node
                    else:
                        helper(node, root.l_child)
                else:
                    if root.r_child is None:
                        root.r_child = node
                    else:
                        helper(node, root.r_child)
        if data is not None:
            node = self.Node(data)
            if self.root is None:
                self.root = node
            else:
                helper(node, self.root)

    def to_list(self):
        lst = []

        def helper(x, lst=lst):
            if not x:
                return
            helper(x.l_child)
            lst.append(x.data)
            helper(x.r_child)
        helper(self.root)
        return lst
