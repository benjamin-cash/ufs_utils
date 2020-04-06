#!/bin/sh
#SBATCH -J sfcf_daily           # Job name
#SBATCH -o sfcf_daily.o%j       # Name of stdout output file
#SBATCH -e sfcf_daily.e%j       # Name of stderr error file
#SBATCH -p normal          # Queue (partition) name
#SBATCH -N 1               # Total # of nodes 
#SBATCH -n 1
#SBATCH -t 12:00:00        # Run time (hh:mm:ss)
#SBATCH --mail-user=bcash@gmu.edu
#SBATCH --mail-type=all    # Send email at begin and end of job
#SBATCH -A TG-ATM140004       # Allocation name (req'd if you have more than 1)

# Other commands must follow all #SBATCH directives...

source ./ufsenv.sh
export EXPVER="CFSA"
echo $EXPVER
python sfcf_daily.py
export EXPVER="ERA5"
python sfcf_daily.py
