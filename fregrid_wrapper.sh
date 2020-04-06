#!/bin/tcsh -fx

#Post-processing using fregrid instead of c2l
#Rev 2.0.1 30 May 14: now have one extra point
#  in lat so that the poles and equator are exactly represented
#Rev 2.1a 30 Nov 15: Adding "prefix_only" option and removing 
#  restart combine options that don't make sense for this program
#Rev 2.1b 5 Jan 15: Fixed problem with "prefix_only" option always
#  being executed, even when empty; also used Zhi's new fregrid which
#  works on single-precision time data; and as per Zhi changed
#  'fregrid_parallel' to 'fregrid' when doing actual remapping, while
#  running each instance of fregrid simultaneously.

#module load netcdf/4.6.2 mvapich2/2.3.1

#hostname | grep -q batch
#set echo

limit stacksize unlimited

alias fregrid /home1/02441/bcash/fregrid

set found_res_switch = 0
set nointerp = 0
set nlon = 360
set nlat = 181
set perdegree = 1
set nlon_set = 0
set nlat_set = 0
set mosaic = atmos_mosaic.nc
set given_remap_file = 0
set boundstr = ""
set limited_domain = 0
set lonBegin = 0
set lonEnd = 360
set latBegin = -90
set latEnd = 90
set method = conserve_order1
set fileTag = ""
set prefix_only = ""

#Assuming cubed-sphere
set do_schmidt = 0 # false
set target_lat = 0
set target_lon = 180
set stretch_factor = 1
set nlon_native = -1
set make_mosaic = 0

