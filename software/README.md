Firmware development
==

Figure out how to document the Python code in a way that a PDF can be extracted easily. Provide profuse
comments explaining everything in detail. Give [Sphinx](http://sphinx-doc.org/tutorial.html) a try.

Whenever you're not projecting an image, it would be nice for the projector to occasionally project the
Raspberry Pi's IP address in red for five seconds. It will help with focusing, and it's
useful to locate the Raspberry Pi on the subnet. It should move around like a screensaver to
minimize the risk of unintentionally curing any resin. It could also include a ruler for calibration
purposes. The screensaver motion should be pausable so that the projected ruler can be compared to a
physical ruler.

The stepper
--

The ugly prototype's stepper is controlled by an Arduino which communicates with the Macbook over a
serial port.

The projector
--

The ugly prototype is controlled by my Macbook Air because I don't yet want to take time to get the
Raspberry Pi working. To drive the projector I decided to use a Google Chrome tab that took up the full
screen on the [extended desktop](http://support.apple.com/kb/HT5019).

The Chrome tab has a piece of Javascript that fetches two things from a web server also running on the
Macbook. One is a very small text file of metadata, the other is the PNG of the image to be projected.
The metadata gives an index as well as the number of milliseconds that the PNG should be projected.

As currently written, the Javascript expects the index to monotonically increase, and will not show an
image if the index is lower than any previously seen index. But really it should just be sure to display
an image any time the index changes, so a 32-bit random number would work as well.

The Javascript is also responsible for the duration for which the image will be projected, because it
hides the image in the DOM at the end of that time, and the background is black. What the JS should do
then is to call an endpoint on the web server to let the server know that it's time to (a) move the
stepper motor one layer height, and (b) change the image file and the metadata file. Or if the print
is done, it should move the stepper to lift the model up out of the liquid.

All this was necessary because I needed two desktops on the Macbook, one for the projector and one for
direct interaction. The RPi will not need the latter. At the moment my idea for projecting from the RPi
(explored in more detail [elsewhere](https://github.com/wware/fbida/blob/master/README.md)) is to use
[fbida](https://www.kraxel.org/blog/linux/fbida/).
