# This script generates a new case and builds an executable. It is designed to be 
# called after ufs_checkout has run successfully, and creates the necessary files 
# for ufs_cold_start.

import argparse
import subprocess
import os

# Create argument parser
parser = argparse.ArgumentParser(description='Create and build base UFS case')
parser.add_argument("--project", default=None, help='Project to charge', required=True)
parser.add_argument("--tag", default=None, help='Model tag', required=True)
parser.add_argument("--compset", default="UFS_S2S", help='Model compset')
parser.add_argument("--res", default="C384_t025", help='Model resolution')
parser.add_argument("--driver", default="nuopc", help='Model driver')
parser.add_argument("--options", default='--run-unsupported', help='Other options')

# Get case variables
args = parser.parse_args()
tag = args.tag
compset = args.compset
res = args.res
driver = args.driver
project = args.project
options = args.options
home=os.environ.get("HOME")

# Go to cime/scripts directory in UFSCOMP 
try:
   os.chdir(home+"/UFSCOMP."+tag+"/cime/scripts")
except:
   print("Could not cd to correct cime/scripts directory, was code checked out successfully?")
   exit()

# Create new case
rc = subprocess.run(["./create_newcase",
                        "--compset", compset,
                        "--res", res,
                        "--case", "build_base",
                        "--driver", driver,
			"--project", project,
                        options])

# Build executable
os.chdir(home+"/UFSCOMP."+tag+"/cime/scripts/build_base")
subprocess.run([os.getcwd()+"/case.setup"])
subprocess.run([os.getcwd()+"/case.build", "--clean"])
subprocess.run([os.getcwd()+"/case.build"])
