import os
from math import pi
from glob import glob

import xarray as xr
import xesmf as xe

def get_filelist(targetdir, fglob):
    flist = glob(targetdir+fglob)
    return flist

def open_filelist(filelist):
    xrdsets = [xr.open_dataset(fname) for fname in filelist]
    return xrdsets

def get_fileroot(filelist):
# This function will take the input file list and return everything except the
# .nc extension so that it can be used to create the path and name for the regridded
# file.
    rootname = [fname.split("/")[-1].split(".nc")[0] for fname in filelist]
    return rootname

def main():
# Define data directory
    # dsin = [xr.open_dataset(fname) for fname in flist]
    #datadir = "/glade/scratch/bcash/ufs.s2s.c384_t025.jan/run/"
    datadir = os.environ.get('UFSOUTPUT_DIR')
    postdir = os.environ.get('UFSPOST_DIR')
    dynf = os.environ.get('UFSOUTPUT_DYNF')
    sfcf = os.environ.get('UFSOUTPUT_SFCF')
    dynlist = get_filelist(datadir,dynf+"???.nc")
    sfclist = get_filelist(datadir,sfcf+"???.nc")
    flist = dynlist+sfclist
    rlist = get_fileroot(flist)
    dsets = open_filelist(flist)

# Iterate over open files
    for i, dsin in enumerate(dsets):
        print(dsin)
        print(rlist[i])
        vlist = list(dsin.data_vars.keys())

# Drop grid_xt and grid_yt from the list of variables to process
        vlist.remove("grid_xt")
        vlist.remove("grid_yt")

# Rename grid_yt->lat and grid_xt->lon for xESMF regridding
        ds = dsin.rename({'grid_xt':'lon','grid_yt':'lat'})

# Convert lat-lon from radians to degrees
        ds['lon']=ds['lon']*180/pi
        ds['lat']=ds['lat']*180/pi

# Read in list of variables to process
        din=[ds[vname] for vname in vlist]
        print(din)
# Generate weights for regridding
#ds_out=xe.util.grid_global(0.25,0.25)
#ds_out.to_netcdf("0p25x0p25_regular_grid.nc")
# ds_out=xr.open_dataset("0p25x0p25_regular_grid.nc")
        ds_out=xr.open_dataset(os.environ.get('TARGET_GRID'))
        regridder = xe.Regridder(ds,ds_out,'bilinear',reuse_weights=True)

# Regrid over variable list
        rgrd=[regridder(dx) for dx in din]

# Merge regridded variable list
        dout = xr.merge(rgrd)

# Add global attribute for CF compliance
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
        dout['lat'].attrs = dsin['grid_yt'].attrs
        dout['lon'].attrs = dsin['grid_xt'].attrs

# Copy over variable attributes
        for vname in vlist:
            dout[vname].attrs = ds[vname].attrs
            dout[vname].encoding['missing_value']=ds[vname].encoding['missing_value']
            dout[vname].encoding['_FillValue']=ds[vname].encoding['_FillValue']

# Fix NaN value for temperature
#dout['tmp'].attrs['_FillValue']=0.
# Write output
        if not os.path.exists(postdir):
            os.makedirs(postdir)
        dout.to_netcdf(postdir+"/"+rlist[i]+"_regrid_0p25x0p25.nc")

if __name__ == "__main__":
    main()
