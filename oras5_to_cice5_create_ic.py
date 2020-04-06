import os
import numpy as np
import xarray as xr

from ufsfileutils import get_filelist, open_filelist, get_fileroot
from ufsvarutils import ice_category_brdcst

def main():

# Define some constants
# Number of input ice layers
    nilyr1 = 3

# Number of CICE5 ice layers
    nilyr2 = 7

# Number of snow layers in each ice category
    nslyr = 1

# Number of ice categories in CICE5
    ncat = 5

# Missing value
    missing = 9.96920996838687e+36

# Category boundaries
    c1 = 0.6445
    c2 = 1.3914
    c3 = 2.4702
    c4 = 4.5673
    cvals = [c1, c2, c3, c4]

# Salinity profile constants
    saltmax = 3.2 # Maximum salinity at ice base
    nsal = 0.407 # Profile constant
    msal = 0.573 # Profile constant

# Density values
    rhoi = 917.0 # Density of ice
    rhos = 330.0 # Density of snow
    cp_ice = 2106.0 # Specific heat of fresh ice
    cp_ocn = 4218.0 # Specific heat of sea water
    Lfresh = 3.34e5 # Latent heat of melting fresh ice

# Define intervals for interpolation to CICE5
    rstart = 0.5*(1/nilyr2)
    rend = 1-rstart
    tlevs = np.linspace(rstart,rend,nilyr2)
    nilyr = tlevs

# Define data directory
    print("Get environment variables.")
    datadir = os.environ.get('UFSDATA_DIR')
    postdir = os.environ.get('UFSPOST_DIR')
    ora_file = os.environ.get('ORAS5_FILE')
    print("End get environment variables.")

# Get list of files to process
    print("Begin open files.")
    flist = get_filelist(datadir,"*"+ora_file+".nc")
    rlist = get_fileroot(flist)
    dsets = open_filelist(flist,__file__)
    print("End open files.")
    print(flist)
    print(dsets)

# Iterate over open files
    for i, dsin in enumerate(dsets):
        print(flist[i])

# Rename input variables for consistency
        part_size = 1.-dsin.frld.squeeze()
        h_ice = dsin.hicif.squeeze()
        h_sno = dsin.hsnif.squeeze()
        t_surf = dsin.sist.squeeze()
        t1 = dsin.tbif1.squeeze()
        t2 = dsin.tbif2.squeeze()
        t3 = dsin.tbif3.squeeze()
#        
        part_size.name = "part_size"
        h_ice.name = "h_ice"
        h_sno.name = "h_sno"
        t_surf.name = "t_surf"
        t1.name = "t1"
        t2.name = "t2"
        t3.name = "t3"

# Get dimensions if input data
        ndims1 = part_size.shape
        nj = part_size.nj.size
        ni = part_size.ni.size

# Initalize dataarrays
        dummy = xr.DataArray(np.zeros((nj,ni), dtype=np.double),coords={'nj':part_size.nj, "ni":part_size.ni},
                        dims=['nj','ni'],name="dummy var")
        iceumask = xr.DataArray(np.full((nj,ni), 1, dtype=np.double),coords={'nj':part_size.nj, "ni":part_size.ni},
                        dims=['nj','ni'],name="iceumask")
        aicen = xr.DataArray(np.zeros((ncat,nj,ni), dtype=np.double),coords={'ncat':range(0,ncat),'nj':part_size.nj, "ni":part_size.ni},
			dims=['ncat','nj','ni'],name="aicen")
        vicen = xr.DataArray(np.zeros((ncat,nj,ni), dtype=np.double),coords={'ncat':range(0,ncat),'nj':part_size.nj, "ni":part_size.ni},
                        dims=['ncat','nj','ni'],name="vicen")
        vsnon = xr.DataArray(np.zeros((ncat,nj,ni), dtype=np.double),coords={'ncat':range(0,ncat),'nj':part_size.nj, "ni":part_size.ni},
                        dims=['ncat','nj','ni'],name="vsnon")
        Tsfcn = xr.DataArray(np.zeros((ncat,nj,ni), dtype=np.double),coords={'ncat':range(0,ncat),'nj':part_size.nj, "ni":part_size.ni},
                        dims=['ncat','nj','ni'],name="Tsfcn")
        tice = xr.DataArray(np.zeros((nilyr1,ncat,nj,ni), dtype=np.double),
                        coords={'nilyr':np.linspace(0,1,3),'ncat':range(0,ncat),'nj':part_size.nj, "ni":part_size.ni},
                        dims=['nilyr','ncat','nj','ni'],name="tice")
        Tin = xr.DataArray(np.zeros((nilyr2,ncat,nj,ni), dtype=np.double),
                        coords={'nilyr':tlevs,'ncat':range(0,ncat),'nj':part_size.nj, "ni":part_size.ni},
                        dims=['nilyr','ncat','nj','ni'],name="Tin")
        sice = xr.DataArray(np.zeros((nilyr2,ncat,nj,ni), dtype=np.double),
                        coords={'nilyr':tlevs,'ncat':range(0,ncat),'nj':part_size.nj, "ni":part_size.ni},
                        dims=['nilyr','ncat','nj','ni'],name="sice")
        qice = xr.DataArray(np.zeros((nilyr2,ncat,nj,ni), dtype=np.double),
                        coords={'nilyr':tlevs,'ncat':range(0,ncat),'nj':part_size.nj, "ni":part_size.ni},
                        dims=['nilyr','ncat','nj','ni'],name="qice")
        qsno = xr.DataArray(np.zeros((nslyr,ncat,nj,ni), dtype=np.double),
                        coords={'nslyr':range(nslyr),'ncat':range(0,ncat),'nj':part_size.nj, "ni":part_size.ni},
                        dims=['nslyr','ncat','nj','ni'],name="qsno")
        print(vicen.shape)
        print(h_ice.shape)

