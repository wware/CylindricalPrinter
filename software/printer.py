import cherrypy
import json
import os
import random
import serial
import threading
import time

from cherrypy import HTTPError
from jinja2 import Environment, PackageLoader

import config
from geom3d import zeroVector
from stl import Stl


BLACK, RED, WHITE = '\x00\x00\x00', '\xff\x00\x00', '\xff\xff\xff'

# as much as possible, make these class or instance variables, not globals
_filename = _originalStl = _stl = _currentZ = _units = None
_printing = False
_stlDirty = True
_unitScale = _scale = 1.0

logger = config.get_logger('PRINTER')

projector = None
stepper = None

env = Environment(loader=PackageLoader('printer', '.'))

_slices = []


class ProjectorState:
    instance = None

    def __init__(self, stamp, imagefile, duration, done):
        self.stamp, self.imagefile, self.duration, self.done = \
            stamp, imagefile, duration, done

    @classmethod
    def getInstance(cls):
        if cls.instance is None:
            cls.instance = ProjectorState(None, None, None, True)
        return cls.instance

    @classmethod
    def setInstance(cls, stamp, imagefile, duration, done):
        cls.instance = ProjectorState(stamp, imagefile, duration, done)


class Projector(object):

    def project(self, filename, milliseconds):
        logger.debug('project ' + filename + ' ' + str(milliseconds))
        ProjectorState.setInstance(
            random.randint(1, 1000000000),
            filename,
            int(milliseconds),
            False
        )
        while not ProjectorState.getInstance().done:
            time.sleep(0.5)

    def getServer(self):
        return ProjectorServer()


class Stepper(object):

    def __init__(self):
        self.ser = None
        if not config.MOCK_ARDUINO:
            try:
                self.ser = serial.Serial(config.SERIAL_PORT, 9600, timeout=0)
            except:
                pass

    def start(self, direction):
        logger.debug('stepper start {0}'.format(direction))
        if self.ser is not None:
            self.ser.write(direction and 'P' or 'N')

    def stop(self):
        logger.debug('stepper stop')
        if self.ser is not None:
            self.ser.write('S')

    def move(self, steps):
        logger.debug('stepper move {0}'.format(steps))
        if self.ser is not None:
            self.ser.write(str(steps + '\n'))
            self.ser.readline()   # wait for "OK"


class UserInterface(object):

    def __init__(self):
        self.projector = Projector()
        self.stepper = Stepper()

    def motorUp(self):
        if not _printing:
            logger.debug("motor up")
            self.stepper.start(True)

    def motorDown(self):
        if not _printing:
            logger.debug("motor down")
            self.stepper.start(False)

    def motorStop(self):
        if not _printing:
            logger.debug("motor stop")
            self.stepper.stop()

    def motorMove(self, n):
        if not _printing:
            logger.debug("motor move {0}".format(n))
            self.stepper.move(n)

    def getZInfo(self):
        global _stl, _originalStl, _stlDirty
        dct = {}

        def jsonVector(v):
            v = v or zeroVector
            return {
                'x': v.x,
                'y': v.y,
                'z': v.z
            }
        if _originalStl is not None:
            if _stlDirty:
                _stl = _originalStl.scale(_scale * _unitScale)
                _stlDirty = False
            dct['min'] = jsonVector(_stl._bbox._min)
            dct['max'] = jsonVector(_stl._bbox._max)
        if _printing:
            dct['z'] = _currentZ
        return json.dumps(dct)

    def setScale(self, scale):
        global _scale, _stlDirty
        _scale = float(scale)
        _stlDirty = True
        return self._getZInfo()

    def setUnits(self, units):
        global _units, _unitScale, _stlDirty
        _units = units
        if units == 'mm':
            _unitScale = 1.0
        elif units == 'cm':
            _unitScale = 10.0
        elif units == 'inch':
            _unitScale = 25.4
        else:
            raise Exception('Bad units: ' + units)
        _stlDirty = True
        return self._getZInfo()

    def isPrinting(self):
        return _printing and "yes" or "no"

    def getCurrentZ(self):
        dct = self._getScaleInfo()
        assert isinstance(dct, dict)
        if _printing:
            dct['z'] = _currentZ
        return json.dumps(dct)

    def setModel(self, filename):
        # Yeah, I know, race condition on _filename.
        # This isn't Twitter we're building here.
        global _filename, _originalStl, _stl, _stlDirty
        if not _printing:
            _stl = _originalStl = None
            _filename = filename
            _originalStl = Stl('models/' + filename)
            _stlDirty = True
        return self._getZInfo()

    def Print(self, thread=True):
        global _filename, _originalStl, _stl, _stlDirty
        if thread:
            # http://stackoverflow.com/questions/17191744
            _thread = threading.Thread(target=self.print_run)
            _thread.setDaemon(True)
            _thread.start()
        else:
            self.print_run()

    def make_slice(self, stl, z, imagefile, thumbnail):
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

    def print_run(self):
        global _slices, _filename, _originalStl, _stl
        global _stlDirty, _printing, _currentZ
        if _printing or _originalStl is None:
            _printing = False
            return
        _printing = True
        if _stl is None or _stlDirty:
            _stl = _originalStl.scale(_scale * _unitScale)
            _stlDirty = False
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
            self.make_slice(_stl, _currentZ, 'static/' + fn, 'static/' + th)
            _slices.append(SliceData(fn, th, _currentZ))
            self.projector.project(fn, config.EXPOSURETIME)
            # move up
            self.stepper.move(config.HYSTERESIS_STEPS)
            time.sleep(0.5)
            # move down a little further
            self.stepper.move(-(config.HYSTERESIS_STEPS + config.STEPS_PER_SLICE))
            _currentZ += config.SLICE_THICKNESS * config.ZSCALE / _unitScale
        _filename = _originalStl = _stl = None
        _printing = False


class ProjectorServer(object):

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
    def index(self):
        template = env.get_template('projector.html')
        return template.render()

    @cherrypy.expose
    def finished(self):
        ProjectorState.getInstance().done = True

    @cherrypy.expose
    def image(self):
        imagefile = os.getcwd() + '/static/' + \
            ProjectorState.getInstance().imagefile
        logger.debug('IMAGE ' + imagefile)
        cherrypy.response.headers['Cache-Control'] = \
            'no-cache, no-store, must-revalidate'
        cherrypy.response.headers['Pragma'] = 'no-cache'
        cherrypy.response.headers['Expires'] = '-1'
        try:
            return open(imagefile, 'r').read()
        except Exception, e:
            logger.debug(e)
            raise HTTPError('404 Not Found')

    @cherrypy.expose
    def info(self):
        pstate = ProjectorState.getInstance()
        if pstate.stamp is None:
            logger.debug('INFO NOPE')
            return 'NOPE'
        logger.debug('INFO ' + str(pstate.stamp) +
                     ' ' + str(pstate.done))
        return (str(pstate.stamp) + ' ' +
                str(pstate.duration))


class SliceData:
    def __init__(self, filename, thumbnail, z):
        self.filename, self.thumbnail, self.z = \
            filename, thumbnail, z

    def __cmp__(self, other):
        # sort by descending Z
        return -cmp(self.z, other.z)


def start_projector(thread=True):
    def pstart():
        ProjectorServer().start()

    if thread:
        # http://stackoverflow.com/questions/17191744
        _thread = threading.Thread(target=pstart)
        _thread.setDaemon(True)
        _thread.start()
    else:
        pstart()


def stop_projector():
    from cherrypy import process
    process.bus.exit()
