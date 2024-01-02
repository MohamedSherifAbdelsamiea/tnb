# CDK Initialization from AWS cloudshell:


* git clone https://github.com/MohamedSherifAbdelsamiea/tnb.git
* cd tnb
* sudo npm install -g aws-cdk
* pip install -r requirements.txt
* cdk bootstrap
* cdk deploy

# Architecture

![image](https://github.com/MohamedSherifAbdelsamiea/tnb/assets/38582068/78bc15fe-fe13-4936-83e8-55d8ff3af34a)

# Description

Define the individual network function (NF) resource requirements, such as compute, storage, and databases, as network function descriptors (NFDs) in the Topology and Orchestration Specification for Cloud Applications (TOSCA) format. Along with these requirements, provide the software images of NFs from your independent software vendor (ISV) as pointers to Amazon ECR images.(VNFDs)

Once upload those files to the respective S3 buckets (tnbpackages-cdkxxxxxx) in the correct paths, EventBridge will be generated to consume those inputs and create function packages and network packages respectively. pointers to the created function packages and network packages are also stored in dynamodb table (CdkTnbStack-tnbconfigxxxxxx)

A network package will be created in the formate (np-xxxxxxx). you can get the created np record in dynamodb table by query the key of S3. 

Use Createnetworkinstance-xxxxx with json input as below to create a network instance. inputs are “Id” which is the network package created and “name” a name for the network instance as example below:

{
"Id": "np-xxxxxxxxxxxxxx",
"name": "5G"
}

Use TerminateNS-xxxxxx step function to instantiate a network. Step function take the below input as JSON object

{
"Id": "ni-xxxxxxxxxxxxxxxx"
}

ni object could be query from dynamodb as a key and associated with attribute np (network package)

Use TerminateNS-xxxxxxxx to terminate the network instance. Step function take the below input as JSON object:

{
"Id": "ni-xxxxxxxxxxxxxxxx"
}

ni object could be query from dynamodb as a key and associated with attribute np (network package)

use Deletenetworkinstance-xxxxx to delete a network instance,  Step function take the below input as JSON object:

{
"Id": "ni-xxxxxxxxxxxxxxxx"
}

ni object could be query from dynamodb as a key and associated with attribute np (network package)

Use DeleteNetworkPackages-xxxxxxx to delete np. step function take the below input as JSON object

{
"Id": "np-xxxxxxxxxxx",
"fp": "all" → optional
}

fp with value all could be included as input to step function which effectively delete all function packages associated with network package and remove all associated files from S3 bucket



# Welcome to your CDK Python project!

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
