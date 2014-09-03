# If no RPi is available, do this.


def _nop(*args):
    pass

setmode = setup = output = _nop

BCM = OUT = HIGH = LOW = None