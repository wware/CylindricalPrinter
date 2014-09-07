Firmware development
==

The stepper
--

The stepper motor is controlled by an Arduino which communicates with the host machine over a
serial port.

The projector
--

The intended host machine is an Ubuntu laptop. I'm doing preliminary work on a Macbook.

To drive the projector I use a Google Chrome tab that takes up the full screen on the
[extended desktop](http://support.apple.com/kb/HT5019). I need to find out whether the same can be
done on the Ubuntu laptop.

The Chrome tab has a piece of Javascript that fetches two things from a web server also running on the
Macbook. One is a very small text file of metadata, the other is the PNG of the image to be projected.
The metadata gives a stamp as well as the number of milliseconds that the PNG should be projected.

The Javascript expects the stamp to change each time the image changes, and will not show an image if
the stamp hasn't changed.

The Javascript is responsible for the duration for which the image will be projected, because it
hides the image in the DOM at the end of that time, and the background is black. What the JS should do
then is to call an endpoint on the web server to let the server know that it's time to (a) move the
stepper motor one layer height, and (b) change the image file and the metadata file. Or if the print
is done, it should move the stepper to lift the model up out of the liquid.

All this was necessary because I needed two desktops on the Macbook, one for the projector and one for
direct interaction. The RPi will not need the latter. At the moment my idea for projecting from the RPi
(explored in more detail [elsewhere](https://github.com/wware/fbida/blob/master/README.md)) is to use
[fbida](https://www.kraxel.org/blog/linux/fbida/).
