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