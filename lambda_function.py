import boto3
import os

s3 = boto3.client('s3')


def lambda_handler(event, context):
    source_bucket = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']
    destination_bucket = os.environ['DESTINATION_BUCKET']

    s3.copy_object(
        Bucket=destination_bucket,
        CopySource={
            'Bucket': source_bucket, 
            'Key': object_key},
        Key=object_key
    )

    print(f"{object_key} copied successfully")

    return {
        'statusCode': 200,
        'body': 'File copied successfully'
    }