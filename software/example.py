#!/usr/bin/env python

import os
import time

from printer import start_projector, stop_projector, UserInterface

os.system('mkdir -p static')

start_projector()

ui = UserInterface()

time.sleep(2)
ui.motorMove(200)
time.sleep(2)

stop_projector()
