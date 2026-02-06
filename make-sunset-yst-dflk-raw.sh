#!/bin/bash
#
# █▀▄▀█ ▄▀█ █▄▀ █▀▀ ▄▄ █▀ █░█ █▄░█ █▀ █▀▀ ▀█▀
# █░▀░█ █▀█ █░█ ██▄ ░░ ▄█ █▄█ █░▀█ ▄█ ██▄ ░█░
#
# convert the raws save tiffs and delete the .pp3 sidecar files
#

WINDOW_SIZE=${1:-"default"}
POLY_ORDER=${2:-"default"}
TARGET_DIR=${3}

basedir="${TARGET_DIR}/"
FILES="*"

mkdir -p "$basedir""sunset_tiffs"
cd "$basedir"

for f in $FILES
do
   if [[ $f == *.CR2 ]]; then
      rawtherapee-cli -o "$basedir""sunset_tiffs" -s -b16 -t -c "$f" > /dev/null 2>&1
      #rawtherapee-cli -o "$basedir""sunset_jpgs-2"  -p /home/ubuntu/.config/RawTherapee/profiles/sunset.pp3 -j100 -js3 -c "$f" 
   fi   
done

cd "$basedir"
rm -f "$basedir"*.pp3
echo "Deleted .pp3 files."
