#!/usr/bin/env python

import cherrypy
import json
import os
import threading
import types

from jinja2 import Environment, PackageLoader

import config
from geom3d import zeroVector
from stl import Stl


BLACK, RED, WHITE = '\x00\x00\x00', '\xff\x00\x00', '\xff\xff\xff'

_filename = _originalStl = _stl = _currentZ = _units = None
_printing = False
_unitScale = _scale = 1.0

logger = config.get_logger('PRINTER')

_projector = None
_stepper = None

env = Environment(loader=PackageLoader('printer', '.'))

os.system('mkdir -p static')

_slices = []


class SliceData:
    def __init__(self, filename, thumbnail, z):
        self.filename, self.thumbnail, self.z = \
            filename, thumbnail, z

    def __cmp__(self, other):
        # sort by descending Z
        return -cmp(self.z, other.z)


def make_slice(stl, z, imagefile, thumbnail):
    bb = stl._bbox
    xmin, xmax = bb._min.x, bb._max.x
    ymin, ymax = bb._min.y, bb._max.y
    x0 = (xmax + xmin) / 2 - 0.5 * config.XYSCALE
    y0 = (ymax + ymin) / 2 - 0.5 * config.XYSCALE
    xs = [(i / 1023.) * config.XYSCALE + x0 for i in range(1024)]
    assert len(xs) == 1024
    ys = [((i + 128) / 1023.) * config.XYSCALE + y0 for i in range(768)]
    assert len(ys) == 768
    outf = open('/tmp/foo.rgb', 'w')

    def pixel_on_callback(n, outf=outf):
        outf.write(n * WHITE)

    def pixel_off_callback(n, outf=outf):
        outf.write(n * BLACK)
    stl.make_layer(z, xs, ys, pixel_on_callback, pixel_off_callback)
    outf.close()
    os.system('convert -size 1024x768 -alpha off ' +
              '-depth 8 /tmp/foo.rgb ' + imagefile)


class UserInterface(object):

    def start(self):
        pass

    def _motorUp(self):
        if _filename is not None:
            return
        logger.debug("motor up")
        _stepper.start(True)

    def _motorDown(self):
        if _filename is not None:
            return
        logger.debug("motor down")
        _stepper.start(False)

    def _motorStop(self):
        if _filename is not None:
            return
        logger.debug("motor stop")
        _stepper.stop()

    def _getScaleInfo(self):
        global _stl, _originalStl
        if _originalStl is not None:
            _stl = _originalStl.scale(_scale * _unitScale)
        dct = {}
        def jsonVector(v):
            v = v or zeroVector
            return {
                'x': v.x,
                'y': v.y,
                'z': v.z
            }
        if _stl is not None:
            dct['min'] = jsonVector(_stl._bbox._min)
            dct['max'] = jsonVector(_stl._bbox._max)
        return dct

    def _scaleInfo(self):
        return json.dumps(self._getScaleInfo())

    def _setScale(self, scale):
        global _scale
        _scale = float(scale)
        return self._scaleInfo()

    def _setUnits(self, units):
        global _units, _unitScale
        _units = units
        if units == 'mm':
            _unitScale = 1.0
        elif units == 'cm':
            _unitScale = 10.0
        elif units == 'inch':
            _unitScale = 25.4
        else:
            raise Exception('Bad units: ' + units)
        return self._scaleInfo()

    def _busyPrinting(self):
        return _printing

    def _getCurrentZ(self):
        dct = self._getScaleInfo()
        assert type(dct) is types.DictType
        if _printing:
            dct['z'] = _currentZ
        return json.dumps(dct)

    def _setModel(self, filename):
        # Yeah, I know, race condition on _filename.
        # This isn't Twitter we're building here.
        global _filename, _originalStl, _stl
        if not _printing:
            _filename = filename
            _originalStl = Stl('models/' + filename)
            _stl = _originalStl.scale(_scale * _unitScale)
        return self._scaleInfo()

    def _print(self, thread=True):
        if _stl is not None:
            if thread:
                # http://stackoverflow.com/questions/17191744
                _thread = threading.Thread(target=print_run)
                _thread.setDaemon(True)
                _thread.start()
            else:
                print_run()


