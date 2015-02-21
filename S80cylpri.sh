#!/bin/bash -e

LOGFILE=/home/root/cp-log.txt
rm -f $LOGFILE

mount /mnt/usbstick 2>/dev/null || echo "Can't mount USB stick. Already mounted?" >> $LOGFILE
cd /home/root
echo "Starting cylindrical printer at $(date)" >> $LOGFILE
cd CylindricalPrinter/software
exec python2.7 rpi.py > $LOGFILE 2>&1 &
