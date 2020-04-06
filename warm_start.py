import subprocess
import os

# Define case variables
tag="cmeps_v0.3"
compset="UFS_S2S"
res="C384_t025"
driver="nuopc"
options="--run-unsupported"
initlist = ["20120101","20120401","20120701","20121001"]
#initlist = ["20120101"]
rlen ="40"
home=os.environ.get("HOME")
project=os.environ.get("PROJECT")
wallclock = "12:00:00"


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
   os.chdir(home+"/UFSCOMP/cime/scripts/"+caselist[init])

# Define xmlchanges
   xmlchanges = ["MEDIATOR_READ_RESTART=TRUE",
                 "JOB_WALLCLOCK_TIME="+wallclock,
                 "STOP_OPTION=ndays",
                 "STOP_N="+str(rlen)] 
   
   rc = [subprocess.run([os.getcwd()+"/xmlchange", xmlchange]) for xmlchange in xmlchanges] 

# Submit
   subprocess.run([os.getcwd()+"/case.submit"])
