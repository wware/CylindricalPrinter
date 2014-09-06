Firmware development
==

Change of direction
--
Circumstances allow me only a couple more days of work on this project. This is a major
simplification of things. Using a Raspberry Pi as a controller for the printer seemed like
a great idea initially, giving the printer networking ability, a lot of autonomy, a
capacity for complex behavior, etc.

But the RPi brought a lot of problems with it. It's a pain to interact with. Maintaining a
network is challenging if it's not near an Ethernet cable or a wifi router. When I slice a
STL file on the RPi, it's very slow, and I was giving serious thought to refactoring
`geom3d.py` and `stl.py` as C extensions to speed it up. Basically the RPi has been a drag
on my development effort.

The Python code for slicing STLs works fine on a laptop. My earlier scheme of using an
Arduino to control the stepper motor also works fine, and requires only that the Arduino
to be no more than a USB-cable-length away from the laptop. The laptop can drive the
projector; I did this with the earlier prototype using a Macbook and while I'll be using
a Linux laptop going forward it should still work fine.

So here's the change of direction. Drive the projector directly from the Linux laptop, and
use the Arduino controlled via USB-serial to move the stepper. The Raspberry Pi is gone.
It's a big change, but it should make the next couple days much more productive.

One other thing that will be changing is that the web UI is probably going to be replaced
by a command line UI since it's on a laptop. I can probably still use a web server to run the
projector, if my experience on the Macbook is an indication. The laptop has Linux Mint
installed (and if I switch, it will be to some other Ubuntu flavor) so this seems relevant:

* http://www.ubuntubuzz.com/2011/12/how-to-dual-monitor-setup-on-xfce.html

Previously
--
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
