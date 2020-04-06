import sys
import xarray as xr
import xesmf as xe
import re
import psutil
import numpy as np
import ESMF

def parse_utgrid(dsin,vname):
    try:
       gtype = dsin[vname].encoding['coordinates']
    except:
       gtype = "Not a grid" 
    return gtype

def find_vector_pairs_cice5(dsin, unames):
    # Get variable long name
    lname = vin['long_name']

def rotate_vector_cice5(uin, vin, gridin, angle):
    if gridin == "tripole":
       urot = uin*np.cos(angle)-vin*np.sin(angle)
       vrot = uin*np.sin(angle)+vin*np.cos(angle)
    elif gridin == "latlon":
       urot = uin*cos(angle)+vin*sin(angle)
       vrot = vin*cos(angle)-uin*sin(angle)
    else:
       print("Grid type not recognized.")
       print("Valid options are 'tripole' or 'latlon'")
       exit()
    return urot, vrot

