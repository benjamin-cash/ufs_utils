#!/bin/sh
#SBATCH -J dynf_daily           # Job name
#SBATCH -o dynf_daily.o%j       # Name of stdout output file
#SBATCH -e dynf_daily.e%j       # Name of stderr error file
#SBATCH -p normal          # Queue (partition) name
#SBATCH -N 1               # Total # of nodes 
#SBATCH -n 1
#SBATCH -t 8:00:00        # Run time (hh:mm:ss)
#SBATCH --mail-user=bcash@gmu.edu
#SBATCH --mail-type=all    # Send email at begin and end of job
#SBATCH -A TG-ATM140004       # Allocation name (req'd if you have more than 1)

# Other commands must follow all #SBATCH directives...

conda init bash
conda activate pangeo
source ./ufsenv.sh

python dynf_daily.py
