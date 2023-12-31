import boto3
import os
import json

def lambda_handler(event, context):
    print("event : {}".format(event))
    try:

        print("np : {}".format(event['Id']))
    except:
        print("No NP")

    dynamodb = boto3.client('dynamodb')
    s3= boto3.resource("s3")
    ddb = boto3.resource('dynamodb')
    table = ddb.Table(os.environ['ddb'])
    sf = boto3.client('stepfunctions')
    try:
        response = dynamodb.query(TableName=os.environ['ddb'], IndexName='np-index', KeyConditionExpression="#np = :np",
                                        ExpressionAttributeNames={
                                            "#np": "np"
                                        },
                                        ExpressionAttributeValues={
                                            ":np": { "S": event['Id'] },
                                        } )
        print("response : {}".format(response))
    except:
        print("Not Valid Query")

    try:
        for nsd in response['Items']:
            if nsd['key']['S'].startswith("nsd/"):
                nsdfile=nsd['key']['S']
                print("NSD : {}".format(nsdfile))
                # Remove file from S3 bucket
                s3.Object(os.environ['bucket'], nsdfile).delete()
                # Delete entry from Dynamodb
                response_s3 = table.delete_item(
                    Key={
                        'key': nsdfile
                    }
                    )
    except:
        print("No parameter too delete NP")
    try:

        for nsd in response['Items']: 
            if event['fp']=="all" and nsd['key']['S'].startswith("vnfd/"):
                vfndfile = nsd['key']['S']
                sfinput = dict(vnfdkey = vfndfile, ddb = os.environ['ddb'], bucket=os.environ['bucket'], fp = nsd['fp']['S'])
                response = sf.start_execution(stateMachineArn = os.environ['sfnvnfd'], input=json.dumps(sfinput))
                # Remove file from S3 bucket
                #s3.Object(os.environ['bucket'], vfndfile).delete()
                # Delete entry from Dynamodb
                #response = table.delete_item(
                #    Key={
                #        'key': vfndfile
                #    }
                #    )
    except:
        print("No parameter to delete all FPs")