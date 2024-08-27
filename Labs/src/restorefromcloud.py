import os
import boto3
import logging
from botocore.exceptions import ClientError
from cloudstorage import test_upload, list_all_objects

#  Reads the S3 bucket and writes the contents of the bucket within the appropriate directories.

ROOT_DIR = '/home/stream/rootdir'  # The root dir for restoring files
ROOT_S3_DIR = '23011392-cloudstorage'  # Bucket name

s3 = boto3.client('s3', region_name='ap-southeast-2')

def download_file(bucket_name, obj_name, file_name):
    '''
    Download a file from S3 to a local path
    :param bucket_name: Name of the S3 bucket
    :param obj_name: Path in S3
    :param file_name: Local path
    :return:
    '''
    try:
        print(f"Downloading {obj_name} to {file_name}")
        s3.download_file(bucket_name, obj_name, file_name)
        print(f"Successfully download {obj_name}")
        return True
    except ClientError as e:
        logging.error(e)
        return False


s3_fp = "rootdir/rootfile.txt"
local_fp = os.path.join(ROOT_DIR, "rootfile.txt")

os.makedirs(os.path.dirname(local_fp), exist_ok=True)

success = download_file(ROOT_S3_DIR, s3_fp, local_fp)

if success:
    print("success")
else:
    print("Failed")

