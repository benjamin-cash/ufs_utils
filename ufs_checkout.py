# Simple script to automate the steps in the checkout process. User supplies location
# of the repo and the desired tag on the command line

import argparse
import subprocess
import os

# Create argument parser
parser = argparse.ArgumentParser(description='Checkout specified UFS repository and tag')
parser.add_argument("--repo", default="https://github.com/ESCOMP/UFSCOMP.git", help='This is the location of the github repo')
parser.add_argument("--tag", default=None, help='This is the model tag to be checked out', required=True)

# Get case variables
args = parser.parse_args()
repo = args.repo
tag = args.tag
home = os.environ.get("HOME")

# Does selected repo/tag exist?
rc = subprocess.run(["git", "ls-remote", repo, tag], stdout=subprocess.PIPE).stdout.decode('utf-8')
if rc:
   print("Repo and tag exist")
else:
   print("Repo or tag not found, exiting.")
   exit()

# Clone repo and tag
os.chdir(home)
rc = subprocess.run(["git", "clone", repo, "UFSCOMP."+tag])
os.chdir(home+"/UFSCOMP."+tag)
rc = subprocess.run(["git", "checkout", tag])
rc = subprocess.run(["./manage_externals/checkout_externals"])
