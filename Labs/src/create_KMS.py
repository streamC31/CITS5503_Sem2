import json
import logging
import boto3
from botocore.exceptions import ClientError

student_number = '23011392'
iam_username = '23011392@student.uwa.edu.au'

key_policy = {
    "Version": "2012-10-17",
    "Id": "key-consolepolicy-3",
    "Statement": [
        {
            "Sid": "Enable IAM User Permissions",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::489389878001:root"
            },
            "Action": "kms:*",
            "Resource": "*"
        },
        {
            "Sid": "Allow access for Key Administrators",
            "Effect": "Allow",
            "Principal": {
                "AWS": f"arn:aws:iam::489389878001:user/{iam_username}"
            },
            "Action": [
                "kms:Create*", "kms:Describe*", "kms:Enable*", "kms:List*", "kms:Put*",
                "kms:Update*", "kms:Revoke*", "kms:Disable*", "kms:Get*", "kms:Delete*",
                "kms:TagResource", "kms:UntagResource", "kms:ScheduleKeyDeletion",
                "kms:CancelKeyDeletion"
            ],
            "Resource": "*"
        },
        {
            "Sid": "Allow use of the key",
            "Effect": "Allow",
            "Principal": {
                "AWS": f"arn:aws:iam::489389878001:user/{iam_username}"
            },
            "Action": [
                "kms:Encrypt", "kms:Decrypt", "kms:ReEncrypt*",
                "kms:GenerateDataKey*", "kms:DescribeKey"
            ],
            "Resource": "*"
        },
        {
            "Sid": "Allow attachment of persistent resources",
            "Effect": "Allow",
            "Principal": {
                "AWS": f"arn:aws:iam::489389878001:user/{iam_username}"
            },
            "Action": [
                "kms:CreateGrant", "kms:ListGrants", "kms:RevokeGrant"
            ],
            "Resource": "*",
            "Condition": {
                "Bool": {
                    "kms:GrantIsForAWSResource": "true"
                }
            }
        }
    ]
}

def get_kms_key_id(alias_name):
    kms = boto3.client('kms', region_name="ap-southeast-2")
    try:
        response = kms.describe_key(KeyId=f'alias/{alias_name}')
        return response['KeyMetadata']['KeyId']
    except ClientError:
        return None

def update_key_policy(key_id, policy):
    """
    The second part of the first task, since I have already created the key with my student number as
    an alias, repeatedly creating key to update policy will trigger an AlreadyExistError.
    So I use this standalone function to update
    """
    kms = boto3.client('kms', region_name="ap-southeast-2")
    try:
        kms.put_key_policy(
            KeyId=key_id,
            PolicyName='default',
            Policy=json.dumps(policy)
        )
        print(f"Policy updated for key: {key_id}")
    except ClientError as e:
        logging.error(f"Failed to update policy: {e}")

def create_or_update_KMS_key(student_id):
    kms = boto3.client('kms', region_name="ap-southeast-2")
    alias_name = f'alias/{student_id}'

    # Check if the alias already exists
    existing_key_id = get_kms_key_id(student_id)

    if existing_key_id:
        print(f"KMS key with alias {alias_name} already exists. Updating policy.")
        update_key_policy(existing_key_id, key_policy)
        return existing_key_id, alias_name

    try:
        response = kms.create_key(
            Description=f'KMS key for {student_id}',
            KeyUsage='ENCRYPT_DECRYPT',
            Policy=json.dumps(key_policy)
        )
        key_id = response['KeyMetadata']['KeyId']

        kms.create_alias(
            AliasName=alias_name,
            TargetKeyId=key_id
        )
        print(f"KMS key created successfully. Key ID: {key_id}")
        print(f"Alias created: {alias_name}")

        return key_id, alias_name
    except ClientError as e:
        logging.error(e)
        return None, None

# Create or update the KMS key with the student number as the alias
key_id, alias = create_or_update_KMS_key(student_number)

if key_id and alias:
    print("KMS key creation/update and alias assignment successful.")
else:
    print("Failed to create/update KMS key or assign alias.")