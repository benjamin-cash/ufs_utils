import os
from math import pi
from glob import glob

import xarray as xr
import xesmf as xe

from ufsfileutils import get_filelist, open_filelist, get_fileroot, check_xrgrid

def main():

# Set model output and postprocessing directories
    datadir = os.environ.get('UFSOUTPUT_DIR')
    postdir = os.environ.get('UFSPOST_DIR')

# Read in target grid
    ds_out=xr.open_dataset(os.environ.get('SFCF_TARGET_GRID'))
    
# Get list of files to process
    flist = get_filelist(datadir,"sfcf???.nc")

# Netcdf output from the model has poorly defined dimensions that causes
# an xarray error. 
    check_xrgrid(flist)

# Get list of file roots for naming output file later
    rlist = get_fileroot(flist)

# Open the files as xarray datasets    
    dsets = open_filelist(flist, __file__)

# Iterate over open files
    for i, dsin in enumerate(dsets):
        print(dsin)
        print(rlist[i])

# Get variables to process
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

# Generate weights for regridding. Only needs to be done once.
        if i==0:
         regridder = xe.Regridder(ds,ds_out,'bilinear',reuse_weights=True,periodic=True)

# Regrid each variable in the list
        rgrd=[regridder(dx) for dx in din]

# Merge regridded variable list into a single dataset
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

# Set unlimited dimension
        dout.encoding['unlimited_dims']="time"

# Write output
        if not os.path.exists(postdir):
            os.makedirs(postdir)
        dout.to_netcdf(postdir+"/"+rlist[i]+"_regrid_0p25x0p25.nc")

if __name__ == "__main__":
    main()
