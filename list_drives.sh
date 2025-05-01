#!/bin/sh

#lsblk --noheadings --output=SERIAL,HCTL --scsi
#lsblk  --output=PATH,SERIAL,LABEL,HCTL --scsi
#lsblk  --noheadings --output=PATH,SERIAL,LABEL,HCTL --scsi

grep -l "drivetemp" /sys/class/hwmon/hwmon*/name | while read -r f; do
printf "/dev/%s\t(%-.2s°C)\t %s\n" "$(ls "${f%/*}"/device/block)" "$(cat "${f%/*}"/temp1_input)" "$(lsblk  --noheadings --output=HCTL,LABEL --scsi /dev/$(ls "${f%/*}"/device/block))" 
done
