import aws_cdk as cdk

from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_s3_deployment as s3_deployment
)

from constructs import Construct

class s3ops(Stack):

    def __init__(self, scope: Construct, construct_id: str, bucket_name: str, components_prefix: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ops_bucket = s3.Bucket(self, 
                               "stack_ops_bucket",
                               bucket_name = bucket_name,
                               versioned = True,
                               removal_policy = cdk.RemovalPolicy.DESTROY,
                               auto_delete_objects = True
                               )

        source_assets = s3_deployment.Source.asset('./components')

        s3_deployment.BucketDeployment(self,
                                       "stacks_components_deployment",
                                       destination_bucket=ops_bucket,
                                       sources=[source_assets],
                                       destination_key_prefix=components_prefix,
                                       retain_on_delete = False
                                       )

