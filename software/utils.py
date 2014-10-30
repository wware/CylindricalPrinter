import os
import time
import config

logger = config.get_logger('RPI')

FBI = "/usr/local/bin/fbi"

# This should make it obvious that we want to normalize the config
# stuff between metadata.py on the USB stick and config.py in the
# repository.


class Projector(object):

    def __init__(self):
        self._go_dark()

    def shutdown(self):
        logger.debug("Projector shutdown")
        self._go_dark()

    def _go_dark(self):
        # project black, and kill any outstanding fbi processes
        cmd = FBI + " -S -1 -T 1 -d /dev/fb0 black.png"
        os.system(cmd)
        try:
            os.system("killall -KILL fbi")
        except:
            pass

    def project(self, filename, milliseconds):
        # call blocks until exposure is done
        cmd = FBI + " -S -1 -T 1 -d /dev/fb0 {0}".format(
            "static/" + filename
        )
        logger.debug(cmd)
        os.system(cmd)
        time.sleep(0.001 * milliseconds)
        self._go_dark()


_projector = Projector()


def move(steps):
    logger.debug('stepper move {0}'.format(steps))
    # TODO


def hack_slice(fn, _config=None):
    if _config is not None:
        slice_thickness = _config.SLICE_THICKNESS
        # 20 threads per inch, 200 steps per rotation, 25.4 mm/inch
        MM_PER_STEP = 25.4 / (200 * 20)
        steps_per_slice = slice_thickness / MM_PER_STEP
        hysteresis = _config.HYSTERESIS    # in slices
        exposure_time = _config.EXPOSURE_TIME
        settling_time = _config.SETTLING_TIME
    else:
        steps_per_slice = config.STEPS_PER_SLICE
        hysteresis = config.HYSTERESIS_STEPS / steps_per_slice
        exposure_time = config.EXPOSURETIME
        settling_time = config.POST_MOVE_SETTLING_TIME

    down_steps = -(hysteresis + 1) * steps_per_slice
    up_steps = hysteresis * steps_per_slice
    _projector.project(fn, exposure_time)
    # move down to wet the surface
    move(down_steps)
    if up_steps > 0:
        # move up but not quite as far
        move(up_steps)
    time.sleep(settling_time)
