from herbie import Herbie
from herbie.toolbox import EasyMap, pc
from herbie import paint

import matplotlib.pyplot as plt
import matplotlib.font_manager as fmgr
from matplotlib import rcParams
import numpy as np

from PIL import Image

import warnings
warnings.filterwarnings('ignore')

rcParams["font.family"] = "Avenir Next"
rcParams["font.weight"] = "bold"

def get(i,d,h):
    H = Herbie(f"2025-03-{d} {i}:00", model="nam", fxx=h)
    ds = H.xarray(f":TMP:2 m above ground")
    return ds, H

def plot(ds, H, h):
    H = H
    ax = EasyMap("50m", crs=ds.herbie.crs, figsize=[7, 7], dpi=400, add_coastlines=True, coastlines_kw={"color":"#1b2433"})
    ax = ax.LAND(edgecolor="k", linewidth=1)
    ax = ax.COUNTIES(edgecolor="k", linewidth=0.5)
    ax = ax.BORDERS(color="#aab9d1", linewidth=1)
    ax = ax.STATES(edgecolor="k", linewidth=1)
    ax = ax.LAKES(facecolor="#ffffff00", linewidth=0.5)
    ax = ax.ax

    p = ax.pcolormesh(
        ds.longitude,
        ds.latitude,
        (9/5)*(ds.t2m - 273.15) + 32,
        transform=pc,
        cmap = paint.NWSTemperature.cmap2,
        norm = paint.make_custom_cmaps(paint.NWSTemperature.name, paint.NWSTemperature.colors, ((paint.NWSTemperature.bounds*2)+30)*.75)[0],
    )
    

    fig = ax.get_figure()
    fig.suptitle(
        f"March 31st, 2025",
        x=0.125,
        y=0.91,
        horizontalalignment="left",
        color="#e1e8f2",
        size=21
    ) 
    ax.set_title(f"Mid-Atlantic // NAM 3km // Init @ {ds.time.dt.strftime('%H:%MZ %d %b %Y').item()}\nHour [{h}] // Valid @ {ds.valid_time.dt.strftime('%H:%MZ %d %b %Y').item()}", 
                loc="left", 
                color="#aab9d1", 
                size=11)

    ax.set_xlim(1500000, 2250000)
    ax.set_ylim(200000, 750000)

    fig.set_facecolor("#1b2433")
    plt.box(on=None)

    fig.text(.12,.065, "Made by Avinash Aravind", color="#e1e8f2", fontsize=14)
    fig.text(.12,.04, "Data from NOAA via AWS/NOMADS | Plotted using Herbie", color="#e1e8f2", fontsize=11, alpha=0.6)

    return ax, p

def aniplot(i,d, h=0):
    plt.clf()
    ds, H = get(i,d, h)
    ax, p = plot(ds, H, h)
    cb = plt.colorbar(
    p,
    ax=ax,
    orientation="horizontal",
    pad=0.01,
    label="2m Temperature (" + r"$\degree$F" + ")",
    spacing="proportional", 
    ticks=(((paint.NWSTemperature.bounds*2)+30)*.75)[1::4],
    )

    cb.ax.tick_params(color="#e1e8f2")
    cb.ax.set_xlabel("2m Temperature (" + r"$\degree$F" + ")", color="#e1e8f2", size=18)
    cb.ax.set_xticklabels((((paint.NWSTemperature.bounds*2)+30)*.75)[1::4].astype(int), color="#e1e8f2", size=14)
    cb.outline.set_visible(False)

    name = f"./images/frame{h}d{d}" 
    plt.savefig(name, dpi=400, bbox_inches="tight", pad_inches=0.3)
    return name

frames = []
for h in range(0,48):
    name = aniplot(18,31,h)
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
output_gif_path = "./gifs/nam_temp.gif"
# Create GIF
create_gif(frames, output_gif_path)

print(f"GIF created and saved at {output_gif_path}")