# Set ice fraction to zero where values are missing, based on surface temperature
        ice_frac = part_size.where(h_ice>0.,other=0)
        ice_frac.name = "ice_frac"

# Calculate ice fraction per category
        aicen = ice_category_brdcst(ice_frac, h_ice, cvals)
        aicen.name = 'aicen'

# Restore missing metadata
        aicen['nj'] = part_size.nj
        aicen['ni'] = part_size.ni
        aicen['ncat'] = range(0,ncat)

# Calculate ice mask
        iceumask = iceumask.where(aicen.sum(dim='ncat')>1e-11,other=0)

# Calculate ice volume per category
        for k in range(ncat):
          vicen[k,:,:] = h_ice.where(h_ice>0,other=0)*aicen[k,:,:]
        vicen.name = "vicen"

# Calculate snow volume per category
        for k in range(ncat):
          vsnon[k,:,:] = h_sno.where(h_sno>0,other=0)*aicen[k,:,:]
        vsnon.name = "vsnon"

# Calculate Surface temperature per category
# Missing value for t_surf is 0, convert to Kelvin to avoid excessive negative values later
        t_surf = t_surf.where(t_surf!=0,other=273.15)
        Tsfcn = ice_category_brdcst(t_surf-273.15, h_ice, cvals)
        Tsfcn = Tsfcn.where(Tsfcn<0, other=0)
        Tsfcn.name = "Tsfcn"

# Calculate ice layer temperature per category and combine
        tice[0,:,:,:] = ice_category_brdcst(t1.where(t1!=0, other=273.15)-273.15, h_ice, cvals)
        tice[1,:,:,:] = ice_category_brdcst(t2.where(t2!=0, other=273.15)-273.15, h_ice, cvals)
        tice[2,:,:,:] = ice_category_brdcst(t3.where(t3!=0, other=273.15)-273.15, h_ice, cvals)

# Linearly interpolate from ORAS5 layers to CICE5
        Tin = tice.interp(nilyr=tlevs)
        Tin.name="Tin"
        Tin = Tin.where(Tin<0, other=0)
        print(Tin)

# Create salinity profile
        zn = np.asarray([(k+1-0.5)/nilyr2 for k in range(nilyr2)])
        print((np.pi*zn**(nsal/(msal+zn))))
        salinz = 0.5*saltmax*(1-np.cos(np.pi*zn**(nsal/(msal+zn))))
        print(salinz)
        for k in range(nilyr2):
          sice[k,:,:,:] = salinz[k]
         
# Determine freezing point depression
        Tmltz = salinz/(-18.48+(0.01848*salinz))

# Calculate ice layer enthalpy
# Don't allow ice temperature to exceed melting temperature
        for k in range(nilyr2):
          Tin[k,:,:,:] = Tin[k,:,:,:].where(Tin[k,:,:,:]<Tmltz[k],other=Tmltz[k])
          qice[k,:,:,:] = rhoi*cp_ice*Tin[k,:,:,:] - rhoi*Lfresh
          qice[k,:,:,:] = qice[k,:,:,:].where(vicen>0, other=0)

# Calculate snow layer enthalpy
        qsno[0,:,:,:] = -rhos*(Lfresh - cp_ice*Tsfcn)
        qsno[0,:,:,:] = qsno[0,:,:,:].where(vsnon>0, other=-rhos*Lfresh)
        Trecon = (Lfresh+qsno/rhos)/cp_ice
        Trecon = Trecon.where(vsnon>0,0)
        Trecon.name = 'Trecon'
        Trecon.to_netcdf("test.nc")

# Write output in expected format
        qsno.to_netcdf("qsno_test.nc")

# Create list of variables initialized to zero
        dlist = ['uvel','vvel','scale_factor','coszen','swvdr','swvdf','swidr','swidf','strocnxT','strocnyT','stressp_1',
		'stressp_2','stressp_3','stressp_4','stressm_1','stressm_2','stressm_3','stressm_4','stress12_1',
		'stress12_2','stress12_3','stress12_4','frz_onset']
        dout = xr.merge([aicen, vicen, vsnon, Tsfcn, iceumask, Tin])
        dout['qsno001'] = qsno[0,:,:,:].squeeze()
        print(np.linspace(0,4,1))
        dout['ncat'] = np.linspace(0,4,5)
        dout['nilyr'] = tlevs
        for vname in dlist:
          dout[vname]=dummy
        for k in range(nilyr2):
          dout['qice00'+str(k+1)] = qice[k,:,:,:]
          dout['sice00'+str(k+1)] = sice[k,:,:,:]
        dout.fillna(missing)
        for vname in dout.data_vars:
           dout[vname].encoding['_FillValue']=missing
        dout.to_netcdf("cice_20120101_test.qsno.nc",format='NETCDF3_CLASSIC') 
if __name__ == "__main__":
    main()

	
	

