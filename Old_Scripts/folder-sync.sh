#!/bin/bash

basedir='/media/ubuntu/Seagate2T/images/'
FILES="/media/ubuntu/Seagate2T/images/unsorted/*"
cd "/media/ubuntu/Seagate2T/images/unsorted"


for f in $FILES
   do
      if [ $(find $f -mtime -1) ]
         then
             printf  "\nProcessing $f file..." #>> /home/canon5d/rsync-log.txt
             exif=$(exiftool "$f" | grep "Create Date")
             exif=${exif##Create Date                     :} # cut off the front
             exif=${exif% *} # cut off the time
             exif=${exif//:/-} # replace semicolons with hyphens
             exif=${exif//[[:blank:]]/} # Remove spaces
             echo "$exif"
             mkdir -p "$basedir$exif"
             #cp -v "$f" "$basedir$exif"  #>> /home/canon5d/rsync-log.txt  # copy the file to a dated folder for procesing.
             mv -nv "$f" "$basedir$exif" # move the file out of the unsorted folder
             ssh pi@192.168.1.103 rm /home/pi/canon5d/images/${f##*/} # deletes the file on the remote 
      fi
   done

#printf "\n$(date)" >> /home/canon5d/rsync.log
#printf "\n" >> /home/canon5d/rsync.log

#/home/canon5d/make-sunset-today.sh # call script to convert raws
