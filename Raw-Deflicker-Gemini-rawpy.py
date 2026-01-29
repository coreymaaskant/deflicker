import os
import subprocess
import shlex
import numpy as np
from scipy import signal
from datetime import datetime as dt
from pathlib import Path
import rawpy

# Configuration
SOURCE_PATH = Path("/home/ubuntu/2023-07-18")
PROFILE_TEMPLATE = Path("/home/ubuntu/.config/RawTherapee/profiles/sunset.pp3")
WINDOW_SIZE = 21  # Must be odd
POLY_ORDER = 2

# 1. Moderate Smoothing (Balanced)
# window_length: 31 to 51
# polyorder: 3
# Why: A window of ~41 points (about 8% of your data) with a cubic polynomial effectively reduces 
# random noise while preserving the shape of significant peaks. 
# 2. Aggressive Smoothing (Heavy Noise)
# window_length: 71 to 91
# polyorder: 2
# Why: If your noise is severe and your signal features are broad, a larger window with a quadratic 
# fit provides heavy suppression of high-frequency fluctuations.

def get_brightness(file_path):
    """
    Decodes RAW and calculates mean brightness using NumPy.
    Replaces dcraw and ImageMagick.
    """
    try:
        with rawpy.imread(str(file_path)) as raw:
            # postprocess(user_flip=0) prevents auto-rotation and scaling
            # half_size=True makes it MUCH faster for brightness analysis
            rgb = raw.postprocess(use_camera_wb=False, 
                                 user_flip=0, 
                                 no_auto_bright=True, 
                                 half_size=True)
            
            # Convert to grayscale (Luminance Y' ≈ 0.299R + 0.587G + 0.114B)
            # Or simply take the mean of all pixels for a raw estimate
            return np.mean(rgb)
    except Exception as e:
        print(f"Failed to process {file_path}: {e}")
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
                # Apply the calculated compensation (+1 I seem to just add 1 stop to all my 5D raw files)
                out_file.write(f"Compensation={E[k] + 1}\n")
            else:
                out_file.write(line)

print(f"Completed at: {dt.now().strftime('%H:%M:%S')}")
