#!/bin/sh

mount /mnt/usbstick || exit 1
cd /home/root
echo "Starting cylindrical printer at $(date)" > T.txt
cd CylindricalPrinter/software
exec python2.7 rpi.py &
