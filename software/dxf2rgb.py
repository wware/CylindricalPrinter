#!/usr/bin/env python
# -*- coding: utf-8 -*-

import string

BLACK, RED, WHITE = '\x00\x00\x00', '\xff\x00\x00', '\xff\xff\xff'

import config
logger = config.get_logger('DXF2RGB')


class ClosedPath(object):
    def __init__(self):
        self.points = []
        self._max_x = None

    def add(self, x, y):
        self.points.append((x, y))
        return self

    def __repr__(self):
        return '<ClosedPath len={0} first={1}>'.format(
            len(self.points),
            self.points[0])

    def max_x(self):
        """
        DO NOT USE this method before all the points have been
        added! Otherwise the memo array will be prematurely
        populated with a bogus result.
        """
        if self._max_x is not None:
            return self._max_x
        if len(self.points) == 0:
            return None
        result = reduce(max, map(lambda point: point[0],
                                 self.points))
        self._max_x = result
        return result

    def __len__(self):
        return len(self.points)

    def transform(self, T):
        path = ClosedPath()
        path.points = [T(point) for point in self.points]
        return path

    def horizontal_intersections(self, y):
        class ApproximateX:
            def __init__(self, x):
                self.x = x

            def __eq__(self, other):
                return abs(self.x - other.x) < 1.0e-4

            def __repr__(self):
                return repr(self.x)

        def intersect_with_segment(segment, y=y):
            (x1, y1), (x2, y2) = segment
            if not (y1 <= y < y2 or y2 <= y < y1):
                # handle both non-horizontal and y bounding at once
                return None
            return x1 + (y - y1) * (x2 - x1) / (y2 - y1)
        intersections = []
        for segment in zip(self.points[:-1], self.points[1:]):
            x = intersect_with_segment(segment)
            if x is None:
                continue
            I = ApproximateX(x)
            if I not in intersections:
                    intersections.append(I)
        intersections = map(lambda I: I.x, intersections)
        intersections.sort()
        return intersections

    def contains(self, point):
        intersections = self.horizontal_intersections(point[1])
        intersections = filter(lambda x, px=point[0]: x < px, intersections)
        return len(intersections) % 2 == 1

    def containsPath(self, other):
        return len(other.points) > 0 and self.contains(other.points[0])

    def fill(self, color, bitmap, width, height):

        def get_lefties(x, intersections):
            if len(intersections) == 0 or intersections[0] > x:
                return []
            if intersections[-1] < x:
                return intersections
            if len(intersections) == 1:
                return (intersections[0] < x) and intersections or []
            n = len(intersections) / 2
            u, v = intersections[:n], intersections[n:]
            return get_lefties(x, u) + get_lefties(x, v)

        newbitmap = ''
        pixels = 0
        xcenter = ycenter = 0.
        n = 0
        for y in range(height):
            intersections = self.horizontal_intersections(y)
            for x in range(width):
                lefties = get_lefties(x, intersections)
                if len(lefties) & 1 == 1:
                    pixels += 1
                    xcenter += x
                    ycenter += y
                    newbitmap += color
                else:
                    newbitmap += bitmap[n:n+3]    # retain previous color
                n += 3
        return newbitmap


class Dxf2Rgb(object):
    def __init__(self, inf=None):
        self.paths = []
        if inf is None:
            return

        def getNumber(inf=inf):
            return string.atof(inf.readline().strip())

        previous = None
        x1 = y1 = x2 = y2 = None
        state = 0
        path = ClosedPath()
        while True:
            L = inf.readline()
            if not L:
                break
            L = L.strip()
            if L == 'LINE':
                state = 1
            elif state > 0:
                if L == '10':
                    x1 = getNumber()
                elif L == '11':
                    x2 = getNumber()
                elif L == '20':
                    y1 = getNumber()
                elif L == '21':
                    y2 = getNumber()
                    state = 0
                    if (x1, y1) != previous:
                        if previous is not None:
                            self.paths.append(path)
                        path = ClosedPath()
                        path.add(x1, y1)
                    path.add(x2, y2)
                    previous = (x2, y2)
        inf.close()
        if len(path) > 2:
            self.paths.append(path)

    def transform(self, T):
        newguy = Dxf2Rgb()
        newguy.paths = [path.transform(T) for path in self.paths]
        return newguy

    def fill(self, width, height,
             color=WHITE, color2=BLACK, bitmap=None):
        paths = self.paths
        for p in paths:
            p.containers = [
                q for q in paths if q is not p and q.containsPath(p)
            ]
        while True:
            nextLayer = filter(lambda p: len(p.containers) == 0,
                               paths)
            for p in nextLayer:
                bitmap = p.fill(color, bitmap, width, height)
            paths = [
                p for p in paths if p not in nextLayer
            ]
            if len(paths) == 0:
                return bitmap
            for p in paths:
                for q in nextLayer:
                    if q in p.containers:
                        p.containers.remove(q)
            color, color2 = color2, color


def cook_dxf(dxf_in, scalefactor, png_out, red=False):
    import os
    w, h = 1024, 768    # resolution of the projector I bought
    dxf2rgb = Dxf2Rgb(open(dxf_in))
    dxf2rgb = dxf2rgb.transform(lambda (x, y),
                                w=w, h=h, scalefactor=scalefactor:
                                (10 * scalefactor * x + w / 2,
                                 10 * scalefactor * y + h / 2))
    bitmap = (w * h) * BLACK
    bitmap = dxf2rgb.fill(w, h, red and RED or WHITE, BLACK, bitmap)
    open('/tmp/foo.rgb', 'w').write(bitmap)
    os.system('convert -size 1024x768 -alpha off ' +
              '-depth 8 /tmp/foo.rgb ' + png_out)
