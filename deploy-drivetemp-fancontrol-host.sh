#! /usr/bin/bash

git pull

systemctl stop drivetemp-fancontrol-host.service

systemctl disable drivetemp-fancontrol-host.service

rm /etc/systemd/system/drivetemp-fancontrol-host.service
#rm -R /opt/drivetemp

cp drivetemp-fancontrol-host.service /etc/systemd/system/

mkdir /opt/drivetemp
cp -avr * /opt/drivetemp/

chmod +x /opt/drivetemp/drivetemp-fancontrol-host.py

systemctl enable drivetemp-fancontrol-host.service

systemctl start drivetemp-fancontrol-host.service

