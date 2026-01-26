import os, sys, re, subprocess, shlex

from datetime import datetime as dt
from datetime import timedelta as td
from math import *
from pylab import *
import rawpy
import cv2
import numpy as np


yesterday = dt.now() - td(1)

#p = "/media/ubuntu/Seagate2T/images/"
#path = os.path.join(p, dt.strftime(yesterday, '%Y-%m-%d'))
#print(os.path.join(path, dt.strftime(yesterday, '%Y-%m-%d')))
path = "/home/ubuntu/Timelapse/test"
profile = open("/home/ubuntu/.config/RawTherapee/profiles/sunset.pp3","r")
lines = profile.readlines()
files = sorted(os.listdir(path))
i = 0;
word = "Compensation="
count = 0 


def get_median(file):
    # decode a raw image
    # convert it to a 500 x 500 grayscale histogram. 
    print("file=", file)
    cmd1 = "dcraw -c -D -4 -o 0 '%s'" % file
#    cmd2 = "convert - -type Grayscale -scale 500x500 -format %c histogram:info:-"
    cmd2 = "convert - -type Grayscale -format %c histogram:info:-"
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
#           print("level=", level)
           count = int(l[:p1-2])
#           print("count=", count)
           X += [level]*count
#          print("X=", X)
    m = median(X)
    print("imagemagic median=", m)
   # Calculate for each pixel
    rawImg = rawpy.imread(file)
    rgb = rawImg.postprocess(use_camera_wb=True)
#    image = cv2.cvtColor(rgb, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)

    h = gray.shape[0]
    w = gray.shape[1]

    brightness = []

    for y in range(0, h, int(h/50)):
        for x in range(0, w, int(w/50)):
#             r,g,b = image[y, x]
#            brightness.append(0.333*r + 0.333*g + 0.333*b)
#            print("RGB=", r, g, b)
             i = gray[y, x]
             brightness.append(i)
#            print("Greyscale=", i)
    j = median(brightness)
    k = mean(brightness)
    print("opencv median=", j)
    print("opencv mean=", k)
    return m

files = sorted(os.listdir(path))
#print(files)
i = 0;
M = [];
for k,f in enumerate(files):
    m = get_median(os.path.join(path, f))
#    print("file=", os.path.join(path, f))
#    print("m=", m)
    M.append(m);
#    print("M=", M)
    E = [-log2(m/M[0]) for m in M]
E = detrend(array(E))
#print("E=", E)



