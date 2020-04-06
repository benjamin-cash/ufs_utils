import subprocess
import sys
import getopt

def get_changes(filename):
    try:
        f = open(filename,"r")
        flines = f.readlines()
    except:
        print(filename,"not found, using defaults")
        flines = ""
    return flines

def apply_change_xml(change):
    action = change.split(" ")[0]
    if action=='xmlchange':
        dowhat = ''.join(change.split(" ")[1:]).rstrip()
        print(action,dowhat)
        subprocess.run([action, dowhat])
        result = "xmlchange"
    else:
        result = change+" is not an action, no change made"
    return result

def apply_change_nl(change):
    action = change.split(" ")[0]
    if "user_nl" in action:
        dowhat = ''.join(change.split(" ")[1:])
        nl_file = open(action,"a")
        nl_file.write(dowhat)
        print(action,dowhat)
        result = "namelist change"
    else:
        result = change+" is not an action, no change made"
    return result

def main(argv):
    xmlfile =''
    nlfile=''
    try:
       opts, args = getopt.getopt(argv,"hx:n:",["xmlchangesfile=","nlchangesfile="])
    except getopt.GetoptError:
       print("change.settings.py -x <xmlchangesfile> -n <nlchangesfile>")
       sys.exit(2)
    for opt, arg in opts:
       if opt == '-h':
         print("change.settings.py -x <xmlchangesfile> -n <nlchangesfile>")
         sys.exit()
       elif opt in ("-x", "--xmlchangesfile"):
         xmlfile = arg
       elif opt in ("-n", "--nlchangesfile"):
         nlfile = arg
    print("XML changes file is ", xmlfile)
    print("NL changes file is ", nlfile)

    # Read in user specified changes files
    changes_xml = get_changes(xmlfile)
    changes_nl = get_changes(nlfile)

    # Apply user specified changes to relevant model xml and nl files
    rc_xml = [apply_change_xml(xmlchange) for xmlchange in changes_xml]
    rc_nl = [apply_change_nl(nlchange) for nlchange in changes_nl]
    print(rc_xml)

if __name__=="__main__":
    main(sys.argv[1:])
