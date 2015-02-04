import os
import re
import string
import struct
import types

from geom3d import Triangle, BBox, Vector, BinaryTree

import config
logger = config.get_logger('STL')

BLACK, RED, WHITE = '\x00\x00\x00', '\xff\x00\x00', '\xff\xff\xff'


class Stl:
    def __init__(self, *args):
        if type(args[0]) in (types.StringType, types.UnicodeType):
            self.filename = args[0]
            self.triangles = []
            inf = open(self.filename)
            triangleList = self.from_input_file(inf)
        else:
            self.filename = self.preamble = ''
            triangleList = args
        self.triangles = triangleList
        bb = BBox()
        for tri in triangleList:
            bb = bb.expand(tri._bbox)
        self._bbox = bb
        self._classify_triangles_by_z()

    def from_input_file(self, inf):
        triangleList = []
        R = inf.read()
        words = re.split('\W+', R)
        if 'facet' in words and 'normal' in words and 'vertex' in words:
            # this is an ASCII STL file
            del words
            lines = re.split('\n', R)
            self.preamble = lines.pop(0)
            while lines:
                line = lines.pop(0).strip()
                words = re.split('[ \t]+', line)
                if words[0] == 'endsolid':
                    break
                assert words[0] == 'facet' and words[1] == 'normal', words
                normal = Vector(string.atof(words[2]),
                                string.atof(words[3]),
                                string.atof(words[4]))
                vertices = []
                line = lines.pop(0).strip()
                assert line == 'outer loop', line
                for i in range(3):
                    line = lines.pop(0).strip()
                    words = re.split('[ \t]+', line)
                    assert words[0] == 'vertex', words
                    vertex = Vector(string.atof(words[1]),
                                    string.atof(words[2]),
                                    string.atof(words[3]))
                    vertices.append(vertex)
                line = lines.pop(0).strip()
                assert line == 'endloop', line
                line = lines.pop(0).strip()
                assert line == 'endfacet', line
                tri = apply(Triangle, vertices + [normal])
                triangleList.append(tri)
        else:
            # this is a binary STL file
            self.preamble = ''.join(filter(lambda ch: ch != '\0',
                                           list(R[:80])))
            R = R[80:]
            numTriangles, R = struct.unpack('I', R[:4])[0], R[4:]
            for i in range(numTriangles):
                tri, R = self.triangle_from_string(R)
                triangleList.append(tri)
        return triangleList

    @classmethod
    def triangle_from_string(cls, str):
        assert len(str) >= 50
        bytes, str = str[:50], str[50:]
        coords = struct.unpack('ffffffffffffH', bytes)
        normal = Vector(coords[:3])
        vertex1 = Vector(coords[3:6])
        vertex2 = Vector(coords[6:9])
        vertex3 = Vector(coords[9:12])
        t = Triangle(vertex1, vertex2, vertex3, normal)
        return (t, str)

    @classmethod
    def unserialize(cls, str):
        f, p, t = str.split(':::')
        triangles = map(Triangle.unserialize, t.split('&&'))
        stl = apply(Stl, triangles)
        stl.filename = f
        stl.preamble = p
        return stl

    def serialize(self):
        return ':::'.join([
            self.filename,
            self.preamble,
            '&&'.join([Triangle.serialize(t) for t in self.triangles])
        ])

    def bbox(self):
        return self._bbox

    def __repr__(self):
        return '<Stl "{0}" {1} triangles>'.format(self.filename,
                                                  len(self.triangles))

    def scale(self, scalefactor):
        triangles = tuple(map(lambda tri, sf=scalefactor: tri.scale(sf),
                              self.triangles))
        stl = apply(Stl, triangles)
        stl.filename = self.filename
        stl.preamble = self.preamble
        return stl

    def _classify_triangles_by_z(self):
        zmin, zmax = self._bbox._min.z, self._bbox._max.z
        n = 100
        dz = (1. * zmax - zmin) / n
        self._zmap = {}

        def z_quantize(z, zmin=zmin, dz=dz, n=n):
            i = int((z - zmin) / dz)
            return max(0, min(n - 1, i))
        self._z_quantize = z_quantize
        for i in range(n):
            self._zmap[i] = []
            z0 = zmin + i * dz
            z1 = z0 + dz
            for tri in self.triangles:
                if tri._bbox.z_overlap(z0, z1):
                    self._zmap[i].append(tri)

    def get_point_list(self, y, z, ztriangles=None):
        if ztriangles is None:
            ztriangles = self.triangles
        xs = BinaryTree(lambda intersection: intersection[0].x)
        for triangle in ztriangles:
            if triangle._bbox.contains_yz(y, z):
                xs.binary_insert(triangle.intersect(y, z))
        return xs.to_list()

    def make_layer(self, z, xvalues, yvalues,
                   pixel_on_callback, pixel_off_callback):
        x0, dx, n = xvalues[0], xvalues[1] - xvalues[0], len(xvalues)
        i = self._z_quantize(z)
        zt = self._zmap[i]   # triangles found at this z value
        for y in yvalues:
            points = self.get_point_list(y, z, zt)
            h = 0
            for point in points:
                i = int((point[0].x - x0) / dx)
                i = max(h, min(i, n))
                if i > h:
                    if point[1].x > 0:
                        pixel_on_callback(i - h)
                    else:
                        pixel_off_callback(i - h)
                h = i
            pixel_off_callback(n - h)

    def make_slice(self, z, imagefile):
        W, H = 1024, 768    # projector resolution
        assert W >= H       # projector must be landscape mode
        bb = self._bbox
        xmin, xmax = bb._min.x, bb._max.x
        ymin, ymax = bb._min.y, bb._max.y
        x0 = (xmax + xmin) / 2 - 0.5 * config.XSCALE
        y0 = (ymax + ymin) / 2 - 0.5 * config.YSCALE
        outf = open('/tmp/foo.rgb', 'w')

        def pixel_on_callback(n, outf=outf):
            outf.write(n * WHITE)

        def pixel_off_callback(n, outf=outf):
            outf.write(n * BLACK)
        self.make_layer(
            z,
            [(1. * i / (W - 1)) * config.XSCALE + x0
             for i in range(W)],
            [((i + 0.5 * (W - H)) / (W - 1)) * config.YSCALE + y0
             for i in range(H)],
            pixel_on_callback,
            pixel_off_callback)
        outf.close()
        os.system('convert -size {}x{} -alpha off -depth 8 /tmp/foo.rgb {}'
                  .format(W, H, imagefile))

    def slices(self, hack_slice=None):
        os.system('rm -rf images')
        os.system('mkdir -p images')
        zmin = self._bbox._min.z
        zmax = self._bbox._max.z
        currentZ = zmin + 0.0001
        i = 0
        while currentZ < zmax - 0.0001:
            fn = 'images/foo%04d.png' % i
            i += 1
            self.make_slice(currentZ, fn)
            if hack_slice is not None:
                hack_slice(fn)
            currentZ += config.SLICE_THICKNESS
        return i
