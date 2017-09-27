#!/bin/sh -e

#
# copy this file to <RASPBERRY>:/home/pi/
# and add the following line to /etc/rc.local (without leading hash)
# /home/pi/startup.sh &
#

sleep 7

cd /home/pi/py2030
python -m py2030.app -y examples/lightCeremony.yml >> /home/pi/log.txt 2>&1 &
