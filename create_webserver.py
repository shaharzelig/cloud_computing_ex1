import random
import boto3
import argparse

USER_DATA_CODE = '''#!/bin/bash
        sudo yum update -y
        sudo yum install -y python3
        sudo yum install -y python3-pip
        sudo yum install -y git
        git clone https://github.com/shaharzelig/cloud_computing_ex1.git
        cd cloud_computing_ex1
        sudo chmod 777 app.py
        sudo pip3 install -r requirements.txt
        sudo python3 app.py'''  # Why sudo? because I want to bind port 80 (and root is required for that)
TAG_NAME = 'cloudcomputing'
TAG_VALUE = 'cloudcomputing2023ex1'


def create_web_server(ec2_client):
    group_name = 'CloudComputingEx1GroupName' + str(random.randint(0, 1000))
    security_groups_names = [security_group["GroupName"] for security_group in
                             ec2_client.describe_security_groups()['SecurityGroups']]
    print("[+] Making sure we don't have a security group with the same name")
    # In the super rare case where we already have a group with the same name or if we have more than 1000 VMs, retry
    while group_name in security_groups_names:
        group_name = 'CloudComputingEx1GroupName' + str(random.randint(0, 1000))

    print("[+] Creating security group %s" % group_name)
    security_group = ec2_client.create_security_group(GroupName=group_name,
                                                      Description='Port 80 for my Flask web server')

    ec2_client.authorize_security_group_ingress(GroupId=security_group['GroupId'], IpPermissions=[
            {
                'IpProtocol': 'tcp',
                'FromPort': 80,
                'ToPort': 80,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
            }
        ]
    )

    print("[+] Creating EC2 instance")
    instance = ec2_client.run_instances(
        ImageId='ami-02396cdd13e9a1257',    # Basic Amazon Linux 2 AMI
        InstanceType='t2.micro',    # The smallest instance type available
        MaxCount=1,
        MinCount=1,
        SecurityGroupIds=[security_group['GroupId']],
        UserData=USER_DATA_CODE
    )

    print("[+] Waiting for instance to be ready")
    instance_id = instance['Instances'][0]['InstanceId']
    ec2_client.get_waiter('instance_running').wait(InstanceIds=[instance_id])

    response = ec2_client.describe_instances(InstanceIds=[instance_id])
    public_ip_address = response['Reservations'][0]['Instances'][0]['PublicIpAddress']

    print(f"[+] The web server is running on http://{public_ip_address}:80")
    print("[*] You should try it out by executing the following commands:")
    print(f"    1. curl -X POST \"http://{public_ip_address}:80/entry?plate=1234567&parkingLot=1\"")
    print(f"    2. curl -X POST \"http://{public_ip_address}:80/exit?ticketId=12345\"")
    print("[*] Please wait for the server to be ready.")


def main():
    parser = argparse.ArgumentParser(description='Create a web server on AWS')
    parser.add_argument('--key', type=str, help='AWS server public key. If you will not provide,'
                                                'environment variables will be used (keys configures in'
                                                ' ~/.aws/credentials using "aws configure"')
    parser.add_argument('--secret', type=str, help='AWS server secret key. If you will not provide,'
                                                   'environment variables will be used (keys configures in'
                                                   ' ~/.aws/credentials using "aws configure"')
    args = parser.parse_args()
    print('[+] Creating session with AWS.')
    session = boto3.Session(
        aws_access_key_id=args.key,
        aws_secret_access_key=args.secret
    )

    ec2 = session.client('ec2', region_name='us-east-1')
    create_web_server(ec2)


if __name__ == '__main__':
    main()