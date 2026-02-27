import boto3
import os

def lambda_handler(event, context):
    try:
        #extract s3 details from event
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']

        #download file from s3
        s3 = boto3.client('s3')
        s3.download_file(bucket, key, '/tmp/file.txt')

        #uppercase all text in file
        input_file = '/tmp/file.txt'
        output_file = '/tmp/file_uppercased.txt'

        with open(input_file, 'r') as file:
            content=file.read()

        uppercased_content = content.upper()

        with open(output_file, 'w') as file:
            file.write(uppercased_content)

        #upload result
        output_bucket = 'BUCKET_NAME'
        output_key = f'processed/{os.path.basename(key)}'
        s3.upload_file(output_file, output_bucket, output_key)
        print(f"Uploaded to {output_bucket}/{output_key}")

        return {
            'statusCode': 200,
            'body': f'Successfully processed {key}'
        }
    except Exception as e:
        print(f" Error: {e}")
        return {
            'statusCode': 500,
            'body': f'Error: {str(e)}'
        }