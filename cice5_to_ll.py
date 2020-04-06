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
    flist = get_filelist(datadir,"*cice*nc")
    #flist = get_filelist(datadir,"ufs.s2s.C384_t025.20120701.cmeps_v0.5.1.cice.h2_06h.2012-07-01-21600_regrid_0p25x0p25.nc")
    rlist = get_fileroot(flist)
    dsets = open_filelist(flist,__file__)

# Get target grid
    regriddir = os.environ.get('REGRID_DIR')
    target_grid = os.environ.get('CICE_TARGET_GRID')
    ds_out=xr.open_dataset(regriddier+target_grid)

# Create target tripolar grids
    txy = {'lon':dsets[0]['TLON'], 'lat':dsets[0]['TLAT']}
    uxy = {'lon':dsets[0]['ULON'], 'lat':dsets[0]['ULAT']}

# Create input latlon grid
    llxy = {'lon':ds_out[0]['lon'], 'lat':ds_out['lat']}

# Create regridders
    tregrid = create_regridder(txy, llxy, 'TGRID.to.'+target_grid)
    uregrid = create_regridder(uxy, llxy, 'UGRID.to.'target_grid)

# Get angle between tripole and N-S grids
    angle = ds_out['ANGLE']

# Define pole types
#    poles = {}
#    poles['ds_in'] = np.array([ESMF.PoleKind.MONOPOLE, ESMF.PoleKind.MONOPOLE], np.int32)
#    poles['ds_out'] = np.array([ESMF.PoleKind.MONOPOLE, ESMF.PoleKind.MONOPOLE], np.int32)
 
# Iterate over open files
    for i, dsin in enumerate(dsets):
        print(flist[i])
        vlist = list(dsin.data_vars.keys())
        glist = {vname:parse_utgrid(dsin,vname) for vname in vlist}

# Create list of different variable types
        tlist = [vname for vname in vlist if "TLAT" in glist[vname]]
        ulist = [vname for vname in vlist if "ULAT" in glist[vname]]
        olist = [vname for vname in vlist if "NA" in  glist[vname]]
        print(ulist)

# Check ugrid variables for vector pairs
        xlist = [vname for vname in ulist if "(x)" in dsin[vname].attrs['long_name']]
        ylist = [vname for vname in ulist if "(y)" in dsin[vname].attrs['long_name']]
        slist = [vname for vname in ulist if "(y)" not in dsin[vname].attrs['long_name'] and "(x)" not in dsin[vname].attrs['long_name']]

# Create list of vector pairs
# NOTE NOTE NOTE this relies on the vector pairs being written out in the propoer order!        
        vpairs = list(zip(xlist,ylist))

# Rotate vector pairs
        xrot={}
        yrot={}
        for vpair in vpairs:
           print(vpair)
           print(dsin[vpair[0]], dsin[vpair[0]])
           xrot[vpair[0]],yrot[vpair[1]] = rotate_vector_cice5(dsin[vpair[0]],dsin[str(vpair[1])], "tripole", angle)
           xrot[vpair[0]].name=vpair[0]
           yrot[vpair[1]].name=vpair[1]

# Regrid each variable type separately
        tvars = [tregrid(dsin[vname]) for vname in tlist]
        uvars = [uregrid(xrot[vname]) for vname in xlist]
        vvars = [uregrid(yrot[vname]) for vname in ylist]
        svars = [uregrid(dsin[vname]) for vname in slist]
        ngvars = [dsin[vname] for vname in olist]

# Merge variables in single xarray object
        dout = xr.merge(tvars+uvars+vvars+svars+ngvars)

        dout.attrs['Conventions']="CF-1.7"

# Set data and metadata for output grid
        x=dout['lon'][0,:]
        y=dout['lat'][:,0]

        dout['y']=y
        dout['y'].attrs['long_name']="latitude"
        dout['y'].attrs['units']="degrees_N"
        dout['y'].attrs['cartesian_axis']="Y"
        dout['x']=x
        dout['x'].attrs['long_name']="longitude"
        dout['x'].attrs['units']="degrees_E"
        dout['x'].attrs['cartesian_axis']="X"

# Copy over variable attributes

        dout = copyattrs(dsin, dout, tlist)
        dout = copyattrs(dsin, dout, ulist)
        dout = copyattrs(dsin, dout, olist)

# Fix NaN value for temperature
#dout['tmp'].attrs['_FillValue']=0.
# Write output
        if not os.path.exists(postdir):
            os.makedirs(postdir)
        dout.to_netcdf(postdir+"/"+rlist[i]+"_regrid_0p25x0p25..nc")

# Delete xarray objects to avoid memory leak?
        del dout

if __name__ == "__main__":
    main()


