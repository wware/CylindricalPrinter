#!/usr/bin/env python

import os
import time

from printer import start_projector, stop_projector, UserInterface

os.system('mkdir -p static')

start_projector()
time.sleep(5)

if True:
    ui = UserInterface()
    ui.setModel('models/dodecahedron.stl')
    ui.setScale(0.4)
    ui.Print()

stop_projector()
