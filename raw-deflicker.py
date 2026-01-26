import os, sys, re, time, datetime, subprocess, shlex
from math import *
from pylab import *

def change_ext(file, newext):
    if newext and (not newext.startswith(".")):
        newext = "." + newext
    return os.path.splitext(file)[0] + newext

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


files = sorted(os.listdir("/home/ubuntu/Timelapse/test"))
print(files)
i = 0;
M = [];
for k,f in enumerate(files):
    m = get_median(os.path.join('/home/ubuntu/Timelapse/test', f))
    print("file=", os.path.join('/home/ubuntu/Timelapse/test', f))
    print("m=", m)
    M.append(m);
    print("M=", M)
    E = [-log2(m/M[0]) for m in M]
E = detrend(array(E))
print("E=", E)
    #cla(); stem(range(1,len(E)+1), E);
    #xlabel('Image number')
    #ylabel('Exposure correction (EV)')
    #title(f)
    #draw();


i = 0;
for k,f in enumerate(files):
    ec = 2 + E[k];
    os.system(cmd)
