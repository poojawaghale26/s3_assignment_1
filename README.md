# AWS S3 Event-Driven File Copy using Lambda

## Overview

This project demonstrates an event-driven architecture using AWS services.

Whenever a file is uploaded to the source S3 bucket:

1. Amazon S3 generates an ObjectCreated event.
2. AWS Lambda is triggered automatically.
3. Lambda copies the uploaded object to the destination S3 bucket.

## AWS Services Used

* Amazon S3
* AWS Lambda
* AWS IAM
* AWS CloudFormation
* GitHub Actions
* Python (Boto3)

## Project Structure

```text
s3-Assignment_1/
│
├── .github/workflows/deploy.yml
├── lambda_function.py
├── deploy.py
├── template.yaml
├── requirements.txt
└── README.md
```

## Deployment

Push code to the main branch:

```bash
git add .
git commit -m "Deploy AWS Infrastructure"
git push origin main
```

GitHub Actions automatically deploys the infrastructure to AWS.

## Architecture

S3 Source Bucket → Lambda Trigger → Destination Bucket

## Author

Pooja Waghale
