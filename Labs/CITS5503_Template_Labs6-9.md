<div style="display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100vh;">

  <h2>Labs 6-9</h2>
  
  <p>Student ID: 23011392</p>
  <p>Student Name: Xiaojun Huang</p>

</div>

# Lab 6

## Set up an EC2 instance

### [1] Create an EC2 micro instance with Ubuntu and SSH into it. 
Same as the Lab 5, this time I create EC2 micro instance in the AWS console with Security Group and secret key. 

![The info page of newly created EC2 instance](img_1.png)

![Successfully connected to the EC2 instance via SSH with ubuntu](img.png)

The local key file is stored under the dir in the image, with public IP addr of my instance in the command.

### [2] Install the Python 3 virtual environment package. 

Since all the operation require root user authentication. I changed the mode to root mode using `sudo bash`.
![Change to root user and update](img_2.png)

After I typed in `apt-get upgrade` following content popped out, the system requires me to select services needed to restart.
In this case I selected ssh.service(5), preventing accidentally connection lost. 

![](img_3.png)

Last, install python3 venv using `apt-get install python3-venv`.



### [3] Access a directory 

`-p` option will create necessary parent dirs automatically. 

```bash
mkdir -p /opt/wwc/mysites
cd /opt/wwc/mysites
```

### [4] Set up a virtual environment


`python3 -m venv myvenv`

![Subdir named myvenv](img_5.png)

After running this command, a subdir named `myvenv` was created.

### [5] Activate the virtual environment

```bash
source myvenv/bin/activate

pip install django

django-admin startproject lab

cd lab

python3 manage.py startapp polls
```

After running the first line, there is a (myvenv) before my username, indicating the activation of virtual environment was successful.

![Activation successful](img_6.png)

For the rest of the command line commands, first install Django using `pip install django`, and create a new Django project named `lab`, and
change into the directory. Last I used `python3 manage.py startapp polls` to create a new Django app named `polls` within my `lab` project. 
 dir named `polls` will be created inside the `lab` dir. 

![Content in the lab directory](img_7.png)


### [6] Install nginx

```apt install nginx```
Following windows popped out when I typed in the command, requires me to select services to restart. I choose to continue without restarting
any services.

![](img_8.png)

### [7] Configure nginx

![server](img_10.png)

For the server section, according to the lab sheet I only need the first two rows, and Location subsection. Delete the rest. Same for Location.

![Location](img_11.png)

### [8] Restart nginx

Type in the command `service nginx restart` to restart nginx after modifying the `default` file.

### [9] Access your EC2 instance

![img_12.png](img_12.png)

Run `manage.py` in the directory I changed to using command `python3 manage.py runserver 8000`, the message popped out.

Open the via a browser:

![Welcome page of Django](img_13.png)

The welcome page of Django indicates that my Django server is running successfully. 

## Set up Django inside the created EC2 instance

### [1] Edit the following files (create them if not exist)

![polls/views.py](img_15.png)

![lab/urls.py](img_16.png)

![polls/urls.py](img_17.png)

Open `polls/views.py` and the rest, add the content in the lab sheet into it.

### [2] Run the web server again

![Run the web server with the same command as previous](img_18.png)

### [3] Access the EC2 instance

I accessed my instance's IP address with endpoint `/polls` `http://18.183.253.227/polls/`, the page only contains a line of text saying 'Hello, world.'

![Hello, world.](img_19.png)

## Set up an ALB

### [1] Create an application load balancer

First go to the AWS Console, and navigate to the corresponding section:

![Corresponding section.](img_20.png)

Click the `Create Load Balancer` button and choose the "Application Load Balancer". Create as follows, with the security group and target group of my instance.

Create the ALB after everything is set up.

![ALB](img_23.png)

### [2] Health check

![Specify path for health check](img_24.png)

For the target group associated with my ALB, navigate to "Target Groups" under "Load Balancing" section in the AWS console, and find the target group 
I created. Edit it in the "Health Check" tab to change the tab from `/` to `/polls/`. The interval here is already 30s, indicates the health check fetches
the page every 30s.

### [3] Access

Delete the instance and ALB created after complete the lab.

# Lab 7

### [Step 1] Create an EC2 instance

