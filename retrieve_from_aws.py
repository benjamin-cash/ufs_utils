import os
import boto3
from botocore import UNSIGNED
from botocore.client import Config

def retrieve_files(bucket, client, name, prefix, path):
    print(prefix)
    for obj in bucket.objects.filter(Prefix=prefix):
#        if obj.key.endswith('.f???'):
            fname = obj.key.split('/')[-1]
            print(fname)
            if not os.path.isfile(f"{path}/{fname}"):
                if not os.path.exists(path):
                    os.makedirs(path)
                try:
                    with open(f"{path}/{fname}", 'wb') as f:
                        client.download_fileobj(name, obj.key, f)
                except IsADirectoryError:
                    print(f"{obj.key} is a directory, skipping")

pdir = "prototype-p5"
ptype = "Prototype5"
bucket_name="noaa-ufs-prototypes-pds"
#bucket_name="noaa-ufs-gefsv13replay-pds"
my_resource = boto3.resource('s3', config=Config(signature_version=UNSIGNED))
my_client = boto3.client('s3', config=Config(signature_version=UNSIGNED))
my_bucket = my_resource.Bucket(bucket_name)
yrlist = ["2018", "2012", "2013", "2014", "2015", "2016", "2017"]
mnlist = ["01"]
for yr in yrlist:
    for mn in mnlist:
        ldate = f"{yr}{mn}01"
        #retrieve_files(my_bucket, my_client, bucket_name, f"{ptype}/{ldate}/pgrb2/gfs.{ldate}/00/atmos", 
        retrieve_files(my_bucket, my_client, bucket_name, f"{ptype}/{ldate}/pgrb2/gfs.{ldate}/00",
            f"/scratch/bcash/{pdir}/{ldate}00")
