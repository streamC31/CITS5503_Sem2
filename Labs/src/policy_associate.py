import json
import logging

import boto3
from botocore.exceptions import ClientError

bucket_name = "23011392-cloudstorage"

policy = {
  "Version": "2012-10-17",
  "Statement": {
   "Sid": "AllowAllS3ActionsInUserFolderForUserOnly",
    "Effect": "DENY",
    "Principal": "*",
    "Action": "s3:*",
    "Resource": f"arn:aws:s3:::{bucket_name}/folder1/folder2/*",
    "Condition": {
      "StringNotLike": {
          "aws:username":"23011392@student.uwa.edu.au"
       }
    }
  }
}

def set_policy(bucket_name, policy):
    """
    set the policy on an S3 bucket
    reference: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-example-bucket-policies.html
    """
    s3 = boto3.client('s3')
    policy = json.dumps(policy) # Convert the policy from JSON dict to string
    try:
        s3.put_bucket_policy(Bucket=bucket_name, Policy=policy)
        print(f"Successfully set policy on bucket {bucket_name}")
        return True
    except ClientError as e:
        logging.error(e)
        print(f"Error setting policy on bucket {bucket_name}: {e}")
        return False

set_policy(bucket_name=bucket_name, policy=policy)