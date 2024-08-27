<div style="display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100vh;">

  <h2>Labs 1-5</h2>
  
  <p>Student ID: 23011392</p>
  <p>Student Name: Xiaojun Huang</p>

</div>

# Lab 1

## AWS Account and Log in

### [1] Log into an IAM user account created for you on AWS.

Starting by opening the URL provided in lab sheet 1, input the account and password as mentioned in the email. After logining
into the home page, change the password of my account immediately.
![img.png](img.png)

### [2] Search and open Identity Access Management

By following the instruction and open the Security Credentials tab under my user account, and obtained my Access Key ID and
the secret access key.

![img3.png](img3.png)
## Set up recent Linux OSes

My Operating System is macOS, so I use UTM as the virtual machine for booting Ubuntu.
## Install Linux packages

Linux VM has already been set up in my UTM, I don't need to re-install it.

### [1] Install Python 3.8.x

![img_1.png](img_1.png)
```bash
python3
```
By using this command line command, I found that my python version is 3.10.12, so I don't need to install python either.
### [2] Install awscli

By inputting the commands in the lab sheet, awscli has been successfully installed. I have already installed it, and checked 
by using the following command:
```bash
aws --version
```
![img_2.png](img_2.png)
### [3] Configure AWS
![IMG_1384.jpeg](IMG_1384.jpeg)
Input both the access keys obtained from Section [2] Search and open Identity Access Management, since my student number is
22984000 – 23370000, ap-northeast-1 would be my Region Name.

### [4] Install boto3

```bash
pip3 install boto3
pip show boto3
```
After running the command, boto3 had been successfully installed, 
using the second command to check whether it had been installed.
![img_4.png](img_4.png)

## Test the installed environment

### [1] Test the AWS environment

```bash
aws ec2 describe-regions --output table
```
The following table for running the command lists the available AWS regions for the EC2 service, with <span style="font-family: Courier;"> Endpoint, OptInStatus, 
RegionName </span>as columns.

* **Endpoint**: the URL for the EC2 service in the respective region;
* **OptInStatus**: Indicates whether the region requires opt-in for access. In this case no opt-in is needed;
* **RegionName**: The name of the AWS region.

![img_3.png](img_3.png)
### [2] Test the Python environment

The script for testing python env used boto3 to create a client object for the EC2 service, and interact with EC2.
And called the <span style="font-family: Courier;"> describe_regions </span>method, retrieving a list of regions where EC2
services are available. The image below displays the output of the response, which contains 2 main parts:
#### **Regions**:
A list of dictionaries, each representing an AWS region, same as the previous table.

#### **ResponseMetaData**:
Metadata about the API request.
  
![img_5.png](img_5.png)
### [3] Write a Python script

The task only requires 2 columns, <span style="font-family: Courier;"> Endpoint, RegionName </span>, using Python's Pandas
library, converting the response into a pandas DataFrame and print in a tabulated format.

First by making sure that we have installed pandas, if not, using the following command to install.
```bash
pip3 install pandas
```

```python
import pandas as pd
import boto3

ec2 = boto3.client('ec2')
response = ec2.describe_regions()

regions = response['Regions']  # Ignore the Metadata since we don't necessarily need them.

df = pd.DataFrame(regions, columns=['Endpoint', 'RegionName'])  # In the Region dict, we only need Endpoint and RegionName as columns.

print(df)  # Print the tabulated data. 
```

The output: 

![img_6.png](img_6.png)
<div style="page-break-after: always;"></div>

# Lab 2

## Create an EC2 Instance

### [1] Create a security group
Type in the command `aws ec2 create-security-group --group-name 23011392-sg --description "security group for development environment"`
into the terminal of Ubuntu
- `23011392-sg`: The security group name that AWS created for me.
- `sg-03d9eeab7a30845e7`: The security group ID I received. 

![img_7.png](img_7.png)

### [2] Authorise inbound traffic for ssh

Type in the command `aws ec2 authorize-security-group-ingress --group-name 23011392-sg --protocol tcp --port 22 --cidr 0.0.0.0/0`
- `"Return": true`: indicating that authorization was successful;
- `"SecurityGroupRules":[...]`: With a security group rule ID: "sgr-0b75b60eeee767008".
![img_8.png](img_8.png)

