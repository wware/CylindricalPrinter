import logging

# Things that can go in here:
# * Everything that is a constant in teststl.py
# * Log level for various components
# * Port number, directories

SERVER_HOST = '0.0.0.0'
SERVER_PORT = 8000

# When we use red, we can see the image on the resin but the resin
# doesn't get cured. Helpful for alignment, focusing, calibration, etc.
USE_RED = True

# It seems like one rotation of the threaded rod is around 450 steps. Why
# should that be? I thought it should be 3600 steps. That's a factor of 8.
# Hmmmm. Anyway, one inch is then 450*20 = 9000
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

PROJECTOR = 'NullProjector'

STEPPER = 'NullStepper'

MOCK_ARDUINO = True

PROJECTOR = 'macbook.Projector'
# STEPPER = 'macbook.Stepper'

# PROJECTOR = 'rpi.Projector'
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
