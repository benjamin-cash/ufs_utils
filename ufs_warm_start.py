import argparse
import subprocess
import os

# Create argument parser
parser = argparse.ArgumentParser(description='Create and build base UFS case')
parser.add_argument("--project", default=None, help='Project to charge', required=True)
parser.add_argument("--tag", default=None, help='Model tag', required=True)
parser.add_argument("--dates", default=None, nargs="+", help='List of start dates', required=True)
parser.add_argument("--length", default=None, help='Run length (days)')
parser.add_argument("--wallclock", default=None, help='Run length (wallclock)')
parser.add_argument("--compset", default="UFS_S2S", help='Model compset')
parser.add_argument("--res", default="C384_t025", help='Model resolution')
parser.add_argument("--driver", default="nuopc", help='Model driver')
parser.add_argument("--options", default='--run-unsupported', help='Other options')

# Get case variables
args = parser.parse_args()
tag = args.tag
dates = args.dates
rlen = args.length
wallclock = args.wallclock
compset = args.compset
res = args.res
driver = args.driver
project = args.project
options = args.options

home=os.environ.get("HOME")


# Create list of cases
caselist={init:"ufs.s2s."+res+"."+init+"."+tag for init in dates}

# Parse initial dates to create reference dates
reflist={init:init[0:4]+"-"+init[4:6]+"-"+init[6:8] for init in dates}
print(reflist)

for init in dates:

# Go to cime/scripts directory in UFSCOMP 
   os.chdir(home+"/UFSCOMP."+tag+"/cime/scripts/"+caselist[init])

# Define xmlchanges
   xmlchanges = ["MEDIATOR_READ_RESTART=TRUE",
                 "JOB_WALLCLOCK_TIME="+wallclock,
                 "STOP_OPTION=ndays",
                 "STOP_N="+str(rlen)] 
   
   rc = [subprocess.run([os.getcwd()+"/xmlchange", xmlchange]) for xmlchange in xmlchanges] 

# Submit
   subprocess.run([os.getcwd()+"/case.submit"])
