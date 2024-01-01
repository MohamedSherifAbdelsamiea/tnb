import boto3
import os
import json

def lambda_handler(event, context):

    s3= boto3.resource("s3")
    # Remove file from S3 bucket
    s3.Object(os.environ['bucket'], event['vfndfile']).delete()