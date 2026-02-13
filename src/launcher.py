import boto3
import os
import requests
from dotenv import load_dotenv

load_dotenv()

class EC2Launcher:
    """Main launcher of EC2 instances"""

    def __init__(self):
        """Initialize AWS Clients"""
        self.region = os.getenv('AWS_REGION', 'us-west-2')

        """Initial EC2 Client"""
        self.ec2_client = boto3.client('ec2', region_name = self.region)
        self.ec2_resource = boto3.resource('ec2', region_name = self.region)

        print(f"EC2 Launcher intitiated (Region: {self.region})")

    def test_connection(self):
        """Test AWS connection"""
        try:
            response = self.ec2_client.describe_instances()
            print("AWS connection successful")
            print(f"Found {len(response['Rservations'])} reservations")
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

    def create_security_group(self, name, description):
        """Create security group with SSH access from current IP only"""
        response = ec2.create_security_group(
            GroupName='web-server-sg',
            Description='Web server with SSH, HTTP, HTTPS'
            )

        sg_id = response['GroupId']

        ec2.authorize_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 22,
                    'ToPort': 22,
                    'IpRanges': [{'CidrIp': f'{my_ip}/32'}]
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

    def create_key_pair(self, key_name):
        """"Create and save SSH Key pair"""
        try:
            #create the key pair
            response = self.ec2_client.create_key_pair(KeyName=key_name)

            #extract private key material
            private_kay = response['KeyMaterial']

            #save to file
            key_path = f'keys/{key_name}.pem'
            os.makdirs('keys', exist_ok=True)

            with open(key_path, 'w') as f:
                f.write(private_key)

            #set file permissions(0400=read-only by owner)
            os.chmod(key_path, 0o400)

            print("Key pair created")
            return key_path

        except Exception as e:
            print(f"Error creating key pair: {e}")

    def launch_instance(self, instance_type='t2.micro', ami_id=None):
        """Launch EC2 instance with security hardening"""
        print("launch_instance to be implemented")
        pass

    def main():
        print("="*50)
        print("EC2 Auto Launcher")
        print("="*50)

if __name__ == "__main__":
    main()