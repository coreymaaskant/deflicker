from datetime import datetime as dt
from datetime import timedelta as td
import os, sys, re, subprocess, shlex
from math import *
from pylab import *
import matplotlib.pyplot as plt
from scipy.signal import detrend
from scipy import signal
import numpy as np

current_datetime = dt.now()
current_time = current_datetime.strftime("%H:%M:%S")
print("The start time is:", current_time)

path = "/home/ubuntu/2023-07-18"
profile = open("/home/ubuntu/RawTherapee/profiles/sunset.pp3","r")
lines = profile.readlines()
files = sorted(os.listdir(path))
i = 0;
word = "Compensation="
count = 0 


def get_median(file):
    # decode a raw image
    # convert it to a 500 x 500 grayscale histogram. 
    cmd1 = "dcraw -c -D -4 -o 0 '%s'" % file # -c standard out, -D greyscale no color scaling, -4 linear 16 bit, 
    cmd2 = "convert - -colorspace Gray -format %[fx:mean*quantumrange] info:" # get the mean brightness
    p1 = subprocess.Popen(shlex.split(cmd1), stdout=subprocess.PIPE)
    p2 = subprocess.Popen(shlex.split(cmd2), stdin=p1.stdout, stdout=subprocess.PIPE)
    v = p2.communicate()[0].decode('utf-8')
    m =float(v)
    return m

files = sorted(os.listdir(path))
i = 0;
M = [];

fig1, ax1 = plt.subplots()
for k,f in enumerate(files):
    m = get_median(os.path.join(path, f))
    M.append(m);
    E = [-log2(m/M[0]) for m in M]
    print("m=", m)
    #print("E=", E)
    cla();
    ax1.plot(range(1,len(E)+1), E, label="No detrending")
    y_smooth = signal.savgol_filter(E, window_length=30, polyorder=3, mode="nearest")
    ax1.plot(range(1,len(y_smooth)+1), y_smooth, label="Savitzky-Golay filter")
    comp = [x - y for x, y in zip(y_smooth, E)]
    ax1.plot(range(1,len(comp)+1), comp, label="compenstion")
    ax1.legend()
    ax1.set(xlabel="Image number", ylabel="Exposure correction (EV)")
    #plt.savefig("my_plot.png")
    plt.pause(0.1)
 
for k,f in enumerate(files):
    print(os.path.join(path, f + ".pp3"))
    f = open(os.path.join(path, f + ".pp3"), "w")
    print("comp=", str(comp[k]))
    for line in lines:
        if line.find(word) != -1:
             f.write("Compensation=") #the compensation slider in Rawttherapee is EV (exposure value) Stops
             f.write(str(comp[k]))
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

print("pp3 files completed")
current_datetime = dt.now()
end_time = current_datetime.strftime("%H:%M:%S")
print("The DFLK end time is:", end_time)

#subprocess.call(['sh', './make-sunset-yst-dflk-raw.sh'])


