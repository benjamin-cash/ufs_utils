#!/bin/sh
#SBATCH -J dynf_regr           # Job name
#SBATCH -o dynf_regr.o%j       # Name of stdout output file
#SBATCH -e dynf_regr.e%j       # Name of stderr error file
#SBATCH -p normal          # Queue (partition) name
#SBATCH -N 1               # Total # of nodes 
#SBATCH -n 1              # Total # of mpi tasks
#SBATCH -t 08:00:00        # Run time (hh:mm:ss)
#SBATCH --mail-user=bcash@gmu.edu
#SBATCH --mail-type=all    # Send email at begin and end of job
#SBATCH -A TG-ATM140004       # Allocation name (req'd if you have more than 1)

# Other commands must follow all #SBATCH directives...

export CASE="ufs.s2s.C384_t025.20120701.cmeps_v0.5.1"
export UFSOUTPUT_DIR=$SCRATCH/$CASE/run/
export UFSPOST_DIR=$SCRATCH/$CASE/postp/
export DYNF_TARGET_GRID="0p25x0p25_regular_grid.nc"
export MOM6_TARGET_GRID="0p25x0p25_regular_grid.nc"
export UFSOUTPUT_DYNF="dynf"
export PROJECT="TG-ATM140004"

# Launch MPI code... 
module load nco
ibrun -n 1 python ./dynf_regrid.py         # Use ibrun instead of mpirun or mpiexec
