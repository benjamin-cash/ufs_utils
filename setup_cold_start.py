import subprocess
import os

# Define case variables
tag="cmeps_v0.5.1"
compset="UFS_S2S"
res="C384_t025"
driver="nuopc"
options="--run-unsupported"
#initlist = ["20120101","20120401","20120701","20121001"]
initlist = ["20120101"]
home=os.environ.get("HOME")
project=os.environ.get("PROJECT")
wallclock = "00:30:00"
rlen="1"

# Create list of cases
caselist={init:"ufs.s2s."+res+"."+init+"."+tag for init in initlist}

# Parse initial dates to create reference dates
reflist={init:init[0:4]+"-"+init[4:6]+"-"+init[6:8] for init in initlist}
print(reflist)

# Check that project is set
if not project:
   print("PROJECT variable not set, exiting.")
   exit()

for init in initlist:

# Go to cime/scripts directory in UFSCOMP 
   os.chdir(home+"/UFSCOMP."+tag+"/cime/scripts")

# Create new cases
   rc = subprocess.run(["./create_newcase",
                        "--compset", compset,
                        "--res", res,
                        "--case", caselist[init],
                        "--driver", driver,
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

# Build and submit
   subprocess.run([os.getcwd()+"/case.build", "--clean"])
   subprocess.run([os.getcwd()+"/case.build"])
   #subprocess.run([os.getcwd()+"/case.submit"])
