Stuff left to do
==

* Add an input for scale. Slider and text window, they update each other. Reset button to go back to 1.0.
* Add a checkbox for inches versus millimeters versus centimeters. Separate multiplier on top of the scale input.
* File chooser and uploader for STLs: http://stackoverflow.com/questions/10997263/html-file-picker-with-jquery

Stuff for the RPi
--

First do this on the RPi

```bash
sudo apt-get update
sudo apt-get install -y git vim python-dev python-virtualenv \
    imagemagick build-essential
git clone https://github.com/wware/CylindricalPrinter.git
(cd fbida && make && sudo make install)
git clone https://github.com/wware/CylindricalPrinter.git
cd CylindricalPrinter/software
```
