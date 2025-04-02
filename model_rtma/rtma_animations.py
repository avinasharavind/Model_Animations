from herbie import Herbie
from herbie.toolbox import EasyMap, pc
from herbie import paint

import matplotlib.pyplot as plt
from matplotlib import rcParams
import numpy as np

from PIL import Image
import warnings
import time

import helpers

warnings.filterwarnings('ignore')

rcParams["font.family"] = "Avenir Next"
rcParams["font.weight"] = "bold"

"""
Varidict holds variable information in the following format:
[Herbie Search Key, Conversion Function, cmap, norm, cbar label, ticklabels]
"""
varidict = {
    "temp": [":TMP:2 m above ground:anl", helpers.tempHelp, paint.NWSTemperature.cmap2, helpers.tempNorm, "2m Temperature (" + r"$\degree$F" + ")", (((paint.NWSTemperature.bounds*2)+30)*.75)[1::4]], 
    }

class realTime:
    """
    Class realTime initalizes a realTime object for easy animation.
    """
    def __init__(self, d, init):
        self.model = "rtma"
        self.d = d
        self.i = init

        self.H = None
        self.ds = None
        self.searchKey = None
        self.convertFunc = None
        self.cmap = None
        self.norm = None
        self.label = None
        self.ticks = None
        self.ax = None
        self.p = None
        self.var = None
        
        self.frames = []

    def variable(self, var):
        """
        Must be one of the following:
            "temp" for Temperature
        """
        self.var = var

        varinfo = varidict[var]
        self.searchKey = varinfo[0]
        self.convertFunc = varinfo[1]
        self.cmap = varinfo[2]
        self.norm = varinfo[3]
        self.label = varinfo[4]
        self.ticks = varinfo[5]

    def plot(self):
        if self.i<10:
            self.i = f"0{self.i}"
        H = Herbie(f"2025-04-{self.d} {self.i}:00", model="rtma", product="anl")

        self.H = H

        ds = self.H.xarray(self.searchKey)
        self.ds = ds

        plt.clf()
        ax = EasyMap("50m", crs=self.ds.herbie.crs, figsize=[7, 7], dpi=400, add_coastlines=True, coastlines_kw={"color":"#1b2433"})
        ax = ax.LAND(edgecolor="k", linewidth=1)
        ax = ax.COUNTIES(edgecolor="k", linewidth=0.5)
        ax = ax.BORDERS(color="#aab9d1", linewidth=1)
        ax = ax.STATES(edgecolor="k", linewidth=1)
        ax = ax.LAKES(facecolor="#ffffff00", linewidth=0.5)
        ax = ax.ax

        p = ax.pcolormesh(
            self.ds.longitude,
            self.ds.latitude,
            self.convertFunc(self.ds),
            transform=pc,
            cmap = self.cmap,
            norm = self.norm(),
        )

        ax.set_title(
            f"{self.ds.time.dt.strftime('%b %d, %Y').item()}\nReal-Time Mesoscale Analysis",
            loc="left",
            color="#e1e8f2",
            size=14
        )
        ax.set_title(f"Mid-Atlantic\n@ {self.ds.valid_time.dt.strftime('%H:%MZ %d %b %Y').item()}", 
                    loc="right", 
                    color="#aab9d1", 
                    size=14)

        ax.set_xlim(1250000, 2250000)
        ax.set_ylim(1600000, 2100000)

        fig = ax.get_figure()
        fig.set_facecolor("#1b2433")
        plt.box(on=None)

        fig.text(.12,.065, "Made by Avinash Aravind", color="#e1e8f2", fontsize=14)
        fig.text(.12,.04, "Data from NOAA via AWS/NOMADS | Plotted using Herbie", color="#e1e8f2", fontsize=11, alpha=0.6)

        self.ax = ax
        self.p = p

        cb = plt.colorbar(
        p,
        ax=ax,
        orientation="horizontal",
        pad=0.01,
        label="2m Temperature (" + r"$\degree$F" + ")",
        spacing="proportional", 
        ticks=self.ticks,
        )

        cb.ax.tick_params(color="#e1e8f2")
        cb.ax.set_xlabel(self.label, color="#e1e8f2", size=18)
        cb.ax.set_xticklabels(self.ticks.astype(int), color="#e1e8f2", size=14)
        cb.outline.set_visible(False)

        name = f"images/frame{self.i}d{self.d}"
        plt.savefig(name, dpi=400, bbox_inches="tight", pad_inches=0.3)
        self.frames.append(name)
    
    def new_frame(self, i, d):
        self.i = i
        self.d = d
        self.plot()

    def create_gif(self):
        images = [Image.open(f"{image_path}.png") for image_path in self.frames]
        # Save as GIF
        images[0].save(
        f"gifs/rtma_{self.var}.gif",
        save_all=True,
        append_images=images[1:],
        duration=500,
        loop=0 # 0 means infinite loop
        )

        print(f"GIF created and saved!")

rtma = realTime(1, 12)
rtma.variable("temp")

d=1
for i in range(12,24):
    rtma.new_frame(i, d)

rtma.create_gif()

        