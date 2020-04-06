import argparse
import subprocess
import os

# Create argument parser
parser = argparse.ArgumentParser(description='Create and build base UFS case')
parser.add_argument("--project", default=None, help='Project to charge', required=True)
parser.add_argument("--tag", default=None, help='Model tag', required=True)
parser.add_argument("--dates", default=None, nargs="+", help='List of start dates', required=True)
parser.add_argument("--compset", default="UFS_S2S", help='Model compset')
parser.add_argument("--res", default="C384_t025", help='Model resolution')
parser.add_argument("--driver", default="nuopc", help='Model driver')
parser.add_argument("--options", default='--run-unsupported', help='Other options')

# Get case variables
args = parser.parse_args()
tag = args.tag
dates = args.dates
compset = args.compset
res = args.res
driver = args.driver
project = args.project
options = args.options

# Fixed values
home=os.environ.get("HOME")
wallclock = "00:30:00"
rlen="1"

# Create list of cases
caselist={init:"ufs.s2s."+res+"."+init+"."+tag for init in dates}

# Parse initial dates to create reference dates
reflist={init:init[0:4]+"-"+init[4:6]+"-"+init[6:8] for init in dates}
print(reflist)

for init in dates:

# Go to cime/scripts directory in UFSCOMP 
   os.chdir(home+"/UFSCOMP."+tag+"/cime/scripts")

# Clone the base build into  new cases
   options = '--keepexe'
   rc = subprocess.run(["./create_clone",
                        "--case", caselist[init],
                        "--clone", "build_base",
                        options])
   os.chdir(home+"/UFSCOMP."+tag+"/cime/scripts/"+caselist[init])
   rc = subprocess.run(["./case.setup"])

# Define xmlchanges
   xmlchanges = ["RUN_REFDATE="+reflist[init],
                 "RUN_STARTDATE="+reflist[init],
                 "JOB_WALLCLOCK_TIME="+wallclock,
                 "DOUT_S=FALSE",
                 "STOP_OPTION=nhours",
                 "STOP_N="+rlen]
   rc = [subprocess.run([os.getcwd()+"/xmlchange", xmlchange]) for xmlchange in xmlchanges] 

# Set path to case ICs
   with open(os.getcwd()+"/env_mach_specific.xml", 'r') as f:
     filedata = f.read()
   filedata = filedata.replace("20120101",init)

   with open(os.getcwd()+"/env_mach_specific.xml", 'w') as f:
     f.write(filedata)
  
# Set cice IC
   with open(os.getcwd()+"/user_nl_cice", "a") as f:
     f.write("ice_ic = \"$ENV{UGCSINPUTPATH}/cice5_model.res_"+init+"00.nc\"\n") 

# Set output options
   with open(os.getcwd()+"/user_nl_fv3gfs", "a") as f:
     f.write("nfhout = 6\n")
     f.write("nfhmax_hf = 0\n")
     f.write("nfhout_hf = 0\n")
     f.write("fhzero = 6.0\n")
     f.write("fdiag = 6.0\n")
     f.write("fhout = 6.0\n")

# Submit run
   #rc = subprocess.run([os.getcwd()+"/case.submit"])   
