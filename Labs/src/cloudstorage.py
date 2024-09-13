import logging
import os
import boto3
import base64
from botocore.exceptions import ClientError

# ------------------------------
# CITS5503
#
# cloudstorage.py
#
# skeleton application to copy local files to S3
#
# Given a root local directory, will return files in each level and
# copy to same path on S3
#
# ------------------------------ 


ROOT_DIR = '/home/stream/rootdir'  # My two nested directories are created under my user dir.
ROOT_S3_DIR = '23011392-cloudstorage'  # The name and the root dir of my bucket.


s3 = boto3.client("s3",region_name='ap-southeast-2')

bucket_config = {'LocationConstraint': 'ap-southeast-2'}

# Reference: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html
def upload_file(folder_name, file, file_name):
    print(f"Uploading {file}")
    try:
        s3_path = os.path.join(folder_name, file_name).lstrip('./')
        s3.upload_file(file, ROOT_S3_DIR, s3_path)
        print(f"Successfully uploaded {file} to {ROOT_S3_DIR}/{s3_path}")
        return True
    except ClientError as e:
        logging.error(e)
        return False



def create_bucket_if_not_exists(bucket_name):
    '''
    Checks if the bucket exists and creates it if it does not.
    :param bucket_name: The name of the bucket
    :return: None
    '''
    # Check whether the bucket name exists by listing all the buckets and find in them
    response = s3.list_buckets()
    exists = any(bucket['Name'] == bucket_name for bucket in response['Buckets'])  # Return True if exists

    if not exists:
        print(f"Bucket {bucket_name} does not exist. Creating...")
        try:
            s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=bucket_config)
        except ClientError as e:
            logging.error(e)
            return False
        print(f"Successfully created bucket {bucket_name}!")
        return True
    print("Bucket exists!")

def list_all_objects():
    try:
        response = s3.list_objects_v2(Bucket=ROOT_S3_DIR)
        print("All objects in bucket:")
        for obj in response.get('Contents', []):
            print(obj['Key'])
    except ClientError as e:
        print(f"Error listing all objects: {e}")

def test_upload(file):
    try:
        # Construct the full S3 path
        s3_path = os.path.relpath(file, ROOT_DIR).replace(os.sep, '/')
        print(f"Searching for file: {s3_path}")

        response = s3.list_objects_v2(Bucket=ROOT_S3_DIR, Prefix=s3_path)

        if 'Contents' in response:
            for obj in response['Contents']:
                print(f"Found in bucket: {obj['Key']}")
            return True
        else:
            print(f"Did not find file: {s3_path}")
            return False
    except ClientError as e:
        print(f"Error listing objects: {e}")
        return False

# Main program
# Insert code to create bucket if not there


# create_bucket_if_not_exists(ROOT_S3_DIR)

# parse directory and upload files
if __name__ == "__main__":
    for dir_name, subdir_list, file_list in os.walk(ROOT_DIR, topdown=True):
        print(dir_name, subdir_list, file_list)
        for fname in file_list:
            upload_file("%s/" % dir_name[1:], "%s/%s" % (dir_name, fname), fname)