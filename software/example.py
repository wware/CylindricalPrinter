#!/usr/bin/env python

import os
import sys
import time

import config

from printer import start_projector, stop_projector, UserInterface

MODEL = 'models/dodecahedron.stl'
# MODEL = 'models/smallish.stl'

REAL = sys.argv[1:2] == ['real']

if REAL:
    start_projector()
    time.sleep(5)

ui = UserInterface()

def go():
    ui.setModel(MODEL)
    ui.setScale(1)
    ui.Print()

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
    stop_projector()
