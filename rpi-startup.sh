#!/bin/bash
# This runs from /etc/rc.local on the Raspberry Pi, see
# http://www.raspberry-projects.com/pi/pi-operating-systems/raspbian/scripts
#
# Added the line:
# nohup /home/pi/CylindricalPrinter/rpi-startup.sh > /home/pi/startup-log.txt 2>&1 &

cd /home/pi/CylindricalPrinter/software

if [ ! -d venv ]
then
    virtualenv venv || exit 1
fi

source venv/bin/activate
pip install -r requirements.txt
python printer.py
