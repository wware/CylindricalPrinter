# If no RPi is available, do this.

import config
logger = config.get_logger("MOCK_RPI")


def doc(name, args):
    logger.debug("{0} {1}".format(name, args))


for name in ('setmode', 'setup', 'output'):
    globals()[name] = lambda *args: doc(name, args)

BCM = OUT = None
HIGH = 1
LOW = 0
