import os
from glob import glob

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

from ufsfileutils import get_filelist, open_filelist, get_fileroot
from ufsvarutils import parse_utgrid, esmf_regrid, copyattrs, create_regridder
from ufsvarutils import rotate_vector_mom6, parse_mom6static
def main():

# Define data directory
    datadir = os.environ.get('UFSOUTPUT_DIR')
    postdir = os.environ.get('UFSPOST_DIR')
    regriddir = os.environ.get('REGRID_DIR')
    gspec = os.environ.get('MOM6_TARGET_GRID')
    flist = get_filelist(datadir,"ufs.s2s.C384_t025.20120701.cmeps_v0.5.1.mom6.sfc._2012_07_01_03600_regrid_0p25x0p25.nc")
    rlist = get_fileroot(flist)
    dsets = open_filelist(flist,__file__)
    dsin = dsets[0]
    uname = 'SSU'
    vname = 'SSV'
    vlist = ['SSU','SSV']

# Get target grid
    ds_stat=xr.open_dataset(regriddir+gspec)

# Get various coordinate combinations
    xhyh,xhyq,xqyh,xqyq = parse_mom6static(ds_stat)
    print(xhyh,xhyq,xqyh,xqyq)

# Create input latlon grid
    llxy = {'lon':dsin['lon'], 'lat':dsin['lat']}

# Create regridders
    xhyhregrid = create_regridder(llxy, xhyh, "0p25x0p25.to.xhyh", regriddir)
    xhyqregrid = create_regridder(llxy, xhyq, "0p25x0p25.to.xhyq", regriddir)
    xqyhregrid = create_regridder(llxy, xqyh, "0p25x0p25.to.xqyh", regriddir)
    xqyqregrid = create_regridder(llxy, xqyq, "0p25x0p25.to.xqyq", regriddir)
    xhyh_to_xqyh = create_regridder(xhyh, xqyh, "xhyh.to.xqyh", regriddir)
    xhyh_to_xhyq = create_regridder(xhyh, xhyq, "xhyh.to.xhyq", regriddir)

# Get angles between tripole and N-S grids
    sin_rot = ds_stat['sin_rot']
    cos_rot = ds_stat['cos_rot']

# Regrid from LL to xhyh grid where rotation angle is defined
    uct = xhyhregrid(dsin[uname])
    vct = xhyhregrid(dsin[vname])
    plt.contourf(dsin[uname][0,:,:])
    plt.colorbar()
    plt.show()
# Rotate vector pairs
    xrot,yrot = rotate_vector_mom6(uct,vct, "latlon", sin_rot, cos_rot)
    xrot.name=uname
    yrot.name=vname

#Restagger
    xout = xhyh_to_xqyh(xrot)
    yout = xhyh_to_xhyq(yrot)    

# Merge variables in single xarray object
    dout = xout.to_dataset(name=uname)
    dout[vname]=yout 

    dout.attrs['Conventions']="CF-1.7"

# Set data and metadata for output grid
    x=ds_stat['geolon']
    y=ds_stat['geolat']

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


