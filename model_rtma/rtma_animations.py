from herbie import Herbie
from herbie.toolbox import EasyMap, pc
from herbie import paint

import matplotlib.pyplot as plt
from matplotlib import rcParams
import numpy as np

from PIL import Image
import warnings
import os

import helpers

warnings.filterwarnings('ignore')

rcParams["font.family"] = "Avenir Next"
rcParams["font.weight"] = "bold"

"""
Varidict holds variable information in the following format:
[Herbie Search Key, Conversion Function, cmap, norm, cbar label, ticklabels, product, mapfix]
"""
varidict = {
    "temp": [":TMP:2 m above ground:anl", helpers.tempHelp, paint.NWSTemperature.cmap2, helpers.tempNorm, "2m Temperature (" + r"$\degree$F" + ")", (((paint.NWSTemperature.bounds*2)+30)*.75)[1::4].astype(int), "anl", helpers.analysis_mapfix], 
    "wind": [":GUST:10 m above ground:anl", helpers.windHelp, helpers.windCmap(), helpers.windNorm, "10m Wind Gusts (" + r"mph" + ")", (paint.NWSWindSpeed.bounds*1.5)[1::2].astype(int), "anl", helpers.analysis_mapfix],
    "precip": [None, helpers.precipHelp, helpers.precipCmap(), helpers.precipNorm, "Hourly Precipitation (" + r"in" + ")", (paint.NWSPrecipitation.bounds/25)[1::2], "pcp", helpers.precip_mapfix],
    }

class realTime:
    """
    Class realTime initalizes a realTime object for easy RTMA plotting and animation.
    The code is... not what I'd consider well written. But it works! And that's what matters, isn't it.
    """
    def __init__(self, m, d, init, title="def"):
        self.model = "rtma"
        self.m = m
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
        self.product = None
        self.mapfix = None
        self.spacing = None

        if title=="def":
            self.title = self.ds.time.dt.strftime('%b %d, %Y').item()
        else:
            self.title = title

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
        self.product = varinfo[6]
        self.mapfix = varinfo[7]

        if self.product=="anl":
            self.spacing="proportional"
        else:
            self.spacing="uniform"

    def plot(self):
        if self.i<10:
            self.i = f"0{self.i}"
        if self.m<10:
            self.m = f"0{self.m}"
        H = Herbie(f"2025-{self.m}-{self.d} {self.i}:00", model=self.model, product=self.product)

        self.H = H

        ds = self.H.xarray(self.searchKey)
        self.ds = ds

        plt.clf()
        ax = EasyMap("50m", crs=self.ds.herbie.crs, figsize=[7, 7], dpi=400, add_coastlines=True, coastlines_kw={"color":"#1b2433"})
        ax = self.mapfix(ax)

        p = ax.pcolormesh(
            self.ds.longitude,
            self.ds.latitude,
            self.convertFunc(self.ds),
            transform=pc,
            cmap = self.cmap,
            norm = self.norm(),
        )

        ax.set_title(
            f"{self.title}\nReal-Time Mesoscale Analysis",
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
        spacing=self.spacing, 
        ticks=self.ticks,
        )

        cb.ax.tick_params(color="#e1e8f2")
        cb.ax.set_xlabel(self.label, color="#e1e8f2", size=18)
        cb.ax.set_xticklabels(self.ticks, color="#e1e8f2", size=14)
        cb.outline.set_visible(False)

        name = f"images/d{self.d}frame{self.i}"
        plt.savefig(name, dpi=400, bbox_inches="tight", pad_inches=0.3)
        self.frames.append(name)
    
    def new_frame(self, m, d, i):
        self.m = m
        self.i = i
        self.d = d
        self.plot()

    def create_gif(self):
        images = [Image.open(f"{image_path}.png") for image_path in self.frames]
        images[0].save(
        f"gifs/rtma_{self.var}.gif",
        save_all=True,
        append_images=images[1:],
        duration=500,
        loop=0
        )

        print(f"GIF created and saved!")

    def clear_folder(self):
        folder_path = "images"

        for item in os.scandir(folder_path):
            if item.is_file():
                os.remove(item.path)

rtma = realTime(3, 29, 12, "Backdoor Cold Front")
rtma.variable("precip")

m=3
d=29
for i in range(20,24):
    rtma.new_frame(m,d,i)
d=30
for i in range(0,2):
    rtma.new_frame(m,d,i)

rtma.create_gif()
rtma.clear_folder()  #Comment out to leave frames in folder

        