while ($#argv > 0)
  #echo $argv[1]
  switch ($argv[1])
    case "-l":
	echo "Original low resolution"
	set nlon = 240
	set nlat = 121
	set perdegree = 1
	set found_res_switch = 1
	echo "Output coarser than 1 degree not permitted, writing out at 1 degree"
	shift; breaksw
    case "-h":
	echo "New higher resolution"
	set nlon = 720
	set nlat = 361
	set perdegree = 2
        set found_res_switch = 1
	shift;	breaksw
    case "-p":
	echo "Production run high resolution"
	set nlon = 1440
	set nlat = 721
	set perdegree = 4
        set found_res_switch = 1
	shift;	breaksw
    case "-low":
	echo "2 deg x 2 deg"
	set nlon = 180
	set nlat = 91
	set perdegree = 1
        set found_res_switch = 1
	echo "Output coarser than 1 degree not permitted, writing out at 1 degree"
	shift;	breaksw
    case "-high":
	echo "0.5 deg x 0.5 deg"
	set nlon = 720
	set nlat = 361
	set perdegree = 2
        set found_res_switch = 1
	shift;	breaksw
    case "-ultra":
	echo "0.25 deg x 0.25 deg"
	set nlon = 1440
	set nlat = 721
	set perdegree = 4
        set found_res_switch = 1
	shift;	breaksw
    case "-mega":
	echo "0.125 deg x 0.125 deg"
	set nlon = 2880
	set nlat = 1441
	set perdegree = 8
        set found_res_switch = 1
	shift;	breaksw
    case "-mjo":
	echo "2.5 deg x 2.5 deg"
	set nlon = 144
	set nlat = 72
	set perdegree = 1
        set found_res_switch = 1
	echo "Output coarser than 1 degree not permitted, writing out at 1 degree"
	shift; 	breaksw
    case "--c96":
	echo "Default C96"
	set nlon = 360
	set nlat = 181
	set remap_file = /archive/Lucas.Harris/model/input/grid/c96/remap_file_360x181.nc
	set mosaic = /archive/Lucas.Harris/model/input/grid/c96/atmos_mosaic.nc
	set given_remap_file = 1
        set found_res_switch = 1
	shift; 	breaksw
    case "--C192":
	echo "NGGPS C192"
	set nlon = 768
	set nlat = 384
	set remap_file = /archive/Shannon.McElhinney/regrid/remap/remap_file_C192_768x384.nc
	set mosaic = /archive/Shannon.McElhinney/regrid/grid/C192_mosaic.nc
	set given_remap_file = 1
        set found_res_switch = 1
	set method = conserve_order1
	shift; 	breaksw
    case "--c384":
	echo "c384"
	set nlon = 1440
	set nlat = 721
	set perdegree = 4
        set  remap_file   = ~/ufscomp_utils/remaps/C384_x1440_y721.nc
        set  mosaic = ~/ufscomp_utils/mosaics/C384/C384_mosaic.nc
	set given_remap_file = 1
        set found_res_switch = 1
	set method = conserve_order1
	shift; 	breaksw
    case "--c384n3":
	echo "c384n3 GHS"
	set nlon = 1440
	set nlat =  721
	set perdegree = 4
	set remap_file = /archive/Lucas.Harris/model/input/grid/C384-nest-GHS-lnoref/remap_file_C384n3-GHS_1440x721.nc
	set mosaic = /archive/Lucas.Harris/model/input/grid/C384-nest-GHS-lnoref/atmos_mosaic_coarse.nc
	set given_remap_file = 1
        set found_res_switch = 1
	set method = conserve_order1
	shift; 	breaksw
    case "--C768":
	echo "NGGPS C768"
	set nlon = 3072
	set nlat = 1536
	set remap_file = /archive/Shannon.McElhinney/regrid/remap/remap_file_C768_3072x1536.nc
	set mosaic = /archive/Shannon.McElhinney/regrid/C768/C768_mosaic.nc
	set given_remap_file = 1
        set found_res_switch = 1
	set method = conserve_order1
	shift; 	breaksw
    case "--C768r14n3":
	echo "NGGPS C768r14n3 STL"
	set nlon = 3072
	set nlat = 1536
	set remap_file = /archive/Lucas.Harris/NGGPS/grid/remap_file_C768r14n3_3072x1536.nc 
	set mosaic = /archive/Lucas.Harris/NGGPS/grid/c768r14n3_coarse_mosaic.nc 
	set given_remap_file = 1
        set found_res_switch = 1
	set method = conserve_order1
	shift; 	breaksw
    case "--C768r14n3nest":
	echo "NGGPS C768r14n3 STL nest"
	set nlon = 2560
	set nlat = 1440
	set remap_file = /archive/Lucas.Harris/NGGPS/grid/remap_file_C768r14n3_nested_2560x1440.nc
	set mosaic = /archive/Lucas.Harris/NGGPS/grid/c768r14n3_nested_mosaic.nc 
	set given_remap_file = 1
        set found_res_switch = 1
	set method = conserve_order1
	set limited_domain = 1
	set lonBegin = 225
	set lonEnd = 305
	set latBegin = 10
	set latEnd = 55
	set nlon_set = 1
	set nlat_set = 1
	set fileTag = "_nested_ltd"
	shift; 	breaksw
    case "--C768r14n3merra":
	echo "NGGPS C768r14n3 STL to 1x1 deg"
	set nlon = 360
	set nlat = 180
	set remap_file = /archive/Lucas.Harris/NGGPS/grid/remap_file_C768r14n3_360x180.nc 
	set mosaic = /archive/Lucas.Harris/NGGPS/grid/c768r14n3_coarse_mosaic.nc 
	set given_remap_file = 1
        set found_res_switch = 1
	set method = conserve_order1
	set fileTag = "_merra"
	shift; 	breaksw
    case "--C768r14n3double":
	echo "NGGPS C768r14n3 STL to double resolution"
	set nlon = 6144
	set nlat = 3072
	set remap_file = /archive/Lucas.Harris/NGGPS/grid/remap_file_C768r14n3_6144x3072.nc 
	set mosaic = /archive/Lucas.Harris/NGGPS/grid/c768r14n3_coarse_mosaic.nc 
	set given_remap_file = 1
        set found_res_switch = 1
	set method = conserve_order1
	set fileTag = "_2x"
	shift; 	breaksw
    case "--C768merra":
	echo "NGGPS C768 to 1x1 deg"
	set nlon = 360
	set nlat = 180
	set remap_file = /archive/Shannon.McElhinney/regrid/remap/remap_file_C768_360x180.nc
	set mosaic = /archive/Shannon.McElhinney/regrid/C768/C768_mosaic.nc
	set given_remap_file = 1
        set found_res_switch = 1
	set method = conserve_order1
	set fileTag = "_merra"
	shift; 	breaksw
    case "--C1024r3mia":
	echo "NGGPS C1024 stretch-by-three over Miami, FL"
	set nlon = 12288
	set nlat = 6144
	set remap_file =  /archive/Shannon.McElhinney/regrid/remap/C1024var3g1_remap_file.nc
	set mosaic = /archive/Shannon.McElhinney/GFS_output/Var3g1/C1024/grid/C1024_mosaic.nc
	set do_schmidt = 1
	set target_lat = 26
	set target_lon = 280
	set stretch_factor = 3
	set given_remap_file = 1
        set found_res_switch = 1
	set method = conserve_order1
	shift; 	breaksw
    case "-n":
	echo "No interpolation to lat-lon grid"
	set nointerp=1
	shift; 	breaksw
    case "-g":
	echo "Only processing atmos_month files"
	set month_only = 1
	shift; 	breaksw
    case "-m":
	echo "Using mosaic $argv[2]"
	set mosaic=$argv[2]
	shift; shift; breaksw
    case "--mosaic":
	echo "Using mosaic $argv[2]"
	set mosaic=$argv[2]
	shift; 	shift; breaksw
    case "-r":
	echo "Using remap file $argv[2]"
	set remap_file = $argv[2]
	set given_remap_file = 1
	shift; shift; breaksw
    case "--remap_file":
	echo "Using remap file $argv[2]"
	set remap_file = $argv[2]
	set given_remap_file = 1
	shift; shift; breaksw
    case "--nlon":
	set nlon = $argv[2]
	set nlon_set = 1
	shift;	shift;	breaksw
    case "--nlat":
	set nlat = $argv[2]
	set nlat_set = 1
	shift;	shift;	breaksw
    case "--target_lon":
	set target_lon = $argv[2]
	set do_schmidt = 1
	shift; 	shift;	breaksw
    case "--target_lat":
	set target_lat = $argv[2]
	set do_schmidt = 1
	shift;	shift;	breaksw
    case "--stretch_factor":
	set stretch_factor = $argv[2]
	set do_schmidt = 1
	shift; breaksw
    case "--stretch_fac":
	set stretch_factor = $argv[2]
	set do_schmidt = 1
	shift; 	shift;	breaksw
    case "--lonBegin":
	set lonBegin = $argv[2]
	set limited_domain = 1
	shift; shift; breaksw
    case "--latBegin":
	set latBegin = $argv[2]
	set limited_domain = 1
	shift; shift; breaksw
    case "--lonEnd":
	set lonEnd = $argv[2]
	set limited_domain = 1
	shift; shift; breaksw
    case "--latEnd":
	set latEnd = $argv[2]
	set limited_domain = 1
	shift; shift; breaksw
    case "--fileTag":
	set fileTag = $argv[2]
	shift; shift; breaksw
    case "--prefix-only":
	set prefix_only = $argv[2]
	echo "Only processing $prefix_only"
	shift; shift; breaksw
    default:
	break #break while
  endsw
end
if ( $found_res_switch == 0 ) then
    echo "DEFAULT: 1 deg x 1 deg"
endif

 set root=''
 if ( $#argv > 0 ) then
    if ( -d $1 ) then
	cd $1
    else
	set root = $1
    endif
 endif

 set files = (`ls -1  *.nc.???? *.nc.?????? |& grep -v 'No match' | sed 's/\.nc\.[0-9]*/.nc/' | uniq | tr '\n' ' '`)
 foreach file ( $files )
    if ($%prefix_only > 0) then
        set base = $file:r:r:r
        if (! ( "$base" == "$prefix_only" ) ) then
            continue
        endif
    endif    
    rm -f $file
    echo "CREATING $1/${file}"
    #64 bit means fewer headaches
    mppnccombine -64 -r $file ${file}.????
 end
 wait

 if ($nointerp == 1) then
    exit
 endif

 #Want to process all files except grid_spec,
 #  mosaic, and compressed land restart files
 foreach file ( ${root}*.tile1.nc  )
    set base = $file:r:r
    if ($base == "horizontal_grid" || $base == "atmos_mosaic") then
	continue
    endif
    if ($%prefix_only > 0) then
	if ( "$base" != "$prefix_only" ) then
	    continue
	endif
    endif

    #Get fields
    echo $file
    set fields=`~/ufscomp_utils/list_ncvars_fmt.csh -st -234 $file`
    echo $fields
    if ( $? > 0 ) then
	echo "list_ncvars is incorrect. Check your environment (or launch an xterm)"
	exit 1
    endif
    if ( x$fields == "x" || x$fields == "x," ) then
	echo "File $file contains no fields to process."
	continue
    endif

    #Create mosaic, if it doesn't exist
    #Try to get nlon_native from input files if it is not specified.
    if ( ! -e $mosaic  || $make_mosaic > 0) then
	set make_mosaic = 1 # for non-existent mosaic
	if ( $nlon_native <= 0 ) then
	    set nlon_native = `ncdump -c ${base}.tile1.nc | grep grid_xt' = [0-9]* ;' | sed 's/^.*= \([0-9]*\).*$/\1/'`
	endif
	@ nlon_native_sg = $nlon_native * 2 # make_hgrid requires twice the input resolution
	if ( $do_schmidt > 0 ) then
	    make_hgrid --grid_type gnomonic_ed --nlon $nlon_native_sg \
		--do_schmidt --stretch_factor $stretch_factor \
		--target_lat $target_lat --target_lon $target_lon
	    set method = conserve_order1
	else
	    make_hgrid --grid_type gnomonic_ed --nlon $nlon_native_sg
	endif
	make_solo_mosaic --num_tiles 6 --dir ./ --mosaic `basename ${mosaic:r}` \
	    --tile_file `ls -1 horizontal_grid.tile[1-6].nc | tr '\n' ','`
	if ( "`dirname $mosaic`" != "." ) then
	    mv `basename $mosaic` horizontal_grid.tile[1-6].nc `dirname $mosaic`
	endif
    endif

    if ( $limited_domain > 0 ) then
	if ( $nlon_set == 0 ) then
	    @ nlon = $perdegree * ( $lonEnd - $lonBegin + 1)
	endif
	if ( $nlat_set == 0 ) then
	    @ nlat = $perdegree * ( $latEnd - $latBegin + 1)
	endif
	set boundstr="--lonBegin $lonBegin --latBegin $latBegin --lonEnd $lonEnd --latEnd $latEnd"
    endif

    #Create remap file, if it does not exist, or if a new mosaic was just made.
    if ( $given_remap_file == 0 ) then
	set remap_file = remap_file_${nlon}x${nlat}.nc
    endif
    if ( ! -e $remap_file || $make_mosaic > 0 ) then
	if ( $do_schmidt > 0 ) then
	    mpirun -np 16 fregrid_parallel --input_mosaic $mosaic --nlon $nlon --nlat $nlat $boundstr --remap_file $remap_file
	else
	    mpirun -np 16 fregrid_parallel --input_mosaic $mosaic --nlon $nlon --nlat $nlat $boundstr --remap_file $remap_file --interp_method $method
	endif
    endif

    set make_mosaic = 0

#According to Zhi and Linjiong (see Email on 30dec15) fregrid_parallel yields no performance gain 
#  when doing the remapping (as opposed to generating the remap file) -- LMH 5jan16
    echo $nlon x $nlat
    if ( $do_schmidt > 0 ) then
		(time fregrid --input_mosaic $mosaic --nlon $nlon --nlat $nlat $boundstr --remap_file $remap_file \
	    	--input_file ${base} --output_file ${base}${fileTag}.nc --input_dir ./ --scalar_field $fields || exit ) &
    else
		(time fregrid --input_mosaic $mosaic --nlon $nlon --nlat $nlat $boundstr --remap_file $remap_file \
	    	--input_file ${base} --output_file ${base}${fileTag}.nc --input_dir ./ --scalar_field $fields --interp_method $method || exit ) &
    endif

 end
wait

