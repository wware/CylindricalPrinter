Electronics for the cylindrical printer
==

The electronics will include the following, mounted in some semi-professional-looking manner.

* a power strip with a long cord
* the 12 volt switching supply
* the green 5 volt thing
* the stepper controller
* the RPi, with the HDMI connector facing up to the open top of the milk crate
* a board with LEDs for the STEP and DIR, and with pushbuttons for UP and DOWN
* a USB hub for the RPi
* possibly an Ethernet switch
* Internal 4-position terminal strip: +5, GND, STEP, DIR
* external 8-position terminal strip: +12, +5, GND, A+, A-, B+, B-, LIMIT
* possibly a keypad and LCD display for the Raspberry Pi

Use spade terminals for the terminal strips, and keep a few spare spade terminals handy.
Maybe those pushbuttons go on the external terminal strip.

I also need the projector, obviously.

Set up the Raspberry Pi to be able to read a USB stick to avoid need for a laptop.

Early on, I had trouble getting the stepper motor to work correctly, and so while printing that octohedron, I
rotated by hand the threaded rod that lowered the build platform into the liquid. Since then I've gotten the
stepper motor to behave with the following pieces. This was a big source of frustration; two or three other
stepper drivers didn't work out.

* CNC Single Axis TB6600 Stepper Controller, part number HY-DIV268N-5A (check Alibaba.com or Aliexpress.com)
* LIHUA 120W (12v, 10 amp) Regulated Switching Power Supply (also see Alibaba.com, Aliexpress.com)
* NEMA-23 motor, part number
  [266-F4.2A-1](http://www.hubbardcnc.com/index.php?main_page=product_info&products_id=362),
  125 oz-in (probably massive overkill)
