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

if config.PRACTICE_MODE:
    WHITE = RED

logger = config.get_logger('PRINTER')


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
        env = Environment(loader=PackageLoader('printer', '.'))
        template = env.get_template('projector.html')
        return template.render()

    @cherrypy.expose
    def finished(self):
        ProjectorState.getInstance().done = True

    @cherrypy.expose
    def image(self):
        imagefile = ProjectorState.getInstance().imagefile
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


class UserInterface(object):

    def __init__(self):
        self.filename = self.originalStl = self.stl = self.currentZ = None
        self.printing = False
        self.stlDirty = True
        self.unitScale = self.scale = 1.0
        self.ser = None
        if not config.PRACTICE_MODE:
            try:
                self.ser = serial.Serial(config.SERIAL_PORT, 9600, timeout=0)
            except:
                pass

    def _start(self, direction):
        logger.debug('stepper start {0}'.format(direction))
        if self.ser is not None:
            self.ser.write(direction and 'P' or 'N')

    def move(self, steps):
        logger.debug('stepper move {0}'.format(steps))
        if self.ser is not None:
            self.ser.write(str(steps) + '\n')
            self.ser.readline()   # wait for "OK"

    def up(self):
        if not self.printing:
            self._start(True)

    def down(self):
        if not self.printing:
            self._start(False)

    def stop(self):
        if not self.printing:
            logger.debug("stepper stop")
            if self.ser is not None:
                self.ser.write('S')
                self.stepper.stop()

    def getZInfo(self):
        dct = {}

        def v2d(v):
            v = v or zeroVector
            return {
                'x': v.x,
                'y': v.y,
                'z': v.z
            }
        if self.originalStl is not None:
            if self.stlDirty:
                self.stl = self.originalStl.scale(self.scale * self.unitScale)
                self.stlDirty = False
            dct['min'] = v2d(self.stl._bbox._min)
            dct['max'] = v2d(self.stl._bbox._max)
        if self.printing:
            dct['z'] = self.currentZ
        return dct

    def setScale(self, scale):
        self.scale = float(scale)
        self.stlDirty = True
        return self.getZInfo()

    def setUnits(self, units):
        # default is millimeters, the units (afaik) for most STL files
        if units == 'mm':
            self.unitScale = 1.0
        elif units == 'cm':
            self.unitScale = 10.0
        elif units == 'inch':
            self.unitScale = 25.4
        else:
            raise Exception('Bad units: ' + units)
        self.stlDirty = True
        return self.getZInfo()

    def isPrinting(self):
        return self.printing and "yes" or "no"

    def setModel(self, filename):
        if not self.printing:
            self.stl = self.originalStl = None
            self.filename = filename
            self.originalStl = Stl(filename)
            self.stlDirty = True
        return self.getZInfo()

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

    def make_slice(self, stl, z, imagefile):
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

    def Print(self):
        if self.printing or self.originalStl is None:
            self.printing = False
            return
        self.printing = True
        if self.stl is None or self.stlDirty:
            self.stl = self.originalStl.scale(self.x * self.unitScale)
            self.stlDirty = False
        os.system('rm -rf images')
        os.system('mkdir -p images')
        zmin = self.stl._bbox._min.z
        zmax = self.stl._bbox._max.z
        logger.debug('zmin = {0}'.format(zmin))
        logger.debug('zmax = {0}'.format(zmax))
        self.currentZ = zmin + 0.0001
        i = 0
        while self.currentZ < zmax - 0.0001:
            fn = 'images/foo%04d.png' % i
            i += 1
            self.make_slice(self.stl, self.currentZ, fn)
            self.project(fn, config.EXPOSURETIME)
            # move down to wet the surface
            self.move(-(config.HYSTERESIS_STEPS +
                        config.STEPS_PER_SLICE))
            if config.HYSTERESIS_STEPS > 0:
                # move up but not quite as far
                self.move(config.HYSTERESIS_STEPS)
            time.sleep(config.POST_MOVE_SETTLING_TIME)
            self.currentZ += config.SLICE_THICKNESS / self.unitScale
        self.filename = self.originalStl = self.stl = None
        self.printing = False
