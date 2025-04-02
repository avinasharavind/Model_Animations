from herbie import Herbie
from herbie.toolbox import EasyMap, pc
from herbie import paint

import matplotlib.pyplot as plt
import matplotlib.font_manager as fmgr
from matplotlib import rcParams
import numpy as np

from PIL import Image
import warnings
import time

warnings.filterwarnings('ignore')

rcParams["font.family"] = "Avenir Next"
rcParams["font.weight"] = "bold"

def get(i,d):
    if i<10:
        i = f"0{i}"
    H = Herbie(f"2025-03-{d} {i}:00", model="rtma", product="anl")
    ds = H.xarray(":GUST:10 m above ground:anl")
    return ds, H

def plot(ds, H):
    H = H
    ax = EasyMap("50m", crs=ds.herbie.crs, figsize=[7, 7], dpi=400, add_coastlines=True, coastlines_kw={"color":"#1b2433"})
    ax = ax.LAND(edgecolor="k", linewidth=1)
    ax = ax.COUNTIES(edgecolor="k", linewidth=0.5)
    ax = ax.BORDERS(color="#aab9d1", linewidth=1)
    ax = ax.STATES(edgecolor="k", linewidth=1)
    ax = ax.LAKES(facecolor="#ffffff00", linewidth=0.5)
    ax = ax.ax

    colors = paint.NWSWindSpeed.colors
    norm, norm2 = paint.make_custom_cmaps("customwind", colors, paint.NWSWindSpeed.bounds*1.5)

    p = ax.pcolormesh(
        ds.longitude,
        ds.latitude,
        ds.i10fg*2,
        transform=pc,
        cmap = plt.get_cmap("customwind"),
        norm = norm2,
    )

    ax.set_title(
        f"March 16th Severe Wind Event \nReal-Time Mesoscale Analysis",
        loc="left",
        color="#e1e8f2",
        size=14
    )
    ax.set_title(f"Northeast US\n@ {ds.valid_time.dt.strftime('%H:%MZ %d %b %Y').item()}", 
                 loc="right", 
                 color="#aab9d1", 
                 size=14)

    ax.set_xlim(1000000, 2500000)
    ax.set_ylim(1500000, 2750000)

    fig = ax.get_figure()
    fig.set_facecolor("#1b2433")
    plt.box(on=False)

    fig.text(.12,.065, "Made by Avinash Aravind", color="#e1e8f2", fontsize=14)
    fig.text(.12,.04, "Data from NOAA via AWS/NOMADS | Plotted using Herbie", color="#aab9d1", fontsize=11)

    return ax, p

def aniplot(i,d):
    plt.clf()
    ds, H = get(i,d)
    ax, p = plot(ds, H)
    cb = plt.colorbar(
    p,
    ax=ax,
    orientation="horizontal",
    pad=0.01,
    label="10m Wind Gusts (" + r"mph" + ")",
    spacing="proportional",
    ticks=(paint.NWSWindSpeed.bounds*1.5)[1::2]
    )

    cb.ax.tick_params(color="#e1e8f2")
    cb.ax.set_xlabel("10m Wind Gusts (" + r"mph" + ")", color="#e1e8f2", size=18)
    cb.ax.set_xticklabels((paint.NWSWindSpeed.bounds*1.5)[1::2].astype(int), color="#e1e8f2", size=14)
    cb.outline.set_visible(False)
    cb.minorticks_off()

    name = f"images/frame{i}d{d}"
    plt.savefig(name, dpi=400, bbox_inches="tight", pad_inches=0.3)
    return name

sttime = time.time()

frames = []
d=24
for i in range(0,16):
    name = aniplot(i,d)
    frames.append(name)

def create_gif(image_paths, output_gif_path, duration=500):
    images = [Image.open(f"{image_path}.png") for image_path in image_paths]
    # Save as GIF
    images[0].save(
    output_gif_path,
    save_all=True,
    append_images=images[1:],
    duration=duration,
    loop=0 # 0 means infinite loop
    )

# List of image file paths
# Output GIF path
output_gif_path = "gifs/rtmawind.gif"
# Create GIF
create_gif(frames, output_gif_path)

print(f"GIF created and saved at {output_gif_path} in {time.time()-sttime:6.3f}s")