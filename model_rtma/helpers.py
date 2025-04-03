from herbie import Herbie
from herbie.toolbox import EasyMap, pc
from herbie import paint

import matplotlib.pyplot as plt
from matplotlib import rcParams
import numpy as np

from PIL import Image
import warnings
import time

warnings.filterwarnings('ignore')

rcParams["font.family"] = "Avenir Next"
rcParams["font.weight"] = "bold"

def tempHelp(temp):
    return (9/5)*(temp.t2m - 273.15) + 32

def tempNorm():
    return paint.make_custom_cmaps(paint.NWSTemperature.name, paint.NWSTemperature.colors, ((paint.NWSTemperature.bounds*2)+30)*.75)[0]

def windHelp(wind):
    return wind.i10fg*2

def windNorm():
    colors = paint.NWSWindSpeed.colors
    norm, norm2 = paint.make_custom_cmaps("customwind", colors, paint.NWSWindSpeed.bounds*1.5)
    return norm2

def windCmap():
    norm2 = windNorm()
    return plt.get_cmap("customwind")

def analysis_mapfix(ax):
    ax = ax.LAND(edgecolor="k", linewidth=1)
    ax = ax.COUNTIES(edgecolor="k", linewidth=0.5)
    ax = ax.BORDERS(color="#aab9d1", linewidth=1)
    ax = ax.STATES(edgecolor="k", linewidth=1)
    ax = ax.LAKES(facecolor="#ffffff00", linewidth=0.5)
    ax = ax.ax
    return ax

def precipHelp(precip):
    return precip.tp/25.4

def precipNorm():
    colors = paint.NWSPrecipitation.colors
    colors[0] = "#1b243300"
    norm, norm2 = paint.make_custom_cmaps("customprecip", colors, paint.NWSPrecipitation.bounds/25)
    return norm2

def precipCmap():
    norm2 = precipNorm()
    return plt.get_cmap("customprecip")

def precip_mapfix(ax):
    ax = ax.LAND(facecolor="#aab9d1", edgecolor="k", linewidth=1)
    ax = ax.COUNTIES(edgecolor="k", linewidth=0.5)
    ax = ax.BORDERS(color="#aab9d1", linewidth=1)
    ax = ax.STATES(facecolor="#aab9d1", edgecolor="k", linewidth=1)
    ax = ax.LAKES(facecolor="#1b243300", linewidth=0.5)
    ax = ax.OCEAN(facecolor="#1b2433")
    ax = ax.ax
    return ax