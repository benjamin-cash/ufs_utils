#!/bin/sh
#SBATCH -J m6stat_regr           # Job name
#SBATCH -o m6stat_regr.o%j       # Name of stdout output file
#SBATCH -e m6stat_regr.e%j       # Name of stderr error file
#SBATCH -p normal          # Queue (partition) name
#SBATCH -N 1               # Total # of nodes 
#SBATCH -n 1              # Total # of mpi tasks
#SBATCH -t 03:00:00        # Run time (hh:mm:ss)
#SBATCH --mail-user=bcash@gmu.edu
#SBATCH --mail-type=all    # Send email at begin and end of job
#SBATCH -A TG-ATM140004       # Allocation name (req'd if you have more than 1)

# Other commands must follow all #SBATCH directives...

export CASE="ufs.s2s.C384_t025.20120701.cmeps_v0.5.1"
export UFSOUTPUT_DIR=$SCRATCH/$CASE/run/
export UFSPOST_DIR=$SCRATCH/$CASE/postp/
export MOM6_GRID_INFO=$CASE.mom6.static.nc
export MOM6_TARGET_GRID="0p25x0p25_regular_grid.nc"
export UFSOUTPUT_PROC="mom6.static"
export PROJECT="TG-ATM140004"
# Launch MPI code... 

ibrun -n 1 python ./mom6.static_regrid.py         # Use ibrun instead of mpirun or mpiexec

