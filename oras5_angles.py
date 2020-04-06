# NEXT STEPS - Apply last two steps from angle code - figure out what values are being used for the last rows

import numpy as np
import xarray as xr

# Read in ocean mesh file
dsin = xr.open_dataset("/work/02441/bcash/stampede2/sosie/data/mesh_mask.nc")
print(dsin['glamt'].shape)

# Define some constants
rpi0 = np.pi
rad0 = rpi0/180.0

# Get T grid information
print("Reading T grid")
glamt = dsin['glamt'].transpose('x','y','t').squeeze()
gphit = dsin['gphit'].transpose('x','y','t').squeeze()

# Get U grid information
print("Reading U grid")
glamu = dsin['glamu'].transpose('x','y','t').squeeze()
gphiu = dsin['gphiu'].transpose('x','y','t').squeeze()

# Get V grid information
print("Reading V grid")
glamv = dsin['glamv'].transpose('x','y','t').squeeze()
gphiv = dsin['gphiv'].transpose('x','y','t').squeeze()

# Get F grid information
print("Reading F grid")
glamf = dsin['glamf'].transpose('x','y','t').squeeze()
gphif = dsin['gphif'].transpose('x','y','t').squeeze()

# Get grid dimensions
ny = glamt['y'].size
nx = glamt['x'].size
print(nx,ny,glamt.shape)

# Initialize arrays
gsint = xr.DataArray(np.zeros(glamt.shape),dims=['x','y'],name='gsint')
gcost = xr.DataArray(np.zeros(glamt.shape),dims=['x','y'],name='gcost')
gsinu = xr.DataArray(np.zeros(glamt.shape),dims=['x','y'],name='gsinu')
gcosu = xr.DataArray(np.zeros(glamt.shape),dims=['x','y'],name='gcosu')
gsinv = xr.DataArray(np.zeros(glamt.shape),dims=['x','y'],name='gsinv')
gcosv = xr.DataArray(np.zeros(glamt.shape),dims=['x','y'],name='gcosv')
gsinf = xr.DataArray(np.zeros(glamt.shape),dims=['x','y'],name='gsinf')
gcosf = xr.DataArray(np.zeros(glamt.shape),dims=['x','y'],name='gcosf')
print(gsint)

# Move elements that can be done all at once outside of the loop
# T-grid
zxnpt = 0.-2.*np.cos(rad0*glamt[1:,1:-1])*np.tan(rpi0/4.-rad0*gphit[1:,1:-1]/2.)
zynpt = 0.-2.*np.sin(rad0*glamt[1:,1:-1])*np.tan(rpi0/4.-rad0*gphit[1:,1:-1]/2.)
znnpt = zxnpt*zxnpt + zynpt*zynpt

# U-grid
zxnpu = 0.- 2.* np.cos(rad0*glamu[1:,1:-1])*np.tan(rpi0/4.-rad0*gphiu[1:,1:-1]/2.)
zynpu = 0.- 2.* np.sin(rad0*glamu[1:,1:-1])*np.tan(rpi0/4.-rad0*gphiu[1:,1:-1]/2.)
znnpu = zxnpu*zxnpu + zynpu*zynpu
print(zxnpu.shape,zynpu.shape,znnpu.shape)

# V grid
zxnpv = 0.-2.*np.cos(rad0*glamv[1:,1:-1])*np.tan(rpi0/4.-rad0*gphiv[1:,1:-1]/2.)
zynpv = 0.-2.*np.sin(rad0*glamv[1:,1:-1])*np.tan(rpi0/4.-rad0*gphiv[1:,1:-1]/2.)
znnpv = zxnpv*zxnpv + zynpv*zynpv

# F grid
zxnpf = 0.-2.*np.cos(rad0*glamf[1:,1:-1])*np.tan(rpi0/4.-rad0*gphif[1:,1:-1]/2.)
zynpf = 0.-2.*np.sin(rad0*glamf[1:,1:-1])*np.tan(rpi0/4.-rad0*gphif[1:,1:-1]/2.)
znnpf = zxnpf*zxnpf + zynpf*zynpf

zlam = glamv[1:,1:-1]   # j-direction: v-point segment direction (around t-point)
zphi = gphiv[1:,1:-1]
zlan = glamv[1:,0:-2]
zphh = gphiv[1:,0:-2]
zxvvt =  2.*np.cos(rad0*zlam)*np.tan(rpi0/4.-rad0*zphi/2.)   \
                 -2.*np.cos(rad0*zlan)*np.tan(rpi0/4.-rad0*zphh/2.)
zyvvt = 2.*np.sin(rad0*zlam)*np.tan(rpi0/4.-rad0*zphi/2.)   \
                 -2.*np.sin(rad0*zlan)*np.tan(rpi0/4.-rad0*zphh/2.)
znvvt = np.sqrt(znnpt*(zxvvt*zxvvt+zyvvt*zyvvt))
znvvt = np.maximum(znvvt,1.e-14)

zlam = glamf[1:,1:-1]   # j-direction: f-point segment direction (around u-point)
zphi = gphif[1:,1:-1]
zlan = glamf[1:,0:-2]
zphh = gphif[1:,0:-2]
zxffu =  2. * np.cos( rad0*zlam ) * np.tan( rpi0/4. - rad0*zphi/2. )   \
                 -  2. * np.cos( rad0*zlan ) * np.tan( rpi0/4. - rad0*zphh/2. )
