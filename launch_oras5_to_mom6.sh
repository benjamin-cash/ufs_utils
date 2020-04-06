#!/bin/sh
#SBATCH -J cice_regr           # Job name
#SBATCH -o cice_regr.o%j       # Name of stdout output file
#SBATCH -e cice_regr.e%j       # Name of stderr error file
#SBATCH -p normal          # Queue (partition) name
#SBATCH -N 1               # Total # of nodes 
#SBATCH -n 1              # Total # of mpi tasks
#SBATCH -t 06:00:00        # Run time (hh:mm:ss)
#SBATCH --mail-user=bcash@gmu.edu
#SBATCH --mail-type=all    # Send email at begin and end of job
#SBATCH -A TG-ATM190009       # Allocation name (req'd if you have more than 1)

# Other commands must follow all #SBATCH directives...

export UFSDATA_DIR=$WORK/ufs_input/
export UFSPOST_DIR=$WORK/ufs_input/
export REGRID_DIR=$WORK/regrid/
export ORAS5_GRID="oras5_grid_spec"
export MOM6_GRID="mom6_grid_spec"
export PROJECT="TG-ATM190009"
# Launch MPI code... 

ibrun -n 1 python ./oras5_to_mom6.py         # Use ibrun instead of mpirun or mpiexec

