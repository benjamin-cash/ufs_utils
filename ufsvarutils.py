import sys
import xarray as xr
import xesmf as xe
import re
import psutil
import numpy as np
import ESMF
import matplotlib.pyplot as plt

ESMF.Manager(debug=True)

def copyattrs(dold, dnew, vlist):

# Copy over variable attributes
    for vname in vlist:
        dnew[vname].attrs = dold[vname].attrs
        try:
          dnew[vname].encoding['missing_value']=dold[vname].encoding['missing_value']
        except:
          print("No missing value")
        try:
          dnew[vname].encoding['_FillValue']=dold[vname].encoding['_FillValue']
        except:
          print("No _FillValue")
    return dnew

def parse_utgrid(dsin,vname):
    try:
       gtype = dsin[vname].encoding['coordinates']
    except:
       gtype = "Not a grid" 
    return gtype

def parse_mom6static(gridin):
    xhyh = {'lon':gridin['geolon'], 'lat':gridin['geolat']}
    xhyq = {'lon':gridin['geolon_v'], 'lat':gridin['geolat_v']}
    xqyh = {'lon':gridin['geolon_u'], 'lat':gridin['geolat_u']}
    xqyq = {'lon':gridin['geolon_c'], 'lat':gridin['geolat_c']}
    return xhyh, xhyq, xqyh, xqyq

def parse_mom6grid(dsin,vname):
    try:
       gtype = dsin[vname].attrs['cell_methods']
    except:
       gtype = "NA"
    print(vname,gtype)
    return gtype

def parse_mom6rgrid(dsin,vname):
    try:
       gtype = dsin[vname].coords
    except:
       gtype = "NA"
    print(vname,gtype)
    return gtype

def rotate_vector_mom6(uin, vin, gridin, sinrot, cosrot):
    if gridin == "tripole":
       urot = uin*cosrot+vin*sinrot
       vrot = vin*cosrot-uin*sinrot
    elif gridin == "latlon":
       urot = uin*cosrot-vin*sinrot
       vrot = uin*sinrot+vin*cosrot 
    else:
       print("Grid type not recognized.")
       print("Valid options are 'tripole' or 'latlon'")
       exit()
    return urot, vrot

def rotate_vector_oras5(uin, vin, gridin, sinrot, cosrot):
    if gridin == "tripole":
       urot = uin*cosrot+vin*sinrot
       vrot = vin*cosrot-uin*sinrot
    elif gridin == "latlon":
       urot = uin*cosrot-vin*sinrot
       vrot = uin*sinrot+vin*cosrot
    else:
       print("Grid type not recognized.")
       print("Valid options are 'tripole' or 'latlon'")
       exit()
    return urot, vrot

def rotate_vector_cice5(uin, vin, gridin, angle):
    if gridin == "tripole":
       urot = uin*np.cos(angle)-vin*np.sin(angle)
       vrot = uin*np.sin(angle)+vin*np.cos(angle)
    elif gridin == "latlon":
       print(np.cos(angle).shape)
       print(uin.shape)
       urot = uin*np.cos(angle)+vin*np.sin(angle)
       vrot = vin*np.cos(angle)-uin*np.sin(angle)
    else:
       print("Grid type not recognized.")
       print("Valid options are 'tripole' or 'latlon'")
       exit()
    return urot, vrot

def ice_category_brdcst(invar, h_ice, cvals):
    nj = h_ice.nj.size
    ni = h_ice.ni.size
    ncat = len(cvals) + 1
    outvar = xr.DataArray(np.zeros((ncat,nj,ni), dtype=np.double),coords={'ncat':range(0,ncat),'nj':h_ice.nj, "ni":h_ice.ni},
                        dims=['ncat','nj','ni'])
    outvar[0,:,:] = invar.where(h_ice<cvals[0],other=0.)
    outvar[1,:,:] = invar.where((h_ice>=cvals[0]) & (h_ice<cvals[1]), other=0)
    outvar[2,:,:] = invar.where((h_ice>=cvals[1]) & (h_ice<cvals[2]), other=0)
    outvar[3,:,:] = invar.where((h_ice>=cvals[2]) & (h_ice<cvals[3]), other=0)
    outvar[4,:,:] = invar.where((h_ice>=cvals[3]), other=0)
    return outvar

def create_regridder(dsin,ds_out,gname,regriddir):
    print(xe.__version__)
    regridder = xe.Regridder(dsin,ds_out,'bilinear',reuse_weights=True,filename=regriddir+gname+".nc",periodic=True, ignore_degenerate=True)
    return regridder

def esmf_regrid(source, sourcegrd, ds_out, poles, name):
    
# Convert data array into ESMF.Grid format
    print("Processing",name)
    grdshape = xr.DataArray.transpose(sourcegrd['lat']).shape
    #esmfgrid = ESMF.Grid(np.array(grdshape), staggerloc=ESMF.StaggerLoc.CENTER, coord_sys=ESMF.CoordSys.SPH_DEG,
    #    pole_kind=poles['ds_in'], num_peri_dims=1, periodic_dim=0, pole_dim=1)
    esmfgrid = ESMF.Grid(np.array(grdshape), staggerloc=ESMF.StaggerLoc.CENTER, coord_sys=ESMF.CoordSys.SPH_DEG,
	num_peri_dims=1, periodic_dim=0, pole_dim=1)
    esmf_lon = esmfgrid.get_coords(0)
    esmf_lat = esmfgrid.get_coords(1)
    esmf_lon[...] = xr.DataArray.transpose(sourcegrd['lon']).values
    esmf_lat[...] = xr.DataArray.transpose(sourcegrd['lat']).values
    sourcefield = ESMF.Field(esmfgrid, name=name)
    data=np.squeeze(xr.DataArray.transpose(source).values)
    sourcefield.data[...]=data[:,:]

