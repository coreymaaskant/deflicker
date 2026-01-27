# Version as of October 2025
# uses the convert - -crop 4378x1700+0+0 to only sample the sky portion of the image
# uses signal.savgol_filter to smoooth out the brightest
#
#
# Tip from chat GPT to try 
# 6. Mean brightness is very sensitive to clouds
# Mean works, but sunsets benefit from median or percentile.
# You already named the function get_median — but you’re computing mean.
# If you want median luminance:
#      -format %[fx:median*quantumrange]
# Or robust percentile:
#      -format %[fx:percentile(70)*quantumrange]
# This alone can massively reduce flicker.
# 
#
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
comp = 1 # final multiplier for final compensation. 


def get_median(file):
    # decode a raw image
    # convert it to a 500 x 500 grayscale histogram. 
    cmd1 = "dcraw -c -4 '%s'" % file # -c standard out, -D greyscale no color scaling, -4 linear 16 bit, 
    #cmd2 = "convert - -colorspace Gray -format %[fx:mean*quantumrange] info:" # get the mean brightness
    cmd2 = "convert - -crop 4378x1700+0+0 -colorspace Gray -format %[fx:mean*quantumrange] info:" # get the mean brightness
    p1 = subprocess.Popen(shlex.split(cmd1), stdout=subprocess.PIPE)
    p2 = subprocess.Popen(shlex.split(cmd2), stdin=p1.stdout, stdout=subprocess.PIPE)
    v = p2.communicate()[0].decode('utf-8')
    m =float(v)
    #print("read file= ", file)
    #print("v=", v)

    return m

files = sorted(os.listdir(path))
#print(files)
i = 0;
M = [];
E = [];
for k,f in enumerate(files):
    m = get_median(os.path.join(path, f))
    #print("got median of ")
    #print("file=", os.path.join(path, f))
    #print("m=", m)
    M.append(m);
    #print("M=", M)
    #E = [-log2(m/M[0]) for m in M]

y_smooth = signal.savgol_filter(M, window_length=30, polyorder=3, mode="nearest")

for k,f in enumerate(files):
    E.append(-log2(M[k]/y_smooth[k]))

for k,f in enumerate(files):
    #print(os.path.join(path, f + ".pp3"))
    f = open(os.path.join(path, f + ".pp3"), "w")
    
    for line in lines:
        if line.find(word) != -1:
             f.write("Compensation=")
             f.write(str((E[k]*comp)+1))
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


