from constructs import Construct
from aws_cdk import (
    Duration,
    Fn,
    Stack,
    aws_s3 as _s3,
    aws_ec2 as _ec2,
    aws_lambda as _lambda,
    aws_iam as _iam,
    aws_dynamodb as ddb,
    aws_stepfunctions as sfn,
    aws_events as events,
    aws_events_targets as targets,
    cloudformation_include as cfn_inc,
    aws_iam as role,
    RemovalPolicy
)
import json
import boto3


class CdkTnbStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        #Create Role for Step Function

        sf_role = role.Role(self, "stepfunction_role", assumed_by=role.ServicePrincipal("states.amazonaws.com"))
        sf_role.add_managed_policy(role.ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess"))

        #Create Role for AWS Lambda

        lambda_role = role.Role(self, "lambda_role", assumed_by=role.ServicePrincipal("lambda.amazonaws.com"))
        lambda_role.add_managed_policy(role.ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess"))

        # Create DynamodB

        my_table = ddb.Table(self, 'tnbconfig',
                             partition_key={'name': 'key', 'type': ddb.AttributeType.STRING})
        
        my_table.add_global_secondary_index(index_name="fp-index", partition_key={'name': 'fp', 'type': ddb.AttributeType.STRING})
        my_table.add_global_secondary_index(index_name="np-index", partition_key={'name': 'np', 'type': ddb.AttributeType.STRING})



        # Create S3 Bucket for TNB Packages and NSD

        uid = Fn.select(0, Fn.split('-', Fn.select(2, Fn.split('/', self.stack_id))))
        bucket = _s3.Bucket(self, "MyBucket", bucket_name='tnbpackages-cdk-{}'.format(uid), removal_policy=RemovalPolicy.DESTROY, event_bridge_enabled=True)

        # Create key pair in EC2 in the same region of TNB deployment
        #cfnKeyPair = _ec2.CfnKeyPair(self, 'MyCfnKeyPair' , key_name='tnb-{}-keypair'.format(Stack.of(self).region))

        # Create Lambda Functions artifacts
        lambdaTNBUploadCSAR = _lambda.Function(
            self, 'lambdaTNBUploadCSAR',
            runtime=_lambda.Runtime.PYTHON_3_10,
            code=_lambda.Code.from_asset('lambda'),
            handler='TNBUploadCSAR.lambda_handler',
            timeout=Duration.minutes(3),
            role=lambda_role
        )
        lambdaTNBuploadNSD = _lambda.Function(
            self, 'lambdaTNBuploadNSD',
            runtime=_lambda.Runtime.PYTHON_3_10,
            code=_lambda.Code.from_asset('lambda'),
            handler='TNBuploadNSD.lambda_handler',
            timeout=Duration.minutes(3),
            role=lambda_role
        )
        lambdaCheckdepolymentstatus = _lambda.Function(
            self, 'lambdaCheckdepolymentstatus',
            runtime=_lambda.Runtime.PYTHON_3_10,
            code=_lambda.Code.from_asset('lambda'),
            handler='Checkdepolymentstatus.lambda_handler',
            timeout=Duration.minutes(3),
            role=lambda_role,
            environment={
                'ddb' : my_table.table_name,
            }
        )
        lambdaReturnTaskToken = _lambda.Function(
            self, 'lambdaReturnTaskToken',
            runtime=_lambda.Runtime.PYTHON_3_10,
            code=_lambda.Code.from_asset('lambda'),
            handler='ReturnTaskToken.lambda_handler',
            timeout=Duration.minutes(3),
            role=lambda_role,
            environment={
                'ddb' : my_table.table_name,
            }
        )

        lambdaupdatefp = _lambda.Function(
            self, 'lambdaupdatefp',
            runtime=_lambda.Runtime.PYTHON_3_10,
            code=_lambda.Code.from_asset('lambda'),
            handler='updatefp.lambda_handler',
            timeout=Duration.minutes(3),
            role=lambda_role,
            environment={
                'ddb' : my_table.table_name,
            }
        )


        # Update Step Function ASL file with CDK parameters
        file_path = 'stepfunction/onboardfunctionpackage.json'
        with open(file_path, 'r', encoding='utf-8') as json_file:
            myasl = json.load(json_file)
        myasl['States']['DynamoDB UploadVNFD']['Parameters']['TableName']=my_table.table_name
        myasl['States']['DynamoDB UploadNSD']['Parameters']['TableName']=my_table.table_name
        myasl['States']['Upload CSAR File']['Parameters']['FunctionName']=lambdaTNBUploadCSAR.function_arn
        myasl['States']['UploadNSDFile']['Parameters']['FunctionName']=lambdaTNBuploadNSD.function_arn
        myasl['States']['Update fps']['Parameters']['FunctionName']=lambdaupdatefp.function_arn
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(myasl, json_file)

        

        # Create State Machine Step Function - onboardfunctionpackage
        file = open("stepfunction/onboardfunctionpackage.json","rt").read()
        """ cfnStateMachine_onboardfunctionpackage = sfn.CfnStateMachine(
            self, 'onboardfunctionpackage', role_arn=sf_role.role_arn,
            definition_string=file) """
        

        #file = open("stepfunction/onboardfunctionpackage.json","rt").read()
        
        cfnStateMachine_onboardfunctionpackage = sfn.StateMachine(
            self, 'onboardfunctionpackage', role=sf_role,
            definition_body=sfn.DefinitionBody.from_string(file)
        )

        # Update Step Function ASL file with CDK parameters
        file_path = 'stepfunction/Createnetworkinstance.json'
        with open(file_path, 'r', encoding='utf-8') as json_file:
            myasl = json.load(json_file)
        myasl['States']['DynamoDB PutItem']['Parameters']['TableName']=my_table.table_name
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(myasl, json_file)

        # Create State Machine Step Function - Createnetworkinstance
        file = open("stepfunction/Createnetworkinstance.json","rt").read()
        cfnStateMachine_Createnetworkinstance = sfn.CfnStateMachine(
            self, 'Createnetworkinstance', role_arn=sf_role.role_arn,
            definition_string=file
        )

        # Update Step Function ASL file with CDK parameters
        file_path = 'stepfunction/InstantiateNS.json'
        with open(file_path, 'r', encoding='utf-8') as json_file:
            myasl = json.load(json_file)
        myasl['States']['Checkdepolymentstatus']['Parameters']['FunctionName']=lambdaCheckdepolymentstatus.function_arn
        myasl['States']['DynamoDB Token']['Parameters']['TableName']=my_table.table_name
        myasl['States']['DynamoDB Token After Rollback']['Parameters']['TableName']=my_table.table_name
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(myasl, json_file)


        # Create State Machine Step Function - InstantiateNS
        file = open("stepfunction/InstantiateNS.json","rt").read()
        cfnStateMachine_InstantiateNS = sfn.CfnStateMachine(
            self, 'InstantiateNS', role_arn=sf_role.role_arn,
            definition_string=file
        )
        
        OnboardPackage_rule = events.Rule(self,'OnboardPackage_rule', event_pattern=events.EventPattern(source=['aws.s3'],detail={
            "bucket": {
            "name": [bucket.bucket_name]
                    }
                },detail_type=["Object Created"]))
        #OnboardPackage_rule.add_target(targets.LambdaFunction(lambdaStart_SFN_onboardfunctionpackage))
        OnboardPackage_rule.add_target(targets.SfnStateMachine(cfnStateMachine_onboardfunctionpackage))

        # Update Step Function ASL file with CDK parameters
        file_path = 'stepfunction/Deletenetworkinstance.json'
        with open(file_path, 'r', encoding='utf-8') as json_file:
            myasl = json.load(json_file)
        myasl['States']['DynamoDB DeleteItem']['Parameters']['TableName']=my_table.table_name
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(myasl, json_file)

        # Create State Machine Step Function - Deletenetworkinstance
        file = open("stepfunction/Deletenetworkinstance.json","rt").read()
        cfnStateMachine_Deletenetworkinstance = sfn.CfnStateMachine(
            self, 'Deletenetworkinstance', role_arn=sf_role.role_arn,
            definition_string=file
        )

        # Update Step Function ASL file with CDK parameters
        file_path = 'stepfunction/TerminateNS.json'
        with open(file_path, 'r', encoding='utf-8') as json_file:
            myasl = json.load(json_file)
        myasl['States']['Checkdepolymentstatus']['Parameters']['FunctionName']=lambdaCheckdepolymentstatus.function_arn
        myasl['States']['DynamoDB DeleteToken']['Parameters']['TableName']=my_table.table_name
        myasl['States']['DynamoDB DeleteTokenAfterRollback']['Parameters']['TableName']=my_table.table_name
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(myasl, json_file)

        # Create State Machine Step Function - TerminateNS
        file = open("stepfunction/TerminateNS.json","rt").read()
        cfnStateMachine_TerminateNS = sfn.CfnStateMachine(
            self, 'TerminateNS', role_arn=sf_role.role_arn,
            definition_string=file
        )

        # Create Event Bridge Rule for TNB-CloudFormation-CreateComplete
        CF_CreateComplete_rule = events.Rule(self,'CF_CreateComplete_rule', event_pattern=events.EventPattern(source=['aws.cloudformation'],detail={
                            "status-details": {
                            "status": ["CREATE_COMPLETE"]
                            }
                            },detail_type=["CloudFormation Stack Status Change"]))
        CF_CreateComplete_rule.add_target(targets.LambdaFunction(lambdaReturnTaskToken))

        # Create Event Bridge Rule for TNB-CloudFormation-DeleteComplete
        CF_DeleteComplete_rule = events.Rule(self,'CF_DeleteComplete_rule', event_pattern=events.EventPattern(source=['aws.cloudformation'],detail={
                            "status-details": {
                            "status": ["DELETE_COMPLETE"]
                            }
                            },detail_type=["CloudFormation Stack Status Change"]))
        CF_DeleteComplete_rule.add_target(targets.LambdaFunction(lambdaReturnTaskToken))

        # Create Event Bridge Rule for TNB-CloudFormation-CREATEFAILED
        CF_CREATEFAILED_rule = events.Rule(self,'CF_CreateFailed_rule', event_pattern=events.EventPattern(source=['aws.cloudformation'],detail={
                            "status-details": {
                            "status": ["ROLLBACK_COMPLETE"]
                            }
                            },detail_type=["CloudFormation Stack Status Change"]))
        CF_CREATEFAILED_rule.add_target(targets.LambdaFunction(lambdaReturnTaskToken))

        # Update Step Function ASL file with CDK parameters
        file_path = 'stepfunction/Deletetnbfunction.json'
        with open(file_path, 'r', encoding='utf-8') as json_file:
            myasl = json.load(json_file)
        myasl['States']['Query Dynamodb']['Parameters']['TableName']=my_table.table_name
        myasl['States']['Map']['ItemProcessor']['States']['DeleteObject']['Parameters']['Bucket']=bucket.bucket_name
        myasl['States']['Map']['ItemProcessor']['States']['DynamoDB DeleteItem']['Parameters']['TableName']=my_table.table_name
        myasl['States']['Map delete only np']['ItemProcessor']['States']['DeleteObject np']['Parameters']['Bucket']=bucket.bucket_name
        myasl['States']['Map delete only np']['ItemProcessor']['States']['DynamoDB DeleteItem np']['Parameters']['TableName']=my_table.table_name
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(myasl, json_file)
            
        # Create State Machine Step Function - Delete TNB Packages
        file = open("stepfunction/Deletetnbfunction.json","rt").read()
        cfnStateMachine_Deletetnbfunction = sfn.CfnStateMachine(
            self, 'Deletetnbfunction', role_arn=sf_role.role_arn,
            definition_string=file
        )

        # Create AWS TNB service role for Amazon EKS cluster

        client = boto3.client('iam')

        try:
            response = client.get_role(
                RoleName='TNBEKSClusterRole'
                    )
            if response['Role']['RoleName']== 'TNBEKSClusterRole':
                TNBEKSClusterRole_exist = True
        except:
            TNBEKSClusterRole_exist = False
        try:
            response = client.get_role(
                RoleName='TNBEKSNodeRole'
                    )
            if response['Role']['RoleName']== 'TNBEKSNodeRole':
                TNBEKSNodeRole_exist = True
        except:
            TNBEKSNodeRole_exist = False
        try:
            response = client.get_role(
                RoleName='TNBMultusRole'
                    )
            if response['Role']['RoleName']== 'TNBMultusRole':
                TNBMultusRole_exist = True
        except:
            TNBMultusRole_exist = False
        try:
            response = client.get_role(
                RoleName='TNBHookRole'
                    )
            if response['Role']['RoleName']== 'TNBHookRole':
                TNBHookRole_exist = True
        except:
            TNBHookRole_exist = False
    
        if TNBEKSClusterRole_exist == False:
            template = cfn_inc.CfnInclude(self, "TNBEKSClusterRole", template_file="cfTemplates/TNBEKSClusterRole.yaml")

        # Create AWS TNB service role for Amazon EKS node group
        if TNBEKSNodeRole_exist == False:
            template = cfn_inc.CfnInclude(self, "TNBEKSNodeRole", template_file="cfTemplates/TNBEKSNodeRole.yaml")

        # Create AWS TNB service role for Multus
        if TNBMultusRole_exist == False:
            template = cfn_inc.CfnInclude(self, "TNBMultusRole", template_file="cfTemplates/TNBMultusRole.yaml")

        # Create AWS TNB service role for a life-cycle hook policy
        if TNBHookRole_exist == False:
            template = cfn_inc.CfnInclude(self, "TNBHookRole", template_file="cfTemplates/TNBHookRole.yaml")
        


        