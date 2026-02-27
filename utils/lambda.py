import boto3

def lambda_handler(event, context):
    #extract s3 details from event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    

    #download file from s3
    s3 = boto3.client('s3')
    s3.download_file(bucket, key, '/tmp/file.txt')

    #uppercase all text in file
    input_file = '/tmp/file.txt'
    output_file = 'file_uppercased.txt'

    with open(input_file, 'r') as file:
        content=file.read()

    uppercased_content = content.upper()

    with open(output_file, 'w') as file:
        file.write(uppercased_content)

    #upload result
    s3.upload_file(f'/tmp/{output_file}', 'output-bucket', output_file)