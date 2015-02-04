#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""/etc/rc.local should look like this
#!/bin/sh -e
#
# rc.local
#
# This script is executed at the end of each multiuser runlevel.
# Make sure that the script will "exit 0" on success or any other
# value on error.
#
# In order to enable or disable this script just change the execution
# bits.
#
# By default this script does nothing.

# Print the IP address
_IP=$(hostname -I) || true
if [ "$_IP" ]; then
  printf "My IP address is %s\n" "$_IP"
fi

nohup /home/pi/CylindricalPrinter/rpi-startup.sh > \
    /home/pi/startup-log.txt 2>&1 &

exit 0
"""


import os
import sys
import config
import platform
import time

# check /etc/fstab for this
USBSTICK = '/mnt/usbstick'

if platform.uname()[:2] == ('Linux', 'raspberrypi'):
    # os.system('pip install RPi.GPIO')
    import RPi.GPIO as GPIO
    # read metadata.py off USB stick to get parameters
    sys_path = sys.path
    sys.path = [USBSTICK, ] + sys_path
    import metadata
    sys.path = sys_path
    slice_thickness = metadata.SLICE_THICKNESS
else:
    import mock_rpi as GPIO
    # TODO: mock out metadata

logger = config.get_logger('RPI')

FBI = "/usr/bin/fbi"

# http://elinux.org/RPi_Low-level_peripherals#Python
# PULSE is the pulses input of the stepper controller
# DIR is the direction input
PULSE = 14
DIR = 15
LED = 18

DOWN_BUTTON = 23
UP_BUTTON = 24
PRINT_BUTTON = 25

GPIO.setmode(GPIO.BCM)

GPIO.setup(PULSE, GPIO.OUT)
GPIO.setup(DIR, GPIO.OUT)

GPIO.setup(PRINT_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(UP_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(DOWN_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def go_dark():
    # project black, and kill any outstanding fbi processes
    cmd = FBI + " -S -1 -T 1 -d /dev/fb0 black.png"
    os.system(cmd)
    try:
        os.system("killall -KILL fbi")
    except:
        pass


def project(filename, milliseconds):
    # call blocks until exposure is done
    cmd = FBI + " -S -1 -T 1 -d /dev/fb0 {0}".format(
        USBSTICK + "/" + filename
    )
    logger.debug(cmd)
    os.system(cmd)
    time.sleep(0.001 * milliseconds)
    go_dark()


def move(steps):
    GPIO.output(DIR, steps < 0)
    for i in range(abs(int(steps))):
        GPIO.output(PULSE, GPIO.HIGH)
        time.sleep(config.STEPPER_TIME)
        GPIO.output(PULSE, GPIO.LOW)
        time.sleep(config.STEPPER_TIME)


def Print():
    print 'start print'
    # 20 threads per inch, 200 steps per rotation, 25.4 mm/inch
    MM_PER_STEP = 25.4 / (200 * 20)
    steps_per_slice = slice_thickness / MM_PER_STEP
    hysteresis = metadata.HYSTERESIS    # in slices
    exposure_time = metadata.EXPOSURE_TIME
    settling_time = metadata.SETTLING_TIME
    down_steps = -(hysteresis + 1) * steps_per_slice
    up_steps = hysteresis * steps_per_slice
    print 'entering loop'

    for i in range(metadata.NUM_SLICES):
        fn = metadata.FILENAME_TEMPLATE % i
        print fn, 'begin'
        project(fn, exposure_time)
        move(down_steps)
        if hysteresis:
            time.sleep(settling_time)
            move(up_steps)
        time.sleep(settling_time)
        print fn, 'end'

    return i


def up_down_button(button):
    # consider a lock to keep this guy inert when printing
    print button, 'press'
    GPIO.output(DIR, button == UP_BUTTON)
    while not GPIO.input(button):
        GPIO.output(PULSE, GPIO.HIGH)
        time.sleep(config.STEPPER_TIME)
        GPIO.output(PULSE, GPIO.LOW)
        time.sleep(config.STEPPER_TIME)
    print button, 'release'


if False:
    try:
        Print()
    except KeyboardInterrupt:
        go_dark()
    raise SystemExit

go_dark()

try:
    while True:
        if not GPIO.input(PRINT_BUTTON):
            Print()
        elif not GPIO.input(UP_BUTTON):
            up_down_button(UP_BUTTON)
        elif not GPIO.input(DOWN_BUTTON):
            up_down_button(DOWN_BUTTON)

except KeyboardInterrupt:
    go_dark()
    GPIO.output(PULSE, GPIO.LOW)
    GPIO.output(DIR, GPIO.LOW)
    GPIO.output(LED, GPIO.LOW)
