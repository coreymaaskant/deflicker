#!/bin/bash
#
# █▀▄▀█ ▄▀█ █▄▀ █▀▀ ▄▄ █▀ █░█ █▄░█ █▀ █▀▀ ▀█▀
# █░▀░█ █▀█ █░█ ██▄ ░░ ▄█ █▄█ █░▀█ ▄█ ██▄ ░█░
#
#  Uses exiftool to find and process raw image files taken after a certain hour of the day.`	
tdy_date=$(date +%Y-%m-%d)
yst_date=$(date --date="yesterday" +"%Y-%m-%d")
basedir="/home/ubuntu/2023-07-18/"
#FILES="/media/ubuntu/Seagate2T/images/""$yst_date/*"
FILES="/home/ubuntu/2023-07-18/*"
mkdir "$basedir""sunset_jpgs"
#mkdir "$basedir""sunset_jpgs-2"
cd "$basedir"

for f in $FILES
do
   if [[ $f == *.CR2 ]]; then
      rawtherapee-cli -o "$basedir""sunset_jpgs" -s -b16 -t -c "$f" > /dev/null 2>&1
      #rawtherapee-cli -o "$basedir""sunset_jpgs-2"  -p /home/ubuntu/.config/RawTherapee/profiles/sunset.pp3 -j100 -js3 -c "$f" 
   fi   
done

cd "$basedir""sunset_jpgs"
ffmpeg -framerate 24 -pattern_type glob -i '*.tif' -c:v libx264 -pix_fmt yuv420p -crf 18 -preset slow -colorspace bt709 -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" dcraw-win71-poly2-tif-24fps.mp4

#cd "$basedir""sunset_jpgs-2"
#ffmpeg -framerate 24 -pattern_type glob -i '*.jpg' -c:v libx264 -pix_fmt yuv420p -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" out-raw-24fps.mp4

