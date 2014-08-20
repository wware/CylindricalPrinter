#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import config
import time
from printer import NullProjector, NullStepper

logger = config.get_logger('RPI')


class Projector(NullProjector):

    def shutdown(self):
        logger.debug("Projector shutdown")
        self._go_dark()

    def _go_dark(self):
        # project black, and kill any outstanding fbi processes
        cmd = "sudo fbi -S -1 -T 1 -d /dev/fb0 black.png"
        os.system(cmd)
        os.system("sudo killall -KILL fbi")

    def project(self, filename, milliseconds):
        cmd = "sudo fbi -S -1 -T 1 -d /dev/fb0 {0}".format(
            "static/" + filename
        )
        logger.debug(cmd)
        os.system(cmd)
        time.sleep(0.001 * milliseconds)
        self._go_dark()


class Stepper(NullStepper):

    def __init__(self):
        raise "Not implemented yet"

    def start(self, direction):
        raise "Not implemented yet"

    def stop(self):
        raise "Not implemented yet"

    def move(self, steps):
        raise "Not implemented yet"
