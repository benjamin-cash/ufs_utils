import os
from glob import glob
import xarray as xr
from subprocess import call

def check_xrgrid(flist):
# The function checks to see if the file grid is xarray compatible and renames it if not
   for fname in flist:
    try:
      dsin = xr.open_dataset(fname)
    except Exception as e:
      errchk = "xarray disallows such variables because they conflict with the coordinates used to label dimensions."
      if errchk in str(e):
         print("Grid error in "+fname+", attempting to fix")
         call(["ncrename", "-O", "-d", "grid_xt,ngrid_xt", "-d", "grid_yt,ngrid_yt", fname])
         dsin = xr.open_dataset(fname)

def get_filelist(targetdir, fglob):
    flist = glob(targetdir+"/"+fglob)
    return flist

def open_filelist(filelist, sname):
    xrdsets = [xr.open_dataset(fname,decode_times=False) for fname in filelist]
    if not xrdsets:
       print("No files found, "+sname+" exiting.")
       exit()
    else:
       return xrdsets

def get_fileroot(filelist):
# This function will take the input file list and return everything except the
# .nc extension so that it can be used to create the path and name for the regridded
# file.
    rootname = [fname.split("/")[-1].split(".nc")[0] for fname in filelist]
    return rootname

