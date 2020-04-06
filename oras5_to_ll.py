import os
from glob import glob

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

from ufsfileutils import get_filelist, open_filelist, get_fileroot
from ufsvarutils import copyattrs, create_regridder
from ufsvarutils import rotate_vector_oras5

import ESMF
ESMF.Manager(debug=True)

def main():

# Define data directory
    print("Get environment variables.")
    datadir = os.environ.get('UFSDATA_DIR')
    postdir = os.environ.get('UFSPOST_DIR')
    regriddir = os.environ.get('REGRID_DIR')
    ll_grid = os.environ.get('LL_GRID')
    ora_grid = os.environ.get('ORAS5_GRID')
    print("End get environment variables.")

# Get grid information
    print("Begin open files.")
    flist = get_filelist(datadir,"*restart.nc")
    rlist = get_fileroot(flist)
    dsets = open_filelist(flist,__file__)
    dsll=xr.open_dataset(regriddir+ll_grid+".nc")
    dsora =  xr.open_dataset(regriddir+ora_grid)
    print("End open files.")

# Define ORAS5 grid
    print("Begin define grids.")
    txy = {'lat':dsora['gphit'].squeeze(), 'lon':dsora['glamt'].squeeze()}
    uxy = {'lat':dsora['gphiu'].squeeze(), 'lon':dsora['glamu'].squeeze()}
    vxy = {'lat':dsora['gphiv'].squeeze(), 'lon':dsora['glamv'].squeeze()}
    fxy = {'lat':dsora['gphif'].squeeze(), 'lon':dsora['glamf'].squeeze()}

# Define latlon grid
    llxy = {'lon':dsll['lon'], 'lat':dsll['lat']}
    print("End define grids.")

# Create regridders
    print("Begin regridder creation.")
    tregrid = create_regridder(txy, llxy, 'ORAS5T.to.'+ll_grid,regriddir)
    uregrid = create_regridder(uxy, llxy, 'ORAS5U.to.'+ll_grid,regriddir)
    vregrid = create_regridder(vxy, llxy, 'ORAS5V.to.'+ll_grid,regriddir)
    fregrid = create_regridder(fxy, llxy, 'ORAS5F.to.'+ll_grid,regriddir) 
    print("End regridder creation.")

# Get angles between tripole and N-S grids
    print("Begin read grid angles.")
    cosu = dsora['cosu']
    sinu = dsora['sinu']
    cost = dsora['cost']
    sint = dsora['sint']
    cosv = dsora['cosv']
    sinv = dsora['sinv']
    cosf = dsora['cosf']
    sinf = dsora['sinf']
    print("End read grid angles.")

# Iterate over open files
    for i, dsin in enumerate(dsets):
        print(flist[i])

# Create list of variables pairs
        vpair = ['un','vn']
        tlist = ['tn','sn']

# Rotate vector pairs
        print("Begin vector rotation.")
        print(dsin[vpair[0]], dsin[vpair[1]])
        xrot,yrot = rotate_vector_oras5(dsin[vpair[0]],dsin[str(vpair[1])], "tripole", sinu, cosu)
        xrot.name=vpair[0]
        yrot.name=vpair[1]
        print("End vector rotation.")

# Regrid each variable type separately to the latlon grid
        print("Begin regridding.")
        tvars = [tregrid(dsin[vname]) for vname in tlist]
        uvars = uregrid(xrot)
        vvars = uregrid(yrot)
        print("End regridding.")

# Merge variables in single xarray object
        dout = xr.merge(tvars+uvars+vvars)

        dout.attrs['Conventions']="CF-1.7"

# Set data and metadata for output grid
        x=llxy['lon'][0,:]
        y=llxy['lat'][:,0]

        dout['y']=y
        dout['y'].attrs['long_name']="latitude"
        dout['y'].attrs['units']="degrees_N"
        dout['y'].attrs['cartesian_axis']="Y"
        dout['x']=x
        dout['x'].attrs['long_name']="longitude"
        dout['x'].attrs['units']="degrees_E"
        dout['x'].attrs['cartesian_axis']="X"

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


