#! /usr/bin/bash

git pull

systemctl stop drivetemp-fancontrol-local.service

systemctl disable drivetemp-fancontrol-local.service

rm /etc/systemd/system/drivetemp-fancontrol-local.service
#rm -R /opt/drivetemp

cp drivetemp-fancontrol-local.service /etc/systemd/system/

mkdir /opt/drivetemp
cp -avr * /opt/drivetemp/

chmod +x /opt/drivetemp/drivetemp-fancontrol-local.py

systemctl enable drivetemp-fancontrol-local.service

systemctl start drivetemp-fancontrol-local.service

