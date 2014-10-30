import logging

STEPPER_POLARITY = True
STEPPER_TIME = 0.001

# Things that can go in here:
# * Everything that is a constant in teststl.py
# * Log level for various components
# * Port number, directories

SERVER_HOST = '0.0.0.0'
SERVER_PORT = 8080

# Where to find the Arduino
SERIAL_PORT = '/dev/tty.usbmodem1421'

# Mock out the Arduino, set the exposure time really quick, and project red
# images to avoid curing the resin.
PRACTICE_MODE = False

# One rotation of the nut for the threaded rod is 200 steps. One Z inch is
# 200 * 20 because the threaded rods are 1/4"-20. A slice is 0.01 inches.
STEPS_PER_INCH = 4000
STEPS_PER_SLICE = int(0.01 * STEPS_PER_INCH)

# The idea here is just to wet the top surface of the cured resin with
# fresh uncured resin. No need to travel far.
HYSTERESIS_STEPS = 2 * STEPS_PER_SLICE
POST_MOVE_SETTLING_TIME = 10   # seconds

# This is the XY scale factor, increasing this number makes the projected
# shape smaller linearly. This number of STL units in the X and Y direction
# maps to one projector screen width. The best way to calibrate is to print
# with test objects with known dimensions, and measure the results with a
# micrometer. NOTE - this number will vary with the height of liquid in the
# bucket, as will the focus setting of the projector!
XYSCALE = 244

if PRACTICE_MODE:
    EXPOSURETIME = 1000
else:
    EXPOSURETIME = 60000    # milliseconds

# This is in millimeters, a hundredth of an inch. It's millimeters because all
# the STL dimensions in printer.py are in millimeters, the de-facto standard
# unit for STL files as far as I have seen.
SLICE_THICKNESS = 0.254


def get(attr, globals=globals()):
    return globals.get(attr, None)


def lookup(globals, dottedThing):
    """
    Usage example:
        klass = config.lookup(globals(), config.PROJECTOR)
        _projector = klass()
    """
    fields = dottedThing.split('.')
    thing = globals[fields.pop(0)]
    while fields:
        try:
            thing = getattr(thing, fields.pop(0))
        except AttributeError:
            raise AttributeError("cannot find " + dottedThing)
    return thing

_ch = logging.StreamHandler()
_ch.setFormatter(
    logging.Formatter(
        "%(asctime)s %(name)s %(filename)s:%(lineno)d %(message)s"
    )
)


def get_logger(name, ch=_ch):
    logger = logging.getLogger(name)
    logger.addHandler(ch)
    logger.setLevel(logging.DEBUG)
    return logger
