import os
from glob import glob

import numpy as np
import xarray as xr
import ESMF
import matplotlib.pyplot as plt

from ufsfileutils import get_filelist, open_filelist, get_fileroot
from ufsvarutils import parse_utgrid, esmf_regrid, copyattrs, create_regridder
from ufsvarutils import rotate_vector_cice5
def main():

# Define data directory
    datadir = os.environ.get('UFSOUTPUT_DIR')
    postdir = os.environ.get('UFSPOST_DIR')
    #flist = get_filelist(datadir,"*cice*nc")
    flist = get_filelist(datadir,"ufs.s2s.C384_t025.20120701.cmeps_v0.5.1.cice.h2_06h.2012-07-01-21600.nc")
    rlist = get_fileroot(flist)
    dsets = open_filelist(flist,__file__)

# Get target grid
    ds_out=xr.open_dataset(os.environ.get('CICE_TARGET_GRID'))

# Create tgrid
    txy = {'lon':dsets[0]['TLON'], 'lat':dsets[0]['TLAT']}
    uxy = {'lon':dsets[0]['ULON'], 'lat':dsets[0]['ULAT']}

# Create regridders
    tregrid = create_regridder(txy,ds_out, 'TGRID')
    uregrid = create_regridder(uxy,ds_out, 'UGRID')

# Get angle between tripole and N-S grids
    angle = dsets[0]['ANGLE']
    anglet = dsets[0]['ANGLET']

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

# Test rotation
        uvel_h_rot, vvel_h_rot = rotate_vector_cice5(dsin['uvel_h'], dsin['vvel_h'], "tripole", angle)
        utest = uregrid(uvel_h_rot)
        vtest = uregrid(vvel_h_rot)
        print(utest.shape)
        #plt.contourf(utest[0,:,:])
        #plt.show()
# Regrid each variable type separately
        #tvars = [esmf_regrid(dsin[vname],txy,ds_out,poles,vname) for vname in tlist]
        #uvars = [esmf_regrid(dsin[vname],uxy,ds_out,poles,vname) for vname in ulist]
        tvars = [tregrid(dsin[vname]) for vname in tlist]
        uvars = [uregrid(dsin[vname]) for vname in ulist]
        ngvars = [dsin[vname] for vname in olist]

# Merge variables in single xarray object
        dout = xr.merge(tvars+uvars+ngvars+utest+vtest)

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
        dout.to_netcdf(postdir+"/"+rlist[i]+"_regrid_0p25x0p25.nc")

# Delete xarray objects to avoid memory leak?
        del dout
if __name__ == "__main__":
    main()