# Regrid each variable type separately
    #destgrid = ESMF.Grid(np.array(xr.DataArray.transpose(ds_out['lat']).shape), staggerloc=ESMF.StaggerLoc.CENTER, coord_sys=ESMF.CoordSys.SPH_DEG,
    #    pole_kind=poles['ds_out'], num_peri_dims=1, periodic_dim=0, pole_dim=1)
    destgrid = ESMF.Grid(np.array(xr.DataArray.transpose(ds_out['lat']).shape), staggerloc=ESMF.StaggerLoc.CENTER, coord_sys=ESMF.CoordSys.SPH_DEG,
	num_peri_dims=1, periodic_dim=0, pole_dim=1)
    dest_lon = destgrid.get_coords(0)
    dest_lat = destgrid.get_coords(1)
    dest_lon[...] = xr.DataArray.transpose(ds_out['lon']).values
    dest_lat[...] = xr.DataArray.transpose(ds_out['lat']).values
    destfield = ESMF.Field(destgrid, name = 'name')
    regrid = ESMF.Regrid(sourcefield, destfield, regrid_method=ESMF.RegridMethod.BILINEAR,unmapped_action=ESMF.UnmappedAction.IGNORE)
    destfield = regrid(sourcefield, destfield)
    eslat = np.squeeze(destfield.grid.coords[0][0][:,0])
    eslon = np.squeeze(destfield.grid.coords[0][1][0,:])
    xrgrid = xr.DataArray(destfield.data,dims=['lat','lon'],coords = {'lat':eslat, 'lon':eslon},name=destfield.name)
    return xr.DataArray.transpose(xrgrid)

def xr_to_esmf(source, gridinfo, vname, pole):
    print(gridinfo['lat'].shape)
    exit()
    esmfgrid = ESMF.Grid(np.array(gridinfo['lat'].shape), staggerloc=ESMF.StaggerLoc.CENTER, coord_sys=ESMF.CoordSys.SPH_DEG,
	pole_kind=pole, num_peri_dims=1, periodic_dim=1, pole_dim=0)
    print(esmfgrid)
    esmf_lon = esmfgrid.get_coords(0)
    esmf_lat = esmfgrid.get_coords(1)
    esmf_lon[...] = gridinfo['lon']
    esmf_lat[...] = gridinfo['lat']
    esmffield = ESMF.Field(esmfgrid, name=vname)
    esmffield.data[...]=np.squeeze(source[:,:,0].values)
    return esmffield

def esmf_to_xr(source):
    print(source.grid.coords[0][0][:,0])
    print(source.grid.coords[0][1][0,:])
    print(source.grid.coords[0][0].shape)
    print(source.grid.coords[0][1].shape)
    eslat = np.squeeze(source.grid.coords[0][0][:,0])
    eslon = np.squeeze(source.grid.coords[0][1][0,:])
    xrgrid = xr.DataArray(source.data,dims=['lat','lon'],coords = {'lat':eslat, 'lon':eslon},name=source.name)
    return xrgrid

'''
def create_tregridder(dsin,ds_out):
    dsin['lon']=dsin['TLON']
    dsin['lat']=dsin['TLAT']
    tregridder = xe.Regridder(dsin,ds_out,'bilinear',reuse_weights=True,filename="TGRID.to.0p25x0p25_regular_grid.nc",periodic="True") 
    return tregridder

def create_uregridder(dsin,ds_out):
    dsin['lon']=dsin['TLON']
    dsin['lat']=dsin['TLAT']
    uregridder = xe.Regridder(dsin,ds_out,'bilinear',reuse_weights=True,filename="UGRID.to.0p25x0p25_regular_grid.nc",periodic="True")
    return uregridder


def tregrid(dsin,ds_out,vname,ginfo,tregridder):

# Rename lat and lon
    proc = psutil.Process()
    dsin['lon']=dsin['TLON']
    dsin['lat']=dsin['TLAT']

# Regrid over variable list
    print('Before tregrid', proc.memory_info().rss, vname)
    rgrd=tregridder(dsin[vname])
    print('After tregrid', proc.memory_info().rss)
    return rgrd

def uregrid(dsin,ds_out,vname,ginfo,uregridder):

# Rename lat and lon
    proc = psutil.Process()
    dsin['lon']=dsin['ULON']
    dsin['lat']=dsin['ULAT']
    #regridder = xe.Regridder(dsin,ds_out,'bilinear',reuse_weights=True,filename="UGRID.to.0p25x0p25_regular_grid.nc",periodic="True")
 #   print(regridder)
    
# Regrid over variable list
    print('Before uregrid', proc.memory_info().rss, vname)
    rgrd=uregridder(dsin[vname])
    print('After uregrid', proc.memory_info().rss)
    return rgrd
'''

