import logging
import os

MODELS_DIR = os.getcwd() + '/models'
os.system('mkdir -p ' + MODELS_DIR)

# Things that can go in here:
# * Everything that is a constant in teststl.py
# * Log level for various components
# * Port number, directories

SERVER_HOST = '0.0.0.0'
SERVER_PORT = 80

# When we use red, we can see the image on the resin but the resin
# doesn't get cured. Helpful for alignment, focusing, calibration, etc.
USE_RED = True

# In case I forget which way I wired the stepper, I have a config bit for
# reversing it without soldering.
STEPPER_POLARITY = True

# How many seconds between level transitions does the stepper need? Looks
# like about a millisecond.
STEPPER_TIME = 0.001

# One rotation of the nut for the threaded rod is 200 steps. One Z inch is
# 200 * 20 because the threaded rods are 1/4"-20.
STEPS_PER_INCH = 4000

# To see fewer thumbnails in the home page, make this number bigger. If you
# want to see every thumbnail, set this to 1.
THUMBNAIL_MODULO = 10

# This is the XY scale factor, increasing this number makes the projected
# shape smaller linearly. This number of STL units in the X and Y direction
# maps to one projector screen width.
XYSCALE = 230

# How many STL units in the Z direction make one inch.
ZSCALE = 40

EXPOSURETIME = 60000    # milliseconds
# EXPOSURETIME = 3000

# This is in inches, because of STEPS_PER_INCH. I should probably move it all
# to millimeters, we'll see if I do that.
SLICE_THICKNESS = 0.01

MOCK_ARDUINO = True

# default values
UI = 'UserInterface'
PROJECTOR = 'NullProjector'
STEPPER = 'NullStepper'

UI = 'ServerUI'

# PROJECTOR = 'macbook.Projector'
# STEPPER = 'macbook.Stepper'

PROJECTOR = 'rpi.Projector'
STEPPER = 'rpi.Stepper'


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
