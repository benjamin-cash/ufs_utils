#!/bin/sh
#SBATCH -J cice_regr           # Job name
#SBATCH -o cice_regr.o%j       # Name of stdout output file
#SBATCH -e cice_regr.e%j       # Name of stderr error file
#SBATCH -p normal          # Queue (partition) name
#SBATCH -N 1               # Total # of nodes 
#SBATCH -n 1              # Total # of mpi tasks
#SBATCH -t 02:30:00        # Run time (hh:mm:ss)
#SBATCH --mail-user=bcash@gmu.edu
#SBATCH --mail-type=all    # Send email at begin and end of job
#SBATCH -A TG-ATM190009       # Allocation name (req'd if you have more than 1)

# Other commands must follow all #SBATCH directives...

export CASE="ufs.s2s.C384_t025.20120701.cmeps_v0.5.1"
export UFSOUTPUT_DIR=$SCRATCH/$CASE/postp/
export UFSPOST_DIR=$SCRATCH/$CASE/postp/
export CICE_TARGET_GRID="cice5_target.nc"
export UFSOUTPUT_CICE="cice"
export PROJECT="TG-ATM190009"
# Launch MPI code... 

ibrun -n 1 python ./cice_ll_to_tri.py         # Use ibrun instead of mpirun or mpiexec

