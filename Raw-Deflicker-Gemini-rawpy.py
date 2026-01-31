import os
import subprocess
import shlex
import numpy as np
from scipy import signal
from datetime import datetime as dt
from pathlib import Path
import rawpy
import matplotlib.pyplot as plt  # Added for graphing

# Configuration
SOURCE_PATH = Path("/home/ubuntu/2023-07-18")
GRAPH_PATH = Path("/home/ubuntu/deflicker-testing")
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

# crop_percent(top, left, height, width)
# Full Image	(0.0, 0.0, 1.0, 1.0)	Averages every single pixel.
# Center Spot	(0.4, 0.4, 0.2, 0.2)	Acts like a "Spot Meter" on a camera. Ignores distracting edges.
# Lower Third	(0.66, 0.0, 0.33, 1.0)	Good if you want to sample just the landscape and ignore a flickering sky.
# Sky Sample	(0.0, 0.0, 0.4, 1.0)	Good for matching exposure based solely on the sky brightness.

def get_brightness(file_path, crop_percent=(0.0, 0.0, 0.6, 1.0)):
    try:
        with rawpy.imread(str(file_path)) as raw:
            rgb = raw.postprocess(use_camera_wb=True, 
                                  user_flip=0, 
                                  no_auto_bright=True, 
                                  half_size=True,
                                  gamma=(1,1))
            
            h, w, _ = rgb.shape
            
            if crop_percent:
                top_p, left_p, height_p, width_p = crop_percent
                
                # Calculate coordinates and clip them to image boundaries
                y1 = int(np.clip(h * top_p, 0, h))
                x1 = int(np.clip(w * left_p, 0, w))
                y2 = int(np.clip(y1 + (h * height_p), 0, h))
                x2 = int(np.clip(x1 + (w * width_p), 0, w))
                
                # Apply the slice
                rgb = rgb[y1:y2, x1:x2, :]

            # --- Safety Check ---
            if rgb.size == 0:
                print(f"Warning: Crop for {file_path} resulted in 0 pixels. Check your crop_percent values.")
                return None

            weights = np.array([0.299, 0.587, 0.114])
            return np.dot(rgb[...,:3], weights).mean()
            
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

# --- 4. Plotting & Saving Section ---
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
plt.subplots_adjust(hspace=0.3)

# Top Graph: Brightness Comparison
ax1.plot(M, label='Raw Brightness (M)', color='lightgray', alpha=0.7)
ax1.plot(y_smooth, label='Savgol Filtered (y_smooth)', color='blue', linewidth=2)
ax1.set_title(f'Brightness Analysis (Window: {WINDOW_SIZE}, Poly: {POLY_ORDER})', fontsize=14)
ax1.set_ylabel('Mean Pixel Value')
ax1.legend()
ax1.grid(True, linestyle='--', alpha=0.6)

# Bottom Graph: Exposure Compensation
# Note: E + 1 reflects the actual value written to the .pp3 files
ax2.plot(E + 1, label='Final Compensation (E + 1)', color='red')
ax2.axhline(y=1, color='black', linestyle='-', linewidth=0.8) # Baseline at +1
ax2.set_title('Calculated Exposure Adjustment (Stops)', fontsize=14)
ax2.set_ylabel('Exposure Value (EV)')
ax2.set_xlabel('Frame Number')
ax2.legend()
ax2.grid(True, linestyle='--', alpha=0.6)

# Generate filename and save
timestamp = dt.now().strftime('%Y%m%d_%H%M%S')
output_plot = GRAPH_PATH / f"deflicker_rawpy_{WINDOW_SIZE}_{POLY_ORDER}.png"

plt.savefig(output_plot, dpi=300, bbox_inches='tight')
print(f"Plot saved to: {output_plot}")

# Optional: Still show the window if you're running interactively
# plt.show() 

plt.close(fig) # Close to free up memory

# 5. Call the shell script to process images and create video
shell_script = "/home/ubuntu/deflicker/make-sunset-yst-dflk-raw.sh"
print(f"Calling shell script: {shell_script} with Window={WINDOW_SIZE}, Poly={POLY_ORDER}")
subprocess.run([shell_script, str(WINDOW_SIZE), str(POLY_ORDER)])

print(f"Completed at: {dt.now().strftime('%H:%M:%S')}")
