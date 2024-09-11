"""
Write a Python script where each file from the S3 bucket is encrypted and then decrypted via the created KMS key.
 Both encrypted and decrypted files will be in the same folder as the original file.

 https://boto3.amazonaws.com/v1/documentation/api/latest/guide/kms-example-encrypt-decrypt-file.html
 https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/kms/client/encrypt.html
"""
import logging

import boto3
from botocore.exceptions import ClientError

s3 = boto3.client('s3', region_name="ap-southeast-2")
kms = boto3.client('kms', region_name="ap-southeast-2")

bucket_name = '23011392-cloudstorage'
kms_alias = 'alias/23011392'


def get_kms_key_id(alias_name):
    """Same as the previous task, retrieve the key id using describe_key function"""
    try:
        response = kms.describe_key(KeyId=kms_alias)
        return response['KeyMetadata']['KeyId']
    except ClientError:
        return None


def encrypt_file(filename, kms_key_id):
    # Read the entire file into memory
    try:
        with open(filename, 'rb') as file:
            file_contents = file.read()
    except IOError as e:
        logging.error(e)
        return False
    try:
        response = kms.encrypt(KeyId=kms_key_id, PlainText=file_contents)
        return response
    except ClientError as e:
        logging.error(e)
        return None

def main():
    kms_key_id = get_kms_key_id(kms_alias)
    if not kms_key_id:
        print("Could not retrieve KMS key ID.")
        exit(1)

    try:
        # Starting by listing all the objects inside the S3 bucket.
        response = s3.list_objects_v2(Bucket=bucket_name)
        if 'Contents' not in response:
            print("No object found in the bucket.")
            exit(1)
        for obj in response['Contents']:
            file = f"{bucket_name}/{obj['Key']}"
            print(f"Processing file: {file}")
            encrypt_file(file, kms_key_id)
    except ClientError as e:
        logging.error(e)
        exit(1)


if __name__ == '__main__':
    main()