import logging

import boto3
import time
from botocore.exceptions import ClientError


STUDENT_NUMBER = '23011392'

REGION = 'ap-northeast-1'

ec2 = boto3.client('ec2', region_name=REGION)
client = boto3.client('elbv2', region_name=REGION)

def wait_for_instance(instance_id):
    """ Ensuring the instances are running so that we can do further manipulation to it"""
    try:
        print(f"Waiting for instance {instance_id} to enter 'running' state...")
        waiter = ec2.get_waiter('instance_running')
        waiter.wait(InstanceIds=[instance_id])
        print(f"Instance {instance_id} is now running.")
    except ClientError as e:
        logging.error(e)

def create_key_pair():
    response = ec2.create_key_pair(
        KeyName='23011392-key',
        KeyType='rsa',
        KeyFormat='pem'
    )
    file = open(f'23011392-key.pem','w')
    file.write(response.get('KeyMaterial'))
    file.close()

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
                    'FromPort': 22,
                    'ToPort': 22,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                },
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 80,
                    'ToPort': 80,
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
            ImageId='ami-0c6359fd9eb30edcf',  # ap-northeast-1
            InstanceType='t2.micro',
            MinCount=1,
            MaxCount=1,
            KeyName='23011392-key', # Already created in previous labs
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

def create_load_balancer(security_group_id, subnets):
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elbv2/client/create_load_balancer.html
    try:
        response = client.create_load_balancer(
            Name=f'{STUDENT_NUMBER}-lb-{int(time.time())}',
            Subnets=subnets,
            SecurityGroups=[security_group_id],
            Scheme='internet-facing',
            IpAddressType='ipv4'
        )

        load_balancer_arn = response['LoadBalancers'][0]['LoadBalancerArn']
        print(f"Application Load Balancer created with ARN: {load_balancer_arn}")
        return load_balancer_arn
    except ClientError as e:
        logging.error(e)
        return None

def create_target_group(vpc_id):
    try:
        response = client.create_target_group(
            Name=f'{STUDENT_NUMBER}-tg-{int(time.time())}',
            Protocol='HTTP',
            Port=80,
            VpcId=vpc_id,
            TargetType='instance'
        )

        target_group_arn = response['TargetGroups'][0]['TargetGroupArn']
        print(f"Target group created with ARN: {target_group_arn}")
        return target_group_arn

    except ClientError as e:
        logging.error(e)
        return None

def register_targets(target_group_arn, instance_ids):
    try:
        targets = [{'Id': instance_id} for instance_id in instance_ids]
        response = client.register_targets(
            TargetGroupArn=target_group_arn,
            Targets=targets
        )
        print(f"Instances {instance_ids} registered to target group {target_group_arn}")
    except ClientError as e:
        logging.error(e)

def create_listener(load_balancer_arn, target_group_arn):
    try:
        response = client.create_listener(
            LoadBalancerArn=load_balancer_arn,
            Protocol='HTTP',
            Port=22,
            DefaultActions=[
                {
                    'Type': 'forward',
                    'TargetGroupArn': target_group_arn
                }
            ]
        )
        listener_arn = response['Listeners'][0]['ListenerArn']
        print(f"Listener created with ARN: {listener_arn}")
        return listener_arn
    except ClientError as e:
        logging.error(e)
        return None

def main():

    # create_key_pair()
    security_group_id = create_security_group()
    if not security_group_id:
        return

    response = ec2.describe_availability_zones()
    availability_zones = [zone['ZoneName'] for zone in response['AvailabilityZones']]

    # Create instances in different availability zones
    instance1 = create_ec2_instance(f'{STUDENT_NUMBER}-vm1', availability_zones[0], security_group_id)
    instance2 = create_ec2_instance(f'{STUDENT_NUMBER}-vm2', availability_zones[1], security_group_id)

    wait_for_instance(instance1)
    wait_for_instance(instance2)

    if not instance1 and instance2:
        return

    # Get subnet ID by using function describe_subnet in ec2
    response = ec2.describe_subnets()
    subnets = [subnet['SubnetId'] for subnet in response['Subnets'][:2]]  # Use the first two subnets
    vpc_id = response['Subnets'][0]['VpcId']
    if len(subnets) < 2:
        print("Error: Not enough subnets available to create a load balancer.")
        return

    # Create a load balancer using the security group and subnets
    lb_arn = create_load_balancer(security_group_id, subnets)

    if not lb_arn:

        return
    # Create a target group in the same VPC as the EC2 instances
    target_group_arn = create_target_group(vpc_id)

    if not target_group_arn:
        print("Error: Failed to create target group.")
        return

    register_targets(target_group_arn, [instance1, instance2])
    listener_arn = create_listener(lb_arn, target_group_arn)
    if not listener_arn:
        print("Error: Failed to create listener.")
        return


if __name__ == "__main__":
    main()