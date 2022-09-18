#!/usr/bin/env python3
import os
import configparser

import aws_cdk as cdk

from ec2_image_builder.ec2_image_builder_stack import Ec2ImageBuilderStack
from s3ops.s3ops import s3ops
from parameterStore.parameterStore import parameterStore

config = configparser.ConfigParser()
config.read("paramaters.properties")

param_aws_region = config['DEFAULT']['aws_region']

# AWS bucket where component configurations will be stored.
param_bucket_name = config['DEFAULT']['component_bucketname']

param_base_image = config['DEFAULT']['base_image']

# imagebuilder pipeline will be built with this name
param_image_pipeline = config['DEFAULT']['image_pipeline_name']

# s3 prefix/key for storing components
components_prefix = "components"


app = cdk.App()

s3ops_stack = s3ops(app,
      "s3ops",
      bucket_name=param_bucket_name,
      components_prefix=components_prefix,
      )

image_pipeline_stack = Ec2ImageBuilderStack(app, "Ec2ImageBuilderStack",
                     bucket_name = param_bucket_name,
                     components_prefix = components_prefix,
                     base_image = param_base_image,
                     image_pipeline_name = param_image_pipeline,

    )

image_pipeline_stack.add_dependency(s3ops_stack)

parameter_stack = parameterStore(app, "SsmParameterStack",
                    parameter_value = "fake-ami+get-from-image-builder-stack"
                    )

parameter_stack.add_dependency(image_pipeline_stack)

app.synth()
