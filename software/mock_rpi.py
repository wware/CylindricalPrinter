# If no RPi is available, do this.
# http://makezine.com/projects/tutorial-raspberry-pi-gpio-pins-and-python/

import config
logger = config.get_logger("MOCK_RPI")


def doc(name, args):
    logger.debug("{0} {1}".format(name, args))


for name in ('setmode', 'setup', 'output', 'input', 'cleanup',
			 'wait_for_edge', 'add_event_detect', 'remove_event_detect'):
    globals()[name] = lambda *args: doc(name, args)


BCM = None
OUT = None
PUD_UP = None
PUD_DOWN = None
RISING = None
FALLING = None

HIGH = 1
LOW = 0
