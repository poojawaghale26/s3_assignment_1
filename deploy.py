import boto3
import botocore
import os
import zipfile

STACK_NAME = "S3LambdaCopyStack"
TEMPLATE_FILE = "template.yaml"

LAMBDA_ZIP = "lambda.zip"
LAMBDA_FILE = "lambda_function.py"
CODE_BUCKET = os.environ.get("CODE_BUCKET", "pooja-lambda-code-bucket-2026")  # Replace with your S3 bucket name
SOURCE_BUCKET = os.environ.get("SOURCE_BUCKET", "my-source-bucket")
DESTINATION_BUCKET = os.environ.get("DESTINATION_BUCKET", "my-destination-bucket")


def zip_lambda():
    with zipfile.ZipFile(LAMBDA_ZIP, 'w') as zipf:
        zipf.write(LAMBDA_FILE)

    print("Lambda zipped successfully.")


def ensure_bucket(bucket_name):
    s3 = boto3.client('s3')
    try:
        s3.head_bucket(Bucket=bucket_name)
        print(f"S3 bucket exists: {bucket_name}")
    except botocore.exceptions.ClientError as error:
        code = error.response.get('Error', {}).get('Code')
        if code in ('404', 'NoSuchBucket'):
            print(f"Bucket {bucket_name} not found. Creating bucket...")
            region = boto3.session.Session().region_name
            create_args = {'Bucket': bucket_name}
            if region and region != 'us-east-1':
                create_args['CreateBucketConfiguration'] = {'LocationConstraint': region}
            s3.create_bucket(**create_args)
            print(f"Bucket {bucket_name} created.")
        elif code in ('403', 'AccessDenied'):
            raise RuntimeError(
                f"Access denied checking or creating bucket {bucket_name}. "
                "Verify that the bucket exists and your AWS credentials have access to it."
            ) from error
        else:
            raise


def upload_lambda_code(bucket_name):
    ensure_bucket(bucket_name)
    s3 = boto3.client('s3')

    try:
        s3.upload_file(LAMBDA_ZIP, bucket_name, LAMBDA_ZIP)
        print("Lambda zip uploaded to S3 successfully.")
    except botocore.exceptions.ClientError as error:
        code = error.response.get('Error', {}).get('Code')
        if code == 'AccessDenied':
            raise RuntimeError(
                f"AccessDenied uploading {LAMBDA_ZIP} to {bucket_name}. "
                "Verify that the bucket exists and your AWS credentials have PutObject access."
            ) from error
        raise


def deploy_stack(template_body, source_bucket, destination_bucket, code_bucket):
    cf = boto3.client('cloudformation')

    parameters = [
        {'ParameterKey': 'SourceBucketName', 'ParameterValue': source_bucket},
        {'ParameterKey': 'DestinationBucketName', 'ParameterValue': destination_bucket},
        {'ParameterKey': 'LambdaCodeBucketName', 'ParameterValue': code_bucket},
    ]

    try:
        cf.describe_stacks(StackName=STACK_NAME)

        print("Stack exists. Updating stack...")

        cf.update_stack(
            StackName=STACK_NAME,
            TemplateBody=template_body,
            Capabilities=['CAPABILITY_NAMED_IAM'],
            Parameters=parameters
        )

        print("Stack update initiated successfully.")

    except botocore.exceptions.ClientError as e:

        if "does not exist" in str(e):
            print("Stack does not exist. Creating stack...")

            cf.create_stack(
                StackName=STACK_NAME,
                TemplateBody=template_body,
                Capabilities=['CAPABILITY_NAMED_IAM'],
                Parameters=parameters
            )

            print("Stack creation initiated successfully.")

        elif "ROLLBACK_COMPLETE" in str(e):
            print("Deleting failed stack...")

            cf.delete_stack(StackName=STACK_NAME)

            waiter = cf.get_waiter('stack_delete_complete')
            waiter.wait(StackName=STACK_NAME)

            print("Creating new stack...")

            cf.create_stack(
                StackName=STACK_NAME,
                TemplateBody=template_body,
                Capabilities=['CAPABILITY_NAMED_IAM'],
                Parameters=parameters
            )

            print("New stack creation initiated.")

        elif "No updates are to be performed" in str(e):
            print("No changes detected in stack.")

        else:
            raise

if __name__ == '__main__':
    zip_lambda()
    upload_lambda_code(CODE_BUCKET)

    with open(TEMPLATE_FILE) as file:
        template = file.read()

    deploy_stack(template, SOURCE_BUCKET, DESTINATION_BUCKET, CODE_BUCKET)

