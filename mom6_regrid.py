import os
import psutil
from glob import glob

import xarray as xr
import xesmf as xe

from ufsfileutils import get_filelist, open_filelist, get_fileroot
from ufsvarutils import parse_mom6static, parse_mom6grid, create_regridder, copyattrs

def main():

    proc = psutil.Process()

# Define data directory
    datadir = os.environ.get('UFSOUTPUT_DIR')
    postdir = os.environ.get('UFSPOST_DIR')
    gridfile = os.environ.get('MOM6_GRID_INFO')
    targetfiles = os.environ.get('UFSPOST_PROC')
    flist = get_filelist(datadir,"*"+targetfiles+"*")
    rlist = get_fileroot(flist)
    dsets = open_filelist(flist,__file__)
    print(flist)

# Get target grid
    ds_out=xr.open_dataset(os.environ.get('MOM6_TARGET_GRID'))

# Get various coordinate combinations
    xhyh,xhyq,xqyh,xqyq = parse_mom6static(dsmgrid)
    print(xhyh,xhyq,xqyh,xqyq)

# Create regridders
    xhyhregridder = create_regridder(xhyh,ds_out, "xhyh")
    xhyqregridder = create_regridder(xhyq,ds_out, "xhyq")
    xqyhregridder = create_regridder(xqyh,ds_out, "xqyh")
    xqyqregridder = create_regridder(xqyq,ds_out, "xqyq")

# Iterate over open files
    for i, dsin in enumerate(dsets):
        print(flist[i])
#        print(rlist[i])
        vlist = list(dsin.data_vars.keys())
        print(vlist)
        glist = {vname:parse_mom6grid(dsin,vname) for vname in vlist}
        print(glist)

# Create list of different variable types
        xhyhlist = [vname for vname in vlist if "xh" in glist[vname] and "yh" in glist[vname]]
        xqyhlist = [vname for vname in vlist if "xq" in glist[vname] and "yh" in glist[vname]]
        xhyqlist = [vname for vname in vlist if "xh" in glist[vname] and "yq" in glist[vname]]
        xqyqlist = [vname for vname in vlist if "xq" in glist[vname] and "yq" in glist[vname]]
        olist = [vname for vname in vlist if "NA" in  glist[vname]]
        print("xhyh list is:",xhyhlist)
        print("xhyq list is:",xhyqlist)
        print("xqyh list is:",xqyhlist)
        print("xqyq list is:",xqyqlist)
        print("Non-grid vars:",olist)

# Regrid each variable type separately
        rgflag = True
        xhyhreg = [xhyhregridder(dsin[vname]) for vname in xhyhlist]
        xhyqreg = [xhyqregridder(dsin[vname]) for vname in xhyqlist]
        xqyhreg = [xqyhregridder(dsin[vname]) for vname in xqyhlist]
        xqyqreg = [xqyqregridder(dsin[vname]) for vname in xqyqlist]
        ngvars = [dsin[vname] for vname in olist]

# Merge variables in single xarray object
        dout = xr.merge(xhyhreg+xhyqreg+xqyhreg+xqyqreg+ngvars)

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

        dout = copyattrs(dsin, dout, xhyhlist)
        dout = copyattrs(dsin, dout, xhyqlist)
        dout = copyattrs(dsin, dout, xqyhlist)
        dout = copyattrs(dsin, dout, xqyqlist)
        dout = copyattrs(dsin, dout, olist)

# Write output
        if not os.path.exists(postdir):
            os.makedirs(postdir)
        dout.to_netcdf(postdir+"/"+rlist[i]+"_regrid_0p25x0p25.nc")

# Delete xarray objects to avoid memory leak?
        print('memory=',proc.memory_info().rss)
        del dout
        print('memory=',proc.memory_info().rss)
if __name__ == "__main__":
    main()


