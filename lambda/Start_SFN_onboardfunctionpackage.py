import boto3
import os
import json


def lambda_handler(event, context):
    print("Event : {}".format(event))
    print("onboardfunctionpackage_arn : {}".format(os.environ['onboardfunctionpackage_arn']) )
    sf = boto3.client('stepfunctions')
    response = sf.start_execution(stateMachineArn = os.environ['onboardfunctionpackage_arn'], input=json.dumps(event))