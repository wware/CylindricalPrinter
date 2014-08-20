from geom3d import sign, Vector, BBox, Triangle


def test_sign():
    assert sign(1.0e-10)
    assert sign(1)
    assert sign(1.0e10)
    assert not sign(-1.0e-10)
    assert not sign(-1)
    assert not sign(-1.0e10)


class TestVector(object):

    def test_init(self):
        v = Vector(1, 2, 3)
        assert v.x == 1
        assert v.y == 2
        assert v.z == 3
        v = Vector((3.1416, 6.2832, 1.41421))
        assert v.x == 3.1416
        assert v.y == 6.2832
        assert v.z == 1.41421

    def test_repr(self):
        v = Vector(1.2, 3.4, 5.6)
        assert repr(v) == "<1.2,3.4,5.6>"

    def test_dot(self):
        v = Vector(1, 2, 3)
        assert v.dot(Vector(4, 5, 6)) == 32

    def test_eq(self):
        assert Vector(1.0, 2.0, 3.0) == \
            Vector(1.00000000001, 1.999999999999, 3.0)
        assert Vector(1.0, 2.0, 3.0) != Vector(1.00001, 1.9999, 3.0)

    def test_abs(self):
        v = Vector(1, 2, 3)
        expected = (1 + 4 + 9) ** .5
        assert abs(v) == expected

    def test_scale(self):
        assert Vector(1, 2, 3).scale(2) == Vector(2, 4, 6)

    def test_unit_length(self):
        p = (1./3) ** .5
        v = Vector(1, 1, 1).unit_length()
        assert v == Vector(p, p, p)

    def test_cross(self):
        v = Vector(1, 2, 3)
        assert v.cross(Vector(4, 5, 6)) == Vector(-3, 6, -3)

    def test_add(self):
        v = Vector(4, 6, 8)
        assert v.add(Vector(1, 2, 3)) == Vector(5, 8, 11)

    def test_diff(self):
        assert Vector(4, 6, 8).diff(Vector(1, 2, 3)) == Vector(3, 4, 5)


class TestBBox(object):

    def test_init(self):
        bbox = BBox(Vector(0, 0, 0), Vector(1, 1, 1))
        assert bbox._min == Vector(0, 0, 0)
        assert bbox._max == Vector(1, 1, 1)

    def test_contains(self):
        bbox = BBox(Vector(0, 0, 0), Vector(1, 1, 1))
        assert Vector(0.5, 0.5, 0.5) in bbox
        assert Vector(0.5, 0.5, 1.1) not in bbox

    def test_copy(self):
        bbox1 = BBox(Vector(1, 2, 3), Vector(4, 5, 6))
        bbox2 = bbox1.copy()
        bbox1._max = Vector(7, 8, 9)
        assert bbox2._min == Vector(1, 2, 3)
        assert bbox2._max == Vector(4, 5, 6)
        assert bbox1._min == Vector(1, 2, 3)
        assert bbox1._max == Vector(7, 8, 9)

    def test_size(self):
        assert BBox(Vector(0, -1, 0),
                    Vector(1, 1, 3)).size() == Vector(1, 2, 3)

    def test_set_size(self):
        bbox = BBox(Vector(0, 0, 0), Vector(1, 1, 1))
        bbox.set_size(Vector(2, 3, 4))
        assert bbox._min == Vector(-0.5, -1.0, -1.5)
        assert bbox._max == Vector(1.5, 2.0, 2.5)

    def test__iterator(self):
        g = BBox()
        assert [x for x in g._iterator(1, 10, 4)] == \
            [1.0, 4.0, 7.0, 10.0]
        assert [x for x in g._iterator(-10, -1, 4)] == \
            [-10.0, -7.0, -4.0, -1.0]

    def test_getXiterator(self):
        bb = BBox(Vector(0.0, 0.0, 1.0), Vector(1.0, 2.0, 4.0))
        assert [x for x in bb.getXiterator(5)] == \
            [0.0, 0.25, 0.5, 0.75, 1.0]
        assert [x for x in bb.getXiterator(5)] == \
            [0.0, 0.25, 0.5, 0.75, 1.0]

    def test_getYiterator(self):
        bb = BBox(Vector(0.0, 0.0, 1.0), Vector(1.0, 2.0, 4.0))
        assert [y for y in bb.getYiterator(9)] == \
            [0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
        assert [y for y in bb.getYiterator(9)] == \
            [0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]

    def test_getZiterator(self):
        bb = BBox(Vector(0.0, 0.0, 1.0), Vector(1.0, 2.0, 4.0))
        assert [z for z in bb.getZiterator(7)] == \
            [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]
        assert [z for z in bb.getZiterator(7)] == \
            [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]


class TestTriangle(object):

    def test_init(self):
        t = Triangle(
            Vector(-20, -15, 0.0),
            Vector(-20, -15, 20.0),
            Vector(-20, -9.0, 0.0),
            Vector(-1.0, 0.0, 0.0)
        )
        assert t.vertices[0] == Vector(-20, -15, 0)
        assert t.vertices[1] == Vector(-20, -15, 20)
        assert t.vertices[2] == Vector(-20, -9, 0)
        assert t.normal == Vector(-1, 0, 0)

        # Test inference of normal vector if it's absent
        t = Triangle(
            Vector(-20, -15, 0.0),
            Vector(-20, -15, 20.0),
            Vector(-20, -9.0, 0.0)
        )
        assert t.normal == Vector(-1, 0, 0)

        # Test that points in the triangle can be detected
        assert Vector(-20, -12, 5.0) in t
        assert Vector(-20, -16, 5.0) not in t
        assert Vector(-20, -12, 20.0) not in t

        # Test a point that is out of plane
        assert Vector(-20.0001, -12, 5.0) not in t

        # Test serialization and unserialization
        s = t.serialize()
        assert isinstance(s, str)
        t2 = Triangle.unserialize(s)
        assert t2.__class__ is Triangle
        assert t2.vertices[0] == Vector(-20, -15, 0)
        assert t2.vertices[1] == Vector(-20, -15, 20)
        assert t2.vertices[2] == Vector(-20, -9, 0)
        assert t2.normal == Vector(-1, 0, 0)
        assert t == t2

    def test_intersect(self):
        t = Triangle(
            Vector(1, 1, 0),
            Vector(1, 0, 0),
            Vector(1, 0, 1)
        )
        assert t.intersect(0.4, 0.4) == \
            (Vector(1, 0.4, 0.4), Vector(-1, 0, 0))
        assert t.intersect(0.6, 0.6) is None

        t = Triangle(
            Vector(1, 0, 0),
            Vector(0, 1, 0),
            Vector(0, 0, 1)
        )

        def f(y, z, t=t):
            v, _ = t.intersect(y, z)
            return v
        assert f(0.00001, 0.00001) == Vector(0.99998, 1e-05, 1e-05)
        assert f(0.2, 0.2) == Vector(0.6, 0.2, 0.2)
        assert f(0.4, 0.4) == Vector(0.2, 0.4, 0.4)
        assert t.intersect(0.6, 0.6) is None

        A = Vector(0, 0, 0)
        C = Vector(0, 1, 0)
        D = Vector(0, 0, 1)
        assert Triangle(A, D, C).intersect(0.25, 0.25) == \
            (Vector(0, 0.25, 0.25), Vector(-1, 0, 0))


# Need tests for BinaryTree
