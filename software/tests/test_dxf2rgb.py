import os
from dxf2rgb import ClosedPath, Dxf2Rgb, BLACK, WHITE, cook_dxf

OPENSCAD = '/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD'


class TestClosedPath(object):

    def test_contains(self):
        path = ClosedPath().add(0, 0).add(2, 0).add(2, 2).add(0, 2).add(0, 0)
        assert path.contains((1, 1))
        assert not path.contains((3, 1))
        assert not path.contains((1, 3))

    def test_containsPath(self):
        path = ClosedPath().add(0, 0).add(3, 0).add(3, 3).add(0, 3).add(0, 0)
        path2 = ClosedPath().add(1, 1).add(2, 1).add(2, 2).add(1, 2).add(1, 1)
        assert path.containsPath(path2)
        assert not path2.containsPath(path)


class TestDxf2rgb(object):

    def test_slicing(self):
        inf = open('tests/simple.dxf')
        dxf2rgb = Dxf2Rgb(inf)
        dxf2rgb = dxf2rgb.transform(lambda (x, y):
                                    (200 * x + 512, 200 * y + 384))
        assert len(dxf2rgb.paths) == 2
        w, h = 1024, 768
        bitmap = (w * h) * BLACK
        bitmap = dxf2rgb.fill(w, h, WHITE, BLACK, bitmap)
        open('foo.rgb', 'w').write(bitmap)
        assert os.popen('md5 foo.rgb').read().strip() \
            .endswith('0ffbd045e71afbee0d6554d748a586e6')
        os.system('rm -f foo.rgb')


def test_cook_dxf():
    cook_dxf('tests/simple.dxf', 3**.5, 'foo.png')
    # remove end stuff to get consistent MD5 of just the image
    # end stuff includes create and update timestamps, which change
    os.system('split -b 296 foo.png')
    md5 = os.popen('md5 xaa').read().strip()
    assert md5.endswith('17a4e0376ed7ddb60fcba146786b26a2')
    os.system('rm -f foo.png xaa xab')
