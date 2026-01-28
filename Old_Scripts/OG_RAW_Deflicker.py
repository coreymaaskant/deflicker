# RAW deflickering script
# Copyright (2012) a1ex. License: GPL.

from __future__ import division
import os, sys, re, time, datetime, subprocess, shlex
from math import *
from pylab import *

def progress(x, interval=1):
    global _progress_first_time, _progress_last_time, _progress_message, _progress_interval
   
    try:
        p = float(x)
        init = False
    except:
        init = True
       
    if init:
        _progress_message = x
        _progress_last_time = time.time()
        _progress_first_time = time.time()
        _progress_interval = interval
    elif x:
        if time.time() - _progress_last_time > _progress_interval:
            print >> sys.stderr, "%s [%d%% done, ETA %s]..." % (_progress_message, int(100*p), datetime.timedelta(seconds = round((1-p)/p*(time.time()-_progress_first_time))))
            _progress_last_time = time.time()


def change_ext(file, newext):
    if newext and (not newext.startswith(".")):
        newext = "." + newext
    return os.path.splitext(file)[0] + newext

def get_median(file):
    cmd1 = "dcraw -c -D -4 -o 0 '%s'" % file
    cmd2 = "convert - -type Grayscale -scale 500x500 -format %c histogram:info:-"
    #~ print cmd1, "|", cmd2
    p1 = subprocess.Popen(shlex.split(cmd1), stdout=subprocess.PIPE)
    p2 = subprocess.Popen(shlex.split(cmd2), stdin=p1.stdout, stdout=subprocess.PIPE)
    lines = p2.communicate()[0].split("\n")
    X = []
    for l in lines[1:]:
        p1 = l.find("(")
        if p1 > 0:
            p2 = l.find(",", p1)
            level = int(l[p1+1:p2])
            count = int(l[:p1-2])
            X += [level]*count
    m = median(X)
    return m

ion()

progress("Analyzing RAW exposures...");
files = sorted(os.listdir("raw"))
i = 0;
M = [];
for k,f in enumerate(files):
    m = get_median(os.path.join('raw', f))
    M.append(m);

    E = [-log2(m/M[0]) for m in M]
    E = detrend(array(E))
    cla(); stem(range(1,len(E)+1), E);
    xlabel('Image number')
    ylabel('Exposure correction (EV)')
    title(f)
    draw();
    progress(k / len(files))

progress("Developing JPG images...");
i = 0;
for k,f in enumerate(files):
    ec = 2 + E[k];
    cmd = "ufraw-batch --out-type=jpg --overwrite --clip=film --saturation=2 --exposure=%s '%s' --output='jpg/%s'" % (ec, os.path.join("raw", f), change_ext(f, ".jpg"))
    os.system(cmd)
    progress(k / len(files))
