import os
from glob import glob

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

from ufsfileutils import get_filelist, open_filelist, get_fileroot
from ufsvarutils import copyattrs, create_regridder

def main():

# Define data directory
    print("Get environment variables.")
    datadir = os.environ.get('UFSDATA_DIR')
    postdir = os.environ.get('UFSPOST_DIR')
    regriddir = os.environ.get('REGRID_DIR')
    mom_grid = os.environ.get('MOM6_GRID')
    ora_grid = os.environ.get('ORAS5_GRID')
    print("End get environment variables.")

# Get grid information
    print("Begin open files.")
    flist = get_filelist(datadir,"*restart.nc")
    rlist = get_fileroot(flist)
    dsets = open_filelist(flist,__file__)
    dsmom = xr.open_dataset(regriddir+mom_grid+".nc")
    dsora = xr.open_dataset(regriddir+ora_grid+".nc")
    print("End open files.")

# Define ORAS5 grid
    print("Begin define grids.")
    txy = {'lat':dsora['gphit'].squeeze(), 'lon':dsora['glamt'].squeeze()}

# Define MOM6 tracer grid
    momxy = {'lon':dsmom['geolon'], 'lat':dsmom['geolat']}
    print("End define grids.")

# Create regridders
    print("Begin regridder creation.")
    tregrid = create_regridder(txy, momxy, 'ORAS5T.to.'+mom_grid,regriddir)
    print("End regridder creation.")

# Set variable list
    tlist = ['tn', 'sn']

# Iterate over open files
    for i, dsin in enumerate(dsets):
        print(flist[i])

# Regrid each variable type separately to the latlon grid
        print("Begin regridding.")
        tvars = [tregrid(dsin[vname]) for vname in tlist]
        print("End regridding.")

# Merge variables in single xarray object
        dout = xr.merge(tvars)

        dout.attrs['Conventions']="CF-1.7"

# Set data and metadata for output grid

        dout['geolat']=dsmom['geolat']
        dout['geolon']=dsmom['geolon']

# Fix NaN value for temperature
#dout['tmp'].attrs['_FillValue']=0.
# Write output
        if not os.path.exists(postdir):
            os.makedirs(postdir)
        dout.to_netcdf(postdir+"/"+rlist[i]+"_regrid_0p25x0p25.nc")

# Delete xarray objects to avoid memory leak?
        del dout

if __name__ == "__main__":
    main()


