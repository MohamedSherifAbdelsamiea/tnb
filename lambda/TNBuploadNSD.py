import json
import boto3

def lambda_handler(event, context):
    # TODO implement
    print("event content")
    print(event)
   
   
    s3 = boto3.client('s3')
    data = s3.get_object(Bucket=event['detail']['bucket']['name'], Key=event['detail']['object']['key'])
    
    
    client = boto3.client('tnb')
    response = client.put_sol_network_package_content(
    contentType='application/zip',
    file=data['Body'].read(),
    nsdInfoId=event['metadata']['Id']
    )
    return {
        'Id': event['metadata']['Id']

    }
    