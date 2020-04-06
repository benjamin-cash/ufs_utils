#!/bin/sh
#SBATCH -J sfcf_regr           # Job name
#SBATCH -o sfcf_regr.o%j       # Name of stdout output file
#SBATCH -e sfcf_regr.e%j       # Name of stderr error file
#SBATCH -p normal          # Queue (partition) name
#SBATCH -N 1               # Total # of nodes 
#SBATCH -n 1              # Total # of mpi tasks
#SBATCH -t 02:30:00        # Run time (hh:mm:ss)
#SBATCH --mail-user=bcash@gmu.edu
#SBATCH --mail-type=all    # Send email at begin and end of job
#SBATCH -A TG-ATM140004       # Allocation name (req'd if you have more than 1)

# Other commands must follow all #SBATCH directives...

export CASE="ufs.s2s.c384_t025"
export UFSOUTPUT_DIR=$SCRATCH/$CASE/run.sfc3z/
export UFSPOST_DIR=$SCRATCH/$CASE/run.sfc3z/postp/
export SFCF_TARGET_GRID="/work/02441/bcash/stampede2/regrid/0p25x0p25_regular_grid.nc"
export PROJECT="TG-ATM140004"
# Launch MPI code... 

ibrun -n 1 python ./sfcf_regrid.py         # Use ibrun instead of mpirun or mpiexec

