#!/bin/bash
#
# █▀▄▀█ ▄▀█ █▄▀ █▀▀ ▄▄ █▀ █░█ █▄░█ █▀ █▀▀ ▀█▀
# █░▀░█ █▀█ █░█ ██▄ ░░ ▄█ █▄█ █░▀█ ▄█ ██▄ ░█░
#
#  Uses exiftool to find and process raw image files taken after a certain hour of the day.
tdy_date=$(date +%Y-%m-%d)
yst_date=$(date --date="yesterday" +"%Y-%m-%d")
basedir="/media/ubuntu/Seagate2T/images/""$tdy_date/"
FILES="/media/ubuntu/Seagate2T/images/""$yst_date/*"

for f in $FILES
   do
      if [[ $f == *.CR2 ]]
      then
         exif=$(exiftool "$f" | grep "EV")
         echo "$exif"
         shutter=$(exiftool "$f" | grep "Shutter Speed Value")
         echo "$shutter"
	 echo "/n"
      fi
   done

