# CDK Initialization from AWS cloudshell:
** Account should be Business or Enterprise support plan

* git clone https://github.com/MohamedSherifAbdelsamiea/tnb.git
* cd tnb
* sudo npm install -g aws-cdk
* pip install -r requirements.txt
* cdk bootstrap
* cdk deploy

# Architecture

![image](https://github.com/MohamedSherifAbdelsamiea/tnb/assets/38582068/c490608e-cc1b-47ed-965e-a311a9960d6c)

# Description

Define the individual network function (NF) resource requirements, such as compute, storage, and databases, as network function descriptors (NFDs) in the Topology and Orchestration Specification for Cloud Applications (TOSCA) format. Along with these requirements, provide the software images of NFs from your independent software vendor (ISV) as pointers to Amazon ECR images.(VNFDs)

Once you upload those files to the respective S3 buckets (tnbpackages-cdkxxxxxx) in the correct paths, EventBridge will trigger the process to consume those inputs and create function packages and network packages. References to the created function packages and network packages will also be stored in the DynamoDB table (CdkTnbStack-tnbconfigxxxxxx) for tracking. 


A network package with the Id np-xxxxxxx will be generated. The network package record can be retrieved from the DynamoDB table by querying the table with the associated S3 key.

To create a network instance, invoke the state machine located at Createnetworkinstance-xxxxx. Provide the following JSON input:
{
"Id": "<network package id>",
"name": "<desired name for network instance>"
}
The input parameters are:
- "Id" - The ID of the network package to use for the instance
- "name" - A name to identify the new network instance
For example:
{
"Id": "np-0983abdef5566789",
"name": "MyNetworkInstance"
}

This will invoke the state machine to create a new network instance using the provided network package and name

To instantiate a network, please utilize the InstantiateNS-xxxxxxxxx step function located at InstantiateNS-xxxxxxxx. This step function takes a JSON object as input with the following structure:

{
 "Id": "ni-xxxxxxxxxxxxxxxx"
}

The ni object can be queried from DynamoDB using the Id as a key. This object is associated with the np (network package) attribute

To terminate the network instance, invoke the TerminateNS-xxxxxxxx step function with the following input JSON:
{
"Id": "ni-xxxxxxxxxxxxxxxx"
}
The network instance Id can be queried from DynamoDB using the ID as the hash key and "np" as the attribute containing the associated network package.
To delete a network instance, invoke the DeleteNetworkInstance-xxxxx step function with the following input JSON:
{
"Id": "ni-xxxxxxxxxxxxxxxx"
}
The network instance ID can be queried from DynamoDB using the ID as the hash key.
To delete a network package, invoke the Deletetnbfunction-xxxxxxx step function with the following input JSON:
{
"Id": "np-xxxxxxxxxxx",
"fp": "all" // Optional
}
Including "fp" : "all" will delete all associated function packages and remove their files from the S3 bucket. The network package ID can be used to query DynamoDB.


<!-- # Welcome to your CDK Python project!

You should explore the contents of this project. It demonstrates a CDK app with an instance of a stack (`cdk_tnb_stack`)
which contains an Amazon SQS queue that is subscribed to an Amazon SNS topic.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization process also creates
a virtualenv within this project, stored under the .venv directory.  To create the virtualenv
it assumes that there is a `python3` executable in your path with access to the `venv` package.
If for any reason the automatic creation of the virtualenv fails, you can create the virtualenv
manually once the init process completes.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

You can now begin exploring the source code, contained in the hello directory.
There is also a very trivial test included that can be run like this:

```
$ pytest
```

To add additional dependencies, for example other CDK libraries, just add to
your requirements.txt file and rerun the `pip install -r requirements.txt`
command.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
 -->