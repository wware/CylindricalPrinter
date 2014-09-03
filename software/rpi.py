#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import config
import time
import threading

from printer import NullProjector, NullStepper

try:
    import RPi.GPIO as GPIO
except:
    import mock_rpi as GPIO

logger = config.get_logger('RPI')

STEPPER_TIME = 0.001


class Projector(NullProjector):

    def shutdown(self):
        logger.debug("Projector shutdown")
        self._go_dark()

    def _go_dark(self):
        # project black, and kill any outstanding fbi processes
        cmd = "fbi -S -1 -T 1 -d /dev/fb0 black.png"
        os.system(cmd)
        os.system("killall -KILL fbi")

    def project(self, filename, milliseconds):
        cmd = "fbi -S -1 -T 1 -d /dev/fb0 {0}".format(
            "static/" + filename
        )
        logger.debug(cmd)
        os.system(cmd)
        time.sleep(0.001 * milliseconds)
        self._go_dark()


_running = False
_steps = 0


class Stepper(NullStepper):

    def __init__(self):
        os.system('pip install RPi.GPIO')
        import RPi.GPIO as GPIO
        # http://elinux.org/RPi_Low-level_peripherals#Python
        # GPIO17 is the pulses input of the stepper controller
        # GPIO18 is the direction input
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(17, GPIO.OUT)
        GPIO.setup(18, GPIO.OUT)

    class StepperProgress(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)

        def run(self):
            global _running, _steps
            if not _running:
                _running = True
                logger.debug("Stepper is starting")
                while _running:
                    if _steps == 0:
                        _running = False
                        return
                    GPIO.output(17, GPIO.HIGH)
                    time.sleep(STEPPER_TIME)
                    GPIO.output(17, GPIO.LOW)
                    time.sleep(STEPPER_TIME)
                    _steps -= 1
                logger.debug("Stepper is stopping")

    def start(self, direction):
        global _steps
        NullStepper.start(self, direction)
        if direction:
            GPIO.output(18, GPIO.HIGH)
        else:
            GPIO.output(18, GPIO.LOW)
        _steps = -1
        self.StepperProgress().start()

    def stop(self):
        global _running
        logger.debug("Stop stepper")
        _running = False

    def move(self, steps):
        global _steps
        logger.debug("Move stepper {0} steps".format(steps))
        if steps > 0:
            GPIO.output(18, GPIO.HIGH)
        else:
            steps = -steps
            GPIO.output(18, GPIO.LOW)
        _steps = steps
        sp = self.StepperProgress()
        sp.run()
