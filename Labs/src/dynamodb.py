import logging
import time

import boto3
from botocore.exceptions import ClientError

client = boto3.client('dynamodb')
s3 = boto3.client('s3', region_name='ap-southeast-2')

BUCKET_NAME = '23011392-cloudstorage'

def create_table():
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/create_table.html
    # Create the table based on the method and syntax provided
    try:
        # Since DynamoDB only requires the key attrs to be defined in the table schema, the task specified userId and
        # fileName as keys.
        response = client.create_table(
            AttributeDefinitions=[
                {'AttributeName': 'userId', 'AttributeType': 'S'},
                {'AttributeName': 'fileName', 'AttributeType': 'S'}
            ],
            TableName='CloudFiles',
            KeySchema=[
                {'AttributeName': 'userId', 'KeyType': 'HASH'},  # Partition key
                {'AttributeName': 'fileName', 'KeyType': 'RANGE'}  # Sort key
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 123,
                'WriteCapacityUnits': 123
            }
        )
        print("Successfully create table!")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            logging.info("Table already exists.")
            return True
        else:
            logging.error(f"Unexpected error: {e}")
            return False


def get_file_attr(bucket):
    # Permission can be obtained using the function get_bucket_acl()
    # https: // boto3.amazonaws.com / v1 / documentation / api / latest / guide / s3 - example - access - permissions.html
    try:
        response = s3.list_objects(Bucket=bucket)
        files_attrs = []

        if 'Contents' in response:
            for item in response['Contents']:
                acl = s3.get_object_acl(Bucket=bucket, Key=item['Key'])
                permission = (acl['Grants'][0]['Permission'])  # Access the permission field of the file's ACL dictionary under the Grant field
                attributes = {
                    'fileName': item['Key'].split('/')[-1] if '/' in item['Key'] else item['Key'],
                    'path': '/'.join(item['Key'].split('/')[:-1]) if '/' in item['Key'] else '',
                    'lastUpdated': item['LastModified'].strftime('%Y-%m-%d %H:%M:%S'),
                    'owner': item['Owner']['DisplayName'],
                    'permissions': permission
                }
                files_attrs.append(attributes)
            print(files_attrs)
            return files_attrs
    except ClientError as e:
        logging.error(e)
        return None

def write_to_dynamodb(item):
    try:
        s3 = boto3.client('dynamodb')

        s3.put_item(
            TableName='CloudFiles',
            Item={
                'userId': {'S': BUCKET_NAME},  # You might want to adjust this
                'fileName': {'S': item['fileName']},
                'path': {'S': item['path']},
                'lastUpdated': {'S': item['lastUpdated']},
                'owner': {'S': item['owner']},
                'permissions': {'S': item['permissions']}
            }
        )
        print(f"Successfully wrote {item['fileName']} to DynamoDB")
        return True
    except ClientError as e:
        logging.error(e)
        return False


def main():
    create_table()

    time.sleep(5)  # Ensuring table has been fully created

    for item in get_file_attr(BUCKET_NAME):
        write_to_dynamodb(item)


if __name__ == "__main__":
    main()