class ServerUI(UserInterface):

    def start(self):
        _config = {
            'global': {
                'server.socket_host': config.SERVER_HOST,
                'server.socket_port': config.SERVER_PORT
            },
            '/static': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': os.getcwd() + '/static'
            }
        }
        cherrypy.quickstart(self, '/', config=_config)

    @cherrypy.expose
    def shutdown(self):
        _projector.shutdown()
        _stepper.shutdown()
        os.system('killall -KILL fbi')
        os.system('killall -KILL python')
        return 'bye\n'

    @cherrypy.expose
    def _motorUp(self):
        super(ServerUI, self)._motorUp()
        return 'ok\n'

    @cherrypy.expose
    def _motorDown(self):
        super(ServerUI, self)._motorDown()
        return 'ok\n'

    @cherrypy.expose
    def _motorStop(self):
        super(ServerUI, self)._motorStop()
        return 'ok\n'

    @cherrypy.expose
    def _setModel(self, filename):
        return super(ServerUI, self)._setModel(filename)

    @cherrypy.expose
    def _print(self):
        return super(ServerUI, self)._print()

    @cherrypy.expose
    def _getCurrentZ(self):
        return super(ServerUI, self)._getCurrentZ()

    @cherrypy.expose
    def _setScale(self, scale):
        return super(ServerUI, self)._setScale(scale)

    @cherrypy.expose
    def _setUnits(self, units):
        return super(ServerUI, self)._setUnits(units)

    @cherrypy.expose
    def _ipaddr(self):
        global _filename
        _filename = "my_ip_addr.png"
        os.system("./gen_ipaddr_image.sh")
        _projector.project(_filename, 5000)
        return 'ok\n'

    @cherrypy.expose
    def index(self):
        def fewer_slices(_, count=[0]):
            count[0] += 1
            return (count[0] % config.THUMBNAIL_MODULO) == 1
        slices = filter(fewer_slices, _slices)
        slices.sort()
        for slice in slices:
            try:
                open('static/' + slice.thumbnail)
            except IOError:
                os.system('convert static/' + slice.filename +
                          ' -geometry 80x60! static/' + slice.thumbnail)
        template = env.get_template('printer.html')
        models = filter(lambda fn: fn.endswith(".stl") or fn.endswith(".STL"),
                        os.listdir(config.MODELS_DIR))
        return template.render(models=models,
                               chosenModel=_filename,
                               units=_units,
                               scale=_scale,
                               refreshTime=3*config.EXPOSURETIME,
                               slices=slices)

    @cherrypy.expose
    def _upload(self, myFile):
        fn = config.MODELS_DIR + '/' + myFile.filename
        assert fn.lower().endswith('.stl')
        # TODO if file exists, add "-1" or "-2" or whatever before ".stl"
        outf = open(fn, 'w')
        while True:
            data = myFile.file.read(8192)
            if not data:
                break
            outf.write(data)
        outf.close()
        raise cherrypy.HTTPRedirect("/")


class NullProjector(object):
    def project(self, filename, milliseconds):
        logger.debug('Projecting {0} for {1} msecs'
                     .format(filename, milliseconds))

    def shutdown(self):
        logger.debug('Projector shutdown')

    def getServer(self):
        return None


class NullStepper(object):
    def start(self, direction):
        logger.debug('Starting stepper, direction={0}'.format(direction))

    def stop(self):
        logger.debug('Stopping stepper')

    def move(self, steps):
        logger.debug('Moving stepper {0} steps'.format(steps))

    def shutdown(self):
        logger.debug('Stepper shutdown')


def print_run():
    global _slices, _filename, _originalStl, _stl, _printing, _currentZ
    if _printing:
        return
    _printing = True
    _slices = []
    logger.debug('Wiping history from previous print')
    os.system('rm -rf static/foo*.png static/thumbnail*.png')
    os.system('mkdir -p static')
    zmin = _stl._bbox._min.z
    zmax = _stl._bbox._max.z
    logger.debug('zmin = {0}'.format(zmin))
    logger.debug('zmax = {0}'.format(zmax))
    _currentZ = zmin + 0.0001
    i = 0
    while _currentZ < zmax - 0.0001:
        fn = 'foo%04d.png' % i
        th = 'thumbnail%04d.png' % i
        i += 1
        make_slice(_stl, _currentZ, 'static/' + fn, 'static/' + th)
        _slices.append(SliceData(fn, th, _currentZ))
        _projector.project(fn, config.EXPOSURETIME)
        _stepper.move(config.STEPS_PER_INCH * config.SLICE_THICKNESS)
        _currentZ += config.SLICE_THICKNESS * config.ZSCALE / _unitScale
    _filename = _originalStl = _stl = None
    _printing = False


if __name__ == "__main__":
    import macbook   # noqa
    import rpi    # noqa
    klass = config.lookup(globals(), config.UI)
    if klass:
        ui = klass()
    klass = config.lookup(globals(), config.PROJECTOR)
    if klass:
        _projector = klass()
        ps = _projector.getServer()
        if ps:
            ui.projector = ps
    klass = config.lookup(globals(), config.STEPPER)
    if klass:
        _stepper = klass()
    logger.debug("Stepper: {0}\nProjector: {1}".format(_stepper, _projector))
    ui.start()