### [3] Create a key pair
```bash
stream@stream:~$ aws ec2 create-key-pair --key-name 23011392-key --query 'KeyMaterial' --output text > 23011392-key.pem

stream@stream:~$ chmod 400 23011392-key.pem
```

- `aws ec2 create-key-pair`: The command used to create a new key pair.
- `--output text > 23011392-key.pem`: Specify the output to be a plain text file and stored in a file named <span style="font-family: Courier;"> 23011392-key.pem </span>
on my local machine.
Create a key pair and set a permission after creating, restricting the permissions of the private key file so that only me can read it.

### [4] Create the instance
Since my student number is between 22984000 and 23370000, the ami_id should be <span style="font-family: Courier;"> ami-0162fe8bfebb6ea16 </span>
replace them with my student id and ami-id.
```bash
stream@stream:~$ aws ec2 run-instances --image-id ami-0162fe8bfebb6ea16 --security-group-ids 23011392-sg --count 1 --instance-type t2.micro --key-name 23011392-key --query 'Instances[0].InstanceId'
"i-0734269bd54fd6dd1"

 ```
The output `i-0734269bd54fd6dd1` is my instance ID that will be used in the next section.

### [5] Add a tag to your Instance

 ```
  aws ec2 create-tags --resources i-0734269bd54fd6dd1 --tags Key=Name,Value=23011392
 ```

### [6] Get the public IP address

```bash
stream@stream:~$ aws ec2 describe-instances --instance-ids i-0734269bd54fd6dd1 --query 'Reservations[0].Instances[0].PublicIpAddress'
"13.231.29.7"
```

`13.231.29.7` is my public IP address.

### [7] Connect to the instance via ssh
```bash
stream@stream:~$ ssh -i 23011392-key.pem ubuntu@13.231.29.7
The authenticity of host '13.231.29.7 (13.231.29.7)' can't be established.
ED25519 key fingerprint is SHA256:7NlgchZs5B8sNuMR8hp1ARtf4UQ9Kyplct0tKB8s0z4.
This key is not known by any other names
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '13.231.29.7' (ED25519) to the list of known hosts.
Welcome to Ubuntu 22.04.4 LTS (GNU/Linux 6.5.0-1022-aws x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/pro

 System information as of Fri Aug  9 07:35:21 UTC 2024

  System load:  0.0               Processes:             97
  Usage of /:   20.7% of 7.57GB   Users logged in:       0
  Memory usage: 21%               IPv4 address for eth0: 172.31.40.211
  Swap usage:   0%

Expanded Security Maintenance for Applications is not enabled.

0 updates can be applied immediately.

Enable ESM Apps to receive additional future security updates.
See https://ubuntu.com/esm or run: sudo pro status


The list of available updates is more than a week old.
To check for new updates run: sudo apt update


The programs included with the Ubuntu system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Ubuntu comes with ABSOLUTELY NO WARRANTY, to the extent permitted by
applicable law.

To run a command as administrator (user "root"), use "sudo <command>".
See "man sudo_root" for details.

ubuntu@ip-172-31-40-211:~$ 
```
The command takes:
- `-i 23011392-key.pem`: The private key file to authenticate the ssh connection.
- `13.231.29.7`: The public IP address of my EC2 instance obtained from the last step.

Besides the welcome message, I also received some system information confirming that I logged into the EC2 instance.

### [8] List the created instance using the AWS console

![img_9.png](img_9.png)

Starting by opening the web browser of AWS Management Console and go to the Instances under the Dashboard.

![img_10.png](img_10.png)

## Create an EC2 instance with Python Boto3

Based on the command line commands in the previous section and the python document of boto3, I found some similar functions in the
boto3 library that have the same effects as command line.
```python
import boto3
from botocore.exceptions import ClientError

# Create EC2 client based on my region associated with my student number
ec2 = boto3.client('ec2', region_name='ap-northeast-1')

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
```

### Functions I have used:
- dfd
- df
- TODO
## Use Docker inside a Linux OS

### [1] Install Docker
```
sudo apt install docker.io -y
```

![img_11.png](img_11.png)

The image illustrates that Docker has been installed in my VM, with the newest version(24.0.7)

