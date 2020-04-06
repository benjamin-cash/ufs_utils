import os
import xarray as xr

from ufsfileutils import get_filelist, open_filelist, get_fileroot
from ufsvarutils import create_regridder

def main():

# Define data directory
    print("Get environment variables.")
    datadir = os.environ.get('UFSDATA_DIR')
    postdir = os.environ.get('UFSPOST_DIR')
    regriddir = os.environ.get('REGRID_DIR')
    cice_grid = os.environ.get('CICE5_GRID')
    ora_grid = os.environ.get('ORAS5_GRID')
    print("End get environment variables.")

# Get grid information
    print("Begin open files.")
    flist = get_filelist(datadir,"*restart_ice.nc")
    rlist = get_fileroot(flist)
    dsets = open_filelist(flist,__file__)
    dscice = xr.open_dataset(regriddir+cice_grid+".nc")
    dsora = xr.open_dataset(regriddir+ora_grid+".nc")
    print("End open files.")

# Define ORAS5 grid
    print("Begin define grids.")
    txy = {'lat':dsora['nav_lat'].squeeze(), 'lon':dsora['nav_lon'].squeeze()}

# Define MOM6 tracer grid
    cicexy = {'lon':dscice['TLON'], 'lat':dscice['TLAT']}
    print("End define grids.")

# Create regridders
    print("Begin regridder creation.")
    tregrid = create_regridder(txy, cicexy, 'ORAS5ice.to.'+cice_grid,regriddir)
    print("End regridder creation.")

# Set variable list
    tlist = ['frld', 'hicif', 'hsnif', 'sist', 'tbif1', 'tbif2', 'tbif3']

# Iterate over open files
    for i, dsin in enumerate(dsets):
        print(flist[i])

# Regrid each variable type separately to the latlon grid
        print("Begin regridding.")
        tvars = [tregrid(dsin[vname]) for vname in tlist]
        print("End regridding.")

# Merge variables in single xarray object
        dout = xr.merge(tvars)

# Add CF convention information
        dout.attrs['Conventions']="CF-1.7"


# Fix NaN value for temperature
#dout['tmp'].attrs['_FillValue']=0.
# Write output
        if not os.path.exists(postdir):
            os.makedirs(postdir)
        dout.to_netcdf(postdir+"/"+rlist[i]+"_regrid_"+cice_grid+".nc")

# Delete xarray objects to avoid memory leak?
        del dout

if __name__ == "__main__":
    main()


