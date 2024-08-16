import boto3
from botocore.exceptions import ClientError

# Create EC2 client
ec2 = boto3.client('ec2', region_name='ap-northeast-1')  # Adjust region if needed

# Check if security group exists, if not create it
try:
    response = ec2.describe_security_groups(GroupNames=['23011392-sg'])
    security_group_id = response['SecurityGroups'][0]['GroupId']
    print(f"Using existing security group: {security_group_id}")
except ClientError as e:
    if e.response['Error']['Code'] == 'InvalidGroup.NotFound':
        print("Creating new security group")
        security_group = ec2.create_security_group(
            GroupName='23011392-sg',
            Description='security group for development environment'
        )
        security_group_id = security_group['GroupId']

        # Authorize inbound SSH traffic
        ec2.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpProtocol='tcp',
            FromPort=22,
            ToPort=22,
            CidrIp='0.0.0.0/0'
        )
    else:
        raise e

# Check if key pair exists, if not create it
try:
    ec2.describe_key_pairs(KeyNames=['23011392-key'])
    print("Key pair already exists")
except ClientError as e:
    if e.response['Error']['Code'] == 'InvalidKeyPair.NotFound':
        print("Creating new key pair")
        key_pair = ec2.create_key_pair(KeyName='23011392-key')
        with open('23011392-key.pem', 'w') as key_file:
            key_file.write(key_pair['KeyMaterial'])
    else:
        raise e

# Create EC2 instance
instance = ec2.run_instances(
    ImageId='ami-0162fe8bfebb6ea16',
    InstanceType='t2.micro',
    KeyName='23011392-key',
    SecurityGroupIds=[security_group_id],
    MinCount=1,
    MaxCount=1
)

instance_id = instance['Instances'][0]['InstanceId']

# Add tag to instance
ec2.create_tags(
    Resources=[instance_id],
    Tags=[{'Key': 'Name', 'Value': '23011392'}]
)

# Get public IP address
response = ec2.describe_instances(InstanceIds=[instance_id])
public_ip = response['Reservations'][0]['Instances'][0]['PublicIpAddress']

print(f"Instance created with ID: {instance_id}")
print(f"Public IP address: {public_ip}")