### [2] Start Docker
```
sudo systemctl start docker
```

### [3] Enable Docker
```
sudo systemctl enable docker
```

After running previous 3 commands, Docker has been successfully installed and enabled on my VM.


### [5] Build and run an httpd container 

Create two files according to the lab sheet:

![img_13.png](img_13.png)


A permission error raised, try `sudo usermod -a -G docker <username>` and rebuild the docker image using `docker build -t my-apache2 .`: 
![img_14.png](img_14.png)
![img_15.png](img_15.png)

Since I am using PyCharm's SSH linking to my VM, I typed `exit` in the terminal to logout of SSH and logged back in using
`ssh stream@<my_vmserver_ip>`

After that, after running the image using `docker run -p 80:80 -dit --name my-app my-apache2` and open the browser with URL for my VM's IP, the following 
page has been displayed. 
![img_16.png](img_16.png)

### [6] Other docker commands
![img_17.png](img_17.png)
By running `docker ps -a`, I there are a bunch of information I can gather:
- Container ID: e3e2cf9c58f8
- Image: my-apache2
- Command: The container is running the <span style="font-family: Courier;"> httpd-foreground </span> command
- Created & Status: The container was created 4 mins ago and has been running for 4 mins.
- Ports: Port 80 inside the container is mapped to the port 80 on my host machine
- Names: The container is named my-app

After the container is stopped, the status of it became <span style="font-family: Courier;"> Exited </span>
![img_18.png](img_18.png)

Same as removing the container, after removing the container it will no longer be listed in the containers.
![img_19.png](img_19.png)

# Lab 3

## Program

### [1] Preparation
Starting by creating a new dir named root dir, I created the `rootdir` dir under my default dir. 
Create a file in it with the content `1\n2\n3\n4\n5\n`

![img_20.png](img_20.png)
![img_21.png](img_21.png)

For the subdir and subfile, using the same command as above:
![img_22.png](img_22.png)

```python3
import logging
import os
import boto3

from botocore.exceptions import ClientError



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

def main():
    
    create_bucket_if_not_exists(ROOT_S3_DIR)
    
    # parse directory and upload files
    for dir_name, subdir_list, file_list in os.walk(ROOT_DIR, topdown=True):
        print(dir_name, subdir_list, file_list)
        for fname in file_list:
            upload_file("%s/" % dir_name[1:], "%s/%s" % (dir_name, fname), fname)

if __name__ == "__main__":
    main()
```

In my python script, I have three functions:
- `create_bucket_if_not_exists(bucket_name)`: This function takes the bucket name we intend to create, starting from
checking whether the bucket exists and search whether it exists in the list of buckets. If not exists, I use `s3.create_bucket()` 
function provided in boto3 to create a new bucket.
- `upload_file()`: It uploads a specific file from the local file system to the corresponding path in the S3 bucket, it takes in
    - `folder_name`: The local folder where the file is located
    - `file`: The full path to the file.
    - `file_name`: The name of the file to be uploaded to S3.

- `test_upload()`: Check if a file was successfully uploaded to the S3 bucket by listing the objects with a specific 
prefix.

In my main function, I changed the `ROOT_DIR` to the abs location of my `rootdir`, traversing the root directory and upload all the files 
underneath it to S3 bucket. For success in uploading a message will be printed to the output. 

![img_23.png](img_23.png)

The images shows that the files in the dirs have been successfully uploaded to my S3 bucket.
### [3] Restore from S3

### [4]
```{'Key': 'home/stream/rootdir/rootfile.txt', 'LastModified': datetime.datetime(2024, 8, 18, 16, 54, 19, tzinfo=tzlocal()), 'ETag': '"f38a850818377e97155d22755caa39d0"', 'Size': 16, 'StorageClass': 'STANDARD'}

{'Key': 'home/stream/rootdir/subdir/subfile.txt', 'LastModified': datetime.datetime(2024, 8, 18, 16, 54, 19, tzinfo=tzlocal()), 'ETag': '"f38a850818377e97155d22755caa39d0"', 'Size': 16, 'StorageClass': 'STANDARD'}
```
The files listed under the 'Content' section in the response, from the dict we retrieved we can easily obtain the data we need to write into DynamoDB.

