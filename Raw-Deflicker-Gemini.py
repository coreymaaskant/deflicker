import os
import subprocess
import shlex
import numpy as np
from scipy import signal
from datetime import datetime as dt
from pathlib import Path

# Configuration
SOURCE_PATH = Path("/home/ubuntu/2023-07-18")
PROFILE_TEMPLATE = Path("/home/ubuntu/RawTherapee/profiles/sunset.pp3")
WINDOW_SIZE = 31  # Must be odd
POLY_ORDER = 3

def get_brightness(file_path):
    """Extracts mean brightness using dcraw and ImageMagick."""
    cmd1 = f"dcraw -c -4 '{file_path}'"
    cmd2 = "convert - -crop 4378x1700+0+0 -colorspace Gray -format %[fx:mean*quantumrange] info:"
    
    try:
        p1 = subprocess.Popen(shlex.split(cmd1), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        p2 = subprocess.Popen(shlex.split(cmd2), stdin=p1.stdout, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        out, _ = p2.communicate()
        return float(out.decode('utf-8').strip())
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

# 1. Gather files and Analyze
files = sorted([f for f in SOURCE_PATH.iterdir() if f.is_file()])
brightness_values = []

print(f"Starting analysis at: {dt.now().strftime('%H:%M:%S')}")

for f in files:
    m = get_brightness(f)
    if m is not None:
        brightness_values.append(m)

# 2. Calculate Smoothing
M = np.array(brightness_values)
y_smooth = signal.savgol_filter(M, window_length=WINDOW_SIZE, polyorder=POLY_ORDER, mode="nearest")
# Exposure compensation: -log2(actual/target)
E = -np.log2(M / y_smooth)

# 3. Generate .pp3 files
with open(PROFILE_TEMPLATE, "r") as f:
    template_lines = f.readlines()

for k, f_path in enumerate(files):
    pp3_path = f_path.with_suffix(f_path.suffix + ".pp3")
    
    with open(pp3_path, "w") as out_file:
        for line in template_lines:
            if line.startswith("Compensation="):
                # Apply the calculated compensation (+1 as per your original logic)
                out_file.write(f"Compensation={E[k] + 1}\n")
            else:
                out_file.write(line)

print(f"Completed at: {dt.now().strftime('%H:%M:%S')}")
