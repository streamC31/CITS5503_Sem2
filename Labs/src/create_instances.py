import logging

import boto3
import time
from botocore.exceptions import ClientError


STUDENT_NUMBER = '23011392'

REGION = 'ap-southeast-2'

ec2 = boto3.client('ec2', region_name=REGION)
client = boto3.client('elbv2')

def create_security_group():
    try:
        security_group = ec2.create_security_group(
            GroupName=f'{STUDENT_NUMBER}-security_group0-{int(time.time())}',
            Description='Security group to authorize inbound traffic for HTTP and SSH'
        )
        security_group_id = security_group['GroupId']  # Access the group ID

        ec2.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 80,
                    'ToPort': 80,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                },
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 22,
                    'ToPort': 22,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                }
            ]
        )

        print(f"Security group created with ID: {security_group_id}")
        return security_group_id
    except ClientError as e:
        logging.error(e)
        return None

def create_ec2_instance(instance_name, availability_zone, security_group_id):
    try:
        response = ec2.run_instances(
            ImageId='ami-0310483fb2b488153',  # ap-southeast-2
            InstanceType='t2.micro',
            MinCount=1,
            MaxCount=1,
            SecurityGroupIds=[security_group_id],
            Placement={'AvailabilityZone': availability_zone},
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': instance_name
                        },
                    ]
                },
            ]
        )
        instance_id = response['Instances'][0]['InstanceId']
        print(f"Instance {instance_name} created with ID: {instance_id} in {availability_zone}")
        return instance_id
    except ClientError as e:
        logging.error(e)
        return None

def create_load_balancer(security_group_id, subnet):
    pass

def main():
    security_group_id = create_security_group()
    if not security_group_id:
        return

    response = ec2.describe_availability_zones()
    availability_zones = [zone['ZoneName'] for zone in response['AvailabilityZones']]

    # Create instances in different availability zones
    create_ec2_instance(f'{STUDENT_NUMBER}-vm1', availability_zones[0], security_group_id)
    create_ec2_instance(f'{STUDENT_NUMBER}-vm2', availability_zones[1], security_group_id)


if __name__ == "__main__":
    main()