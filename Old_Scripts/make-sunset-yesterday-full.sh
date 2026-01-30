#!/bin/bash
#
# █▀▄▀█ ▄▀█ █▄▀ █▀▀ ▄▄ █▀ █░█ █▄░█ █▀ █▀▀ ▀█▀
# █░▀░█ █▀█ █░█ ██▄ ░░ ▄█ █▄█ █░▀█ ▄█ ██▄ ░█░
#
#  Uses exiftool to find and process raw image files taken after a certain hour of the day.
tdy_date=$(date +%Y-%m-%d)
yst_date="2023-07-03"  #$(date --date="yesterday" +"%Y-%m-%d")
basedir="/media/ubuntu/Seagate2T/images/2023-07-03/"
FILES="/media/ubuntu/Seagate2T/images/2023-07-03/*"
sunset=17 # set hour uses greater than. set 1 h lower that the desired.
mkdir "$basedir""sunset"
mkdir "$basedir""sunset-2"
#echo "$FILES"

#for f in $FILES
#   do
#      if [[ $f == *.CR2 ]]
#      then
#         exif=$(exiftool "$f" | grep "Create Date")
#         exif=${exif##Create Date                     : } # cut off the front
#         exif=${exif#* } # cut off the date
#         exif=${exif%%:*} # cut off the minutes and seconds
#         exif=${exif//[[:blank:]]/} # Remove spaces
#         echo "$exif"
#         if [[ $((10#$exif)) -gt $((10#$sunset)) ]]
#         then
#          rawtherapee-cli -o "$basedir""sunset"  -s -j100 -js3 -c "$f"
#	  rawtherapee-cli -o "$basedir""sunset-2"  -p /home/ubuntu/.config/RawTherapee/profiles/sunset.pp3 -j100 -js3 -c "$f" # the .pp3 file is a RawTherapee profile
#         fi
#      fi
#   done

cd "$basedir""sunset"
ffmpeg -framerate 24 -pattern_type glob -i '*.jpg' -c:v libx264 -pix_fmt yuv420p -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" out-dflk-24fps_"$yst_date".mp4
#ffmpeg -framerate 10 -pattern_type glob -i '*.jpg' -c:v libx264 -pix_fmt yuv420p out-10fps_"$tdy_date".mp4
#ffmpeg -framerate 24 -pattern_type glob -i '*.jpg' -c:v libx264 -pix_fmt yuv420p out-24fps_"$tdy_date".mp4


cd "$basedir""sunset-2"
ffmpeg -framerate 24  -pattern_type glob -i '*.jpg' -c:v libx264 -pix_fmt yuv420p -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" out-24fps_"$yst_date".mp4
#ffmpeg -framerate 24 -pattern_type glob -i '*.jpg' -c:v libx264 -pix_fmt yuv420p -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" out-24fps_"$yst_date".mp4
#sftp -P 8000 pi@2strader.duckdns.org:/home/pi/Sunsets  <<< $'put out-24fps_'"$yst_date"'.mp4'
