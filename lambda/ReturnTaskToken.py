import json
import boto3
import os

def lambda_handler(event, context):

    print("event : {}".format(event))

    stepfunctions = boto3.client("stepfunctions")
    #s3 = boto3.client("s3")
    dynamodb = boto3.client("dynamodb")
    print("Table Name : {}".format(os.environ['ddb']))
    response = dynamodb.get_item(TableName=os.environ['ddb'], Key={'key':{'S':'token'}})
    print("response : {}".format(response))
    #response = s3.get_object(Bucket="tnbautomation", Key="task_token.txt")
    task_token_content = response["Item"]["token"]["S"]
    #task_token_content = task_token_content.decode("utf-8")
    status=event['detail']['status-details']['status']
    stack=event['detail']['stack-id'].split('/')[1]
    stack=stack.split('-')[1]
    #response=s3.get_object(Bucket="tnbautomation", Key="NetworkID.txt")
    NetworkID=response["Item"]["NetworkID"]["S"].replace('-','')

    print("stack : {}".format(stack))
    print("NetworkID : {}".format(NetworkID))
    print("status : {}".format(status))
    

    if stack==NetworkID:
        if status == "DELETE_COMPLETE" or status=="CREATE_COMPLETE":
            response = stepfunctions.send_task_success(
                    taskToken=task_token_content,
                    output=json.dumps(
                        {
                            "result": status,
                            "job": "success"
                        }
                    ),
                )
        elif status=="CREATE_IN_PROGRESS" or status=="DELETE_IN_PROGRESS":
            print("Job in Progress")
        else:
            response = stepfunctions.send_task_failure(
                taskToken=task_token_content,
                error="Deployment Failed",
                cause=json.dumps(
                    {
                        "result": status,
                        "job": "fail",
                    }
                ),
            )
