import os
import subprocess
import shlex
import shutil
import numpy as np
from scipy import signal
from datetime import datetime as dt
from pathlib import Path
import rawpy
import csv
from PIL import Image
import matplotlib.pyplot as plt  # Added for graphing

# Configuration
SOURCE_PATH = Path("/home/ubuntu")
FOLDER = "2022-06-29"
GRAPH_PATH = Path("/home/ubuntu/deflicker-testing")
PROFILE_TEMPLATE = Path("/home/ubuntu/.config/RawTherapee/profiles/sunset.pp3")
TIFF_PATH = SOURCE_PATH / FOLDER / "sunset_tiffs"
WINDOW_SIZE = 51  # Must be odd
POLY_ORDER = 2
EV_OFFSET = 1

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

def get_brightness_tiff(file_path, crop_percent=(0.0, 0.0, 0.6, 1.0)):
    try:
        img = plt.imread(str(file_path))
        
        # Handle dimensions
        h, w = img.shape[:2]
        
        if crop_percent:
            top_p, left_p, height_p, width_p = crop_percent
            y1 = int(np.clip(h * top_p, 0, h))
            x1 = int(np.clip(w * left_p, 0, w))
            y2 = int(np.clip(y1 + (h * height_p), 0, h))
            x2 = int(np.clip(x1 + (w * width_p), 0, w))
            img = img[y1:y2, x1:x2]

        return img.mean()
    except Exception as e:
        print(f"Failed to process TIFF {file_path}: {e}")
        return None

# 1. Gather files and Analyze
files = sorted([f for f in (SOURCE_PATH / FOLDER).iterdir() if f.is_file()])
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
                out_file.write(f"Compensation={E[k] + EV_OFFSET}\n")
            else:
                out_file.write(line)

# 4. Call the shell script to process images and create video (PASS 1)
shell_script = "/home/ubuntu/deflicker/make-sunset-yst-dflk-raw.sh"
folder_name = FOLDER
print(f"--- Running Pass 1: Generating initial TIFFs and video for {folder_name} ---")
subprocess.run([shell_script, str(WINDOW_SIZE), str(POLY_ORDER), str(SOURCE_PATH / FOLDER)])

# 5. Analyze Generated TIFFs (from Pass 1)
tiff_folder = TIFF_PATH
tiff_files = sorted(list(tiff_folder.glob("*.tif")))
tiff_brightness_p1 = []
tiff_brightness_p2 = []
E_adjust = None

if tiff_files:
    print(f"Analyzing {len(tiff_files)} TIFF files from Pass 1...")
    for f in tiff_files:
        m = get_brightness_tiff(f)
        if m is not None:
            tiff_brightness_p1.append(m)

    # 5.5. Pass 2: Refinement using Pillow
    print("\n--- Starting Pass 2: Refining TIFFs with Pillow ---")
    # Calculate adjustment based on Pass 1 TIFFs
    M_p1 = np.array(tiff_brightness_p1)
    M_p1 = np.maximum(M_p1, 1e-5) # Avoid division by zero
    y_smooth_p1 = signal.savgol_filter(M_p1, window_length=WINDOW_SIZE, polyorder=POLY_ORDER, mode="nearest")
    y_smooth_p1 = np.maximum(y_smooth_p1, 1e-5)
    
    E_adjust = -np.log2(M_p1 / y_smooth_p1)

    print("Applying brightness adjustments to TIFFs...")
    # Apply adjustments to each TIFF
    for i, file_path in enumerate(tiff_files):
        if i >= len(E_adjust): break
        
        img_p1 = plt.imread(file_path)
        
        dtype_p1 = img_p1.dtype
        max_val = np.iinfo(dtype_p1).max if np.issubdtype(dtype_p1, np.integer) else 1.0
        
        img_p1_float = img_p1.astype(np.float32)
        adjustment_factor = 2 ** E_adjust[i]
        img_p2_float = img_p1_float * adjustment_factor
        
        img_p2_float = np.clip(img_p2_float, 0, max_val)
        img_p2 = img_p2_float.astype(dtype_p1)
        
        # Overwrite the TIFF file with the adjusted image using Pillow
        pil_img = Image.fromarray(img_p2)
        pil_img.save(file_path)

    print("Pillow adjustments complete. Re-running FFMPEG.")
    
    # Re-run FFMPEG to create the final video with -y to overwrite
    video_out_path = GRAPH_PATH / f"deflicker_rawpy_{folder_name}_w{WINDOW_SIZE}_p{POLY_ORDER}.mp4"
    ffmpeg_cmd = [
        'ffmpeg', '-y',
        '-framerate', '24',
        '-pattern_type', 'glob', '-i', f'{tiff_folder}/*.tif',
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'slow',
        '-colorspace', 'bt709', '-vf', 'pad=ceil(iw/2)*2:ceil(ih/2)*2',
        str(video_out_path)
    ]
    subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("Final video generated.")

    # Re-analyze TIFFs for final graph (Pass 2 results)
    print(f"Analyzing {len(tiff_files)} adjusted TIFF files from Pass 2...")
    for f in tiff_files:
        m = get_brightness_tiff(f)
        if m is not None:
            tiff_brightness_p2.append(m)

