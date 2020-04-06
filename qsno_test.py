import xarray as xr

# Density values
rhoi = 917.0 # Density of ice
rhos = 330.0 # Density of snow
cp_ice = 2106.0 # Specific heat of fresh ice
cp_ocn = 4218.0 # Specific heat of sea water
Lfresh = 3.34e5 # Latent heat of melting fresh ice

print(Lfresh)
qsno = xr.open_dataset('cice_20120101_test.nc')['qsno001']
vsno = xr.open_dataset('cice_20120101_test.nc')['vsnon']
tsfc = (Lfresh+qsno/rhos)/cp_ice
tsfc = tsfc.where(vsno>0,0) 
tsfc.to_netcdf('test.nc')
