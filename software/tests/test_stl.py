from geom3d import Vector, Triangle
from stl import Stl


def approximate(x, y):
    return abs(x - y) <= 0.000001 * min(abs(x), abs(y))


class TestStl(object):

    def test_triangle_from_string(self):
        t, s = Stl.triangle_from_string(
            "\x00\x00\x80\xbf" +   # normal
            "\x00\x00\x00\x00\x00\x00\x00\x00" +
            "\x0c\x02\xa0\xc1" +   # vertex1
            "\x58\x39\x72\xc1\x00\x00\x00\x00" +
            "\x0c\x02\xa0\xc1" +   # vertex2
            "\x58\x39\x72\xc1\x00\x00\xa0\x41" +
            "\x0c\x02\xa0\xc1" +   # vertex3
            "\x00\x00\x10\xc1\x00\x00\x00\x00" +
            "\x12\x34"    # don't care
        )
        assert len(s) == 0
        n, v = t.normal, t.vertices
        assert n != 'dont care'
        assert len(v) == 3
        norm = t.normal
        assert norm.x == -1
        assert norm.y == 0
        assert norm.z == 0
        v = t.vertices[0]
        assert approximate(v.x, -20.001)
        assert approximate(v.y, -15.139)
        assert approximate(v.z, 0)
        v = t.vertices[1]
        assert approximate(v.x, -20.001)
        assert approximate(v.y, -15.139)
        assert approximate(v.z, 20)
        v = t.vertices[2]
        assert approximate(v.x, -20.001)
        assert approximate(v.y, -9)
        assert approximate(v.z, 0)

    def te_st_get_point_list(self):
        A = Vector(0, 0, 0)
        B = Vector(1, 0, 0)
        C = Vector(0, 1, 0)
        D = Vector(0, 0, 1)
        stl = Stl(Triangle(A, B, D),
                  Triangle(A, C, B),
                  Triangle(A, D, C),
                  Triangle(B, C, D))
        tz = stl.triangles

        (I, _), (J, _) = stl.get_point_list(0.25, 0.25, tz)
        assert approximate(I.x, 0)
        assert approximate(I.y, 0.25)
        assert approximate(I.z, 0.25)
        assert approximate(J.x, 0.5)
        assert approximate(J.y, 0.25)
        assert approximate(J.z, 0.25)

        assert stl.get_point_list(2, 2) == []
        assert stl.get_point_list(1, 1) == []
        (I, _), = stl.get_point_list(0.5, 0.5)
        assert approximate(I.x, 0)
        assert approximate(I.y, 0.5)
        assert approximate(I.z, 0.5)
