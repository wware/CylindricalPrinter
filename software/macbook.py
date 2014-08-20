#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cherrypy
import config
import os
import random
import serial
import time

from cherrypy import HTTPError
from jinja2 import Environment, PackageLoader

from printer import NullProjector, NullStepper

logger = config.get_logger('MACBOOK')
env = Environment(loader=PackageLoader('printer', '.'))


class ProjectorState:
    def __init__(self, stamp, imagefile, duration, done):
        self.stamp, self.imagefile, self.duration, self.done = \
            stamp, imagefile, duration, done

_projector_state = ProjectorState(None, None, None, True)


class ProjectorServer(object):

    @cherrypy.expose
    def index(self):
        template = env.get_template('macbook.html')
        return template.render()

    @cherrypy.expose
    def finished(self):
        _projector_state.done = True

    @cherrypy.expose
    def image(self):
        imagefile = os.getcwd() + '/static/' + _projector_state.imagefile
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
        if _projector_state.stamp is None:
            logger.debug('INFO NOPE')
            return 'NOPE'
        logger.debug('INFO ' + str(_projector_state.stamp) +
                     ' ' + str(_projector_state.done))
        return (str(_projector_state.stamp) + ' ' +
                str(_projector_state.duration))


class Projector(NullProjector):

    def project(self, filename, milliseconds):
        global _projector_state
        logger.debug('project ' + filename + ' ' + str(milliseconds))
        _projector_state = ProjectorState(
            random.randint(1, 1000000000),
            filename,
            int(milliseconds),
            False
        )
        while not _projector_state.done:
            time.sleep(0.5)

    def getServer(self):
        return ProjectorServer()


class Stepper(NullStepper):

    def __init__(self):
        if config.MOCK_ARDUINO:
            self.ser = None
        else:
            self.ser = serial.Serial('/dev/tty.usbmodem1421', 9600, timeout=0)

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
