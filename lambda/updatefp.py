import json
import boto3
import os


def lambda_handler(event, context):
    print("event : {}".format(event))
    
    dynamodb = boto3.client('dynamodb')
    
    for network in event['NetworkPackages']:
        np = network['Id']
        for functions in network['VnfPkgIds']:
            print("np : {}".format(np))
            print("fp : {}".format(functions))
            try:

                response = dynamodb.query(TableName=os.environ['ddb'], IndexName='fp-index', KeyConditionExpression="#fp = :fp",
                                        ExpressionAttributeNames={
                                            "#fp": "fp"
                                        },
                                        ExpressionAttributeValues={
                                            ":fp": { "S": functions },
                                        } )
                print("response : {}".format(response))
                print("key : {}".format(response['Items'][0]['key']['S']))
                mykey= response['Items'][0]['key']['S']

                response = dynamodb.update_item(TableName=os.environ['ddb'], Key={'key': {'S': mykey}},
                                                UpdateExpression="set np = :r",
                                                ExpressionAttributeValues={':r' : {'S': np}},
                                                ReturnValues="UPDATED_NEW",)
                
                print("Table update response : {}".format(response))
            except:
                print("Not a valid fp")
            
        
    