
# Makes a .pp3 file for every file in a folder. 
# Needs to only make one for .CR2 files 
import os, sys, re,mmap, time, datetime, subprocess, shlex

path = "/home/ubuntu/Timelapse/test"
profile = open("/home/ubuntu/.config/RawTherapee/profiles/sunset.pp3","r")
lines = profile.readlines()
files = sorted(os.listdir(path))
i = 0;
word = "Compensation="
count = 0 

for k,f in enumerate(files):
    print(os.path.join(path, f + ".pp3"))
    f = open(os.path.join(path, f + ".pp3"), "w")
    for line in lines:
        if line.find(word) != -1:
             f.write("meow\n")
             print('Line Number:',lines.index(line))
             print('Line:', line)
        else:
            count += 1
            f.write(lines[lines.index(line)])
        #print('Line Number:',lines.index(line))
    f.close()
    profile.seek(0)
profile.close()

