import json
import boto3
import os

def lambda_handler(event, context):
    print("event : {}".format(event))
    token = event["token"]
    s3 = boto3.client("s3")
    dynamodb = boto3.client('dynamodb')
    
    try:
        dynamodb.put_item(TableName=os.environ['ddb'], Item={'key': {'S' : 'token'}, 'token' : {'S' : token}, 'NetworkID' : {'S' : event['NetworkID']}})
        #s3.put_object(Bucket=os.environ['buckectname'], Key="task_token.txt", Body=token)
        #s3.put_object(Bucket="tnbautomation", Key="NetworkID.txt", Body=event['NetworkID']['NsLcmOpOccId'])
        response = {
            "statusCode": 200,
            "body": json.dumps("Task token uploaded successfully."),
        }
    except Exception as e:
        response = {
            "statusCode": 500,
            "body": json.dumps(f"Error uploading task token: {str(e)}"),
        }
    
    return response
