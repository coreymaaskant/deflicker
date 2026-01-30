#! /bin/bash
email=coreymaaskant@gmail.com
i=192.168.2.11
#ping -q -c1  $i >/dev/null
#if [ $? -ne 0 ]
#then


count=$(ping -c 5  $i | grep 'received' | awk -F',' '{ print $2 }' | awk '{ print $1 }') #ping pi 5 times 
if [ $count -eq 0 ]; then
   echo "$i is down"|mailx -s "connectivity test" $email # if 0 response email
fi

