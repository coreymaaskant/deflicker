from datetime import datetime as dt
from datetime import timedelta as td
import os, sys, re, subprocess, shlex
from math import *
from pylab import *

yesterday = dt.now() - td(1)

p = "/media/ubuntu/Seagate2T/images/"
path = os.path.join(p, dt.strftime(yesterday, '%Y-%m-%d'))
#path = "/home/ubuntu/Timelapse/test"
#print(os.path.join(path, dt.strftime(yesterday, '%Y-%m-%d')))
profile = open("/home/ubuntu/.config/RawTherapee/profiles/sunset.pp3","r")
lines = profile.readlines()
files = sorted(os.listdir(path))
i = 0;
word = "Compensation="
count = 0 
comp = 0.8 # This will be added to the final adjustment to bring the final exposure up. this could also be read out of the origional profile. 

def get_median(file):
    # decode a raw image
    # convert it to a 500 x 500 grayscale histogram. 
    cmd1 = "dcraw -c -D -4 -o 0 '%s'" % file
    cmd2 = "convert - -type Grayscale -scale 500x500 -format %c histogram:info:-"
    p1 = subprocess.Popen(shlex.split(cmd1), stdout=subprocess.PIPE)
    p2 = subprocess.Popen(shlex.split(cmd2), stdin=p1.stdout, stdout=subprocess.PIPE)
    lines = p2.communicate()[0].decode('utf-8')
    #print(lines)
    lines = lines.splitlines()

    X = []
    #iterate through all the 500x500 pixels and find the brightness values  
    #adds them to a list and then returns the median value as m.
    for l in lines[1:]:
        p1 = l.find("(")
        if p1 > 0:
           p2 = l.find(",", p1)
           level = int(l[p1+1:p2])
           #print("level=", level)
           count = int(l[:p1-2])
           X += [level]*count
           m = median(X)
    return m


files = sorted(os.listdir(path))
#print(files)
i = 0;
M = [];
for k,f in enumerate(files):
    m = get_median(os.path.join(path, f))
    print("file=", os.path.join(path, f))
#    print("m=", m)
    M.append(m);
#    print("M=", M)
    E = [-log2(m/M[0]) for m in M]
E = detrend(array(E))
print("E=", E)

for k,f in enumerate(files):
    #print(os.path.join(path, f + ".pp3"))
    f = open(os.path.join(path, f + ".pp3"), "w")
    for line in lines:
        if line.find(word) != -1:
             f.write("Compensation=")
             f.write(str(E[k]+comp))
             f.write("\n")
             #print('Line Number:',lines.index(line))
             #print('Line:', line)
        else:
            count += 1
            f.write(lines[lines.index(line)])
        #print('Line Number:',lines.index(line))
    f.close()
    profile.seek(0)
profile.close()


