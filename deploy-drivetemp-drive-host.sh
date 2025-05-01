#! /usr/bin/bash

git pull

systemctl stop drivetemp-drive-host-0.service
systemctl stop drivetemp-drive-host-1.service

systemctl disable drivetemp-drive-host-0.service
systemctl disable drivetemp-drive-host-1.service

rm /etc/systemd/system/drivetemp-drive-host-0.service
rm /etc/systemd/system/drivetemp-drive-host-1.service
#rm -R /opt/drivetemp

cp drivetemp-drive-host-0.service /etc/systemd/system/
cp drivetemp-drive-host-1.service /etc/systemd/system/

mkdir /opt/drivetemp
cp -avr * /opt/drivetemp/

chmod +x /opt/drivetemp/drivetemp-drive-host.py

systemctl enable drivetemp-drive-host-0.service
systemctl enable drivetemp-drive-host-1.service

systemctl start drivetemp-drive-host-0.service
systemctl start drivetemp-drive-host-1.service

