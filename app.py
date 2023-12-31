#!/usr/bin/env python3

import aws_cdk as cdk

from cdk_tnb.cdk_tnb_stack import CdkTnbStack


app = cdk.App()
CdkTnbStack(app, "CdkTnbStack")

app.synth()
