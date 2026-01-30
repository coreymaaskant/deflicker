#!/bin/bash
foldername=$(date +%Y-%m-%d)
mkdir -p  /media/ubuntu/Seagate2T/images/"$foldername"
chmod 777 -R images > /dev/null 2>&1
