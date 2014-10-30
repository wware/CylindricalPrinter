#!/usr/bin/env python

import sys

import config

from printer import UserInterface

MODEL = 'models/dodecahedron.stl'
# MODEL = 'models/smallish.stl'

REAL = sys.argv[1:2] == ['real']

if REAL:
    # start_projector()
    # time.sleep(5)
    pass

ui = UserInterface()

_format = """\
SLICE_THICKNESS = {0}
NUM_SLICES = {1}
HYSTERESIS = {2}
EXPOSURE_TIME = {3}
SETTLING_TIME = {4}
FILENAME_TEMPLATE = "{5}"
"""


def go():
    ui.setModel(MODEL)
    ui.setScale(1)
    # num_slices = ui.Print()
    num_slices = ui.slices()
    P = _format.format(
        config.SLICE_THICKNESS,
        num_slices,
        config.HYSTERESIS_STEPS / config.STEPS_PER_SLICE,
        config.EXPOSURETIME,
        config.POST_MOVE_SETTLING_TIME,
        'images/foo%04d.png')
    open('metadata.py', 'w').write(P)


def U(n=1):
    ui.move(int(config.STEPS_PER_INCH * n))


def D(n=1):
    ui.move(int(-config.STEPS_PER_INCH * n))


def stir():
    for i in range(10):
        ui.move(-16000)
        ui.move(16000)

if REAL:
    go()
    # stop_projector()
