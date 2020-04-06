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
    datadir = os.environ.get('INPUT_DIR')
    postdir = os.environ.get('INPUT_DIR')
    regriddir = os.environ.get('REGRID_DIR')
    gspec = os.environ.get('MOM6_TARGET_GRID')
    flist = get_filelist(datadir,"oras5_MOM6_IC_UV_v1.nc")
    dsets = open_filelist(flist,__file__)
    uname = 'u'
    vname = 'v'
    vlist = ['u','v']

# Get target grid
    ds_stat=xr.open_dataset(regriddir+gspec)

# Get various coordinate combinations
    xhyh,xhyq,xqyh,xqyq = parse_mom6static(ds_stat)
    print(xhyh,xhyq,xqyh,xqyq)

# Create input latlon grid
    llxy = {'lon':dsets[0]['xt_ocean'], 'lat':dsets[0]['yt_ocean']}

# Create regridders
# ORAS5 latlon to MOM6 Ct grid
    xhyhregrid = create_regridder(llxy, xhyh, "0p25x0p25.to.xhyh", regriddir)

#MOM6 Ct grid to U    
    xhyh_to_xqyh = create_regridder(xhyh, xqyh, "xhyh.to.xqyh", regriddir)

# MOM6 Ct grid to V
    xhyh_to_xhyq = create_regridder(xhyh, xhyq, "xhyh.to.xhyq", regriddir)

# Get angles between MOM6 tripole and N-S grids
    sin_rot = ds_stat['sin_rot']
    cos_rot = ds_stat['cos_rot']

# Regrid from LL to xhyh grid where rotation angle is defined
    #plt.contourf(usets[0][uname][0,0,:,:])
    #plt.colorbar()
    #plt.show()

    uct = xhyhregrid(dsets[0][uname])
    vct = xhyhregrid(dsets[0][vname])
    #plt.contourf(uct[0,0,:,:])
    #plt.colorbar()
    #plt.show()

# Rotate vector pairs
    xrot,yrot = rotate_vector_mom6(uct, vct, "latlon", sin_rot, cos_rot)
    xrot.name=uname
    yrot.name=vname

# Regrid from Ct to staggered U and V 
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

    #dout = copyattrs(usets[0], dout, ulist)
    #dout = copyattrs(vsets[0], dout, vlist)

# Write output
    if not os.path.exists(postdir):
        os.makedirs(postdir)
    dout.to_netcdf(postdir+"/ORAS5_"+uname+"_"+vname+"_to_MOM6_tripolar.nc")

# Delete xarray objects to avoid memory leak?
    del dout

if __name__ == "__main__":
    main()


