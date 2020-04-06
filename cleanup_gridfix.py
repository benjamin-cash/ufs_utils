import os
from subprocess import call 
from glob import glob

baseindir = "/scratch/02440/lmarx/ufs.s2s.c384_t025/run.CFSA/"
baseoutdir = "/scratch/02441/bcash/ufs.s2s.c384_t025/run.CFSA/postp/"

sfcinlist = glob(baseindir+"sfcf???.nc")
dyninlist = glob(baseindir+"dynf???.nc")

for sfcname in sfcinlist:
	print(sfcname)
	if not os.path.isfile(baseoutdir+sfcname.split("/")[-1]):
           try:
             dsin = xr.open_dataset(sfcname)
           except Exception as e:
             errchk = "xarray disallows such variables because they conflict with the coordinates used to label dimensions."
             if errchk in str(e):
               print("Grid error in "+sfcname+", attempting to fix")
               call(["ncrename", "-d", "grid_xt,ngrid_xt", "-d", "grid_yt,ngrid_yt", sfcname, baseoutdir+sfcname.split("/")[-1]])

for dynname in dyninlist:
           print(dynname)
           try:
             dsin = xr.open_dataset(baseoutdir+dynname.split("/")[-1])
           except Exception as e:
             errchk = "xarray disallows such variables because they conflict with the coordinates used to label dimensions."
             if errchk in str(e):
               print("Grid error in "+dynname+", attempting to fix")
               call(["ncrename", "-O", "-d", "grid_xt,ngrid_xt", "-d", "grid_yt,ngrid_yt", dynname, baseoutdir+dynname.split("/")[-1]])
