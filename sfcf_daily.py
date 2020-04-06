import xarray as xr
import os

expver=os.environ.get('EXPVER')
print(expver)

dsets = xr.open_mfdataset("/scratch/02441/bcash/ufs.s2s.c384_t025/run."+expver+"/postp/sfcf???_regrid*nc")
print(dsets)

# Get variable information
vlist = list(dsets.data_vars.keys())

# Downsample to daily mean
avg = dsets.resample(time="D",keep_attrs=True).mean('time')

# Copy over attribute data
for vname in vlist:
            avg[vname].attrs = dsets[vname].attrs
            avg[vname].encoding['_FillValue']=dsets[vname].encoding['_FillValue']

# Write out file
avg.to_netcdf("/scratch/02441/bcash/ufs.s2s.c384_t025/run."+expver+"/postp/sfcf_daily_"+expver+"_0p25x0p25.nc")
