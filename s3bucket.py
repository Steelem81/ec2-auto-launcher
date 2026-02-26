import boto3
from botocore.exceptions import ClientError

class S3Manager:
    def __init__(self, bucket_name, region='us-west-2'):
        self.s3 = boto3.client('s3', region_name=region)
        self.bucket_name = bucket_name
        self.region = region
    
    def create_bucket(self):
        """Create an S3 bucket"""
        print(self.bucket_name)
        try:    
            if self.region == 'us-east-1':
                response = self.s3.create_bucket(Bucket=self.bucket_name)
            else:
                response = self.s3.create_bucket(
                    Bucket=self.bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': self.region}
                )
            print(f"Bucket created: {self.bucket_name}")
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                print(f"Bucket already exists: {self.bucket_name}")
                return False
            else:
                print(f"Failed to create bucket: {e}")
                return False
    
    def upload_file(self, local_path, s3_key, encrypt=True):
        try:
            extra_args = {}
            if encrypt:
                extra_args['ServerSideEncryption'] =  'AES256'
                self.s3.upload_file(local_path, self.bucket_name, s3_key, ExtraArgs=extra_args)
                print(f"File uploaded to bucket: {s3_key}")
                return True
        except FileNotFoundError:
            print(f"Local file not found: {local_path}")
            return False
        except ClientError as e:
            print(f"Failed to upload file: {e}")
            return False
    
    def list_files(self):
        bucket = self.s3.Bucket(self.bucket_name)
        try:
            self.list_objects_v2(
                Bucket=bucket,
                Delimber=',',
            )
        except Exception as e:
            print(f"Failed to list files: {e}")
    
    def download_file(self, s3_key, local_path):
        try:
            bucket = s3.Bucket(self.bucket_name)
            self.download_file(bucket, s3_key, local_path)
            print(f"Downloaded {s3_key} to {local_path}")
        except Exception as e:
            print(f"Failed to download file: {e}")

    def generate_presigned_url(self, s3_key, expiration=3600):
        try:
            bucket = s3.Bucket(self.bucket_name)
            url = self.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket, 'Key': s3_key},
                ExpiresIn=expiration
            )
            print(f"Presigned url created: {url}")
        except:
            print(f"failed to generate url: {e}")
    
    def cleanup(self):
        try:
            response = self.s3.list_objects_v2(Bucket=self.bucket_name)

            if 'Contents' in response:
                objects = [{'Key': obj['Key']} for obj in response['Contents']]
                self.s3.delete_objects(
                    Bucket=self.bucket_name,
                    Delete={'Objects': objects}
                )
                print(f"Bucket and all items deleted")
            
            self.s3.delete_bucket(Bucket=self.bucket_name)
            print(f"Bucket deleted: {self.bucket_name}")
            return True
        except ClientError as e:
            print(f"Failed to cleanup: {e}")
            return False
    
if __name__ == "__main__":
    manager = S3Manager('the-test-bucket-12345')
    print("="*50)
    print("Testing S3 Manager")
    print("="*50)

    print("-"*50)
    print("Testing create bucket")
    manager.create_bucket()

    print("-"*50)
    print("Testing upload file")
    with open('test.txt', 'w') as f:
        f.write('Hello S3!')
    manager.upload_file('test.txt', 'uploads/test.txt')

    print("-"*50)
    print("Cleaning up")
    manager.cleanup()