zyffu =  2. * np.sin( rad0*zlam ) * np.tan( rpi0/4. - rad0*zphi/2. )   \
                 -  2. * np.sin( rad0*zlan ) * np.tan( rpi0/4. - rad0*zphh/2. )
znffu = np.sqrt( znnpu * ( zxffu*zxffu + zyffu*zyffu )  )
znffu = np.maximum( znffu, 1.e-14 )

zlam = glamf[1:,1:-1]   # i-direction: f-point segment direction (around v-point)
zphi = gphif[1:,1:-1]
zlan = glamf[1:,0:-2]
zphh = gphif[1:,0:-2]
zxffv =  2. * np.cos( rad0*zlam ) * np.tan( rpi0/4. - rad0*zphi/2. )   \
                 -  2. * np.cos( rad0*zlan ) * np.tan( rpi0/4. - rad0*zphh/2. )
zyffv =  2. * np.sin( rad0*zlam ) * np.tan( rpi0/4. - rad0*zphi/2. )   \
               -  2. * np.sin( rad0*zlan ) * np.tan( rpi0/4. - rad0*zphh/2. )
znffv = np.sqrt( znnpv * ( zxffv*zxffv + zyffv*zyffv )  )
znffv = np.maximum( znffv, 1.e-14 )

zlam = glamu[1:,2:]   # j-direction: u-point segment direction (around f-point)
zphi = gphiu[1:,2:]
zlan = glamu[1:,1:-1]
zphh = gphiu[1:,1:-1]
zxuuf =  2. * np.cos( rad0*zlam ) * np.tan( rpi0/4. - rad0*zphi/2. )   \
                 -  2. * np.cos( rad0*zlan ) * np.tan( rpi0/4. - rad0*zphh/2. )
zyuuf =  2. * np.sin( rad0*zlam ) * np.tan( rpi0/4. - rad0*zphi/2. )   \
                -  2. * np.sin( rad0*zlan ) * np.tan( rpi0/4. - rad0*zphh/2. )
znuuf = np.sqrt( znnpf * ( zxuuf*zxuuf + zyuuf*zyuuf )  )
znuuf = np.maximum( znuuf, 1.e-14 )

# cosinus and sinus using dot and cross products
ggsint = ( zxnpt*zyvvt - zynpt*zxvvt ) / znvvt
ggcost = ( zxnpt*zxvvt + zynpt*zyvvt ) / znvvt
print(ggsint.shape, ggcost.shape)
exit()
gsint.name='gsint'
gcost.name='gcost'

gsinu = ( zxnpu*zyffu - zynpu*zxffu ) / znffu
gcosu = ( zxnpu*zxffu + zynpu*zyffu ) / znffu
gsinu.name='gsinu'
gcosu.name='gcosu'
            #
gsinf = ( zxnpf*zyuuf - zynpf*zxuuf ) / znuuf
gcosf = ( zxnpf*zxuuf + zynpf*zyuuf ) / znuuf
gsinf.name='gsinf'
gcosf.name='gcosf'

            #
gsinv = ( zxnpv*zxffv + zynpv*zyffv ) / znffv
gcosv =-( zxnpv*zyffv - zynpv*zxffv ) / znffv
gsinv.name='gsinv'
gcosv.name='gcosv'
print(gsint)

# Note entirely sure what this check is
gsint = np.where(np.mod(np.absolute(glamv[1:,1:-1]-glamv[1:,0:-2]), 360.)< 1e-8,0,gsint)
gcost = np.where(np.mod(np.absolute(glamv[1:,1:-1]-glamv[1:,0:-2]), 360.)< 1e-8,1,gcost)

gsinu = np.where(np.mod(np.absolute(glamf[1:,1:-1]-glamf[1:,0:-2]), 360.)< 1e-8,gsinu)
gcosu = np.where(np.mod(np.absolute(glamf[1:,1:-1]-glamf[1:,0:-2]), 360.)< 1e-8,gcosu)

gsinv = np.where(np.absolute(gphif[1:,1:-1]-gphif[0:-1,1:-1])< 1e-8,0,gsinv)
gcosv = np.where(np.absolute(gphif[1:,1:-1]-gphif[0:-1,1:-1])< 1e-8,1,gcosv)

gsinf = np.where(np.mod(np.absolute(glamu[1:,1:-1]-glamu[1:,2:]), 360.)< 1e-8,0,gsinf)
gcosf = np.where(np.mod(np.absolute(glamu[1:,1:-1]-glamu[1:,2:]), 360.)< 1e-8,1,gcosf)

# Set lateral boundary conditions


# Write out
gsint.transpose('y','x').to_netcdf("/work/02441/bcash/stampede2/sosie/data/gsint.nc")
gcost.transpose('y','x').to_netcdf("/work/02441/bcash/stampede2/sosie/data/gcost.nc")
gsinu.transpose('y','x').to_netcdf("/work/02441/bcash/stampede2/sosie/data/gsinu.nc")
gcosu.transpose('y','x').to_netcdf("/work/02441/bcash/stampede2/sosie/data/gcosu.nc")
gsinv.transpose('y','x').to_netcdf("/work/02441/bcash/stampede2/sosie/data/gsinv.nc")
gcosv.transpose('y','x').to_netcdf("/work/02441/bcash/stampede2/sosie/data/gcosv.nc")
gsinf.transpose('y','x').to_netcdf("/work/02441/bcash/stampede2/sosie/data/gsinf.nc")
gcosf.transpose('y','x').to_netcdf("/work/02441/bcash/stampede2/sosie/data/gcosf.nc")

