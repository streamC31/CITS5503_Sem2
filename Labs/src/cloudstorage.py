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


ROOT_DIR = 'rootdir'
ROOT_S3_DIR = '23011392-cloudstorage'


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


def test_upload(file):
    try:
        response = s3.list_objects_v2(Bucket=ROOT_S3_DIR, Prefix=file)
        for obj in response.get('Contents', []):
            print(f"Found in bucket: {obj['Key']}")
            return True
        print("Did not find.")
    except ClientError as e:
        print(f"Error listing objects: {e}")
# Main program
# Insert code to create bucket if not there


# create_bucket_if_not_exists(ROOT_S3_DIR)

# parse directory and upload files

for dir_name, subdir_list, file_list in os.walk(ROOT_DIR, topdown=True):
    print(11)
    print(dir_name, subdir_list, file_list)
    # if dir_name != ROOT_DIR:
    #     for fname in file_list:
    #         upload_file("%s/" % dir_name[2:], "%s/%s" % (dir_name, fname), fname)


# print("done")
# test_upload("rootfile.txt")
#
# # upload_file("", "rootfile.txt", os.path.basename("rootfile.txt"))
# try:
#     s3.delete_object(Bucket=ROOT_S3_DIR, Key="rootfile.txt")
#     print(f"Successfully deleted.")
# except ClientError as e:
#     logging.error(e)
#     print(f"Failed to delete. Error: {e}")
#
# test_upload("rootfile.txt")