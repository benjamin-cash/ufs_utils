import os
from glob import glob

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

from ufsfileutils import get_filelist, open_filelist, get_fileroot
from ufsvarutils import parse_utgrid, esmf_regrid, copyattrs, create_regridder
from ufsvarutils import rotate_vector_cice5
def main():

# Define data directory
    datadir = os.environ.get('UFSOUTPUT_DIR')
    postdir = os.environ.get('UFSPOST_DIR')
    #flist = get_filelist(datadir,"*cice*nc")
    flist = get_filelist(datadir,"ufs.s2s.C384_t025.20120701.cmeps_v0.5.1.cice.h2_06h.2012-07-01-21600_regrid_0p25x0p25.nc")
    rlist = get_fileroot(flist)
    dsets = open_filelist(flist,__file__)
    uname = 'uvel_h'
    vname = 'vvel_h'
    vlist = ['uvel_h','vvel_h']

# Get target grid
    ds_out=xr.open_dataset(os.environ.get('CICE_TARGET_GRID'))
    dsin = dsets[0]
# Create target tripolar grids
    txy = {'lon':ds_out['TLON'], 'lat':ds_out['TLAT']}
    uxy = {'lon':ds_out['ULON'], 'lat':ds_out['ULAT']}

# Create input latlon grid
    llxy = {'lon':dsets[0]['lon'], 'lat':dsets[0]['lat']}

# Create regridders
    tregrid = create_regridder(llxy, txy, '0p25x0p25.to.TGRID')
    uregrid = create_regridder(llxy, uxy, '0p25x0p25.to.UGRID')

# Get angle between tripole and N-S grids
    angle = ds_out['ANGLE']

# Regrid from LL to tripole grid
    ureg = uregrid(dsin[uname]) 
    vreg = uregrid(dsin[vname])

# Rotate vector pairs
    xrot,yrot = rotate_vector_cice5(ureg,vreg, "latlon", angle)
    xrot.name=uname
    yrot.name=vname

# Merge variables in single xarray object
    dout = xrot.to_dataset(name=uname)
    dout[vname]=yrot 

    dout.attrs['Conventions']="CF-1.7"

# Set data and metadata for output grid
    x=dout['ULON']
    y=dout['ULAT']

    dout['y']=y
    dout['y'].attrs['long_name']="latitude"
    dout['y'].attrs['units']="degrees_N"
    dout['y'].attrs['cartesian_axis']="Y"
    dout['x']=x
    dout['x'].attrs['long_name']="longitude"
    dout['x'].attrs['units']="degrees_E"
    dout['x'].attrs['cartesian_axis']="X"

# Copy over variable attributes

    dout = copyattrs(dsin, dout, vlist)

# Fix NaN value for temperature
#dout['tmp'].attrs['_FillValue']=0.
# Write output
    if not os.path.exists(postdir):
        os.makedirs(postdir)
    dout.to_netcdf(postdir+"/"+uname+"_"+vname+"_regrid_tripolar.nc")

# Delete xarray objects to avoid memory leak?
    del dout

if __name__ == "__main__":
    main()