# --- 6. Plotting & Saving Section ---
fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(12, 20), sharex=True)
plt.subplots_adjust(hspace=0.3)

# Top Graph: Brightness Comparison
ax1.plot(M, label='Raw Brightness (M)', color='lightgray', alpha=0.7)
ax1.plot(y_smooth, label='Savgol Filtered (y_smooth)', color='blue', linewidth=2)
ax1.set_title(f'Brightness Analysis (Window: {WINDOW_SIZE}, Poly: {POLY_ORDER})', fontsize=14)
ax1.set_ylabel('Mean Pixel Value')
ax1.legend()
ax1.grid(True, linestyle='--', alpha=0.6)

# Middle Graph: Exposure Compensation
# Note: E + EV_OFFSET reflects the actual value written to the .pp3 files
ax2.plot(E + EV_OFFSET, label='Final Compensation (E + EV_OFFSET)', color='red')
ax2.axhline(y=1, color='black', linestyle='-', linewidth=0.8) # Baseline at +1
ax2.set_title('Calculated Exposure Adjustment (Stops)', fontsize=14)
ax2.set_ylabel('Exposure Value (EV)')
ax2.legend()
ax2.grid(True, linestyle='--', alpha=0.6)

# Bottom Graph: Final TIFF Brightness
ax3.plot(tiff_brightness_p1, label='Pass 1 TIFFs (Before Refinement)', color='orange', alpha=0.7, linestyle='--')
ax3.plot(tiff_brightness_p2, label='Pass 2 TIFFs (Final)', color='green', linewidth=2)
ax3.set_title('TIFF Brightness: Before and After Pass 2 Refinement', fontsize=14)
ax3.set_ylabel('Mean Pixel Value')
ax3.legend()
ax3.grid(True, linestyle='--', alpha=0.6)

# Bottom Graph: Pass 2 Adjustment
if E_adjust is not None:
    ax4.plot(E_adjust, label='Pass 2 Adjustment (EV)', color='purple')
    ax4.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
    ax4.set_title('Pass 2 Brightness Correction Applied', fontsize=14)
    ax4.set_ylabel('Correction (EV)')
    ax4.set_xlabel('Frame Number')
    ax4.legend()
    ax4.grid(True, linestyle='--', alpha=0.6)

# Generate filename and save
timestamp = dt.now().strftime('%Y%m%d_%H%M%S')
output_plot = GRAPH_PATH / f"deflicker_rawpy_{folder_name}_{WINDOW_SIZE}_{POLY_ORDER}.png"

plt.savefig(output_plot, dpi=300, bbox_inches='tight')
print(f"Plot saved to: {output_plot}")

plt.close(fig) # Close to free up memory

# 6.5 Save brightness data to CSV
csv_output_path = GRAPH_PATH / f"deflicker_rawpy_brightness_{folder_name}_{WINDOW_SIZE}_{POLY_ORDER}.csv"
print(f"Saving brightness data to: {csv_output_path}")

with open(csv_output_path, 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(['Frame', 'RawBrightness', 'SmoothedBrightness', 'ExposureCompensation', 'TiffBrightness_P1', 'TiffBrightness_P2'])

    # Write data row by row
    for i in range(len(M)):
        # Handle cases where tiff brightness lists might be shorter
        tiff_val_p1 = tiff_brightness_p1[i] if i < len(tiff_brightness_p1) else ''
        tiff_val_p2 = tiff_brightness_p2[i] if i < len(tiff_brightness_p2) else ''
        csv_writer.writerow([i, M[i], y_smooth[i], E[i], tiff_val_p1, tiff_val_p2])

# 7. Cleanup TIFFs
if tiff_folder.exists():
    print(f"Cleaning up TIFF folder: {tiff_folder}")
    shutil.rmtree(tiff_folder)

print(f"Completed at: {dt.now().strftime('%H:%M:%S')}")