Permission of files need to be retrieved using `get_object_acl()` function:
```
{'ResponseMetadata': {'RequestId': 'F9PWB9S8H2TKACXD', 'HostId': '9Vk5cdkiLbA60T9J7/NSdgQa45q6KztmBcjWaDAUfPaEGuzhVa8acEzO/SqnmLuJI+5OXXuvEdFwoHSM6dsxWg==', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amz-id-2': '9Vk5cdkiLbA60T9J7/NSdgQa45q6KztmBcjWaDAUfPaEGuzhVa8acEzO/SqnmLuJI+5OXXuvEdFwoHSM6dsxWg==', 'x-amz-request-id': 'F9PWB9S8H2TKACXD', 'date': 'Tue, 20 Aug 2024 04:32:30 GMT', 'content-type': 'application/xml', 'transfer-encoding': 'chunked', 'server': 'AmazonS3'}, 'RetryAttempts': 0}, 'Owner': {'DisplayName': 'zhi.zhang', 'ID': '2a5fac7aada1ad2caa48c9ab08cc4e2428d4eb596108daa3b59f1204ae96482e'}, 'Grants': [{'Grantee': {'DisplayName': 'zhi.zhang', 'ID': '2a5fac7aada1ad2caa48c9ab08cc4e2428d4eb596108daa3b59f1204ae96482e', 'Type': 'CanonicalUser'}, 'Permission': 'FULL_CONTROL'}]}
{'ResponseMetadata': {'RequestId': 'F9PV47T217TVX6PZ', 'HostId': 'qtDxZ5bdOB+gHp89GO/c9t/eRPn52dDYxqS+m0hi9iZxI/+nUh+l3X5YaoY0BmLGLiymm73ZfjWtBbVnTeo8/w==', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amz-id-2': 'qtDxZ5bdOB+gHp89GO/c9t/eRPn52dDYxqS+m0hi9iZxI/+nUh+l3X5YaoY0BmLGLiymm73ZfjWtBbVnTeo8/w==', 'x-amz-request-id': 'F9PV47T217TVX6PZ', 'date': 'Tue, 20 Aug 2024 04:32:30 GMT', 'content-type': 'application/xml', 'transfer-encoding': 'chunked', 'server': 'AmazonS3'}, 'RetryAttempts': 0}, 'Owner': {'DisplayName': 'zhi.zhang', 'ID': '2a5fac7aada1ad2caa48c9ab08cc4e2428d4eb596108daa3b59f1204ae96482e'}, 'Grants': [{'Grantee': {'DisplayName': 'zhi.zhang', 'ID': '2a5fac7aada1ad2caa48c9ab08cc4e2428d4eb596108daa3b59f1204ae96482e', 'Type': 'CanonicalUser'}, 'Permission': 'FULL_CONTROL'}]}
```
The last field of the dict is `Permission`, under the `Grant` list.

```python
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
```
## [5]
By typing into the following command, the table named `CloudFiles` I just created has been scanned, and output a sequence of 
file information I've written into the DynamoDB, along with their data types.
```bash
stream@stream:~/CITS5503_Sem2/Labs/src$ aws dynamodb scan --table-name CloudFiles
\{
    "Items": [
        {
            "owner": {
                "S": "zhi.zhang"
            },
            "lastUpdated": {
                "S": "2024-08-18 16:54:19"
            },
            "fileName": {
                "S": "rootfile.txt"
            },
            "path": {
                "S": "home/stream/rootdir"
            },
            "userId": {
                "S": "23011392-cloudstorage"
            },
            "permissions": {
                "S": "FULL_CONTROL"
            }
        },
        {
            "owner": {
                "S": "zhi.zhang"
            },
            "lastUpdated": {
                "S": "2024-08-18 16:54:19"
            },
            "fileName": {
                "S": "subfile.txt"
            },
            "path": {
                "S": "home/stream/rootdir/subdir"
            },
            "userId": {
                "S": "23011392-cloudstorage"
            },
            "permissions": {
                "S": "FULL_CONTROL"
            }
        }
    ],
    "Count": 2,
    "ScannedCount": 2,
    "ConsumedCapacity": null
}
```
## [6]
![img_24.png](img_24.png)
# Lab 4

<div style="page-break-after: always;"></div>

# Lab 5

