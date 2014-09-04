import logging
import os

MODELS_DIR = os.getcwd() + '/models'
os.system('mkdir -p ' + MODELS_DIR)

# Things that can go in here:
# * Everything that is a constant in teststl.py
# * Log level for various components
# * Port number, directories

SERVER_HOST = '0.0.0.0'
# You could set the port to 80, but then you need to sudo printer.py and you
# leave junk around owned by root. Too much hassle.
SERVER_PORT = 8080

# When we use red, we can see the image on the resin but the resin
# doesn't get cured. Helpful for alignment, focusing, calibration, etc.
USE_RED = True

# One rotation of the nut for the threaded rod is 450 steps, when I expected
# to see 3600 steps. That's a factor of 8. Hmmm. Anyway, one Z inch is
# 450 * 20 because the threaded rods are 1/4"-20. Still plenty of Z
# resolution.
STEPS_PER_INCH = 9000

# To see fewer thumbnails in the home page, make this number bigger. If you
# want to see every thumbnail, set this to 1.
THUMBNAIL_MODULO = 10

# This is the XY scale factor, increasing this number makes the projected
# shape smaller linearly. This number of STL units in the X and Y direction
# maps to one projector screen width.
XYSCALE = 200

# How many STL units in the Z direction make one inch.
ZSCALE = 40

# EXPOSURETIME = 60000    # milliseconds
EXPOSURETIME = 3000

SLICE_THICKNESS = 0.01

MOCK_ARDUINO = True

# default values
UI = 'UserInterface'
PROJECTOR = 'NullProjector'
STEPPER = 'NullStepper'

UI = 'ServerUI'

# PROJECTOR = 'macbook.Projector'
# STEPPER = 'macbook.Stepper'

# PROJECTOR = 'rpi.Projector'
# STEPPER = 'rpi.Stepper'


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
