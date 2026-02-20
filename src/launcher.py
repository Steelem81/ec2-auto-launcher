import boto3
import os
import requests
import click
from dotenv import load_dotenv


load_dotenv()

class EC2Launcher:
    """Main launcher of EC2 instances"""

    def __init__(self):
        self.region = os.getenv('AWS_REGION', 'us-west-2')
        """Initialize AWS Clients"""
        self.ec2_client=boto3.client('ec2',
        region_name=self.region,
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        self.ec2_resource = boto3.resource('ec2', region_name = self.region)

        print(f"EC2 Launcher intitiated (Region: {self.region})")

    def test_connection(self):
        """Test AWS connection"""
        try:
            response = self.ec2_client.describe_instances()
            print("AWS connection successful")
            print(f"Found {len(response['Reservations'])} reservations")
            return True
        except Exception as e:
            print(f"AWS Connection failed: {e}")
            return False

    def get_my_ip(self):
        """Get current IP for sec group rules"""
        try:
            response = requests.get('https://api.ipify.org?format=json', timeout=5)
            ip = response.json()['ip']
            print(f"Your public ip is: {ip}")
            return ip
        except Exception as e:
            print(f"Failed to get ip: {e}")
            return None

    def get_or_create_security_group(self, name, description, ip):
        """Get existing security group or create a new one"""
        try:
            response = self.ec2_client.describe_security_groups(
                Filters=[
                    {'Name': 'group-name', 'Values': [name]}
                ]
            )

            if response['SecurityGroups']:
                sg_id = response['SecurityGroups'][0]['GroupId']
                print(f"using existing security group: {sg_id}")
                return sg_id
        
            # Create security group with SSH access from current IP only
            print(f"Creating new security group: {name}")
            response = self.ec2_client.create_security_group(
                GroupName=name,
                Description=description
                )

            sg_id = response['GroupId']

            # Add rules
            self.ec2_client.authorize_security_group_ingress(
                GroupId=sg_id,
                IpPermissions=[
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 22,
                        'ToPort': 22,
                        'IpRanges': [{'CidrIp': f'{ip}/32'}]
                    },
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 80,
                        'ToPort': 80,
                        'IpRanges':[{'CidrIp': '0.0.0.0/0'}]
                    },
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 443,
                        'ToPort': 443,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                    }
                ]
            )

            return sg_id

        except Exception as e:
            print(f"Error with security group: {e}")
            return None

    def create_key_pair(self, key_name):
        """"Create and save SSH Key pair"""
        try:
            #create the key pair
            response = self.ec2_client.create_key_pair(KeyName=key_name)

            #extract private key material
            private_kay = response['KeyMaterial']

            #save to file
            key_path = f'keys/{key_name}.pem'
            os.mkdirs('keys', exist_ok=True)

            with open(key_path, 'w') as f:
                f.write(private_key)

            #set file permissions(0400=read-only by owner)
            os.chmod(key_path, 0o400)

            print("Key pair created")
            return key_path

        except Exception as e:
            print(f"Error creating key pair: {e}")

    def launch_instance(self, instance_type='t2.micro', ami_id=None, key_name=None, security_group_id=None):
        """Launch EC2 instance with security hardening"""
        #Default to Amazon Linux 2 if no AMI specified
        if ami_id is None:
            ami_id = 'ami-0c55b159cbfafe1f0'

        try:
            response = self.ec2_client.run_instances(
                ImageId=ami_id,
                InstanceType=instance_type,
                KeyName=key_name,
                SecurityGroupIds=[security_group_id],
                MinCount=1,
                MaxCount=1,
                TagSpecifications=[{
                    'ResourceType': 'instance',
                    'Tags': [
                        {'Key': 'Name', 'Value': 'auto-launched-instance'},
                        {'Key': 'ManagedBy', 'Value': 'EC2-Auto_Launcher'}
                    ]
                }]
            )

            instance_id = response['Instances'][0]['InstanceId']
            print(f'Instance Launced: {instance_id}')

            #Wait for instance to be running
            print("Waiting for instance to start...")
            waiter = self.ec2_client.get_waiter('instance_running')
            waiter.wait(InstanceIds=[instance_id])

            #Get public IP
            instance_info = self.ec2_client.describe_instances(
                InstanceIds=[instance_id]
            )
            public_ip = instance_info['Reservations'][0]['Instances'][0].get('PublicIpAddress')

            print(f'Instance running at: {public_ip}')
            return instance_id, public_ip
        
        except Exception as e:
            print(f'Failure to lanch: {e}')

    def cleanup_resources(self, sg_name, key_name):
        """Delete test resources"""
        print("Cleanup mode - deleting resources")

        if sg_name:
            try:
                response = self.ec2_client.describe_security_groups(
                    Filters=[{'Name': 'group-name', 'Values': [sg_name]}]
                )
                if response['SecurityGroups']:
                    sg_id = response['SecurityGroups'][0]['GroupId']
                    self.ec2_client.delete_security_group(GroupId=sg_id)
                    print(f"Deleted security group: {sg_name}")
            except Exception as e:
                print(f"Error deleting {e}")

        # Delete key path
        if key_name:
            try:
                self.ec2_client.delete_key_pair(KeyName=key_name)
                print(f"Deleted key pair: {key_name}")

                # delete local path
                key_path = f"keys/{key_name}.pem"
                if os.path.exists(key_path):
                    os.remove(key_path)
                    print(f"Deleted local key: {key_path}")
            except Exception as e:
                print(f"Error deleting key: {e}")

@click.command()
@click.option('--cleanup', is_flag=True, help='Delete test resources')
def main(cleanup):
    print("="*50)
    print("EC2 Auto Launcher")
    print("="*50)

    launcher = EC2Launcher()

    #cleanup mode
    if cleanup:
        launcher.cleanup_resources(sg_name='auto-launcher-sg', key_name='auto-launcher-key')
        return 

    #Test Connection
    if not launcher.test_connection():
        print("AWS connection failed")
        return

    #Get your IP
    my_ip = launcher.get_my_ip()
    if not my_ip:
        print("Count not determine IP")
        return
    
    #Create security group
    sg_id = launcher.get_or_create_security_group(
        name='auto-launcher-sg',
        description='Auto-generated security group',
        ip=my_ip
    )

    #Create ey pair
    key_path = launcher.create_key_pair('auto-launcher-key')

    #Launch instance
    instance_id, public_ip = launcher.launch_instance(
        key_name='auto-launcher-key',
        security_group_id=sg_id
    )

    #show connection info
    if instance_id:
        print("\n"+"="*50)
        print("Succes!")
        print(f"Instance_id: {instance_id}")
        print(f"Public IP: {public_ip}")
        print(f"SSH Command: ssh -i {key_path} ec2-user@{public_ip}")
        print("="*50)


if __name__ == "__main__":
    main()