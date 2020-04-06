import os
from math import pi

import xarray as xr
import xesmf as xe
from cdo import Cdo

# Define variable list for processing
vlist = ['clwmr','delz','dpres','dzdt','hgtsfc','o3mr','pressfc','spfh','tmp','ugrd','vgrd']
#vlist = ['ugrd','vgrd']

# Open test file
datadir = "/glade/scratch/bcash/ufs.s2s.c384_t025.jan/run/"
#datadir = os.environ.get('UFSOUTPUT_DIR')
tile1 = xr.open_dataset(datadir+"atmos_4xdaily.tile1.nc")
tile2 = xr.open_dataset(datadir+"atmos_4xdaily.tile2.nc")
tile3 = xr.open_dataset(datadir+"atmos_4xdaily.tile3.nc")
tile4 = xr.open_dataset(datadir+"atmos_4xdaily.tile4.nc")
tile5 = xr.open_dataset(datadir+"atmos_4xdaily.tile5.nc")
tile6 = xr.open_dataset(datadir+"atmos_4xdaily.tile6.nc")

print(tile1)
exit()

# Rename grid_yt->lat and grid_xt->lon for xESMF regridding
ds = dsin.rename({'grid_xt':'lon','grid_yt':'lat'})

# Convert lat-lon from radians to degrees
ds['lon']=ds['lon']*180/pi
ds['lat']=ds['lat']*180/pi

# Read in list of variables to process
din=[ds[vname] for vname in vlist]

# Generate weights for regridding
#ds_out=xe.util.grid_global(0.25,0.25)
#ds_out.to_netcdf("0p25x0p25_regular_grid.nc")
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
dout.to_netcdf(datadir+"dynf_regrid_0p25x0p25.nc")