Similar to the previous labs, use the code to create an EC2 instance so that I can do operations later on:
```python3
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

        # Authorize inbound SSH and HTTP traffic
        ec2.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpProtocol='tcp',
            FromPort=22,
            ToPort=22,
            CidrIp='0.0.0.0/0'
        )
        ec2.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpProtocol='tcp',
            FromPort=80,
            ToPort=80,
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
    Tags=[{'Key': 'Name', 'Value': '23011392-vm1'}]
)

# Get public IP address
response = ec2.describe_instances(InstanceIds=[instance_id])
public_ip = response['Reservations'][0]['Instances'][0]['PublicIpAddress']

print(f"Instance created with ID: {instance_id}")
print(f"Public IP address: {public_ip}")
```
### [Step 2] Install and configure Fabric on your VM

Starting from installing fabric via the command `pip install fabric`, and create a config file inside "~/.ssh":

`vim ~/.ssh/congig`

``` 
Host 23011392-vm1
	Hostname ec2-18-183-253-227.ap-northeast-1.compute.amazonaws.com
	User ubuntu
	UserKnownHostsFile /dev/null
	StrictHostKeyChecking no
	PasswordAuthentication no
	IdentityFile /home/streamc/Desktop/Labs/23011392-key.pem

```

same as previous labs, connect to my created EC2 instance using ssh:

`ssh -i 23011392-key.pem ubuntu@18.183.253.227`

Last, test the following python code locally, successfully output "Linux":

![Python output](img_25.png)


### [Step 3] Write a python script to automate the installation of nginx

```python
import io

from fabric import Connection


c = Connection('23011392-vm1')


def setup_nginx(c):
    """"""

    # Update the packet list
    c.sudo('apt-get update')

    # Install nginx
    c.sudo('apt-get install -y nginx')

    # Start nginx service
    c.sudo('systemctl start nginx')

    # Enable nginx to start on boot
    c.sudo('systemctl enable nginx')

    # Configure nginx
    nginx_config = '''
       server {
          listen 80 default_server;
          listen [::]:80 default_server;
        
          location / {
            proxy_set_header X-Forwarded-Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        
            proxy_pass http://127.0.0.1:8000;
          }
        }
       '''

    # Write the nginx configuration
    config_file = io.StringIO(nginx_config)
    c.put(config_file, '/tmp/nginx_config')
    c.sudo('mv /tmp/nginx_config /etc/nginx/sites-available/default')

    # Restart nginx to apply changes
    c.sudo('systemctl restart nginx')

    print("Nginx has been installed and configured.")


if __name__ == '__main__':
    setup_nginx(c)
```

### Step[4]

Starting from updating my script in step[3].

![Fabric Transfer File](img_26.png)

![Command Line Task](img_27.png)

# Lab 8

## Set Up Python Environment
Starting from installing pandas, numpy, jupyter notebook, and sagemaker.

## Prepare SageMaker session

![No such entity](img_28.png)

The first time I execute the Jupyter Notebook script and a NoSuchEntity exception raised, and I found in the IAM roles there 
is no role named `Role_AWS_SageMaker`. So I viewed the role list and found the closest one: `SageMakerRole`.

## Download Dataset

Answer the following questions:
    - Which variables are categorical?
Categorical variables are usually non-numerical and represent catagory labels: `job`, `marital`, `education`, `default`, `housing`, 
`loan`, `contact`, `month`, `day_of_week`, `poutcome`, `y`
    - Which ones are numerical?
Continuous or discrete numbers in the dataset: `age`, `duration`, `campaign`, `pdays`, `previous`, `emp.var.rate`, `cons.price.idx`, 
`cons.conf.idx`, `euribor3m`, `nr.employed`.

```python
boto3.Session().resource("s3").Bucket(bucket).Object(
    os.path.join(prefix, "train/train.csv")
).upload_file("train.csv")
boto3.Session().resource("s3").Bucket(bucket).Object(
    os.path.join(prefix, "validation/validation.csv")
).upload_file("validation.csv")
```

In this python script, it uploads the training and validation file into my S3 bucket.

![train.csv inside the bucket](img_29.png)

![validation.csv inside the bucket](img_30.png)
# Lab 9

